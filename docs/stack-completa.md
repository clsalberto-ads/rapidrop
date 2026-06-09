# RapiDrop — Stack Completa (Refência)

> Tudo que usamos para construir o RapiDrop, organizado por camada.
> Fácil de entender, fácil de consultar.

---

## ⚡ Resumo em 30 Segundos

```
LINGUAGENS:  Python 3.12+  ·  TypeScript 5.x
APPS:        Next.js 15 (Web)  ·  React Native / Expo (Mobile)
BACKEND:     FastAPI  ·  SQLAlchemy Async  ·  PostgreSQL 16
CANAIS:      Site da loja  ·  App do Cliente  ·  App do Entregador
             Painel do Lojista  ·  Admin SaaS
NUVEM:       Railway → AWS ECS  ·  GitHub Actions
```

---

## 📦 Índice

1. [Visão Geral — O Ecossistema](#1-visão-geral--o-ecossistema)
2. [Frontend Web (Next.js)](#2-frontend-web-nextjs)
3. [App Mobile (React Native / Expo)](#3-app-mobile-react-native--expo)
4. [Backend (FastAPI + Python)](#4-backend-fastapi--python)
5. [Banco de Dados e Armazenamento](#5-banco-de-dados-e-armazenamento)
6. [Infraestrutura e DevOps](#6-infraestrutura-e-devops)
7. [Observabilidade](#7-observabilidade)
8. [Integrações Externas](#8-integrações-externas)
9. [Modelo de Dados — Todas as Tabelas](#9-modelo-de-dados--todas-as-tabelas)
10. [Segurança](#10-segurança)

---

## 1. Visão Geral — O Ecossistema

```
                        ┌──────────────────────────────────────┐
                        │        💻 CLIENTES FINAIS            │
                        │  (consomem das lojas)                │
                        │  ┌─────────┐  ┌───────────────┐      │
                        │  │ Site    │  │ App RapiDrop   │      │
                        │  │ White   │  │ (descobre      │      │
                        │  │ Label   │  │  lojas, pede)  │      │
                        │  └────┬────┘  └───────┬───────┘      │
                        └───────┼────────────────┼──────────────┘
                                │                │
┌───────────────────────────────┼────────────────┼──────────────────┐
│                               │                │                   │
│             ┌─────────────────▼────────────────▼──────────────┐   │
│             │            FASTAPI (Backend)                     │   │
│             │                                                  │   │
│             │  ┌──────────┬──────────┬──────────┬──────────┐  │   │
│             │  │   Auth   │  Orders  │ Catalog  │  Riders  │  │   │
│             │  ├──────────┼──────────┼──────────┼──────────┤  │   │
│             │  │Customers │ Payments │ Reports  │  Notif.  │  │   │
│             │  ├──────────┴──────────┴──────────┴──────────┤  │   │
│             │  │        Segment Engine (config-driven)      │  │   │
│             │  └───────────────────────────────────────────┘  │   │
│             └──────────────────────┬─────────────────────────┘   │
│                                    │                              │
│              ┌─────────────────────┼────────────────────┐         │
│              ▼                     ▼                     ▼         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐│
│  │   PostgreSQL 16   │  │     Redis 7      │  │  RabbitMQ /      ││
│  │   + PostGIS       │  │  Cache + PubSub  │  │  Celery          ││
│  │   Dados principais│  │  + Sessões       │  │  Fila de tasks   ││
│  └──────────────────┘  └──────────────────┘  └──────────────────┘│
│                                    │                               │
│                                    ▼                               │
│                        ┌──────────────────────┐                    │
│                        │  Object Storage      │                    │
│                        │  (S3 / MinIO)        │                    │
│                        │  Fotos, comprovantes │                    │
│                        └──────────────────────┘                    │
└────────────────────────────────────────────────────────────────────┘
         │                          │                       │
         ▼                          ▼                       ▼
┌───────────────┐   ┌──────────────────────┐  ┌──────────────────────┐
│   LOJISTA     │   │   ENTREGADOR         │  │   ADMIN SAAS         │
│  (Painel Web) │   │   (App Mobile)       │  │   (Painel Web)       │
│               │   │                      │  │                      │
│ Dashboard     │   │ GPS tracking         │  │ Gerenciar lojistas   │
│ Pedidos       │   │ Notificações push    │  │ Ver métricas globais │
│ Catálogo      │   │ Fila de entregas     │  │ Planos e cobranças   │
│ Relatórios    │   │ Histórico de ganhos   │  │ Auditoria           │
│ Configurações │   │ Ranking e bônus      │  │ Suporte             │
└───────────────┘   └──────────────────────┘  └──────────────────────┘
```

### 1.1 Os 5 Aplicativos do RapiDrop

| # | App | Quem usa | Tecnologia | Finalidade |
|:-:|-----|----------|------------|------------|
| 1 | **Site White Label** | Cliente final | Next.js | Site próprio de cada loja (ex: `pizzariadonorte.com.br`) |
| 2 | **App RapiDrop** | Cliente final | React Native / Expo | Descobrir lojas, favoritar, pedir |
| 3 | **Painel do Lojista** | Lojista/Dono | Next.js | Gerenciar loja, pedidos, catálogo, entregadores |
| 4 | **App do Entregador** | Entregador | React Native / Expo | Receber entregas, GPS, ganhos |
| 5 | **Admin SaaS** | Equipe RapiDrop | Next.js | Gerenciar lojistas, planos, suporte |

---

## 2. Frontend Web (Next.js)

### 2.1 Stack

```
Framework:     Next.js 15 (App Router)
Linguagem:     TypeScript 5.x (strict mode)
Estilos:       TailwindCSS 4.x + shadcn/ui
Dados:         TanStack Query v5 (servidor + cliente)
Formulários:   React Hook Form + Zod (validação)
Animações:     Framer Motion
Ícones:        Lucide React
```

### 2.2 Os Sites que Rodam em Next.js

```
Site Público (landing + blog):
  └─ /              → Landing page RapiDrop
  └─ /blog/*        → Blog de conteúdo
  └─ /preco         → Planos e preços

Site White Label da Loja (cada loja tem um):
  └─ /:store-domain → Página pública da loja
      ├─ Cardápio completo
      ├─ Carrinho e checkout
      ├─ Login do cliente
      └─ Acompanhamento do pedido

Painel do Lojista:
  └─ /app/pedidos         → Pedidos em tempo real
  └─ /app/catalogo        → Produtos, categorias
  └─ /app/entregadores    → Gestão de entregadores
  └─ /app/clientes        → Base de clientes
  └─ /app/relatorios      → Métricas e exports
  └─ /app/configuracoes   → Dados da loja, horários, taxas
  └─ /app/financeiro      → Faturas, assinatura

Admin SaaS:
  └─ /admin/lojistas     → CRUD de lojistas
  └─ /admin/planos       → Planos e precificação
  └─ /admin/metricas     → Métricas globais
  └─ /admin/faturas      → Cobranças e inadimplência
  └─ /admin/suporte      → Tickets de suporte
```

### 2.3 Componentização (shadcn/ui)

```
Componentes base (customizados do shadcn):
  Button, Card, Input, Select, Dialog, Sheet,
  Table, Badge, Avatar, DropdownMenu, Tabs,
  Toast, Skeleton, Progress

Componentes de negócio (específicos do RapiDrop):
  OrderCard       → Card do pedido com status + ações
  ProductForm     → Formulário de produto (adaptável por segmento)
  RiderCard       → Card do entregador com localização
  CustomerRow     → Linha de cliente com histórico
  DeliveryMap     → Mapa com rota em tempo real
  PaymentSummary  → Resumo de pagamento
```

### 2.4 SEO (cada loja ranqueia no Google)

```
SEO por loja:
  - URL canônica: pizzariadonorte.com.br
  - Meta tags próprias (title, description, OG)
  - Structured data (LocalBusiness, Menu, Product)
  - Sitemap XML por loja
  - Core Web Vitals monitorados
```

---

## 3. App Mobile (React Native / Expo)

### 3.1 Stack

```
Framework:      React Native 0.76+ (New Architecture)
Plataforma:     Expo SDK 52+
Roteamento:     expo-router 4.x
Estilos:        NativeWind 4 (Tailwind para mobile)
Animações:      Reanimated 3 + Gesture Handler
Dados:          TanStack Query v5
Cache local:    MMKV (rápido, síncrono)
Banco local:    WatermelonDB (dados offline)
Mapas:          expo-location + @maplibre/maplibre-react-native
Routing:        OSRM auto-hospedado (cálculo de distância e ETA)
Geocoding:      Nominatim + Photon (auto-hospedados)
Push:           expo-notifications
Segurança:      expo-secure-store (tokens)
Ícones:         expo-symbols (SF Symbols no iOS)
```

### 3.2 Os Dois Apps Mobile

```
┌─────────────────────────────────────────────┐
│         📱 APP RAPIDROP (CLIENTE)           │
├─────────────────────────────────────────────┤
│                                             │
│  Tela inicial:                              │
│  ├─ Lojas perto de você                     │
│  ├─ Favoritos (lojas + pratos)              │
│  └─ "Pedir de novo"                         │
│                                             │
│  Loja:                                      │
│  ├─ Cardápio com categorias                 │
│  ├─ Busca por produto                       │
│  ├─ Carrinho + checkout                     │
│  └─ Acompanhamento ao vivo                  │
│                                             │
│  Perfil:                                    │
│  ├─ Endereços salvos                        │
│  ├─ Formas de pagamento                     │
│  ├─ Histórico de pedidos                    │
│  └─ Favoritos e fidelidade                  │
│                                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│      📱 APP DO ENTREGADOR                   │
├─────────────────────────────────────────────┤
│                                             │
│  Tela inicial:                              │
│  ├─ Fila de entregas                        │
│  ├─ Online/Offline                          │
│  └─ Ganhos do dia                           │
│                                             │
│  Entrega:                                   │
│  ├─ Ver detalhes do pedido                  │
│  ├─ Navegar até o endereço                  │
│  ├─ Ligar para o cliente                    │
│  └─ Confirmar entrega                       │
│                                             │
│  Perfil:                                    │
│  ├─ Histórico de ganhos                     │
│  ├─ Ranking e bônus                         │
│  └─ Metas de desempenho                     │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.3 Deep Links (URL que abre o app)

```
Link compartilhado no WhatsApp:
  rapidrop.com.br/s/pizzariadonorte

  ├─ Se cliente tem app → abre direto na loja
  └─ Se não tem app → abre o site white label

Configuração:
  iOS: apple-app-site-association (Universal Links)
  Android: assetlinks.json (App Links)
```

---

## 4. Backend (FastAPI + Python)

### 4.1 Stack

```
Framework:      FastAPI (Python 3.12+)
ORM:            SQLAlchemy 2.x (modo async)
Validação:      Pydantic v2 (integrado ao FastAPI)
Migrações:      Alembic
Tasks:          Celery + RabbitMQ
Cache:          Redis 7
Geo:            PostGIS (PostgreSQL)
Testes:         pytest + httpx (async)
Linting:        Ruff + mypy (strict mode)
```

### 4.2 Módulos do Backend

```
rapidrop/apps/api/src/modules/

  auth/           → Login (JWT + refresh), OTP por SMS, OAuth
  │                  (Google, Apple)
  │
  merchants/      → Cadastro do lojista, segmento, configurações
  │
  customers/       → Clientes finais, endereços, formas de pagamento
  │
  catalog/        → Produtos, categorias, variações, importação
  │
  orders/         → Ciclo de vida do pedido (criar → entregar)
  │
  riders/         → Entregadores, assignment, pagamento, ranking
  │
  payments/       → Gateway (Stripe/Asaas), faturas, reembolsos
  │
  notifications/  → Push, WhatsApp, Email (template por segmento)
  │
  reports/        → Relatórios, exportação CSV/Excel, métricas
  │
  saas_admin/     → Admin do SaaS: lojistas, planos, cobranças
  │
  segment/        → Segment Engine — configs por segmento
  │
  subscriptions/  → Assinatura SaaS: fase 1 (%), fase 2 (fixo)
  │
  webhooks/       → Integrações externas (iFood, parceiros)
  │
  promotions/     → Cupons, descontos, fidelidade, indicação
```

### 4.3 Segment Engine (O Coração)

```
O Segment Engine permite que o MESMO código sirva
restaurantes, farmácias e mercados sem "ifs" espalhados.

Como funciona:

  merchant.segment = "food"

  Catalog Config:
    food:     tem tamanhos (P/M/G), sabores, adicionais
    pharmacy: tem princípio ativo, tarja, receita, laboratório
    grocery:  tem peso, código de barras, substitutos

  Order Config:
    food:     tempo de preparo, vista da cozinha, impressão
    pharmacy: validação de receita, verificação refrigeração
    grocery:  fluxo de substituição, agendamento de entrega

  UI Config (frontend renderiza diferente):
    food:     ícones de comida, cores quentes
    pharmacy: ícones de saúde, cores verdes
    grocery:  ícones de mercado, tons frescos
```

### 4.4 WebSocket — Tempo Real

```
Conexão persistente entre servidor e cliente.

Eventos enviados para o LOJISTA:
  order.new               → Novo pedido 📢
  order.status_changed    → Pedido mudou de status
  rider.location_update   → GPS do entregador
  rider.status_changed    → Entregador online/offline

Eventos enviados para o ENTREGADOR:
  order.assigned          → Pedido atribuído a você
  order.cancelled         → Pedido cancelado
  cargo.special_alert     → Carga especial (refrigeração/frágil)

Eventos enviados para o CLIENTE:
  order.confirmed         → Pedido confirmado ✅
  order.preparing         → Em preparo
  order.out_for_delivery  → Saiu para entrega 🛵
  rider.location_update   → Onde está o entregador (mapa)
```

---

## 5. Banco de Dados e Armazenamento

### 5.1 Stack de Dados

```
Banco principal:   PostgreSQL 16 + PostGIS + pgvector
Cache:             Redis 7 (PubSub para WebSocket)
Tasks assíncronas: Celery + RabbitMQ
Storage:           S3/MinIO (fotos de produtos, comprovantes, receitas)
Cache local:       MMKV (app mobile)
Banco local:       WatermelonDB (app mobile — dados offline)
```

### 5.2 PostgreSQL — O Que Guardamos

| Tipo de dado | Exemplo |
|:------------:|---------|
| **Usuários e contas** | Lojistas, clientes finais, entregadores, admin SaaS |
| **Catálogo** | Produtos, categorias, variações, preços |
| **Pedidos** | Itens, status, valores, endereço, observações |
| **Pagamentos** | Transações, faturas, recebimentos |
| **Geográfico (PostGIS)** | Endereços, coordenadas, rotas, raio de entrega |
| **Assinaturas** | Planos, fase 1 (%), fase 2 (fixo), histórico |
| **Cupons e promoções** | Descontos, fidelidade, indicação |
| **Notificações** | Push tokens, preferências, histórico |

### 5.3 Redis — O Que Cacheamos

```
Cache de catálogo:     produtos mais vistos (evita bater no DB)
Sessões:               refresh tokens, login temporário
PubSub WebSocket:      eventos em tempo real (pedidos, GPS)
Filas (via Celery):    jobs pendentes
Rate limiting:         controle de requisições por IP/loja
```

### 5.4 S3/MinIO — O Que Guardamos em Arquivos

```
Fotos de produtos     → /merchants/{id}/products/{id}.webp
Logos da loja         → /merchants/{id}/logo.png
Comprovantes          → /payments/{id}/receipt.pdf
Receitas médicas      → /prescriptions/{id}.jpg (criptografado)
Relatórios exportados → /reports/{merchant_id}/{date}.csv
```

---

## 6. Infraestrutura e DevOps

### 6.1 Stack

```
Containerização:  Docker + Docker Compose (local)
CI/CD:            GitHub Actions
Hospedagem:       Railway → AWS ECS (escala)
Observabilidade:  Ver seção 7 (documentação completa em docs/observabilidade.md)
Domínios:         Vercel (sites white label) + Cloudflare (DNS)
```

### 6.2 Ambientes

```
Local (desenvolvimento):
  docker-compose up
  └─ FastAPI na porta 8000
  └─ PostgreSQL na porta 5432
  └─ Redis na porta 6379
  └─ RabbitMQ na porta 5672
  └─ MinIO na porta 9000
  └─ Prometheus na porta 9090
  └─ Grafana na porta 3001
  └─ Loki na porta 3100
  └─ Tempo (tracing) na porta 4317
  └─ Next.js na porta 3000

Staging:
  railway.app/rapidrop-staging
  └─ Branch develop → deploy automático
  └─ DB separado (staging)
  └─ Dados anonimizados

Produção:
  rapidrop.com.br
  └─ Branch main → deploy com aprovação
  └─ AWS ECS (escala automática)
  └─ Multi-AZ (alta disponibilidade)
```

### 6.3 CI/CD (GitHub Actions)

```
Pull Request → Testes (pytest + lint) → Build → Preview

Merge na develop → Deploy no staging
  ├─ Migrations automáticas (Alembic)
  ├─ Testes de integração
  └─ Testes E2E (Playwright)

Merge na main → Deploy em produção
  ├─ Health checks
  ├─ Rollback automático se falhar
  └─ Notificação no Slack
```

---

## 7. Observabilidade

> Documentação completa: [`docs/observabilidade.md`](observabilidade.md)

### 7.1 Stack de Observabilidade

```
Métricas:     Prometheus (scrape /metrics a cada 15s)
Dashboards:   Grafana (dashboards por persona: SRE, Negócio, Mobile)
Logs:         JSON estruturado (structlog) → Loki / CloudWatch
Tracing:      OpenTelemetry → Tempo (Grafana) / Jaeger
Erros:        Sentry (exceções não tratadas, crash reporting)
Alertas:      Alertmanager → Slack (P0: PagerDuty + WhatsApp)
Health check: Endpoint GET /health (DB, Redis, filas)
```

### 7.2 Os Três Pilares

| Pilar | Ferramenta | O que responde |
|-------|-----------|----------------|
| **📊 Métricas** | Prometheus + Grafana | "O que está acontecendo?" — requests/s, latência, erros, filas |
| **📝 Logs** | JSON stdout → Loki | "O que aconteceu exatamente?" — evento por evento |
| **🔍 Tracing** | OpenTelemetry → Tempo | "Por que está lento?" — onde o tempo é gasto |

### 7.3 Docker Compose (local)

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-data:/var/lib/grafana

  loki:
    image: grafana/loki:latest
    ports: ["3100:3100"]

  tempo:
    image: grafana/tempo:latest
    ports: ["4317:4317"]   # OTLP gRPC
```

### 7.4 Métricas Essenciais

| Categoria | Exemplos | Onde |
|-----------|----------|------|
| **Sistema** | CPU, memória, disco, conexões DB | Prometheus node_exporter |
| **API** | requests/s, latência p50/p95/p99, 5xx | prometheus-fastapi-instrumentator |
| **Negócio** | pedidos/min, faturamento, cancelamentos, churn | Custom (decorator) + SQL no Grafana |
| **Filas** | tamanho das filas, tasks/s, falhas | RabbitMQ exporter |
| **Mobile** | crash rate, telas, conversão | Sentry + Firebase Analytics |

### 7.5 Alertas Principais

```
🔴 P0 — Acorda 24h:
   ├─ Erro na API > 5% por 2 minutos
   ├─ Banco de dados offline
   └─ Latência p99 > 10s

🟡 P1 — Horário comercial:
   ├─ CPU > 80% por 15 minutos
   ├─ Filas > 1000 mensagens
   └─ Churn > 7% no mês

🔵 P2 — Slack apenas:
   ├─ Queda de pedidos > 20% vs ontem
   ├─ SSL expirando em < 7 dias
   └─ Slow queries detectadas
```

---

## 8. Integrações Externas

### 8.1 Gateways de Pagamento

| Serviço | Uso |
|---------|-----|
| **Stripe** | Pagamentos com cartão de crédito (tokenização) |
| **Asaas** | PIX e boleto para lojistas (assinatura SaaS) |
| **AppsFlyer** | Atribuição de campanhas (app mobile) |
| **RevenueCat** | Assinaturas no app (mobile) |

### 8.2 Notificações e Comunicação

| Serviço | Uso |
|---------|-----|
| **WhatsApp API** | Notificações para lojista e cliente |
| **Expo Push** | Push notifications para apps mobile |
| **Resend** | Emails transacionais (faturas, recovery) |
| **Twilio** | SMS de fallback (código OTP) |

### 8.3 Mapas e Localização

> Documentação completa: [`docs/mapas-roteirizacao.md`](mapas-roteirizacao.md)

| Serviço | Uso | Open Source? |
|---------|-----|:------------:|
| **MapLibre GL JS** | Renderização de mapas no web (Next.js) | ✅ |
| **MapLibre GL Native** | Renderização de mapas no mobile (React Native) | ✅ |
| **OSRM** | Cálculo de rotas, distâncias, ETA (auto-hospedado) | ✅ |
| **Nominatim** | Geocoding (endereço → coordenadas) | ✅ |
| **Photon** | Autocomplete de endereço para busca | ✅ |
| **PostGIS** | Consultas geográficas (raio de entrega, ST_DWithin) | ✅ |
| **Redis GEO** | Busca de entregadores próximos em tempo real | ✅ |
| **OpenFreeMap** | Tiles de mapa gratuitos (ou auto-hospedar OpenMapTiles) | ✅ |

> **Custo:** R$ 0 de API. Apenas o servidor (~R$ 400/mês).
> vs R$ 11.000/mês de Google Maps + Mapbox. Economia de **R$ 127.200/ano**.

### 8.4 Marketplaces (Integrações Futuras)

| Serviço | Uso |
|---------|-----|
| **iFood API** | Receber pedidos do iFood no dashboard RapiDrop |
| **WhatsApp Cloud API** | Receber pedidos via WhatsApp no dashboard |

---

## 9. Modelo de Dados — Todas as Tabelas

### 9.1 Convenções

```
PK  = Chave primária UUIDv7 (time-ordered)
FK  = Chave estrangeira
UX  = Índice único
IDX = Índice
jsonb = Campo flexível (varia por segmento)
```

**UUIDv7** é o padrão para todas as chaves primárias (`id`). Diferente do UUIDv4 (aleatório), o UUIDv7 é **ordenado por timestamp**, o que:
- Mantém índices B-tree do PostgreSQL sequenciais (sem fragmentação)
- Melhora performance de INSERT em tabelas com muitos registros
- Permite ordenação por criação sem campo `created_at` extra
- Gerado via `uuid.uuid7()` (nativo do Python 3.14+) ou função SQL `gen_uuid_v7()` via extensão `pg_uuidv7`

### 9.2 Contas e Acesso

```sql
-- Quem gerencia a plataforma (nós)
saas_admin
  id (PK), email (UX), name, password_hash,
  role (superadmin/support/finance)

-- Quem usa o SaaS para vender (lojistas)
merchant
  id (PK), name, business_name, document (CNPJ/CPF),
  email, phone, segment (food/pharmacy/grocery),
  address (jsonb), logo_url, is_active,
  settings (jsonb) → horários, taxa de entrega, etc
  created_at, trial_ends_at

-- Clientes finais (compram das lojas)
customer
  id (PK), name, phone (UX), phone_verified_at,
  email (UX), cpf, avatar_url,
  is_active, created_at

-- Login social dos clientes
customer_social_login
  id (PK), customer_id (FK), provider (google/apple),
  provider_user_id (UX)

-- Sessões dos clientes (refresh token)
customer_session
  id (PK), customer_id (FK),
  refresh_token_hash, device_info (jsonb),
  ip_address, expires_at

-- Push tokens dos clientes
customer_push_token
  id (PK), customer_id (FK),
  platform (ios/android/web), token
```

### 9.3 Endereços e Pagamentos (Cliente)

```sql
-- Endereços salvos do cliente
customer_address
  id (PK), customer_id (FK),
  label ("Casa", "Trabalho"),
  zipcode, street, number, complement,
  neighborhood, city, state,
  latitude, longitude, reference_point,
  is_default, is_active

-- Cartões e métodos de pagamento salvos
customer_payment_method
  id (PK), customer_id (FK),
  type (credit_card/pix/cash/card_on_delivery),
  gateway (stripe/asaas),
  gateway_payment_method_id (token),
  card_last_four (4 dígitos),
  card_brand (visa/mastercard),
  card_holder_name, card_expiry_month/year,
  is_default, is_active
```

### 9.4 Catálogo

```sql
-- Categorias de produtos (adaptável por segmento)
product_category
  id (PK), merchant_id (FK),
  name, sort_order, is_active,
  segment_fields (jsonb) → campos extras

-- Produtos
product
  id (PK), merchant_id (FK), category_id (FK),
  name, description, price_cents,
  image_url, barcode (EAN),
  unit_type (unit/kg/g/l/ml/pack/dozen),
  is_available, has_variations,
  stock_quantity, stock_alert_at,
  segment_specific (jsonb) → campos por segmento
    food: prep_time_minutes, recipe_url
    pharmacy: active_ingredient, tarja, requires_prescription, lab_name
    grocery: department, substitute_product_id

-- Variações de produto (tamanhos, sabores)
product_variation
  id (PK), product_id (FK),
  name ("Grande", "500mg", "1kg"),
  price_cents_adjustment, is_default
```

### 9.5 Pedidos

```sql
-- Pedido
order
  id (PK), merchant_id (FK), customer_id (FK),
  rider_id (FK), sequential_id (#42 por loja),
  channel (whatsapp/instagram/site/app/presencial),
  status (pending/confirmed/preparing/out_for_delivery/
          delivered/cancelled),
  items (jsonb) → lista de itens com preços,
  subtotal_cents, delivery_fee_cents,
  discount_cents, total_cents,
  payment_method, payment_status,
  customer_address (jsonb), customer_notes,
  segment_data (jsonb) → dados específicos,
  timestamps de cada status

-- Ligação entre pedido e entregador
order_rider
  id (PK), order_id (FK), rider_id (FK),
  status (assigned/accepted/picked_up/delivered),
  assigned_at, accepted_at, picked_up_at, delivered_at
```

### 9.6 Entregadores

```sql
-- Entregador
rider
  id (PK), merchant_id (FK),
  name, phone, vehicle_type (motorcycle/bike/car),
  document (CPF), pix_key (para pagamento),
  is_online, current_location (lat,lng,updated_at),
  is_active, created_at

-- Configuração de pagamento do entregador (por loja)
rider_payment_config
  id (PK), merchant_id (FK),
  method (daily_rate / per_delivery / hybrid),
  strategy (fixed_with_minimum / tiered_by_volume / etc),
  config (jsonb) → valores, faixas, bônus,
  ranking_enabled, ranking_config (jsonb)

-- Período de pagamento (ex: semana 01-07/ago)
rider_payment_period
  id (PK), merchant_id (FK), rider_id (FK),
  period_start, period_end,
  base_amount_cents, additional_cents,
  ranking_bonus_cents, total_cents,
  ranking_position,
  delivery_breakdown (jsonb),
  status (calculating/pending/approved/paid),
  paid_at, payment_method
```

### 9.7 Assinatura SaaS

```sql
-- Plano de precificação por segmento
pricing_plan
  id (PK), segment (food/pharmacy/grocery),
  name, percentage_rate (0.02 = 2%),
  trial_months, trial_max_orders

-- Assinatura do lojista (evolui com o tempo)
merchant_subscription
  id (PK), merchant_id (FK), pricing_plan_id (FK),
  status (trial/active_percentage/active_fixed/suspended/cancelled),
  current_phase (phase_1_percentage/phase_2_percentage/phase_2_fixed),
  percentage_rate,
  fixed_monthly_cents, fixed_monthly_next_review,
  trial_ends_at, trial_orders_count,
  billing_day, payment_gateway, gateway_customer_id,
  cancellation_reason, cancelled_at

-- Histórico de mudanças de fase
merchant_subscription_phase_log
  id (PK), subscription_id (FK),
  previous_phase, new_phase,
  changed_by (system/merchant/admin),
  metadata (jsonb) → dados do cálculo

-- Fatura do lojista para o SaaS
invoice
  id (PK), merchant_id (FK), subscription_id (FK),
  type (percentage/fixed/adjustment/credit),
  period_start, period_end, due_date,
  amount_cents, percentage_amount_cents,
  fixed_amount_cents, adjustments_cents,
  payment_status (pending/paid/overdue/cancelled),
  paid_at, payment_method, gateway_invoice_id

-- Detalhamento da fatura (percentual)
invoice_transaction
  id (PK), invoice_id (FK), order_id (FK),
  order_amount_cents, percentage_rate, amount_cents
```

### 9.8 Clientes, Favoritos e Fidelidade

```sql
-- Loja favorita do cliente
customer_favorite_store
  id (PK), customer_id (FK), store_id (FK), UX(customer,store),
  notify_promotions, notify_open

-- Produto favorito do cliente
customer_favorite_product
  id (PK), customer_id (FK), product_id (FK), store_id (FK),
  UX(customer,product)

-- Preferências de notificação
customer_notification_preference
  id (PK), customer_id (FK), store_id (FK),
  promotions, order_updates, reorder_reminders

-- Programa de fidelidade (config da loja)
loyalty_program
  id (PK), store_id (FK),
  type (stamp/points),
  stamp_goal, stamp_reward_type,
  points_per_reais_cents, points_redeem_cents

-- Selos/pontos do cliente
loyalty_stamp
  id (PK), customer_id (FK), store_id (FK),
  program_id (FK),
  stamps_count, points_balance

-- Movimentação de fidelidade
loyalty_transaction
  id (PK), stamp_id (FK),
  type (earn/redeem/expire),
  amount, description, order_id (FK)
```

### 9.9 Cupons e Promoções

```sql
-- Cupom de desconto
coupon
  id (PK), store_id (FK),
  code (UX), type (percentage/fixed_amount/free_delivery),
  value_cents, min_order_cents,
  usage_limit, usage_per_customer,
  applies_to (all/category/product), applies_to_id,
  valid_from, valid_until,
  weekday_only (array de dias),
  time_from, time_until,
  is_active

-- Cupom atribuído a um cliente específico
coupon_assignment
  id (PK), coupon_id (FK), customer_id (FK),
  reason (welcome/referral/birthday),
  used_at, expires_at

-- Indicação de amigos
referral
  id (PK), store_id (FK),
  referrer_customer_id (FK), referred_customer_id (FK),
  referral_code (UX),
  status (sent/clicked/registered/first_order/rewarded),
  referrer_reward_cents, referred_reward_cents
```

### 9.10 Farmácia (Específico)

```sql
-- Receita médica
prescription
  id (PK), order_id (FK), customer_id (FK),
  image_url (criptografado),
  doctor_name, doctor_crm,
  issue_date, expiry_date,
  validated_at, validated_by,
  status (pending/validated/rejected),
  rejection_reason
```

### 9.11 Pagamentos e Transações

```sql
-- Transação financeira (gateway)
payment_transaction
  id (PK), order_id (FK), merchant_id (FK),
  gateway (stripe/asaas/pagseguro),
  gateway_transaction_id,
  amount_cents, fee_cents,
  status, method,
  paid_at, refunded_at
```

---

## 10. Segurança

### 10.1 Autenticação e Autorização

| Mecanismo | Detalhe |
|-----------|---------|
| **JWT** | Access token (15 min) + Refresh token (7 dias) |
| **Senhas** | Hash com bcrypt |
| **OTP** | Login por celular via SMS (Twilio) / WhatsApp |
| **OAuth** | Login com Google e Apple (cliente final) |
| **RBAC** | 4 roles: `saas_admin`, `merchant_owner`, `rider`, `customer` |
| **Rate limit** | Por IP (60 req/min), por rota de auth (5 tentativas/min) |

### 10.2 Dados Sensíveis

| Dado | Proteção |
|------|----------|
| **Senhas** | Hash bcrypt |
| **Cartões de crédito** | Tokenizados no gateway (Stripe/Asaas) — nunca armazenamos número |
| **Receitas médicas** | Criptografia AES-256 em repouso. Acesso só do farmacêutico da loja |
| **Tokens JWT** | Armazenados em SecureStore (mobile) / httpOnly cookies (web) |
| **Dados do cliente** | LGPD: exportação e exclusão a pedido. Retenção máxima de 24 meses após último pedido |

### 10.3 Proteções de API

```
Toda request passa por:
  1. HTTPS (SSL/TLS)
  2. Rate limiting (redis)
  3. Validação de token (JWT)
  4. Verificação de tenant (só vê dados da sua loja)
  5. Validação de entrada (Pydantic/Zod)

Endpoints sensíveis (+ autenticação de 2 fatores):
  - Alterar chave PIX do entregador
  - Excluir conta
  - Ações financeiras
```

---

## 📌 Resumo Final — Stack em Uma Tabela

| Camada | Tecnologia | Versão |
|--------|-----------|:------:|
| **API** | FastAPI (Python) | 3.12+ |
| **ORM** | SQLAlchemy + Alembic | 2.x async |
| **Validação** | Pydantic | v2 |
| **Web app** | Next.js (App Router) | 15 |
| **Mobile** | React Native + Expo | 0.76+ / SDK 52 |
| **Mobile estilos** | NativeWind 4 (Tailwind) | 4.x |
| **Web estilos** | TailwindCSS + shadcn/ui | 4.x |
| **Dados frontend** | TanStack Query | v5 |
| **Formulários** | React Hook Form + Zod | — |
| **Animações** | Framer Motion / Reanimated 3 | — |
| **Banco principal** | PostgreSQL + PostGIS + pgvector | 16 |
| **Cache** | Redis | 7 |
| **Fila** | Celery + RabbitMQ | — |
| **Storage** | S3 / MinIO | — |
| **Container** | Docker + Docker Compose | — |
| **CI/CD** | GitHub Actions | — |
| **Infra** | Railway → AWS ECS | — |
| **Métricas** | Prometheus (scrape a cada 15s) | — |
| **Dashboards** | Grafana (SRE, Negócio, Mobile) | — |
| **Logs** | JSON estruturado (structlog) → Loki | — |
| **Tracing** | OpenTelemetry → Tempo / Jaeger | — |
| **Erros** | Sentry (crash reporting) | — |
| **Alertas** | Alertmanager → Slack + PagerDuty | — |
| **Qualidade de dados** | Great Expectations + dbt | — |
| **Governança** | Audit trail + LGPD nativa | — |
| **Pagamentos** | Stripe + Asaas | — |
| **Notificações** | Expo Push + WhatsApp + Resend | — |
| **Mapas (renderização)** | MapLibre GL JS + MapLibre GL Native | — |
| **Geocoding** | Nominatim + Photon (auto-hospedados) | — |
| **Routing** | OSRM (auto-hospedado, C++) | — |
| **Dados geográficos** | PostGIS + Redis GEO | — |
| **IA (futuro)** | Anthropic Claude + pgvector | — |

---

## 📁 Estrutura do Monorepo

```
rapidrop/
├── apps/
│   ├── api/                    # FastAPI (backend)
│   │   ├── src/
│   │   │   ├── core/           # Config, database, security
│   │   │   ├── modules/        # auth, orders, catalog, etc
│   │   │   ├── shared/         # Utilitários comuns
│   │   │   └── main.py
│   │   ├── alembic/            # Migrações
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── web/                    # Next.js (todos os sites)
│   │   ├── src/
│   │   │   ├── app/            # Rotas: /, /app, /admin
│   │   │   ├── components/
│   │   │   └── lib/
│   │   └── package.json
│   │
│   └── mobile/                 # React Native / Expo
│       ├── src/
│       │   ├── app/            # expo-router
│       │   └── components/
│       └── package.json
│
├── packages/                   # Código compartilhado
│   ├── shared/                 # Types, Zod schemas
│   ├── api-client/            # Hooks TanStack Query
│   └── tokens/                # Design tokens
│
├── docker-compose.yml
├── turbo.json                  # Turborepo
├── package.json                # Root (pnpm workspace)
└── .github/workflows/          # CI/CD
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.1
> **Baseado nos documentos:** `docs/ideacao-rapidrop.md`, `docs/assinatura-saas.md`,
> `docs/pagamento-entregadores.md`, `docs/experiencia-cliente.md`,
> `docs/observabilidade.md`, `docs/analise-dados.md`
