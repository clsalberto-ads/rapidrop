# RapiDrop — Mapas, Rastreamento e Roteirização

> Stack open-source de mapas e geolocalização para web + mobile.
> Estratégias de ordenação e otimização de entregas.

---

## Índice

1. [Stack de Mapas (Open Source)](#1-stack-de-mapas-open-source)
2. [Mapas no Web (Next.js)](#2-mapas-no-web-nextjs)
3. [Mapas no Mobile (React Native)](#3-mapas-no-mobile-react-native)
4. [Geocoding — Endereço → Coordenadas](#4-geocoding--endereço--coordenadas)
5. [Routing Engine — Cálculo de Rotas](#5-routing-engine--cálculo-de-rotas)
6. [Rastreamento GPS dos Entregadores](#6-rastreamento-gps-dos-entregadores)
7. [Atribuição Inteligente de Entregas](#7-atribuição-inteligente-de-entregas)
8. [Roteirização de Múltiplas Entregas](#8-roteirização-de-múltiplas-entregas)
9. [Infraestrutura e Custo](#9-infraestrutura-e-custo)

---

## 1. Stack de Mapas (Open Source)

### 1.1 Filosofia

```
┌─────────────────────────────────────────────────────────────┐
│              MAPAS 100% OPEN SOURCE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🗺️  Dados:        OpenStreetMap (OSM)                     │
│  🧭  Renderização:  MapLibre GL (fork do Mapbox GL)         │
│  📍  Geocoding:     Nominatim + Pelias                      │
│  🛣️  Rotas:         OSRM / GraphHopper                      │
│  📡  Autohospedável: Tudo roda na nossa infra               │
│                                                             │
│  Zero custo de API. Zero dependência de fornecedor.         │
│  Controle total dos dados e da disponibilidade.             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Comparação: Antes vs Depois

| Serviço | ANTES (pago) | DEPOIS (open source) | Economia |
|---------|:------------:|:--------------------:|:--------:|
| **Mapas (renderização)** | Google Maps API / Mapbox | MapLibre GL + tiles OSM | ~R$ 5.000/mês |
| **Geocoding** | Google Places API | Nominatim + Pelias | ~R$ 1.000/mês |
| **Rotas** | Google Directions API | OSRM / GraphHopper | ~R$ 3.000/mês |
| **Autocomplete** | Google Places API | Pelias + OSM | ~R$ 2.000/mês |
| **Total** | ~R$ 11.000/mês | **R$ 0 (infra própria)** | **R$ 132.000/ano** |

> Além do custo: independência total de APIs de terceiros.
> Google Maps API sobe preço todo ano. OpenStreetMap é da comunidade, para sempre.

### 1.3 Stack Completa

```
┌─────────────────────────────────────────────────────────────────┐
│                  STACK DE GEOLOCALIZAÇÃO                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🗺️  DADOS CARTOGRÁFICOS                                        │
│  ├─ OpenStreetMap (fonte de dados global)                       │
│  ├─ OpenMapTiles (vector tiles processados do OSM)             │
│  └─ GeoJSON / .mbtiles (armazenamento local dos tiles)         │
│                                                                  │
│  🧭  RENDERIZAÇÃO                                               │
│  ├─ Web:    MapLibre GL JS (v4.x)                              │
│  │          → Componente React: react-map-gl                    │
│  │                                                              │
│  └─ Mobile: MapLibre GL Native                                  │
│             → Componente RN: @maplibre/maplibre-react-native    │
│                                                                  │
│  📍  GEOCODING (endereço ↔ coordenadas)                         │
│  ├─ Nominatim (pesquisa por texto: "Rua das Flores, Natal")    │
│  ├─ Pelias / Photon (autocomplete rápido para buscas)          │
│  └─ PostGIS (consultas geográficas no banco)                   │
│                                                                  │
│  🛣️  ROTEAMENTO (cálculo de distâncias e rotas)                │
│  ├─ OSRM (rota mais rápida, ótimo para carro)                 │
│  ├─ GraphHopper (suporte a bike, pedestre, caminhão)           │
│  └─ pgRouting (rotas direto no PostgreSQL)                     │
│                                                                  │
│  📡  GPS EM TEMPO REAL                                          │
│  ├─ expo-location (captura GPS no mobile)                      │
│  ├─ WebSocket (envio de posição a cada 5s)                     │
│  └─ Redis Geo (busca de entregadores próximos)                 │
│                                                                  │
│  🗄️  ARMAZENAMENTO GEOGRÁFICO                                   │
│  └─ PostgreSQL + PostGIS (ST_DWithin, ST_Distance, índices)    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Mapas no Web (Next.js)

### 2.1 Stack

```
Biblioteca:   react-map-gl (v7.x) ← MapLibre GL JS wrapper
Tiles:        OpenFreeMap (gratuito) ou auto-hospedado
Instalação:   npm install react-map-gl maplibre-gl
```

### 2.2 Componente de Mapa

```tsx
// src/components/map/DeliveryMap.tsx

'use client'

import Map, { Marker, NavigationControl, Popup, Source, Layer } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { MapRef, ViewState } from 'react-map-gl/maplibre'
import { useRef, useState } from 'react'

// Tile gratuito (OpenFreeMap) — sem chave de API
const TILE_URL = 'https://tiles.openfreemap.org/styles/liberty'

interface DeliveryMapProps {
  riders: RiderLocation[]
  route?: GeoJSON.FeatureCollection  // rota calculada pelo OSRM
  onRiderClick?: (riderId: string) => void
}

interface RiderLocation {
  id: string
  name: string
  latitude: number
  longitude: number
  status: 'online' | 'busy' | 'offline'
  lastUpdate: string
}

export function DeliveryMap({ riders, route, onRiderClick }: DeliveryMapProps) {
  const mapRef = useRef<MapRef>(null)
  const [popup, setPopup] = useState<RiderLocation | null>(null)
  const [viewState, setViewState] = useState<ViewState>({
    latitude: -5.7945,   // Natal/RN (padrão)
    longitude: -35.211,
    zoom: 13,
  })

  return (
    <Map
      ref={mapRef}
      {...viewState}
      onMove={evt => setViewState(evt.viewState)}
      mapStyle={TILE_URL}
      style={{ width: '100%', height: '100%' }}
      attributionControl={false}
    >
      {/* Entregadores */}
      {riders.map(rider => (
        <Marker
          key={rider.id}
          latitude={rider.latitude}
          longitude={rider.longitude}
          onClick={() => {
            setPopup(rider)
            onRiderClick?.(rider.id)
          }}
        >
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold
            ${rider.status === 'online' ? 'bg-green-500' : ''}
            ${rider.status === 'busy' ? 'bg-yellow-500' : ''}
            ${rider.status === 'offline' ? 'bg-gray-400' : ''}
          `}>
            🛵
          </div>
        </Marker>
      ))}

      {/* Rota (linha no mapa) */}
      {route && (
        <Source id="route" type="geojson" data={route}>
          <Layer
            id="route-line"
            type="line"
            paint={{
              'line-color': '#3b82f6',
              'line-width': 4,
              'line-opacity': 0.8,
            }}
          />
        </Source>
      )}

      {/* Popup do entregador */}
      {popup && (
        <Popup
          latitude={popup.latitude}
          longitude={popup.longitude}
          onClose={() => setPopup(null)}
          closeButton={true}
        >
          <div className="p-2">
            <p className="font-bold">{popup.name}</p>
            <p className="text-sm text-gray-600">{popup.status}</p>
            <p className="text-xs text-gray-400">
              Última atualização: {new Date(popup.lastUpdate).toLocaleTimeString()}
            </p>
          </div>
        </Popup>
      )}

      {/* Controles */}
      <NavigationControl position="bottom-right" />
    </Map>
  )
}
```

### 2.2 Mapa no Painel do Lojista

```
┌─────────────────────────────────────────────────────────────────┐
│  🗺️  ACOMPANHAMENTO DE ENTREGAS                     [ 🔄 ]     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │    🛵 João (online)         🛵 Maria (ocupada)          │    │
│  │    📍 Loja                    📦 Cliente                 │    │
│  │                                                         │    │
│  │    [ Mapa com entregadores, rota e marcadores ]          │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────────────────────┐                      │
│  │  📋 Entregas Ativas                   │                      │
│  │  João → Rua das Flores, 123  ~8 min   │                      │
│  │  Maria → Av. Paulista, 1000  ~15 min  │                      │
│  │  Carlos → Rua 7 de Setembro  ~5 min   │                      │
│  └───────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Mapa no Site do Cliente (Acompanhamento)

```tsx
// components/map/OrderTracking.tsx

interface TrackingProps {
  merchantLocation: { lat: number; lng: number }
  riderLocation: { lat: number; lng: number } | null
  destination: { lat: number; lng: number }
}

export function OrderTracking({ merchantLocation, riderLocation, destination }: TrackingProps) {
  return (
    <Map
      initialViewState={{
        latitude: merchantLocation.lat,
        longitude: merchantLocation.lng,
        zoom: 14,
      }}
      mapStyle={TILE_URL}
      style={{ width: '100%', height: 300 }}
    >
      {/* Loja */}
      <Marker latitude={merchantLocation.lat} longitude={merchantLocation.lng}>
        <span className="text-2xl">🏪</span>
      </Marker>

      {/* Entregador (se já saiu) */}
      {riderLocation && (
        <Marker latitude={riderLocation.lat} longitude={riderLocation.lng}>
          <span className="text-2xl animate-bounce">🛵</span>
        </Marker>
      )}

      {/* Destino */}
      <Marker latitude={destination.lat} longitude={destination.lng}>
        <span className="text-2xl">📍</span>
      </Marker>
    </Map>
  )
}
```

---

## 3. Mapas no Mobile (React Native)

### 3.1 Stack

```
Biblioteca:   @maplibre/maplibre-react-native
GPS:          expo-location (captura de posição)
Instalação:   npx expo install @maplibre/maplibre-react-native
              npx expo install expo-location
```

### 3.2 Configuração Inicial

```tsx
// src/app/_layout.tsx — configuração do MapLibre no app do entregador

import MapLibreGL from '@maplibre/maplibre-react-native'
import { useEffect } from 'react'
import * as Location from 'expo-location'

// Tile gratuito (OpenFreeMap)
const TILE_URL = 'https://tiles.openfreemap.org/styles/liberty'

export default function Layout() {
  useEffect(() => {
    // Inicializa MapLibre
    MapLibreGL.setAccessToken(null)  // sem token — tiles abertos

    // Pede permissão de localização
    Location.requestForegroundPermissionsAsync()
  }, [])

  return <Stack />
}
```

### 3.3 Mapa do Entregador (App Mobile)

```tsx
// src/components/map/RiderMap.tsx

import MapLibreGL, { MapView, Camera, UserLocation, MarkerView } from '@maplibre/maplibre-react-native'
import { View, Text } from 'react-native'

interface DeliveryPoint {
  id: string
  type: 'pickup' | 'dropoff'
  latitude: number
  longitude: number
  address: string
  orderId: string
}

interface RiderMapProps {
  deliveries: DeliveryPoint[]
  routeGeoJSON?: GeoJSON.FeatureCollection
  onMapPress?: (coords: { latitude: number; longitude: number }) => void
}

export function RiderMap({ deliveries, routeGeoJSON, onMapPress }: RiderMapProps) {
  return (
    <MapView
      style={{ flex: 1 }}
      styleURL="https://tiles.openfreemap.org/styles/liberty"
      onPress={onMapPress}
    >
      {/* Câmera segue o entregador */}
      <Camera
        followUserLocation
        followZoomLevel={15}
        animationDuration={1000}
      />

      {/* Posição do entregador */}
      <UserLocation renderCustomMarker={() => (
        <View style={styles.riderMarker}>
          <Text style={styles.riderIcon}>🛵</Text>
        </View>
      )} />

      {/* Rota (linha) */}
      {routeGeoJSON && (
        <MapLibreGL.ShapeSource id="route" shape={routeGeoJSON}>
          <MapLibreGL.LineLayer
            id="route-line"
            style={{
              lineColor: '#3b82f6',
              lineWidth: 4,
              lineOpacity: 0.8,
            }}
          />
        </MapLibreGL.ShapeSource>
      )}

      {/* Pontos de entrega */}
      {deliveries.map(point => (
        <MarkerView
          key={point.id}
          coordinate={[point.longitude, point.latitude]}
        >
          <View style={[
            styles.marker,
            point.type === 'pickup' ? styles.pickup : styles.dropoff
          ]}>
            <Text style={styles.markerText}>
              {point.type === 'pickup' ? '🏪' : '📍'}
            </Text>
          </View>
        </MarkerView>
      ))}
    </MapView>
  )
}
```

### 3.4 Deep Link para Navegação

Quando o entregador precisa de navegação turn-by-turn:

```tsx
// Quando o entregador clica "Navegar até o endereço"
// Abre o app de mapas nativo do celular com a rota pronta

import { Linking, Platform } from 'react-native'

async function openNavigation(destinationLat: number, destinationLng: number) {
  const url = Platform.select({
    ios: `maps://app?daddr=${destinationLat},${destinationLng}`,
    android: `geo:${destinationLat},${destinationLng}?q=${destinationLat},${destinationLng}`,
  })

  if (url) {
    await Linking.openURL(url)
  }
}
```

---

## 4. Geocoding — Endereço → Coordenadas

### 4.1 Stack

```
Servidor:     Nominatim (self-hosted) + Photon (autocomplete)
Banco:        PostGIS (coordenadas armazenadas)
Cache:        Redis (resultados de geocoding frequentes)
```

### 4.2 Fluxo de Geocoding

```
Cliente digita endereço:
  "Rua das Flores, 123 — Petrópolis, Natal/RN"

  1. Autocomplete: Photon (resposta em < 50ms)
     ├─ "Rua das Flores, 123"
     ├─ "Rua das Flores, 456"
     └─ "Rua das Orquídeas, 50"

  2. Geocoding: Nominatim (quando seleciona)
     └─ { lat: -5.7945, lng: -35.211 }

  3. Cache: Redis (TTL 7 dias)
     └─ "rua das flores 123 petropolis natal" → coordenadas

  4. Armazenamento: PostGIS
     └─ customer_address.latitude, customer_address.longitude
