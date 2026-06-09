# RapiDrop — Observabilidade

> Prometheus + Grafana + OpenTelemetry + Logs Estruturados
> Como medimos, monitoramos e debugamos o RapiDrop em produção.

---

## Índice

1. [Filosofia](#1-filosofia)
2. [Stack de Observabilidade](#2-stack-de-observabilidade)
3. [Métricas (Prometheus)](#3-métricas-prometheus)
4. [Dashboards (Grafana)](#4-dashboards-grafana)
5. [Logs Estruturados](#5-logs-estruturados)
6. [Tracing Distribuído (OpenTelemetry)](#6-tracing-distribuído-opentelemetry)
7. [Alertas](#7-alertas)
8. [Instrumentação no Código](#8-instrumentação-no-código)
9. [Métricas de Negócio](#9-métricas-de-negócio)

---

## 1. Filosofia

### 1.1 Os Três Pilares

```
OBSERVABILIDADE NO RAPIDROP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
  │    MÉTRICAS     │  │      LOGS       │  │     TRACING     │
  │  (Prometheus)   │  │ (JSON stdout)   │  │ (OpenTelemetry) │
  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
  │ O que está      │  │ O que aconteceu │  │ Por que         │
  │ acontecendo?    │  │ exatamente?     │  │ está lento?     │
  │                 │  │                 │  │                 │
  │ "Quantos        │  │ "Pedido #1234  │  │ "O request      │
  │  pedidos/min?"  │  │  falhou porque  │  │  demorou 2s no  │
  │ "Latência       │  │  gateway        │  │  banco, 1s no   │
  │  média?"        │  │  recusou"       │  │  Redis"         │
  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 1.2 Princípios

| Princípio | Prática |
|-----------|---------|
| **Tudo é métrica** | Se algo pode ser medido, viramos métrica. |
| **Log estruturado sempre** | JSON, nunca texto solto. Facilita busca e agregação. |
| **Alertas que acordam** | Só alarmamos o que exige ação humana imediata. |
| **Dashboards para cada persona** | Dev, DevOps, Product Manager — cada um vê o que importa. |
| **Custo controlado** | Métricas cardinalizadas (sem tags únicas infinitas). Logs com rotação. |
| **Privacidade** | Nunca logamos dados sensíveis (senhas, tokens, cartões, CPF). |

---

## 2. Stack de Observabilidade

### 2.1 Ferramentas

```
Coleta de métricas:  Prometheus (com service discovery via Docker/AWS)
Visualização:        Grafana (dashboards + alertas)
Logs:                JSON stdout → Loki / CloudWatch
Tracing:             OpenTelemetry (instrumentação automática + manual)
Erros:               Sentry (exceções não tratadas, crash reporting)
Health checks:       Uptime Kuma / Grafana Synthetic Monitoring
```

### 2.2 Como os Dados Fluem

```
┌──────────────────────────────────────────────────────────────────┐
│                         APLICAÇÃO                                 │
│                                                                   │
│  ┌────────────┐   ┌──────────────┐   ┌──────────────────────┐   │
│  │ FastAPI    │   │  Celery      │   │  Next.js / Mobile    │   │
│  │ metrics    │   │  metrics     │   │  Web Vitals          │   │
│  │ endpoint   │   │  (prometheus │   │  (CLS, LCP, FID)     │   │
│  │ /metrics   │   │   client)    │   │                      │   │
│  └──────┬─────┘   └──────┬───────┘   └──────────┬───────────┘   │
│         │                │                       │                │
│         └────────────────┼───────────────────────┘                │
│                          ▼                                       │
│                 ┌────────────────┐                               │
│                 │   /metrics     │                               │
│                 │  (HTTP GET)    │                               │
│                 └────────────────┘                               │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼ scrape (a cada 15s)
                  ┌──────────────────┐
                  │   PROMETHEUS     │
                  │                  │
                  │ Armazena séries  │
                  │ temporais        │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
      ┌────────────┐ ┌──────────┐ ┌────────────┐
      │  GRAFANA   │ │ ALERTMANAGER│ │  API       │
      │  Dashboards│ │          │   │ Query      │
      │  + Alertas │ │ Notifica │   │ (grafana)  │
      └────────────┘ │ Slack    │   └────────────┘
                     │ Email    │
                     │ PagerDuty│
                     └──────────┘

Logs:
  Aplicação → JSON stdout → Loki / CloudWatch → Grafana (explore)

Tracing:
  FastAPI → OpenTelemetry → Jaeger / Tempo → Grafana

Erros:
  App → Sentry (stack trace + contexto)
```

### 2.3 Stack de Logs

| Serviço | Função |
|---------|--------|
| **JSON stdout** | Todo log da aplicação em JSON (não arquivo) |
| **Loki** | Agregador de logs (Grafana Labs) — query tipo PromQL |
| **CloudWatch Logs** | Fallback AWS (se estamos em ECS) |
| **Docker driver** | `json-file` com rotação (local) / `awslogs` (produção) |

### 2.4 Stack de Tracing

| Serviço | Função |
|---------|--------|
| **OpenTelemetry SDK** | Instrumentação automática + manual no Python/JS |
| **Tempo (Grafana)** | Backend de tracing (alternativa: Jaeger) |
| **Grafana** | Visualização de traces conectados a métricas e logs |

---

## 3. Métricas (Prometheus)

### 3.1 Como Instrumentamos

```
No FastAPI, expomos um endpoint /metrics que o Prometheus scrapeia.

Integração nativa:
  pip install prometheus-fastapi-instrumentator

from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

Isso já gera automaticamente:
  - http_request_duration_seconds (bucket por endpoint)
  - http_request_total (contador por status code)
  - http_request_size_bytes
  - http_response_size_bytes
```

### 3.2 Métricas por Categoria

#### 🖥️ Métricas de Sistema (Infra)

| Métrica | Descrição | Alerta? |
|---------|-----------|:-------:|
| `cpu_usage_percent` | CPU do container/servidor | ✅ > 80% |
| `memory_usage_bytes` | Memória usada | ✅ > 85% |
| `disk_usage_percent` | Disco (logs, uploads) | ✅ > 80% |
| `postgres_connections` | Conexões ativas no banco | ✅ > 80% do max |
| `postgres_replication_lag` | Atraso da réplica | ✅ > 10s |
| `redis_memory_usage_bytes` | Memória usada no Redis | ✅ > 80% |
| `rabbitmq_queue_messages` | Mensagens na fila | ✅ > 1000 |
| `docker_container_restarts` | Reinícios de container | ✅ > 0 em 5min |

#### ⚙️ Métricas de Aplicação (FastAPI)

| Métrica | Descrição | Rótulos |
|---------|-----------|---------|
| `http_requests_total` | Total de requests | method, endpoint, status_code |
| `http_request_duration_seconds` | Latência (bucket) | method, endpoint (p50, p95, p99) |
| `http_requests_in_flight` | Requests simultâneos | method |
| `http_exceptions_total` | Erros 5xx | endpoint, exception_type |
| `http_requests_by_merchant` | Requests por lojista | merchant_id (cardinalidade controlada) |
| `websocket_connections_active` | Conexões WebSocket ativas | — |
| `celery_tasks_total` | Tasks executadas | task_name, status |
| `celery_task_duration_seconds` | Duração das tasks | task_name |
| `celery_queue_length` | Tasks na fila | queue_name |

#### 📊 Métricas de Negócio (Custom)

| Métrica | Descrição | Rótulos |
|---------|-----------|---------|
| `orders_total` | Pedidos criados | merchant_id, segment, channel |
| `orders_by_status` | Pedidos por status | merchant_id, status |
| `orders_revenue_cents_total` | Faturamento total | merchant_id, segment |
| `orders_avg_ticket_cents` | Ticket médio | merchant_id, segment |
| `orders_cancellation_rate` | % de cancelamento | merchant_id, reason |
| `riders_online_total` | Entregadores online | merchant_id |
| `riders_acceptance_rate` | % de aceite de entregas | merchant_id |
| `delivery_time_seconds` | Tempo até entrega (bucket) | merchant_id, segment |
| `customers_registered_total` | Clientes cadastrados | merchant_id |
| `subscriptions_by_phase` | Assinaturas por fase | phase (percentage/fixed) |
| `subscription_revenue_cents_total` | Receita de assinaturas | merchant_id |
| `merchants_by_segment` | Lojistas ativos por segmento | segment |
| `promotions_usage_total` | Uso de cupons | coupon_id, merchant_id |

#### 📱 Métricas Mobile

| Métrica | Descrição | Fonte |
|---------|-----------|-------|
| `app_crashes_total` | Crash rate | Sentry → Prometheus |
| `app_screen_views` | Telas abertas | Firebase Analytics |
| `app_order_conversion` | Carrinho → pedido | Backend |
| `push_notification_open_rate` | % que abriu notificação | Backend |

### 3.3 Cardinalidade — Regras para não explodir

```
⚠️ Cardinalidade é o número de séries temporais únicas.

Regras:
  1. merchant_id como label: APENAS para top 20 merchants
     (senão Prometheus explode com milhares de séries)

  2. Tags com valores únicos infinitos são PROIBIDOS:
     ❌ order_id, request_id, session_id, email, phone
     ✅ status_code, method, segment, phase, channel

  3. Para métricas por lojista (ordens, faturamento):
     → Agregar em labels de segment (food/pharmacy/grocery)
     → Detalhamento por lojista vai para Grafana via SQL
       (query no Postgres, não no Prometheus)

  4. Métricas de negócio com alta cardinalidade:
     → Exportar para tabela separada no PostgreSQL
     → Grafana consulta direto no banco (SQL)
     → Prometheus só para agregações leves
```

---

## 4. Dashboards (Grafana)

### 4.1 Dashboards por Persona

| Dashboard | Para quem | Principal informação |
|-----------|-----------|---------------------|
| **Visão Geral (SRE)** | DevOps/CTO | CPU, memória, latência, erros, filas |
| **API Performance** | Backend | Latência p50/p95/p99 por endpoint, taxa de erro |
| **Pedidos em Tempo Real** | Suporte | Pedidos/minuto, cancelamentos, entregas ativas |
| **Negócio Executivo** | CEO/PM | Lojistas ativos, receita, ticket médio, churn |
| **Saúde do Banco** | DBA/DevOps | Conexões, slow queries, tamanho do banco, replicação |
| **Entregadores** | Operações | Online/offline, tempo de entrega, aceite |
| **Mobile** | Mobile Dev | Crash rate, tela mais acessada, conversão |
| **Assinatura SaaS** | Financeiro | Lojistas em cada fase, MRR, churn, inadimplência |

### 4.2 Dashboard Visão Geral (SRE) — Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  🟢 RAPIDROP — VISÃO GERAL (PRODUÇÃO)                        🇧🇷    │
│  Últimos 60 minutos                                         [ 🔄 ] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Requests/s  │ │ Latência    │ │ Erro %      │ │ Pedidos     │   │
│  │    142      │ │   187ms     │ │   0.3%      │ │   28/min    │   │
│  │ ▲ 12%       │ │ p50  p95    │ │ 5xx  4xx    │ │             │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  LATÊNCIA P50 / P95 / P99 POR ENDPOINT                   5m  │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │  ╱‾‾‾╲           ╱╲                                   │ │   │
│  │  │ ╱    ╲─────────╱──╲─────── p99                        │ │   │
│  │  │╱                       ╲─── p95                        │ │   │
│  │  │                          ╲── p50                       │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │  14:00   14:10   14:20   14:30   14:40   14:50             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐    │
│  │  HTTP ERROR RATE     │  │  TOP SLOW ENDPOINTS              │    │
│  │  ┌────────────┐      │  │  ┌─────────────────────────────┐ │    │
│  │  │ ╱╲          │      │  │  │ POST /orders       892ms  │ │    │
│  │  │╱  ╲___      │      │  │  │ GET /catalog       654ms  │ │    │
│  │  │       ╲     │      │  │  │ POST /payments     512ms  │ │    │
│  │  │         ╲_  │      │  │  └─────────────────────────────┘ │    │
│  │  └────────────┘      │  └──────────────────────────────────┘    │
│  └──────────────────────┘                                          │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐    │
│  │  CPU / MEMÓRIA       │  │  FILAS (RabbitMQ)                │    │
│  │  CPU: ████████░░ 72% │  │  ┌─── ─── ─── ───               │    │
│  │  RAM: ██████░░░ 58% │  │  │ notifications     23 msg      │    │
│  │  DISK:███░░░░░ 32%  │  │  │ webhooks           5 msg      │    │
│  │  PG: ████████░ 78%  │  │  │ emails             0 msg      │    │
│  └──────────────────────┘  │  │ imports            1 msg      │    │
│                            │  └─── ─── ─── ───               │    │
│                            └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Dashboard de Negócio — Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 RAPIDROP — NEGÓCIO                                        MÊS  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Lojistas    │ │ MRR         │ │ Ticket Médio│ │ Pedidos     │   │
│  │ Ativos      │ │ R$ 47.320   │ │ R$ 48,50    │ │ 142.830     │   │
│  │ 342         │ │ ▲ 8% vs mês │ │ ▲ 3% vs mês │ │ ▲ 15% vs mês│   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────┐ ┌──────────────────────────┐  │
│  │  LOJISTAS POR SEGMENTO           │ │  RECEITA POR SEGMENTO    │  │
│  │  ┌───────────┐                   │ │  ┌───────────┐           │  │
│  │  │ 🍕 68%    │                   │ │  │ 🍕 72%    │           │  │
│  │  │ 💊 22%    │                   │ │  │ 💊 18%    │           │  │
│  │  │ 🛒 10%    │                   │ │  │ 🛒 10%    │           │  │
│  │  └───────────┘                   │ │  └───────────┘           │  │
│  └──────────────────────────────────┘ └──────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────┐ ┌──────────────────────────┐  │
│  │  CHURN MENSAL                    │ │  ASSINATURAS POR FASE   │  │
│  │  ┌──────────────────┐           │ │  ┌──────────────────┐    │  │
│  │  │  ░░░░░░░░░░░░░░ 5.2% │           │  │ Fase 1: 78%     │    │  │
│  │  │  Meta: < 5%     │           │ │  │ Fase 2%: 15%     │    │  │
│  │  │  ████████████████  │           │  │ Fase 2 fixo: 7%  │    │  │
│  │  └──────────────────┘           │ │  └──────────────────┘    │  │
│  └──────────────────────────────────┘ └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Logs Estruturados

### 5.1 Formato — Sempre JSON

```
❌ ERRADO: "Pedido 1234 finalizado com sucesso"
✅ CERTO:   {"event": "order.completed", "order_id": 1234, "merchant_id": 42,
             "total_cents": 4990, "duration_ms": 340, "channel": "site",
             "trace_id": "abc123", "timestamp": "2026-06-09T14:30:00Z"}
```

### 5.2 Campos Obrigatórios em Todo Log

```json
{
  "timestamp": "2026-06-09T14:30:00.123Z",
  "level": "info",
  "service": "api",
  "environment": "production",
  "trace_id": "abc123def456",
  "span_id": "789ghi",
  "event": "order.created",
  "message": "Novo pedido criado",
  "merchant_id": 42,
  "request_id": "req_xyz",
  "duration_ms": 340
}
```

| Campo | Obrigatório? | Descrição |
|-------|:-----------:|-----------|
| `timestamp` | ✅ | ISO 8601 com timezone |
| `level` | ✅ | debug, info, warn, error, fatal |
| `service` | ✅ | api, web, mobile, worker |
| `environment` | ✅ | production, staging, local |
| `trace_id` | ✅ | Correlation ID (OpenTelemetry) |
| `event` | ✅ | Nome do evento (ex: `order.completed`) |
| `message` | ✅ | Legível para humanos |
| `merchant_id` | Quando aplicável | Filtro por lojista |
| `request_id` | Quando aplicável | ID da requisição HTTP |

### 5.3 Níveis de Log

| Nível | Uso | Exemplo |
|-------|-----|---------|
| **debug** | Desenvolvimento — não vai para produção | "Cache miss for key X" |
| **info** | Eventos de negócio importantes | "Pedido #123 foi pago" |
| **warn** | Algo errado, mas não crítico | "Gateway pagamento recusou — tentando de novo" |
| **error** | Algo quebrou, precisa investigar | "Falha ao conectar no gateway após 3 tentativas" |
| **fatal** | Sistema não pode continuar | "Banco de dados indisponível" |

### 5.4 O que NUNCA logar

```
❌ Senhas, tokens, secrets
❌ Número completo de cartão de crédito
❌ CPF completo (logar só últimos 3 dígitos: ***.***.**-23)
❌ Dados biométricos
❌ Conteúdo de mensagens privadas
❌ Chaves de API
```

### 5.5 Configuração no FastAPI

```python
# src/core/logging.py

import structlog
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id")

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Em produção: JSON
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None):
    return structlog.get_logger(name)
```

### 5.6 Uso no Código

```python
# Antes (ruim)
logger.info(f"Pedido {order_id} finalizado. Total: R$ {total}")

# Depois (bom)
logger.info(
    "order.completed",
    order_id=order.id,
    merchant_id=order.merchant_id,
    total_cents=order.total_cents,
    duration_ms=order.delivery_duration_ms,
    channel=order.channel,
)
```

### 5.7 No Next.js (Frontend Web)

```typescript
// lib/logging.ts

type LogLevel = "debug" | "info" | "warn" | "error"

interface LogEntry {
  timestamp: string
  level: LogLevel
  service: "web" | "mobile"
  event: string
  message: string
  [key: string]: unknown
}

function log(level: LogLevel, event: string, message: string, data?: Record<string, unknown>) {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level,
    service: typeof window === "undefined" ? "web" : "mobile",
    event,
    message,
    ...data,
  }

  if (process.env.NODE_ENV === "production") {
    // Em produção: envia para Loki via API
    fetch("/api/logs", {
      method: "POST",
      body: JSON.stringify(entry),
    }).catch(() => {})
  } else {
    console[JSON.stringify(entry, null, 2)]
  }
}

export const logger = {
  debug: (event: string, message: string, data?: Record<string, unknown>) => log("debug", event, message, data),
  info: (event: string, message: string, data?: Record<string, unknown>) => log("info", event, message, data),
  warn: (event: string, message: string, data?: Record<string, unknown>) => log("warn", event, message, data),
  error: (event: string, message: string, data?: Record<string, unknown>) => log("error", event, message, data),
}
```

---

## 6. Tracing Distribuído (OpenTelemetry)

### 6.1 Por que Precisamos

```
Cenário: Um pedido demorou 30 segundos para ser criado.
Onde está o gargalo?

Sem tracing:     "O pedido está lento" → chute
Com tracing:     "O request /orders gastou:
                   • 2s no auth
                   • 25s no gateway de pagamento
                   • 1s no catálogo
                   • 2s no banco"
```

### 6.2 Como Funciona

```
┌─────────────────────────────────────────────────────────────────┐
│  🕐 REQUEST HTTP POST /api/v1/orders                            │
│                                                                  │
│  Trace ID: abc123 (mesmo ID em todos os serviços)                │
│                                                                  │
│  ┌─ FastAPI ──────────────────────────────────────────────────┐  │
│  │  Span: POST /orders                            Total: 30s  │  │
│  │  ├─ Span: validate_auth()                      0.002s      │  │
│  │  ├─ Span: validate_cart()                      0.001s      │  │
│  │  ├─ Span: process_payment(gateway)             25s   ← 🐌  │  │
│  │  ├─ Span: save_order(db)                       0.050s      │  │
│  │  ├─ Span: publish_event(rabbitmq)               0.010s      │  │
│  │  └─ Span: send_notification(whatsapp)           1.5s        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  → Trace exportado para Tempo / Jaeger                           │
│  → Visualizado no Grafana (Explore → Traces)                     │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Instrumentação no FastAPI

```python
# main.py (setup)
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource.create({"service.name": "api"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://tempo:4317"))
)
trace.set_tracer_provider(provider)

# Instrumentação automática
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument()
RequestsInstrumentor().instrument()
```

### 6.4 Tracing Manual (para blocos críticos)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def create_order(data: OrderCreate):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("merchant_id", data.merchant_id)
        span.set_attribute("total_cents", data.total_cents)

        with tracer.start_as_current_span("validate_prescription"):
            # Só para farmácia
            ...

        with tracer.start_as_current_span("process_payment"):
            result = await gateway.charge(data.payment)
            span.set_attribute("payment_success", result.success)
            if not result.success:
                span.set_status(Status(StatusCode.ERROR, "Payment failed"))
```

---

## 7. Alertas

### 7.1 Categorias de Alerta

```
🔴 P0 — Crítico (acorda alguém 24h)
    ├─ API com erro > 5% nos últimos 5 minutos
    ├─ Banco de dados offline
    ├─ Filas de pagamento paradas > 10 minutos
    └─ Qualquer endpoint com latência > 10s (p99)

🟡 P1 — Alto (alerta em horário comercial)
    ├─ CPU > 80% por mais de 15 minutos
    ├─ Disco > 80%
    ├─ Mais de 50 erros 5xx/hora em qualquer endpoint
    ├─ Redis com memória > 80%
    └─ RabbitMQ com mais de 1000 mensagens na fila

🔵 P2 — Médio (dashboard, notificação no Slack)
    ├─ Churn mensal acima de 7%
    ├─ Queda de > 20% em pedidos na última hora vs mesma hora ontem
    ├─ Novo deploy feito (notificação)
    └─ Certificado SSL perto de expirar (< 7 dias)

⚪ P3 — Baixo (ticket no sistema, sem urgência)
    ├─ Slow query (> 5s) identificada
    ├─ Log de warning repetitivo
    └─ Uso de disco crescendo acima do normal
```

### 7.2 Regras de Alerta (Prometheus + Alertmanager)

```yaml
# Exemplos de regras (prometheus-rules.yml)

groups:
  - name: api_alerts
    rules:
      # 🔴 P0: Erro alto na API
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 2m
        labels:
          severity: critical
          priority: P0
        annotations:
          summary: "API com {{ $value | humanizePercentage }} de erro"
          runbook: "https://wiki.rapidrop.com.br/runbooks/high-error-rate"

      # 🔴 P0: Latência alta
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
          ) > 10
        for: 2m
        labels:
          severity: critical
          priority: P0
        annotations:
          summary: "Endpoint {{ $labels.endpoint }} com p99 > 10s"

      # 🟡 P1: Banco de dados
      - alert: PostgresHighConnections
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
          priority: P1
        annotations:
          summary: "PostgreSQL com {{ $value }} conexões ativas"

      # 🟡 P1: Tasks na fila
      - alert: QueueBacklog
        expr: rabbitmq_queue_messages > 1000
        for: 5m
        labels:
          severity: warning
          priority: P1
        annotations:
          summary: "Fila {{ $labels.queue }} com {{ $value }} mensagens"

      # 🔵 P2: Queda de pedidos
      - alert: OrderDrop
        expr: |
          rate(orders_total[1h])
          / on()
          rate(orders_total[1h] offset 1d)
          < 0.8
        for: 10m
        labels:
          severity: info
          priority: P2
        annotations:
          summary: "Queda de {{ $value | humanizePercentage }} nos pedidos vs ontem"
```

### 7.3 Canais de Notificação

| Canal | Para qual alerta |
|-------|------------------|
| **Slack (#rapidrop-alerts)** | 🔴 P0 + 🟡 P1 + 🔵 P2 |
| **SMS / Push (PagerDuty)** | 🔴 P0 (se não confirmar em 5min no Slack) |
| **Email** | 🔵 P2 + ⚪ P3 (resumo diário) |
| **WhatsApp** | 🔴 P0 (grupo de plantão) |

---

## 8. Instrumentação no Código

### 8.1 Decorator para Métricas Custom

```python
# src/shared/metrics.py

from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
from time import time

# Definição das métricas
orders_total = Counter(
    "orders_total",
    "Total de pedidos criados",
    ["merchant_id", "segment", "channel"],
)

order_duration = Histogram(
    "order_duration_seconds",
    "Tempo do pedido (criação até entrega)",
    ["merchant_id", "segment"],
    buckets=[60, 120, 300, 600, 1200, 1800, 3600],
)

active_riders = Gauge(
    "active_riders",
    "Entregadores online",
    ["merchant_id"],
)

delivery_distance = Histogram(
    "delivery_distance_km",
    "Distância percorrida na entrega",
    ["merchant_id"],
    buckets=[1, 2, 3, 5, 7, 10, 15, 20],
)


def track_order_metrics(merchant_id: str, segment: str, channel: str):
    """Decorator para registrar métricas de pedido"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time()
            result = await func(*args, **kwargs)
            duration = time() - start

            orders_total.labels(
                merchant_id=merchant_id,
                segment=segment,
                channel=channel,
            ).inc()

            order_duration.labels(
                merchant_id=merchant_id,
                segment=segment,
            ).observe(duration)

            return result
        return wrapper
    return decorator
```

### 8.2 Health Check Endpoint

```python
# src/core/health.py

from fastapi import APIRouter
from src.core.database import get_session
from src.core.redis import redis_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check usado pelo load balancer e Prometheus"""
    checks = {
        "status": "ok",
        "database": await check_database(),
        "redis": await check_redis(),
        "version": "1.0.0",
    }

    if all(check.get("status") == "ok" for check in checks.values()
           if isinstance(check, dict)):
        return {"status": "ok", "checks": checks}

    return {"status": "degraded", "checks": checks}


async def check_database():
    try:
        # Query simples para verificar conexão
        async with get_session() as session:
            await session.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def check_redis():
    try:
        await redis_client.ping()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## 9. Métricas de Negócio

### 9.1 As Métricas que REALMENTE Importam

São as que respondem: "O RapiDrop está saudável como negócio?"

| Métrica | O que mede | Fonte | Alerta se |
|---------|-----------|-------|-----------|
| **Lojistas Ativos (MAU)** | Lojistas que venderam no mês | PostgreSQL (SQL) | Cair > 10% vs mês anterior |
| **MRR (Monthly Recurring Revenue)** | Receita recorrente de assinaturas | PostgreSQL (SQL) | Cair > 5% |
| **Churn Rate** | % de lojistas que cancelaram | PostgreSQL (SQL) | > 7% no mês |
| **Ticket Médio** | Valor médio por pedido | PostgreSQL (SQL) | Cair > 15% |
| **Pedidos/dia** | Volume de pedidos processados | Prometheus | Cair > 20% vs 7 dias atrás |
| **Tempo Médio de Entrega** | Do pedido até a entrega | Prometheus | > 60 min (food) |
| **% de Cancelamento** | Cancelamentos vs total | Prometheus | > 8% |
| **Engajamento (cliente)** | % de clientes que repetem pedido | PostgreSQL (SQL) | < 30% |
| **Novos Lojistas** | Lojistas que se cadastraram | PostgreSQL (SQL) | Zero por 7 dias |

### 9.2 Dashboard de Negócio (Grafana com SQL)

Para métricas de negócio, ao invés de Prometheus, consultamos **diretamente o PostgreSQL**:

```sql
-- Exemplo: MRR (Monthly Recurring Revenue)
SELECT
    DATE_TRUNC('month', i.created_at) AS month,
    SUM(i.amount_cents) / 100.0 AS revenue_brl,
    COUNT(DISTINCT i.merchant_id) AS paying_merchants
FROM invoice i
WHERE i.payment_status = 'paid'
    AND i.created_at >= NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', i.created_at)
ORDER BY month DESC;

-- Exemplo: Churn rate
WITH months AS (
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        COUNT(*) AS active_merchants
    FROM merchant
    WHERE is_active = true
        AND created_at >= NOW() - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', created_at)
),
cancellations AS (
    SELECT
        DATE_TRUNC('month', cancelled_at) AS month,
        COUNT(*) AS cancelled
    FROM merchant
    WHERE cancelled_at IS NOT NULL
        AND cancelled_at >= NOW() - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', cancelled_at)
)
SELECT
    m.month,
    m.active_merchants,
    COALESCE(c.cancelled, 0) AS cancelled,
    (COALESCE(c.cancelled, 0) * 100.0 / m.active_merchants) AS churn_rate_pct
FROM months m
LEFT JOIN cancellations c ON m.month = c.month
ORDER BY m.month DESC;
```

---

## 📌 Checklist de Implementação

### 🚀 Fase 1 — Setup Inicial (MVP)

```
[ ] prometheus.yml configurado (scrape /metrics a cada 15s)
[ ] FastAPI com prometheus-fastapi-instrumentator
[ ] Endpoint /health implementado
[ ] Logs em JSON (structlog) configurados
[ ] docker-compose com Prometheus + Grafana
[ ] Dashboard "Visão Geral (SRE)" criado
```

### 📈 Fase 2 — Métricas de Negócio

```
[ ] Métricas custom de pedidos, entregadores, clientes
[ ] Métricas de assinatura SaaS (fase 1, fase 2)
[ ] Dashboard "Negócio Executivo" criado
[ ] Dashboard "Assinatura SaaS" criado
[ ] Alertas P0 configurados (Slack + PagerDuty)
```

### 🔍 Fase 3 — Tracing e Profiling

```
[ ] OpenTelemetry SDK no FastAPI
[ ] Tempo/Jaeger configurado como backend de tracing
[ ] Tracing manual nos blocos críticos (pagamento, webhook)
[ ] Dashboard "API Performance" com traces
[ ] Sentry integrado para exceções
```

### 🛡️ Fase 4 — Maturidade

```
[ ] Testes de carga com k6 + métricas exportadas
[ ] Synthetic monitoring (Grafana) — ping endpoints a cada 5min
[ ] Runbooks para cada alerta P0
[ ] Revisão trimestral de métricas e dashboards
[ ] Budget de alertas (não alarmar sem necessidade)
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
