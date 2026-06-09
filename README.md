# RapiDrop — Delivery Intelligence

**SaaS multi-segmento de delivery** para restaurantes, farmácias, mercados e qualquer negócio que queira ter seu próprio canal de entregas — sem depender de iFood ou similares.

## Stack

```yaml
Backend:
  Python 3.14 | FastAPI | SQLAlchemy 2.x async
  PostgreSQL 16 + PostGIS + pgvector
  Redis 7 | Celery 5 | RabbitMQ 4

Frontend Web:
  Next.js 15 (App Router) | React 19 | TypeScript 5.x
  Tailwind CSS v4 | TanStack Query v5 | Framer Motion

Mobile:
  React Native 0.76 (New Architecture) | Expo SDK 52
  NativeWind 4 | Reanimated 3 | Gesture Handler
  MapLibre GL (mapas e rotas)

Infra:
  Docker Compose (dev) | Railway → AWS ECS (prod)
  Prometheus + Grafana + Loki + Tempo + OpenTelemetry
  Sentry (erros) | MinIO (assets S3-compatible)

Pagamentos:
  Asaas (marketplace de pagamentos)

Monorepo:
  Turborepo + pnpm workspaces
```

## Estrutura do Monorepo

```
rapidrop/
├── apps/
│   ├── api/              # Backend FastAPI
│   │   ├── src/
│   │   │   ├── api/          # Rotas públicas (health, CEP)
│   │   │   ├── core/         # Config, database, auth deps, uuid7
│   │   │   ├── models/       # SQLAlchemy models (23 tabelas)
│   │   │   ├── modules/      # Módulos funcionais
│   │   │   │   ├── auth/     # Registro, login, JWT, refresh
│   │   │   │   ├── merchants/# Perfil, configurações, logo
│   │   │   │   ├── onboarding/ # State machine (5 etapas)
│   │   │   │   ├── categories/ # CRUD de categorias
│   │   │   │   └── products/   # CRUD de produtos + variações
│   │   │   └── integrations/ # ViaCEP, Asaas, etc.
│   │   ├── alembic/        # Migrations (23 tabelas criadas)
│   │   └── tests/          # Testes (pytest)
│   │
│   ├── web/              # Frontend Next.js (painel do lojista)
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (auth)/     # Login + Registro (3 etapas)
│   │       │   ├── app/        # Dashboard, Sidebar, Produtos, Categorias, Config
│   │       │   ├── onboarding/ # Checklist de onboarding
│   │       │   └── admin/      # Admin multi-loja
│   │       ├── components/     # Button, Input, Card, etc.
│   │       └── lib/            # API client, Auth context
│   │
│   └── mobile/           # App React Native + Expo
│       └── src/
│           ├── app/          # Telas (expo-router)
│           ├── components/   # UI components
│           └── lib/          # API client, hooks, stores
│
├── packages/
│   ├── shared/           # Tipos TypeScript, schemas Zod
│   ├── api-client/       # TanStack Query hooks, fetch wrapper
│   └── tokens/           # Design tokens (Figma → código)
│
├── docs/                 # 14 documentos de especificação
├── infra/                # Config Prometheus, Grafana, etc.
├── docker-compose.yml    # PostgreSQL, Redis, RabbitMQ, MinIO, etc.
├── turbo.json            # Pipeline Turborepo
└── Makefile              # Comandos de setup, dev, test
```

## Funcionalidades Implementadas

### Autenticação e Multi-tenancy
- Registro de lojista com 3 etapas (dados, endereço, segmento)
- Login com JWT (access token + refresh token)
- Auto-refresh transparente no frontend
- Isolamento multi-tenant por `merchant_id`

### Onboarding do Lojista
- State machine com 5 etapas: perfil → endereço → segmento → produtos → pagamento
- API de progresso e avanço controlado

### Produtos e Categorias
- CRUD completo de categorias (soft-delete, ordenação)
- CRUD completo de produtos com variações (tamanhos, preços)
- Upload de logo (placeholder)
- Filtros por categoria, disponibilidade, busca textual

### Configurações da Loja
- Horários de funcionamento (JSON)
- Área de entrega (GeoJSON)
- Taxa de entrega

### Financeiro
- Integração Asaas para split de pagamentos
- Repasse automático para entregadores