```

### 4.3 Endpoint de Geocoding

```python
# src/modules/geo/geocoding.py

"""
Geocoding usando Nominatim + Photon.
Auto-hospedado = sem limite de requisições, sem custo.
"""

import httpx
from redis import Redis
import structlog

logger = structlog.get_logger()
redis = Redis.from_url("redis://redis:6379/0")


async def autocomplete(query: str, limit: int = 5) -> list[dict]:
    """
    Autocomplete rápido de endereços.
    Usa Photon (baseado em OSM, resposta < 50ms).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://photon:2322/api",
            params={"q": query, "limit": limit, "lang": "pt"},
        )
        return response.json().get("features", [])


async def geocode(address: str) -> dict | None:
    """
    Converte endereço em coordenadas.
    Usa Nominatim (mais preciso que Photon).
    """

    # 1. Tenta cache primeiro
    cache_key = f"geo:{address.lower().strip()}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Consulta Nominatim
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://nominatim:8080/search",
            params={
                "q": address,
                "format": "json",
                "limit": 1,
                "countrycodes": "br",
                "addressdetails": 1,
            },
            headers={"User-Agent": "RapiDrop/1.0"},
        )

        data = response.json()
        if not data:
            return None

        result = {
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"]),
            "display_name": data[0]["display_name"],
        }

        # 3. Salva em cache por 7 dias
        redis.setex(cache_key, 604800, json.dumps(result))
        return result


async def reverse_geocode(lat: float, lng: float) -> str | None:
    """
    Converte coordenadas em endereço legível.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://nominatim:8080/reverse",
            params={"lat": lat, "lon": lng, "format": "json"},
            headers={"User-Agent": "RapiDrop/1.0"},
        )
        data = response.json()
        return data.get("display_name")
```

### 4.4 Docker Compose

```yaml
services:
  # Geocoding (auto-hospedado)
  nominatim:
    image: mediagis/nominatim:4.4
    ports: ["8080:8080"]
    volumes:
      - nominatim-data:/var/lib/postgresql/14/main
    environment:
      - PBF_URL=https://download.geofabrik.de/south-america/brazil-latest.osm.pbf
      - REPLICATION_URL=https://download.geofabrik.de/south-america/brazil-updates
    shm_size: 8gb
    deploy:
      resources:
        limits:
          memory: 16g

  # Autocomplete rápido
  photon:
    image: komoot/photon:latest
    ports: ["2322:2322"]
    volumes:
      - photon-data:/photon_data
    command: -nominatim-api http://nominatim:8080

  # Tiles de mapa (auto-hospedado)
  openmaptiles:
    image: maptiler/tileserver-gl:latest
    ports: ["8081:80"]
    volumes:
      - ./tiles:/data
    command: --mbtiles /data/brazil.mbtiles
```

---

## 5. Routing Engine — Cálculo de Rotas

### 5.1 Stack

```
Servidor:        OSRM (Open Source Routing Machine)
Alternativa:     GraphHopper (bike/pedestre/caminhão)
Uso principal:   Calcular distância e tempo entre pontos
                 Gerar polilinha da rota para exibir no mapa