### Observabilidade
- Prometheus + Grafana (métricas)
- Loki (logs) + Tempo (tracing distribuído)
- OpenTelemetry SDK instrumentado
- Sentry para captura de erros

## Pré-requisitos

- **Docker** + Docker Compose
- **Python 3.12+** e Poetry (`pipx install poetry`)
- **Node.js 22+** e pnpm (`npm install -g pnpm`)

## Desenvolvimento Local

```bash
# 1. Clone e entre no diretório
git clone git@github.com:clsalberto-ads/rapidrop.git
cd rapidrop

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env se necessário (padrão já funciona para dev local)

# 3. Setup completo (infra + dependências + migrations)
make setup

# Os serviços serão iniciados em segundo plano:
#   PostgreSQL :5432, Redis :6379, RabbitMQ :5672
#   MinIO :9000, Prometheus :9090, Grafana :3001

# 4. Inicie todos os serviços
make up

# URLs locais:
#   API:      http://localhost:8000
#   Web:      http://localhost:3000
#   Grafana:  http://localhost:3001
#   MinIO:    http://localhost:9001
```

### Comandos úteis

```bash
make test     # Roda testes do backend e frontend
make lint     # Ruff (Python) + ESLint (frontend)
make logs     # Logs dos containers Docker
make down     # Para todos os serviços
make clean    # Remove containers e diretórios de build
```

Também é possível iniciar cada app individualmente:

```bash
# API (http://localhost:8000)
cd apps/api && poetry run uvicorn src.main:app --reload

# Web (http://localhost:3000)
cd apps/web && pnpm dev

# Mobile
cd apps/mobile && pnpm dev
```

## Testes

```bash
# Backend (pytest)
cd apps/api && poetry run pytest -v

# Frontend (vitest)
cd apps/web && pnpm test
```

## Pipeline CI/CD

GitHub Actions com 6 jobs paralelos:

1. **Lint Python** — Ruff + mypy strict
2. **Lint Web** — ESLint + Prettier
3. **Test API** — pytest com cobertura
4. **Test Web** — vitest
5. **Build API** — Docker build + scan
6. **Build Web** — next build

## Migrations (Alembic)

```bash
cd apps/api

# Criar nova migration
alembic revision --autogenerate -m "descricao"

# Aplicar pendentes
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Decisões Técnicas

- **UUIDv7** como chave primária (time-ordered, evita index fragmentation)
- **Monolito bem definido** no backend (FastAPI + módulos), não microsserviços
- **RLS (Row-Level Security)** via SQL para isolar dados de cada lojista
- **State machine** para pedidos e onboarding (evita estado inconsistente)
- **Offline-first** no mobile com WatermelonDB + sync
- **Single package** para pagamentos via Asaas (split automático)
- **Core Web Vitals** e SEO técnico como requisito, não depois

## Pacotes Compartilhados

| Pacote | Descrição |
|--------|-----------|
| `@rapidrop/shared` | Tipos TypeScript e schemas Zod validados por backend e frontend |
| `@rapidrop/api-client` | Hooks TanStack Query e fetch wrapper para web e mobile |
| `@rapidrop/tokens` | Design tokens (Figma → Style Dictionary → CSS + NativeWind) |

## Documentação

A pasta `docs/` contém 14 documentos de especificação cobrindo:

- [Ideação e modelo de negócio](docs/ideacao-rapidrop.md)
- [Stack completa e decisões](docs/stack-completa.md)
- [Modelo de assinatura SaaS](docs/assinatura-saas.md)
- [Pagamento de entregadores](docs/pagamento-entregadores.md)
- [Experiência do cliente](docs/experiencia-cliente.md)
- [Fluxo financeiro](docs/fluxo-financeiro.md)
- [Multi-tenancy](docs/multi-tenancy.md)
- [Máquina de estados do pedido](docs/maquina-estados-pedido.md)
- [Observabilidade](docs/observabilidade.md)
- [Governança de dados](docs/analise-dados.md)
- [Mapas e roteirização](docs/mapas-roteirizacao.md)
- [WhatsApp integration](docs/integracao-whatsapp.md)
- [Onboarding do lojista](docs/onboarding-lojista.md)
- [Plano de implementação](docs/plano-implementacao.md)

## Licença

Proprietária — todos os direitos reservados.