```

### 5.2 OSRM — Docker Compose

```yaml
services:
  osrm:
    image: ghcr.io/project-osrm/osrm-backend
    ports: ["5000:5000"]
    volumes:
      - ./osrm-data:/data
    command: >
      sh -c "
        osrm-extract -p /opt/car.lua /data/brazil-latest.osm.pbf &&
        osrm-contract /data/brazil-latest.osrm &&
        osrm-routed --algorithm mld /data/brazil-latest.osrm
      "
```

### 5.3 Uso no Backend — Cálculo de Rota

```python
# src/modules/geo/routing.py

"""
Cálculo de rotas usando OSRM auto-hospedado.
Usado para:
  - Calcular distância e tempo de entrega
  - Gerar rota para exibir no mapa
  - Otimizar ordem de múltiplas entregas
"""

import httpx
from typing import List, Tuple
import structlog

logger = structlog.get_logger()

OSRM_URL = "http://osrm:5000"


async def calculate_route(
    origin: Tuple[float, float],       # (lng, lat)
    destination: Tuple[float, float],   # (lng, lat)
) -> dict | None:
    """
    Calcula rota entre dois pontos.
    Retorna distância (metros), duração (segundos) e geometria.
    """
    lng1, lat1 = origin
    lng2, lat2 = destination

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OSRM_URL}/route/v1/driving/{lng1},{lat1};{lng2},{lat2}",
            params={
                "overview": "full",     # geometria completa da rota
                "geometries": "geojson", # formato GeoJSON
                "steps": "false",
            },
        )

        data = response.json()
        if data["code"] != "Ok":
            return None

        route = data["routes"][0]
        return {
            "distance_meters": route["distance"],
            "distance_km": round(route["distance"] / 1000, 1),
            "duration_seconds": route["duration"],
            "duration_minutes": round(route["duration"] / 60, 0),
            "duration_text": format_duration(route["duration"]),
            "geometry": route["geometry"],  # GeoJSON LineString
        }


async def calculate_distance(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
) -> float:
    """Calcula distância EM RODA entre dois pontos (em km).

    Diferente da distância linear (ST_Distance do PostGIS),
    esta é a distância real de carro.
    """
    result = await calculate_route(origin, destination)
    return result["distance_km"] if result else 999.9  # fallback


async def calculate_eta(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
) -> int:
    """Calcula tempo estimado de entrega (em minutos)."""
    result = await calculate_route(origin, destination)
    return int(result["duration_minutes"]) if result else 30  # fallback


def format_duration(seconds: float) -> str:
    """Formata duração legível."""
    mins = int(seconds / 60)
    if mins < 60:
        return f"{mins} min"
    hours = mins // 60
    remaining = mins % 60
    return f"{hours}h{remaining:02d}"


async def batch_distance_matrix(
    points: List[Tuple[float, float]],  # [(lng, lat), ...]
) -> List[List[float]]:
    """
    Calcula matriz de distância entre múltiplos pontos.
    Usado pelo otimizador de rotas para resolver o TSP.

    Exemplo: batch_distance_matrix([loja, cliente1, cliente2])
    → [[0, 5.2, 8.1], [5.2, 0, 3.4], [8.1, 3.4, 0]]
    """
    coordinates = ";".join(f"{lng},{lat}" for lng, lat in points)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OSRM_URL}/table/v1/driving/{coordinates}",
            params={"annotations": "distance"},
        )

        data = response.json()
        if data["code"] != "Ok":
            return [[0] * len(points)] * len(points)

        # Converte de metros para km
        return [
            [round(d / 1000, 1) for d in row]
            for row in data["distances"]
        ]
```

---

## 6. Rastreamento GPS dos Entregadores

### 6.1 Fluxo de Envio de Posição

```
App do entregador (mobile):
  ├─ expo-location captura GPS
  ├─ A cada 5 segundos: envia posição via WebSocket
  └─ Se ficar parado > 30s: reduz para 1 envio a cada 30s

Servidor (FastAPI WebSocket):
  ├─ Recebe: { rider_id, lat, lng, speed, bearing, timestamp }
  ├─ Atualiza: rider.current_location (PostGIS)
  ├─ Atualiza: Redis GEO (para busca de próximos)
  └─ Broadcast: para o lojista via WebSocket
```

### 6.2 Envio de Posição (App do Entregador)

```tsx
// src/hooks/useLocationTracking.ts

import { useEffect, useRef } from 'react'
import * as Location from 'expo-location'
import { useWebSocket } from './useWebSocket'

interface LocationUpdate {
  riderId: string
  latitude: number
  longitude: number
  speed: number | null        // m/s
  bearing: number | null      // graus (0=N, 90=E)
  timestamp: string
}

export function useLocationTracking(riderId: string) {
  const ws = useWebSocket()
  const lastSentRef = useRef<number>(0)
  const lastPositionRef = useRef<Location.LocationObject | null>(null)

  useEffect(() => {
    let interval: NodeJS.Timeout

    async function startTracking() {
      // Configura GPS para alta precisão
      await Location.requestForegroundPermissionsAsync()

      // Inicia watch de posição
      Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.BestForNavigation,
          timeInterval: 5000,       // a cada 5s
          distanceInterval: 10,     // ou a cada 10m
        },
        (location) => {
          const now = Date.now()
          lastPositionRef.current = location

          // Rate limiting: não enviar mais que 1 vez a cada 4s
          if (now - lastSentRef.current < 4000) return
          lastSentRef.current = now

          const update: LocationUpdate = {
            riderId,
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            speed: location.coords.speed,
            bearing: location.coords.heading,
            timestamp: new Date().toISOString(),
          }

          // Envia via WebSocket
          ws.send('rider.location_update', update)
        }
      )
    }

    startTracking()

    return () => clearInterval(interval)
  }, [riderId])
}
```

### 6.3 Recebimento no Servidor

```python
# src/modules/riders/websocket.py

"""
WebSocket handler para receber posição dos entregadores
 e broadcast para o lojista.
"""

from fastapi import WebSocket, WebSocketDisconnect
from redis import Redis
from src.core.database import async_session
from src.models.rider import Rider
from geoalchemy2 import WKTElement
import json
import structlog

logger = structlog.get_logger()
redis = Redis.from_url("redis://redis:6379/0")


class RiderConnectionManager:
    """Gerencia conexões WebSocket dos entregadores."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, rider_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[rider_id] = websocket

    def disconnect(self, rider_id: str):
        self.active_connections.pop(rider_id, None)

    async def broadcast_to_merchant(self, merchant_id: str, message: dict):
        """Envia posição atualizada para o lojista."""
        # Lógica de broadcast para WebSocket do lojista
        ...


manager = RiderConnectionManager()


async def rider_websocket(websocket: WebSocket, rider_id: str):
    """
    Endpoint WebSocket: /ws/rider/{rider_id}

    O entregador conecta e começa a enviar posições.
    """
    await manager.connect(rider_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "location_update":
                await handle_location_update(
                    rider_id=rider_id,
                    lat=data["latitude"],
                    lng=data["longitude"],
                    speed=data.get("speed"),
                    bearing=data.get("bearing"),
                )

    except WebSocketDisconnect:
        manager.disconnect(rider_id)
        await handle_rider_offline(rider_id)


async def handle_location_update(
    rider_id: str,
    lat: float,
    lng: float,
    speed: float | None,
    bearing: float | None,
):
    """
    Processa atualização de posição do entregador.

    1. Atualiza PostGIS (current_location)
    2. Atualiza Redis GEO (para busca de próximos)
    3. Atualiza status (se estava offline, fica online)
    """

    async with async_session() as session:
        # 1. Atualiza no banco
        rider = await session.get(Rider, rider_id)
        if rider:
            rider.current_location = WKTElement(
                f"POINT({lng} {lat})", srid=4326
            )
            rider.current_location_updated_at = datetime.utcnow()
            rider.is_online = True
            rider.speed = speed
            rider.bearing = bearing
            await session.commit()

    # 2. Atualiza Redis GEO (expira em 1h se não atualizar)
    redis.geoadd("online_riders", (lng, lat, rider_id))
    redis.expire("online_riders", 3600)

    # 3. Broadcast para o lojista
    await manager.broadcast_to_merchant(rider.merchant_id, {
        "type": "rider.location",
        "rider_id": rider_id,
        "latitude": lat,
        "longitude": lng,
        "speed": speed,
        "timestamp": datetime.utcnow().isoformat(),
    })
```

### 6.4 Busca de Entregadores Próximos

```python
# src/modules/geo/nearby.py

"""
Busca de entregadores próximos usando Redis GEO + PostGIS.
"""

from redis import Redis
from geoalchemy2 import functions as geo_func
from src.core.database import async_session
from src.models.rider import Rider


async def find_nearest_riders(
    latitude: float,
    longitude: float,
    merchant_id: str,
    radius_km: float = 5.0,
    limit: int = 5,
) -> list[dict]:
    """
    Encontra os entregadores mais próximos de um ponto.

    Usado para:
      - Atribuir novo pedido ao entregador mais próximo
      - Mostrar entregadores próximos no mapa
    """

    # 1. Tenta Redis primeiro (mais rápido)
    nearest = redis.geosearch(
        "online_riders",
        longitude=longitude,
        latitude=latitude,
        radius=radius_km,
        unit="km",
        count=limit,
        sort="ASC",
    )

    if nearest:
        rider_ids = [r[0].decode() for r in nearest]
        # Busca dados completos no banco
        async with async_session() as session:
            riders = await session.execute(
                select(Rider).where(
                    Rider.id.in_(rider_ids),
                    Rider.merchant_id == merchant_id,
                    Rider.is_online == True,
                )
            )
            return [rider.to_dict() for rider in riders.scalars()]

    # 2. Fallback: PostGIS (mais preciso)
    async with async_session() as session:
        point = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
        riders = await session.execute(
            select(Rider).where(
                Rider.merchant_id == merchant_id,
                Rider.is_online == True,
                geo_func.ST_DWithin(
                    Rider.current_location,
                    point,
                    radius_km * 1000,  # km → metros
                ),
            ).order_by(
                geo_func.ST_Distance(Rider.current_location, point)
            ).limit(limit)
        )
        return [rider.to_dict() for rider in riders.scalars()]
```

---

## 7. Atribuição Inteligente de Entregas

### 7.1 Estratégias de Atribuição

Quando um novo pedido chega, o sistema decide **qual entregador** deve recebê-lo.

```
┌─────────────────────────────────────────────────────────────────┐
│              ESTRATÉGIAS DE ATRIBUIÇÃO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🎯  ESTRATÉGIA 1: MAIS PRÓXIMO (padrão)                       │
│       "Atribui ao entregador mais próximo da loja."            │
│       ✅ Mais rápido para o primeiro pedido                     │
│       ❌ Ignora entregas já atribuídas (pode atrasar outras)    │
│                                                                  │
│  🎯  ESTRATÉGIA 2: MENOS OCUPADO                                │
│       "Atribui ao entregador com menos entregas ativas."       │
│       ✅ Distribui carga uniformemente                          │
│       ✅ Justo para os entregadores                             │
│       ❌ Pode ser um entregador longe da loja                   │
│                                                                  │
│  🎯  ESTRATÉGIA 3: HÍBRIDO (recomendada)                       │
│       "Score = (proximidade × 0.6) + (disponibilidade × 0.4)"  │
│       ✅ Melhor dos dois mundos                                 │
│       ✅ Configurável por lojista                               │
│                                                                  │
│  🎯  ESTRATÉGIA 4: MANUAL (lojista decide)                     │
│       "Sistema sugere, lojista confirma."                      │
│       ✅ Controle total                                         │
│       ❌ Mais lento (depende da ação do lojista)               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Implementação — Atribuidor Automático

```python
# src/modules/orders/assignment.py

"""
Atribuição automática de pedidos a entregadores.
Estratégia híbrida: proximidade + disponibilidade.
"""

from dataclasses import dataclass
from typing import List, Optional
import structlog

logger = structlog.get_logger()


@dataclass
class RiderScore:
    rider_id: str
    rider_name: str
    distance_km: float
    active_deliveries: int
    score: float


class DeliveryAssigner:
    """
    Atribui pedidos a entregadores usando estratégia configurável.

    Uso:
        assigner = DeliveryAssigner(merchant_id="m42")
        rider = await assigner.find_best_rider(
            order_id="ord_789",
            strategy="hybrid",
        )
    """

    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id

    async def find_best_rider(
        self,
        order_id: str,
        strategy: str = "hybrid",
    ) -> Optional[dict]:
        """
        Encontra o melhor entregador para um pedido.

        Args:
            order_id: ID do pedido a ser atribuído
            strategy: 'nearest' | 'least_busy' | 'hybrid' | 'manual'

        Returns:
            dict com dados do entregador selecionado, ou None
        """

        # 1. Busca dados do pedido (loja, endereço do cliente)
        order = await self._get_order(order_id)
        merchant_location = (order.merchant_lng, order.merchant_lat)

        # 2. Busca entregadores online
        riders = await self._get_online_riders()

        if not riders:
            logger.warning("assignment.no_riders", order_id=order_id)
            return None

        if strategy == "manual":
            return None  # lojista decide manualmente

        # 3. Calcula score para cada entregador
        scored_riders = []
        for rider in riders:
            distance = await calculate_distance(
                merchant_location,
                (rider["lng"], rider["lat"]),
            )
            active = rider["active_deliveries"]

            if strategy == "nearest":
                score = 100 - (distance * 10)  # quanto mais perto, maior

            elif strategy == "least_busy":
                score = 100 - (active * 20)  # quanto menos ocupado, maior

            else:  # hybrid (padrão)
                # Normaliza: proximidade (0-100) + disponibilidade (0-100)
                proximity_score = max(0, 100 - (distance * 10))
                availability_score = max(0, 100 - (active * 20))
                score = (proximity_score * 0.6) + (availability_score * 0.4)

            scored_riders.append(RiderScore(
                rider_id=rider["id"],
                rider_name=rider["name"],
                distance_km=distance,
                active_deliveries=active,
                score=round(score, 1),
            ))

        # 4. Ordena por score (maior primeiro)
        scored_riders.sort(key=lambda r: r.score, reverse=True)
        best = scored_riders[0]

        logger.info(
            "assignment.rider_selected",
            order_id=order_id,
            rider_id=best.rider_id,
            rider_name=best.rider_name,
            strategy=strategy,
            score=best.score,
            distance_km=best.distance_km,
        )

        return {
            "rider_id": best.rider_id,
            "rider_name": best.rider_name,
            "score": best.score,
            "distance_km": best.distance_km,
        }

    async def _get_order(self, order_id: str):
        """Busca dados do pedido (coordenadas da loja)."""
        # ... query no banco

    async def _get_online_riders(self) -> List[dict]:
        """
        Busca entregadores online com suas cargas atuais.
        Usa Redis GEO + query no banco.
        """
        # ... implementação
```

### 7.3 Como o Entregador Recebe a Atribuição

```
1. Sistema encontra o melhor entregador
2. Envia notificação push:
     🛵 "Nova entrega! 🍕 Pizzaria do Norte → Rua das Flores, 123"
3. Entregador tem 30 segundos para ACEITAR ou RECUSAR
   ┌──────────────────┐
   │  🛵 NOVA ENTREGA │
   │                  │
   │  🍕 Pizzaria do  │
   │     Norte        │
   │  📍 Rua das      │
   │     Flores, 123  │
   │  💰 R$ 7,00      │
   │  📏 2,3 km       │
   │                  │
   │  [ ✅ Aceitar ]  │
   │  [ ❌ Recusar ]  │
   │     ⏱ 25s        │
   └──────────────────┘
4. Se recusar ou expirar:
   → Atribui ao próximo da lista
   → Marca como "recusou" (reduz score futuramente)
5. Se aceitar:
   → Pedido atribuído
   → Envia rota para o app do entregador
```

---

## 8. Roteirização de Múltiplas Entregas

### 8.1 O Problema

```
Cenário: Entregador tem 3 pedidos para entregar.

Ordem A (instinto):                       Ordem B (otimizada):
  Loja → Cliente A (5km)                   Loja → Cliente C (2km)
       → Cliente B (8km)                        → Cliente A (3km)
       → Cliente C (12km)                       → Cliente B (4km)
  Total: 25km                              Total: 9km
  Tempo: ~60 min                           Tempo: ~25 min

  Diferença: 16km a menos, 35min mais rápido 🚀
```

### 8.2 Algoritmo — Nearest Neighbor (Vizinho Mais Próximo)

```python
# src/modules/geo/optimizer.py

"""
Otimizador de rotas para múltiplas entregas.
Algoritmo: Nearest Neighbor (rápido, bom o suficiente).
Alternativa: 2-opt (mais preciso, mais lento).
"""

from typing import List, Tuple
from src.modules.geo.routing import calculate_distance


async def optimize_route(
    origin: Tuple[float, float],       # loja (lng, lat)
    destinations: List[dict],           # entregas pendentes
) -> List[dict]:
    """
    Otimiza a ordem de entregas usando Nearest Neighbor.

    Args:
        origin: coordenadas da loja
        destinations: lista de {id, lng, lat, address, order_id}

    Returns:
        Mesma lista, reordenada para a rota mais eficiente

    Algoritmo:
        1. Começa na loja
        2. Encontra a entrega MAIS PRÓXIMA do ponto atual
        3. Move para ela
        4. Repete até todas as entregas serem visitadas
    """
    if not destinations:
        return []

    current = origin
    remaining = destinations.copy()
    optimized = []

    while remaining:
        # Encontra o destino mais próximo do ponto atual
        nearest = None
        nearest_dist = float("inf")

        for dest in remaining:
            dist = await calculate_distance(
                current,
                (dest["lng"], dest["lat"]),
            )
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = dest

        if nearest:
            nearest["distance_from_previous_km"] = round(nearest_dist, 1)
            optimized.append(nearest)
            current = (nearest["lng"], nearest["lat"])
            remaining.remove(nearest)

    return optimized
```

### 8.3 Algoritmo 2-Opt (Mais Preciso)

```python
async def optimize_route_2opt(
    origin: Tuple[float, float],
    destinations: List[dict],
) -> List[dict]:
    """
    Otimização por 2-opt: mais preciso que Nearest Neighbor.
    Troca pares de arestas para reduzir a distância total.

    Para 10 entregas, Nearest Neighbor pode ser 10-15% pior que o ideal.
    2-opt chega a < 2% do ideal em segundos.
    """
    # 1. Começa com Nearest Neighbor (solução inicial)
    route = await optimize_route(origin, destinations)

    # 2. Converte para lista de coordenadas
    points = [(origin["lng"], origin["lat"])] + [
        (d["lng"], d["lat"]) for d in route
    ]

    # 3. Aplica 2-opt (melhora a rota)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(points) - 2):
            for j in range(i + 1, len(points) - 1):
                # Calcula distância antes e depois da troca
                before = (
                    await calculate_distance(points[i-1], points[i])
                    + await calculate_distance(points[j], points[j+1])
                )
                after = (
                    await calculate_distance(points[i-1], points[j])
                    + await calculate_distance(points[i], points[j+1])
                )

                if after < before:
                    # Troca: reverte o segmento i..j
                    points[i:j+1] = reversed(points[i:j+1])
                    improved = True

    # 4. Reordena as entregas conforme os pontos otimizados
    ordered = []
    for pt in points[1:]:  # pula a loja (primeiro ponto)
        for dest in destinations:
            if (dest["lng"], dest["lat"]) == pt:
                ordered.append(dest)
                break

    return ordered
```

### 8.4 Quando Roteirizar

```
📦 NOVO PEDIDO
    │
    ▼
  Entregador está livre? ──Sim──→ Atribui pedido direto
    │
    Não
    │
    ▼
  Entregador tem 2+ pedidos? ──Não──→ Aguarda próximo
    │
    Sim
    │
    ▼
  Rode roteirização:
    ├─ Se for o primeiro pedido extra → otimizar rota
    ├─ Se já tem rota otimizada → re-otimizar
    └─ Se o lojista pedir → re-otimizar manualmente

  Mostra rota otimizada no app do entregador:
    "🛵 Rota otimizada! Sua próxima entrega é:
     1️⃣ Rua das Flores, 123 (2km)
     2️⃣ Av. Paulista, 1000 (3km)
     3️⃣ Rua 7 de Setembro (4km)"
```

### 8.5 Priorização por Urgência

Além da distância, podemos priorizar entregas por:

| Fator | Peso | Quando usar |
|-------|:----:|-------------|
| **Tempo desde o pedido** | Alto | Pedido está esperando há muito tempo |
| **Tipo de produto** | Médio | Comida fria (sorvete, gelado) prioritário |
| **Cliente VIP** | Baixo | Cliente frequente ou com reclamação recente |
| **Janela de entrega** | Alto | Cliente marcou horário específico |
| **Valor do pedido** | Baixo | Pedidos maiores geram mais receita |

```python
async def score_by_urgency(delivery: dict) -> float:
    """
    Calcula score de urgência para uma entrega.
    Quanto maior o score, mais prioritária.
    """
    score = 0

    # Quanto mais tempo esperando, maior o score
    wait_minutes = (datetime.utcnow() - delivery["created_at"]).total_seconds() / 60
    score += wait_minutes * 2  # +2 pontos por minuto de espera

    # Comida quente/fria perde qualidade com o tempo
    if delivery.get("requires_refrigeration"):
        score += (60 - wait_minutes) * 1.5  # quanto mais tempo, menos urgente (já era)

    if delivery.get("is_hot_food"):
        score += max(0, 30 - wait_minutes) * 2  # prioridade nos primeiros 30min

    # Cliente VIP
    if delivery.get("is_vip"):
        score += 100

    # Janela de entrega
    if delivery.get("delivery_window_end"):
        remaining = (delivery["delivery_window_end"] - datetime.utcnow()).total_seconds() / 60
        if remaining < 15:
            score += 200  # MUITO urgente

    return score
```

---

## 9. Infraestrutura e Custo

### 9.1 Serviços e Como Rodam

```
┌─────────────────────────────────────────────────────────────────┐
│              INFRAESTRUTURA DE MAPAS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Serviço         | Porto     | Stack       | Custo              │
│  ────────────────|───────────|─────────────|──────────────────── │
│  Nominatim       | 8080      | GeoFabrik   | HDD 500GB + RAM 8GB│
│  Photon          | 2322      | Java        | RAM 2GB            │
│  OpenMapTiles    | 8081      | Node.js     | RAM 2GB + SSD      │
│  OSRM            | 5000      | C++         | RAM 16GB + SSD     │
│  MapLibre (web)  | Navegador | JS          | Grátis (cliente)   │
│  MapLibre (mobile)| Device   | Native      | Grátis (device)    │
│                                                                  │
│  ESTIMATIVA DE CUSTO (auto-hospedado):                          │
│    Servidor: ~R$ 400/mês (8 vCPU, 32GB RAM, 200GB SSD)         │
│    vs ~R$ 11.000/mês de APIs Google/Mapbox                      │
│                                                                  │
│  Economia: ~R$ 10.600/mês ou R$ 127.200/ano                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Dimensionamento

```
Setup MÍNIMO (desenvolvimento / poucas lojas):
  └─ Servidor único: 4 vCPU, 16GB RAM, 100GB SSD
  └─ Nominatim + OSRM compartilham o mesmo host
  └─ Tiles: tiles.openfreemap.org (gratuito, sem auto-hospedar)
  └─ ~R$ 200/mês

Setup RECOMENDADO (produção / dezenas de lojas):
  └─ Servidor de mapas: 8 vCPU, 32GB RAM, 200GB SSD
  └─ OSRM dedicado (uso intenso de CPU/RAM)
  └─ Nominatim + Photon no mesmo host
  └─ Tiles auto-hospedados (OpenMapTiles)
  └─ ~R$ 400/mês

Setup ESCALADO (centenas de lojas, todo Brasil):
  └─ Cluster: 3 servidores
  └─ OSRM em cluster (Brazil extract = 7GB)
  └─ Nominatim replicado para alta disponibilidade
  └─ CDN para tiles (Cloudflare)
  └─ ~R$ 1.200/mês
```

### 9.3 Comparativo de Custos vs APIs Pagas

```
Volume de requisições por mês (estimativa para 100 lojas):

                Google Maps API    |  Open Source
                ───────────────────|──────────────
  Map views     500.000  R$ 2.500  |  R$ 0
  Geocoding     50.000   R$ 2.000  |  R$ 0
  Directions    100.000  R$ 3.000  |  R$ 0
  Autocomplete  200.000  R$ 2.000  |  R$ 0
  Places        50.000   R$ 1.500  |  R$ 0
                ───────────────────|──────────────
  TOTAL                  R$ 11.000 |  R$ 400 (servidor)
                                    |
  Economia anual: R$ 127.200 🚀     |
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Responsáveis:** @cruz (mobile), @dani (web), @kira (backend), @theo (infra)
> **Ferramentas:** MapLibre GL, OSRM, Nominatim, Photon, OpenFreeMap, PostGIS, Redis GEO
