# Plano de Implementação — RapiDrop

> Documento mestre de execução. Consolida toda a especificação em tarefas
> granulares, organizadas por sprint, com dependências, responsáveis e
> critérios de aceitação.

---

## Visão Geral

### Metodologia

| Aspecto | Abordagem |
|---------|-----------|
| **Ciclo** | Sprints semanais (7 dias) |
| **Estimativa** | Dias-homem (DH). 1 DH = 1 pessoa trabalhando 1 dia inteiro no assunto |
| **Time** | 3 pessoas (backend + frontend + mobile/geral). @kira, @dani, @cruz |
| **Orçamento** | ~60 sprints = ~60 semanas = ~15 meses até versão completa |
| **MVP** | Sprint 1-12 (12 semanas) — Food segment, pedidos manuais + site, fatura mensal |

### Time e Responsabilidades

| Agente | Papel | Foco |
|--------|-------|------|
| @kira | Backend | FastAPI, PostgreSQL, integrações, máquina de estados |
| @dani | Frontend Web | Next.js, dashboard lojista, site white-label, admin |
| @cruz | Mobile | React Native/Expo (app entregador + app cliente), GPS |
| @theo | DevOps | Infraestrutura, CI/CD, deploy, Docker |
| @kira + @dani | Juntos | Modelagem de dados, API contracts, integração front/back |
| @maya | CTO | Arquitetura, revisão de PRs, decisões técnicas |

### Dependências Entre Epics

```
Sprint 1-2:         Sprint 3-4:         Sprint 5-6:         Sprint 7-9:
┌──────────┐       ┌──────────┐        ┌──────────┐        ┌──────────┐
│  Fundação│──────►│ Merchant │───────►│ Catálogo │───────►│ Pedidos  │
│  0.0-0.5 │       │ 1.0-1.4 │        │ 2.0-2.3 │        │ 3.0-3.5 │
└──────────┘       └──────────┘        └──────────┘        └────┬─────┘
                                                                  │
                     ┌────────────────────────────────────────────┘
                     ▼
            Sprint 10-12:        Sprint 13-14:        Sprint 15-16:
            ┌──────────┐        ┌──────────┐        ┌──────────┐
            │  Site    │───────►│ WhatsApp │───────►│  Admin   │
            │ Cliente  │        │ Outbound │        │  SaaS    │
            │ 4.0-4.4  │        │ 5.0-5.2  │        │ 8.0-8.3  │
            └──────────┘        └──────────┘        └──────────┘

Sprint 17-18:       Sprint 19-21:       Sprint 22-24:
┌──────────┐       ┌──────────┐        ┌──────────┐
│ Financeiro│──────►│ Entregador│──────►│ Farmácia │
│ 6.0-6.3  │       │ App + Mapas│       │ + Mercado│
└──────────┘       │ 7.0-7.4  │        │ 11.0-11.3│
                    └──────────┘        └──────────┘
```

---

## Sprint 0 — Fundação (Semana 1)

**Meta:** Ambiente de desenvolvimento pronto para começar a codar.

### 0.1 Monorepo + Docker Compose

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 0.1.1 | Inicializar monorepo com Turborepo + pnpm workspace | 0.5 | @cruz | — |
| 0.1.2 | Criar `docker-compose.yml` (PostgreSQL 16 + Redis 7 + RabbitMQ) | 1 | @theo | — |
| 0.1.3 | Criar `Dockerfile` para API (FastAPI) | 0.5 | @theo | 0.1.2 |
| 0.1.4 | Criar `Dockerfile` para Web (Next.js) | 0.5 | @theo | 0.1.2 |
| 0.1.5 | Configurar variáveis de ambiente (`.env.example`) | 0.5 | @theo | — |
| 0.1.6 | Script `make setup` que sobe tudo e roda migrations | 0.5 | @theo | 0.1.2-0.1.5 |

**Critério de aceitação:** `docker compose up` sobe API, Web, PostgreSQL, Redis, RabbitMQ. `make setup` cria banco e roda migrations.

### 0.2 Estrutura do Projeto

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 0.2.1 | Criar estrutura de pastas do backend (FastAPI modular) | 0.5 | @kira | 0.1.1 |
| 0.2.2 | Criar estrutura de pastas do frontend (Next.js App Router) | 0.5 | @dani | 0.1.1 |
| 0.2.3 | Configurar linters (Ruff para Python, ESLint para TS) | 0.5 | @kira/@dani | 0.2.1-0.2.2 |
| 0.2.4 | Configurar testes (pytest para backend, Vitest para frontend) | 0.5 | @kira/@dani | 0.2.1-0.2.2 |
| 0.2.5 | Configurar pacotes compartilhados (`packages/shared`) | 0.5 | @cruz | 0.1.1 |

**Critério de aceitação:** `pytest` roda e passa no backend. `pnpm test` roda e passa no frontend.

### 0.3 CI/CD + Deploy

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 0.3.1 | Configurar GitHub Actions: lint + test + build | 1 | @theo | 0.2.3-0.2.4 |
| 0.3.2 | Configurar Railway project (staging) | 0.5 | @theo | 0.1.2 |
| 0.3.3 | Configurar Sentry (backend + frontend) | 0.5 | @theo | 0.3.1 |
| 0.3.4 | Registrar domínio rapidrop.com.br + SSL | 0.5 | @theo | — |
| 0.3.5 | Deploy automático: push na main → deploy em staging | 0.5 | @theo | 0.3.1-0.3.2 |

**Critério de aceitação:** Push na `main` faz deploy automático em staging. Sentry captura erros.

### 0.4 Modelagem de Dados Inicial

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 0.4.1 | Criar modelos SQLAlchemy: `merchants`, `plans`, `plan_features` | 1 | @kira | 0.2.1 |
| 0.4.2 | Criar migrações Alembic iniciais | 0.5 | @kira | 0.4.1 |
| 0.4.3 | Criar modelos: `products`, `product_categories`, `product_variations` | 1 | @kira | 0.4.1 |
| 0.4.4 | Criar modelos: `riders`, `customers`, `customer_addresses` | 1 | @kira | 0.4.1 |
| 0.4.5 | Criar modelos: `orders`, `order_items`, `order_rider` | 1 | @kira | 0.4.1 |
| 0.4.6 | Criar modelos financeiros: `invoices`, `payment_transactions` | 1 | @kira | 0.4.1 |
| 0.4.7 | Criar modelos de onboarding: `merchant_onboarding`, `onboarding_event` | 0.5 | @kira | 0.4.1 |
| 0.4.8 | Aplicar `merchant_id` + índices em todas as tabelas de tenant | 1 | @kira | 0.4.2-0.4.7 |
| 0.4.9 | Criar modelos de auditoria: `audit_log` | 0.5 | @kira | 0.4.1 |

**Critério de aceitação:** `alembic upgrade head` cria todas as tabelas. Todos os modelos têm `merchant_id` e `created_at`.

### 0.5 Observabilidade Básica

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 0.5.1 | Configurar structlog (JSON logging) no FastAPI | 0.5 | @kira | 0.2.1 |
| 0.5.2 | Adicionar middleware de tracing (OpenTelemetry) | 0.5 | @kira | 0.2.1 |
| 0.5.3 | Exportar métricas Prometheus (`/metrics` endpoint) | 0.5 | @kira | 0.2.1 |
| 0.5.4 | Configurar Loki + Promtail no Docker Compose | 0.5 | @theo | 0.1.2 |
| 0.5.5 | Configurar Grafana com dashboards básicos | 0.5 | @theo | 0.5.4 |

**Critério de aceitação:** Logs aparecem no Loki. Métricas no Prometheus. Grafana acessível em `localhost:3000`.

---

## Epic 1 — Autenticação e Multi-tenancy (Sprint 1)

**Meta:** Sistema de login + isolamento entre lojistas funcionando.

### 1.0 Auth System

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 1.0.1 | Implementar registro de lojista (email + senha + segmento) | 1 | @kira | 0.4.1 |
| 1.0.2 | Implementar login (JWT + refresh token) | 1 | @kira | 1.0.1 |
| 1.0.3 | Implementar middleware de autenticação (FastAPI dependency) | 0.5 | @kira | 1.0.2 |
| 1.0.4 | Extrair `merchant_id` do JWT e injetar no request context | 0.5 | @kira | 1.0.3 |
| 1.0.5 | Página de login/cadastro no Next.js | 1 | @dani | 1.0.2 |
| 1.0.6 | Configurar refresh token automático no frontend | 1 | @dani | 1.0.5 |
| 1.0.7 | Testes de autenticação (registro, login, token expirado, refresh) | 1 | @kira | 1.0.1-1.0.3 |

**Critério de aceitação:** Usuário se cadastra, recebe JWT, faz login, token expira e renova automaticamente.

### 1.1 Multi-tenancy Layer

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 1.1.1 | Implementar `MerchantRepository` com filtro obrigatório de `merchant_id` | 1 | @kira | 0.4.8, 1.0.4 |
| 1.1.2 | Configurar RLS no PostgreSQL (policies por tabela) | 1 | @kira | 0.4.8 |
| 1.1.3 | Implementar `configure_rls_session()` no middleware | 0.5 | @kira | 1.1.2 |
| 1.1.4 | Implementar audit log de acesso admin a tenant | 0.5 | @kira | 0.4.9 |
| 1.1.5 | Testes de isolamento (tenant A não vê dados de B) | 1 | @kira | 1.1.1-1.1.3 |

**Critério de aceitação:** Lojista A faz query e só vê seus dados. Se tentar acessar dados de B via API, retorna 403 ou vazio. Admin consegue acessar tudo (com audit log).

---

## Epic 2 — Merchant Onboarding (Sprint 1-2)

**Meta:** Lojista completa cadastro e vê o dashboard.

### 2.0 Merchant Registration Flow

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 2.0.1 | API: criar merchant (dados da loja) | 0.5 | @kira | 0.4.1, 1.0.1 |
| 2.0.2 | API: escolher segmento (food/pharmacy/grocery) | 0.5 | @kira | 2.0.1 |
| 2.0.3 | Tela de cadastro (step 1: email + senha) | 0.5 | @dani | 1.0.5 |
| 2.0.4 | Tela de cadastro (step 2: dados da loja) | 1 | @dani | 2.0.3 |
| 2.0.5 | Tela de cadastro (step 3: segmento) | 0.5 | @dani | 2.0.4 |
| 2.0.6 | API: CEP → auto-complete endereço (ViaCEP) | 0.5 | @kira | 2.0.1 |
| 2.0.7 | Tela de boas-vindas + checklist de onboarding | 1 | @dani | 2.0.5 |
| 2.0.8 | Implementar máquina de estados do onboarding (back) | 1 | @kira | 0.4.7, 2.0.1 |

**Critério de aceitação:** Lojista completa cadastro em < 5 minutos. Vê dashboard com checklist de onboarding.

### 2.1 Store Configuration

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 2.1.1 | API: configurar horário de funcionamento | 0.5 | @kira | 2.0.1 |
| 2.1.2 | API: configurar área de entrega (raio km + bairros) | 1 | @kira | 2.0.1 |
| 2.1.3 | API: configurar taxa de entrega (fixa, por km, grátis acima de) | 0.5 | @kira | 2.1.2 |
| 2.1.4 | Tela de horário de funcionamento | 1 | @dani | 2.1.1 |
| 2.1.5 | Tela de área de entrega (MapLibre com raio visual) | 2 | @dani | 2.1.2 |
| 2.1.6 | Tela de taxa de entrega | 0.5 | @dani | 2.1.3 |
| 2.1.7 | Upload de logo + cor primária (white-label config) | 1 | @dani/@kira | 2.0.3 |

**Critério de aceitação:** Lojista configura horários, desenha área de entrega no mapa, define taxa. Configurações salvam e refletem no dashboard.

---

## Epic 3 — Catálogo de Produtos (Sprint 2-3)

**Meta:** Lojista gerencia produtos, categorias e variações.

### 3.0 Product Catalog

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 3.0.1 | API: CRUD de categorias | 1 | @kira | 0.4.3 |
| 3.0.2 | API: CRUD de produtos | 1.5 | @kira | 0.4.3 |
| 3.0.3 | API: CRUD de variações (tamanho, sabor, borda) | 1 | @kira | 3.0.2 |
| 3.0.4 | API: upload de foto do produto | 1 | @kira | 0.4.3 |
| 3.0.5 | API: toggle disponibilidade (ativar/desativar produto) | 0.5 | @kira | 3.0.2 |
| 3.0.6 | Tela de categorias (listar, criar, editar, reordenar) | 1.5 | @dani | 3.0.1 |
| 3.0.7 | Tela de produtos (listar, criar, editar, buscar) | 2 | @dani | 3.0.2 |
| 3.0.8 | Tela de variações (adicionar tamanhos/preços) | 1 | @dani | 3.0.3 |
| 3.0.9 | Componente de upload de foto com preview | 0.5 | @dani | 3.0.4 |
| 3.0.10 | Sugestão de categorias padrão por segmento | 1 | @kira | 3.0.1, 2.0.2 |

**Critério de aceitação:** Lojista adiciona 10 produtos em < 5 minutos. Vê fotos, preços, variações. Pode ativar/desativar.

### 3.1 Catalog Import (Pós-MVP)

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 3.1.1 | API: importar produtos via CSV | 1.5 | @kira | 3.0.2 |
| 3.1.2 | Tela de importação CSV com validação prévia | 1 | @dani | 3.1.1 |
| 3.1.3 | API: importar por código de barras (EAN) — farmácia | 1 | @kira | 3.0.2 |

**Critério de aceitação:** Upload de CSV cria produtos em lote. Erros de formatação são exibidos sem perder dados válidos.

---

## Epic 4 — Entregadores (Sprint 3-4)

**Meta:** Lojista cadastra entregadores + app do entregador básico.

### 4.0 Rider Management

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 4.0.1 | API: CRUD de entregadores | 1 | @kira | 0.4.4 |
| 4.0.2 | API: toggle online/offline do entregador | 0.5 | @kira | 4.0.1 |
| 4.0.3 | API: convite via WhatsApp (enviar link do app) | 0.5 | @kira | 4.0.1, 5.0.1 |
| 4.0.4 | API: listar entregadores com status online/offline | 0.5 | @kira | 4.0.1-4.0.2 |
| 4.0.5 | Tela de entregadores (listar, cadastrar, editar) | 1.5 | @dani | 4.0.1 |
| 4.0.6 | Tela de detalhe do entregador (histórico, status, extrato) | 1 | @dani | 4.0.4 |
| 4.0.7 | Testes de CRUD de entregadores | 0.5 | @kira | 4.0.1 |

**Critério de aceitação:** Lojista cadastra entregador. Entregador recebe convite. Status online/offline reflete no dashboard.

### 4.1 Rider App (Mobile) — MVP

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 4.1.1 | Setup do projeto React Native/Expo para entregador | 1 | @cruz | 0.1.1 |
| 4.1.2 | Tela de login com PIN/QR Code | 1 | @cruz | 4.1.1 |
| 4.1.3 | Tela principal: lista de entregas pendentes | 1.5 | @cruz | 4.1.2 |
| 4.1.4 | Tela de detalhe da entrega (endereço, itens, valor) | 1 | @cruz | 4.1.3 |
| 4.1.5 | Botões de status: "Sair para entrega" / "Entregue" | 1 | @cruz | 4.1.4 |
| 4.1.6 | API: atualizar status da entrega (picked_up, delivered) | 1 | @kira | 4.1.5 |
| 4.1.7 | Notificação push de novo pedido atribuído | 1 | @cruz | 4.1.2 |
| 4.1.8 | Toggle online/offline no app | 0.5 | @cruz | 4.1.2 |

**Critério de aceitação:** Entregador faz login, vê entregas pendentes, marca saída e entrega. Status atualiza no dashboard do lojista em tempo real.

### 4.2 Rider Payment Config

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 4.2.1 | API: configurar método de pagamento (diária/por entrega/híbrido) | 1 | @kira | 0.4.4 |
| 4.2.2 | API: configurar valores por método | 0.5 | @kira | 4.2.1 |
| 4.2.3 | API: gerar extrato do período | 1 | @kira | 4.2.1, 0.4.5 (orders) |
| 4.2.4 | Tela de configuração de pagamento de entregadores | 1 | @dani | 4.2.1-4.2.2 |
| 4.2.5 | Tela de extrato do entregador (para o lojista) | 1 | @dani | 4.2.3 |
| 4.2.6 | Tela de extrato do dia (para o entregador no app) | 1 | @cruz | 4.2.3 |

**Critério de aceitação:** Lojista configura pagamento. Extrato gerado automaticamente no fim do período.

---

## Epic 5 — Pedidos e Máquina de Estados (Sprint 4-6)

**Meta:** Pedidos funcionando com máquina de estados completa + dashboard em tempo real.

### 5.0 Order State Machine

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 5.0.1 | Implementar enum `OrderStatus` com todos os estados | 0.5 | @kira | 0.4.5 |
| 5.0.2 | Implementar `Transition` dataclass + tabela de transições | 1 | @kira | 5.0.1 |
| 5.0.3 | Implementar função `transition_order()` (único ponto de mudança) | 1.5 | @kira | 5.0.2 |
| 5.0.4 | Implementar guards: `can_confirm`, `can_cancel`, etc. | 1.5 | @kira | 5.0.3 |
| 5.0.5 | Implementar timestamps automáticos por transição | 0.5 | @kira | 5.0.3 |
| 5.0.6 | Implementar transições de farmácia (aguardando receita) | 1 | @kira | 5.0.3 |
| 5.0.7 | Implementar transições de mercado (aguardando substituição) | 1 | @kira | 5.0.3 |
| 5.0.8 | Implementar estados concorrentes de pagamento | 0.5 | @kira | 5.0.3 |
| 5.0.9 | Implementar estados concorrentes de entregador | 0.5 | @kira | 5.0.3 |
| 5.0.10 | Implementar transições proibidas com erro explícito | 1 | @kira | 5.0.3 |
| 5.0.11 | Testes de todas as transições (T1-T29) | 2 | @kira | 5.0.3-5.0.10 |

**Critério de aceitação:** Todas as 29 transições funcionam. Transições inválidas retornam erro. Testes passam.

### 5.1 Order Dashboard (Lojista)

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 5.1.1 | API: listar pedidos com filtros (status, data, canal) | 1 | @kira | 0.4.5 |
| 5.1.2 | API: criar pedido manual | 1 | @kira | 5.0.3 |
| 5.1.3 | API: detalhe do pedido (itens, cliente, entregador, timeline) | 0.5 | @kira | 5.1.1 |
| 5.1.4 | Tela de central de pedidos (kanban: novo → pendente → preparo → ...) | 3 | @dani | 5.1.1 |
| 5.1.5 | Tela de detalhe do pedido (itens, endereço, valor, status) | 2 | @dani | 5.1.3 |
| 5.1.6 | Botões de ação por status (confirmar, cancelar, iniciar preparo, etc.) | 1.5 | @dani | 5.0.3, 5.1.5 |
| 5.1.7 | Notificação sonora ao receber novo pedido | 0.5 | @dani | 5.1.4 |
| 5.1.8 | WebSocket: pedidos em tempo real (novo pedido aparece sem refresh) | 2 | @kira/@dani | 5.1.1 |
| 5.1.9 | Filtro por canal de origem (WhatsApp, site, manual) | 0.5 | @dani | 5.1.4 |

**Critério de aceitação:** Lojista vê pedidos em tempo real. Clica para confirmar, cancelar, mudar status. Tudo via WebSocket, sem refresh.

### 5.2 Order Timeouts & SLA

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 5.2.1 | Implementar timer de timeout por estado (pendente: 30min) | 1 | @kira | 5.0.3 |
| 5.2.2 | Implementar ação automática ao expirar timeout (cancelar, notificar) | 1 | @kira | 5.2.1 |
| 5.2.3 | Implementar alerta de atraso no preparo | 0.5 | @kira | 5.2.1 |
| 5.2.4 | Implementar cálculo de ETA (tempo_preparo + tempo_rota) | 1 | @kira | 5.0.3 |
| 5.2.5 | Celery Beat: worker de timeouts roda a cada minuto | 1 | @kira | 5.2.1 |

**Critério de aceitação:** Pedido sem confirmação em 30 min é cancelado automaticamente. Alerta de atraso dispara.

---

## Epic 6 — Site White-Label do Cliente (Sprint 6-8)

**Meta:** Cliente final acessa o site da loja, monta pedido e finaliza.

### 6.0 Storefront Page

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 6.0.1 | API: rota pública do catálogo (por slug da loja) | 1 | @kira | 3.0.2, 2.0.1 |
| 6.0.2 | API: buscar produtos com filtro por categoria | 0.5 | @kira | 6.0.1 |
| 6.0.3 | Página pública da loja (header com logo, nome, horário) | 1 | @dani | 6.0.1 |
| 6.0.4 | Grid de categorias + produtos com fotos e preços | 2 | @dani | 6.0.2 |
| 6.0.5 | Busca de produtos (por nome) | 1 | @dani | 6.0.4 |
| 6.0.6 | Layout responsivo (funciona no celular) | 1 | @dani | 6.0.3-6.0.5 |

**Critério de aceitação:** Cliente acessa `rapidrop.com.br/p/{slug}`, vê cardápio com fotos e preços, busca por nome.

### 6.1 Cart + Checkout

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 6.1.1 | API: adicionar item ao carrinho (session-based) | 1 | @kira | 6.0.1 |
| 6.1.2 | API: criar pedido a partir do carrinho | 1 | @kira | 6.1.1 |
| 6.1.3 | API: calcular taxa de entrega por CEP/distância | 1 | @kira | 2.1.3 |
| 6.1.4 | Componente de carrinho (itens, quantidades, total) | 1.5 | @dani | 6.1.1 |
| 6.1.5 | Tela de checkout (endereço, pagamento, confirmação) | 2 | @dani | 6.1.2 |
| 6.1.6 | Formulário de endereço com busca por CEP | 1 | @dani | 6.1.5 |
| 6.1.7 | Cálculo de taxa de entrega no frontend (via CEP) | 0.5 | @dani | 6.1.3 |
| 6.1.8 | Escolha de forma de pagamento (PIX, cartão, dinheiro) | 0.5 | @dani | 6.1.5 |

**Critério de aceitação:** Cliente adiciona itens ao carrinho, informa endereço, vê taxa de entrega, escolhe pagamento e finaliza pedido.

### 6.2 Order Tracking (Cliente)

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 6.2.1 | API: buscar status do pedido por ID público | 0.5 | @kira | 5.0.3 |
| 6.2.2 | Página pública de tracking (status, timeline, ETA) | 1 | @dani | 6.2.1 |
| 6.2.3 | Atualização automática via WebSocket | 1 | @kira/@dani | 6.2.2 |
| 6.2.4 | (Futuro) Mapa com posição do entregador | 1.5 | @cruz/@dani | 7.3.3 |

**Critério de aceitação:** Cliente acessa link de tracking, vê status em tempo real, timeline de eventos, ETA.

### 6.3 Customer Account (Simplificado)

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 6.3.1 | API: cliente se identifica por telefone (login via WhatsApp) | 1.5 | @kira | 0.4.4 |
| 6.3.2 | API: salvar endereços do cliente | 0.5 | @kira | 6.3.1 |
| 6.3.3 | API: histórico de pedidos do cliente | 0.5 | @kira | 6.3.1 |
| 6.3.4 | Tela de "meus pedidos" (histórico + status) | 1 | @dani | 6.3.3 |
| 6.3.5 | "Pedir novamente" com 1 clique | 1 | @dani/@kira | 6.3.4 |
| 6.3.6 | Login via WhatsApp (link mágico no zap) | 1 | @dani/@kira | 6.3.1 |

**Critério de aceitação:** Cliente informa telefone, recebe link no WhatsApp, acessa histórico, repete pedido em 1 clique.

---

## Epic 7 — WhatsApp Notifications (Sprint 7-8)

**Meta:** Cliente recebe notificações de status do pedido no WhatsApp.

### 7.0 WABA Setup + Outbound Engine

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 7.0.1 | Registrar WABA RapiDrop no Meta Business (admin) | 0.5 | @theo | — |
| 7.0.2 | Implementar webhook endpoint (`POST /api/v1/whatsapp/webhook`) | 1 | @kira | 0.2.1 |
| 7.0.3 | Implementar verificação de webhook (GET, hub.challenge) | 0.5 | @kira | 7.0.2 |
| 7.0.4 | Criar tabelas: `whatsapp_message_log`, `customer_consent` | 0.5 | @kira | 0.4.1 |
| 7.0.5 | Implementar worker Celery `send_whatsapp()` | 1 | @kira | 7.0.2 |
| 7.0.6 | Implementar verificação de consentimento antes do envio | 0.5 | @kira | 7.0.4 |
| 7.0.7 | Implementar opt-out (palavras PARE/SAIR) | 0.5 | @kira | 7.0.2 |

**Critério de aceitação:** Webhook configurado e respondendo. Worker envia mensagens. Consentimento é verificado.

### 7.1 Templates + Notificações

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 7.1.1 | Criar template `order_confirmed` e submeter ao Meta | 0.5 | @kira/@theo | 7.0.1 |
| 7.1.2 | Criar template `order_out_for_delivery` e submeter | 0.5 | @kira/@theo | 7.0.1 |
| 7.1.3 | Criar template `order_delivered` e submeter | 0.5 | @kira/@theo | 7.0.1 |
| 7.1.4 | Criar template `order_cancelled` e submeter | 0.5 | @kira/@theo | 7.0.1 |
| 7.1.5 | Criar template `payment_pix` e submeter | 0.5 | @kira/@theo | 7.0.1 |
| 7.1.6 | Integrar envio com a máquina de estados (T9, T10, T23, T25, T27) | 1 | @kira | 7.0.5, 5.0.3 |
| 7.1.7 | Sistema de fallback: SMS quando WhatsApp indisponível | 1 | @kira | 7.0.5 |
| 7.1.8 | Consentimento no checkout do site (opt-in checkbox) | 0.5 | @dani | 7.0.6 |

**Critério de aceitação:** Cliente recebe "Pedido confirmado 🤩" via WhatsApp. Se bloquear o número, fallback SMS.

---

## Epic 8 — Pagamentos (Sprint 8-10)

**Meta:** Cliente paga, lojista recebe, RapiDrop cobra a taxa.

### 8.0 Asaas Integration

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 8.0.1 | Criar cliente Asaas client wrapper (Python) | 1 | @kira | — |
| 8.0.2 | API: criar cobrança PIX (QR Code dinâmico) | 1.5 | @kira | 8.0.1 |
| 8.0.3 | API: criar cobrança cartão crédito (tokenizado) | 1.5 | @kira | 8.0.1 |
| 8.0.4 | Implementar webhook do Asaas (`POST /api/v1/asaas/webhook`) | 1 | @kira | 8.0.1 |
| 8.0.5 | Integrar PIX no checkout (mostrar QR Code + copia-cola) | 1.5 | @dani | 8.0.2 |
| 8.0.6 | Tokenização de cartão no frontend (campo seguro) | 1 | @dani | 8.0.3 |
| 8.0.7 | Testes: criação de cobrança, webhook, expiração PIX | 1 | @kira | 8.0.1-8.0.4 |

**Critério de aceitação:** Cliente paga com PIX → QR Code gerado → webhook confirma → pedido segue. Cartão é tokenizado e autorizado.

### 8.1 Invoice Generation (Fase 1 — Fatura Mensal)

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 8.1.1 | Implementar `calculate_monthly_invoice()` | 1 | @kira | 0.4.6, 5.0.3 |
| 8.1.2 | API: gerar fatura do mês | 0.5 | @kira | 8.1.1 |
| 8.1.3 | API: listar faturas do lojista | 0.5 | @kira | 8.1.2 |
| 8.1.4 | API: detalhe da fatura (breakdown por pedido) | 0.5 | @kira | 8.1.2 |
| 8.1.5 | Criar cobrança da fatura no Asaas (PIX/boleto) | 1 | @kira | 8.0.1, 8.1.2 |
| 8.1.6 | Tela de faturas (listar, pagar, histórico) | 1.5 | @dani | 8.1.3-8.1.4 |
| 8.1.7 | Agendar job mensal de geração de faturas (Celery Beat) | 0.5 | @kira | 8.1.1 |

**Critério de aceitação:** No dia 1 de cada mês, fatura é gerada automaticamente. Lojista vê breakdown por pedido e paga com PIX.

### 8.2 Dunning + Suspension

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 8.2.1 | Implementar `dunning_check()` (worker diário) | 1 | @kira | 8.1.5 |
| 8.2.2 | Implementar envio de lembretes automáticos (D+1, D+3, D+7) | 0.5 | @kira | 8.2.1 |
| 8.2.3 | Implementar suspensão automática (D+9 sem pagamento) | 1 | @kira | 8.2.1 |
| 8.2.4 | Implementar reativação automática ao pagar | 0.5 | @kira | 8.0.4, 8.2.3 |
| 8.2.5 | Tela de "fatura vencida" com alerta no dashboard | 0.5 | @dani | 8.2.1 |
| 8.2.6 | Testes de ciclo completo: fatura → lembrete → suspensão → pagamento → reativação | 1 | @kira | 8.2.1-8.2.4 |

**Critério de aceitação:** Fatura vencida D+9 → lojista é suspenso. Ao pagar → reativado automaticamente.

---

## Epic 9 — Maps + GPS Tracking (Sprint 11-13)

**Meta:** Entregador compartilha localização. Lojista vê no mapa.

### 9.0 MapLibre Infrastructure

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 9.0.1 | Configurar servidor OSRM (Docker + extract OSM Brasil) | 2 | @theo | — |
| 9.0.2 | Configurar Nominatim para geocoding reverso | 2 | @theo | — |
| 9.0.3 | Configurar tiles OpenFreeMap (ou auto-hospedar) | 0.5 | @theo | — |
| 9.0.4 | Integrar MapLibre GL JS no dashboard do lojista | 1 | @dani | 0.2.2 |
| 9.0.5 | Integrar MapLibre GL Native no app do entregador | 1 | @cruz | 4.1.1 |

**Critério de aceitação:** Mapa aparece no dashboard. OSRM calcula rotas. Geocoding funciona.

### 9.1 Rider GPS Tracking

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 9.1.1 | App: capturar localização em background (expo-location) | 1 | @cruz | 9.0.5 |
| 9.1.2 | App: enviar posição via WebSocket a cada 5s | 1 | @cruz/@kira | 9.1.1 |
| 9.1.3 | API: WebSocket endpoint para receber posições | 1 | @kira | 9.1.2 |
| 9.1.4 | API: broadcast de posição para o dashboard do lojista | 1 | @kira | 9.1.3 |
| 9.1.5 | Dashboard: marcador do entregador no mapa (atualizado em tempo real) | 1.5 | @dani | 9.0.4, 9.1.4 |
| 9.1.6 | App: sinalização de carga especial (refrigeração, frágil) | 0.5 | @cruz | 4.1.4 |
| 9.1.7 | Fallback: link de localização via WhatsApp se GPS falhar | 0.5 | @kira | 9.1.3 |

**Critério de aceitação:** Entregador liga app → posição aparece no mapa do lojista em tempo real. Se GPS falhar, link do WhatsApp.

### 9.2 Delivery Assignment

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 9.2.1 | Implementar atribuição manual (lojista escolhe entregador) | 0.5 | @kira | 4.0.2, 5.0.3 |
| 9.2.2 | Implementar atribuição automática (entregador mais próximo) | 1.5 | @kira | 9.1.4, 9.0.1 |
| 9.2.3 | Implementar notificação push ao entregador ao ser atribuído | 0.5 | @kira/@cruz | 9.2.1 |
| 9.2.4 | Implementar timeout de aceite (2 min) + reatribuição | 0.5 | @kira | 9.2.3 |
| 9.2.5 | Tela de atribuição no dashboard (arrastar pedido para entregador) | 1 | @dani | 9.2.1 |
| 9.2.6 | Testes de atribuição (manual, automática, reatribuição por timeout) | 1 | @kira | 9.2.1-9.2.4 |

**Critério de aceitação:** Pedido pronto → sistema encontra entregador mais próximo → notifica → entregador aceita → sai para entrega.

---

## Epic 10 — Admin SaaS (Sprint 14-15)

**Meta:** Dono do RapiDrop gerencia lojistas, planos e métricas.

### 10.0 Admin Dashboard

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 10.0.1 | API: dashboard metrics endpoint (MRR, churn, lojistas ativos) | 1.5 | @kira | 8.1.1, 0.4.1 |
| 10.0.2 | API: listar todos os lojistas (com filtros: status, segmento, plano) | 1 | @kira | 0.4.1 |
| 10.0.3 | API: detalhe do lojista (pedidos, faturamento, fatura) | 0.5 | @kira | 10.0.2 |
| 10.0.4 | Tela de login do admin (separado do login do lojista) | 0.5 | @dani | 1.0.2 |
| 10.0.5 | Dashboard do admin (cards: MRR, lojistas, pedidos, crescimento) | 2 | @dani | 10.0.1 |
| 10.0.6 | Tela de listagem de lojistas (tabela + busca + filtros) | 1.5 | @dani | 10.0.2 |
| 10.0.7 | Tela de detalhe do lojista (pedidos, fatura, config, ações) | 1 | @dani | 10.0.3 |
| 10.0.8 | Audit log de acesso admin a dados de lojistas | 0.5 | @kira | 1.1.4 |

**Critério de aceitação:** Admin faz login, vê métricas do SaaS, busca lojistas, vê detalhes. Cada acesso é registrado.

### 10.1 Plan Management

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 10.1.1 | API: CRUD de planos | 0.5 | @kira | 0.4.1 |
| 10.1.2 | API: associar plano ao lojista | 0.5 | @kira | 10.1.1 |
| 10.1.3 | Tela de gerenciamento de planos (admin) | 1 | @dani | 10.1.1 |
| 10.1.4 | Aplicar restrições por plano (max entregadores, max pedidos) | 1 | @kira | 10.1.2 |

**Critério de aceitação:** Admin cria plano (ex: "Básico: 2%, 1 entregador"). Lojista associado ao plano tem restrições aplicadas.

---

## Epic 11 — Analytics e Data Quality (Sprint 15-17)

**Meta:** Dados confiáveis com testes automatizados + dashboards de BI.

### 11.0 dbt + Data Models

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 11.0.1 | Configurar dbt no projeto | 0.5 | @kira | — |
| 11.0.2 | Criar staging models (RAW → DOMAIN) | 1 | @kira | 11.0.1 |
| 11.0.3 | Criar marts (DOMAIN → ANALYTIC): orders, revenue, churn | 1.5 | @kira | 11.0.2 |
| 11.0.4 | Criar dashboard de BI no Grafana (pedidos, faturamento, cancelamentos) | 1.5 | @kira/@theo | 11.0.3 |

**Critério de aceitação:** `dbt run` transforma dados. Grafana mostra gráficos de pedidos/dia, faturamento, churn.

### 11.1 Data Quality Tests

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 11.1.1 | Configurar Great Expectations no CI | 0.5 | @kira | 0.3.1 |
| 11.1.2 | Criar expectations: `merchant_id NOT NULL`, chaves estrangeiras, valores | 2 | @kira | 11.1.1 |
| 11.1.3 | Criar teste de conciliação diária (orders × payment_transactions) | 1 | @kira | 5.0.3, 8.0.1 |

**Critério de aceitação:** CI bloqueia deploy se `merchant_id` estiver NULL em tabela de tenant.

---

## Epic 12 — Customer App (Mobile) (Sprint 18-20)

**Meta:** Cliente final pode pedir pelo app RapiDrop.

### 12.0 Customer App Setup

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 12.0.1 | Setup do React Native/Expo para app do cliente | 1 | @cruz | 0.1.1 |
| 12.0.2 | Tela de login com WhatsApp (OTP) | 1.5 | @cruz | 12.0.1 |
| 12.0.3 | Feed de lojas próximas (lista + busca) | 2 | @cruz | 12.0.2 |

**Critério de aceitação:** Cliente abre app, faz login com WhatsApp, vê lojas próximas.

### 12.1 Ordering Flow (App)

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 12.1.1 | Tela de catálogo da loja (no app) | 1.5 | @cruz | 6.0.1, 12.0.3 |
| 12.1.2 | Carrinho + checkout no app | 2 | @cruz | 12.1.1 |
| 12.1.3 | Histórico de pedidos + favoritos (lojas e pratos) | 1 | @cruz | 12.0.2 |

**Critério de aceitação:** Cliente navega, adiciona itens, finaliza pedido, paga. Tudo no app.

---

## Epic 13 — Multi-Segmento (Sprint 21-24)

**Meta:** Farmácia e mercado funcionando com suas particularidades.

### 13.0 Pharmacy Extensions

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 13.0.1 | Adicionar campos de farmácia no produto (princípio ativo, tarja, ANVISA) | 1 | @kira | 3.0.2 |
| 13.0.2 | Implementar `aguardando_receita` → `receita_validada` → `receita_rejeitada` | 1.5 | @kira | 5.0.6 |
| 13.0.3 | API: upload de receita (imagem criptografada) | 1 | @kira | 13.0.2 |
| 13.0.4 | API: validação de receita pelo farmacêutico | 1 | @kira | 13.0.3 |
| 13.0.5 | Schema separado para dados de farmácia (`tenant_{id}`) | 1 | @kira | 1.1.2 |
| 13.0.6 | Tela de validação de receita no dashboard | 1 | @dani | 13.0.4 |
| 13.0.7 | Checkout: upload de receita + aviso de tarja | 1 | @dani | 13.0.3 |
| 13.0.8 | Aviso de refrigeração no app do entregador | 0.5 | @cruz | 13.0.1 |

**Critério de aceitação:** Cliente compra remédio de tarja → faz upload da receita → farmacêutico valida → pedido segue.

### 13.1 Grocery Extensions

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 13.1.1 | Adicionar campos de mercado (departamento, EAN, peso fracionado) | 1 | @kira | 3.0.2 |
| 13.1.2 | Implementar `aguardando_substituicao` + `cancelado_parcial` | 1.5 | @kira | 5.0.7 |
| 13.1.3 | API: sugerir substituto (product.substitute_product_id) | 1 | @kira | 13.1.2 |
| 13.1.4 | API: cliente aprova/rejeita substituto | 0.5 | @kira | 13.1.3 |
| 13.1.5 | Checkout: seleção de janela de entrega | 1 | @dani | 13.1.2 |
| 13.1.6 | Fluxo de substituição via WhatsApp | 1 | @kira | 13.1.4, 7.0.5 |
| 13.1.7 | Tela de "item em falta → sugerir substituto" no dashboard | 1 | @dani | 13.1.3 |

**Critério de aceitação:** Mercado separa pedido → item em falta → cliente recebe WhatsApp com substituto → aprova → segue.

---

## Epic 14 — Refinamentos e Escala (Sprint 25+)

**Meta:** Performance, testes, documentação, polishing.

### 14.0 Performance

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 14.0.1 | Cache de catálogo no Redis (evitar DB a cada visita) | 1 | @kira | 3.0.2 |
| 14.0.2 | Paginação com cursor em listas de pedidos | 0.5 | @kira | 5.1.1 |
| 14.0.3 | Compressão de imagens (WebP automático) | 0.5 | @kira | 3.0.4 |
| 14.0.4 | Configurar CDN para assets estáticos | 0.5 | @theo | — |
| 14.0.5 | Teste de carga com k6 (100 usuários concorrentes) | 1 | @kira/@theo | 5.0.3, 3.0.2 |

**Critério de aceitação:** Página do catálogo carrega em < 1s. Pedido é criado em < 500ms.

### 14.1 Testes Gerais

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 14.1.1 | Cobertura de testes do backend > 80% | 3 | @kira | Todas as APIs |
| 14.1.2 | Testes E2E com Playwright (fluxo completo: cadastro → pedido → entrega) | 3 | @dani | 6.1.2, 5.1.4 |
| 14.1.3 | Testes de segurança (OWASP top 10 básico) | 1 | @kira | 1.0.3 |

**Critério de aceitação:** `pytest --cov > 80%`. Playwright cobre fluxo completo.

### 14.2 Documentação

| # | Tarefa | DH | Responsável | Depende |
|---|--------|:--:|:-----------:|:-------:|
| 14.2.1 | Swagger/OpenAPI automático (FastAPI já gera) | 0 | @kira | — |
| 14.2.2 | README do projeto com instruções de setup | 0.5 | @cruz | 0.1.6 |
| 14.2.3 | Documentação de deploy (para @theo) | 0.5 | @theo | 0.3.5 |

**Critério de aceitação:** `localhost:8000/docs` funciona. README cobre setup.

---

## Resumo de Esforço

### Por Epic

| Epic | DH Total | Sprints | MVP? |
|------|:--------:|:-------:|:----:|
| 0 — Fundação | 16 | 1 | ✅ |
| 1 — Auth + Multi-tenancy | 11 | 1 | ✅ |
| 2 — Merchant Onboarding | 14 | 1-2 | ✅ |
| 3 — Catálogo | 16 | 2-3 | ✅ |
| 4 — Entregadores | 17 | 3-4 | ✅ |
| 5 — Pedidos | 24 | 4-6 | ✅ |
| 6 — Site Cliente | 27 | 6-8 | ✅ |
| 7 — WhatsApp | 11 | 7-8 | ✅ |
| 8 — Pagamentos | 20 | 8-10 | ✅ |
| 9 — Maps + GPS | 19 | 11-13 | ❌ (Fase 2) |
| 10 — Admin SaaS | 12 | 14-15 | ❌ (Fase 2) |
| 11 — Analytics | 8 | 15-17 | ❌ (Fase 2) |
| 12 — App Cliente | 10 | 18-20 | ❌ (Fase 3) |
| 13 — Multi-segmento | 16 | 21-24 | ❌ (Fase 3) |
| 14 — Refinamentos | 13 | 25+ | ❌ (Contínuo) |
| **Total** | **~234 DH** | **~60 sprints** | |

### MVP (Sprints 1-12) — 12 Semanas

| Sprint | DH | Entrega Principal |
|:------:|:--:|-------------------|
| 0 | 16 | Fundação: Docker, CI/CD, banco, estrutura |
| 1 | 12 | Auth + Cadastro do lojista + Multi-tenancy |
| 2 | 9 | Configuração da loja + Início catálogo |
| 3 | 10 | Catálogo completo + Início entregadores |
| 4 | 10 | Entregadores + App entregador básico |
| 5 | 10 | Máquina de estados do pedido (core) |
| 6 | 7 | Dashboard de pedidos + WebSocket + Timeouts |
| 7 | 12 | Site white-label: catálogo + carrinho |
| 8 | 10 | Checkout + Pagamento PIX + Tracking |
| 9 | 8 | Conta do cliente + "Pedir de novo" |
| 10 | 8 | WhatsApp: WABA + outbound + 4 templates |
| 11 | 9 | Pagamento: fatura mensal + Asaas |
| 12 | 8 | Dunning + suspensão + testes finais |

**Total MVP:** ~129 DH = ~13 semanas com time de 3 pessoas.

---

## Dicionário de Siglas

| Sigla | Significado |
|-------|-------------|
| DH | Dias-Homem (1 pessoa trabalhando 1 dia) |
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| RLS | Row-Level Security (PostgreSQL) |
| WABA | WhatsApp Business Account |
| OSRM | Open Source Routing Machine |
| ETA | Estimated Time of Arrival |
| MRR | Monthly Recurring Revenue |
| dbt | Data Build Tool |
| EAN | European Article Number (código de barras) |

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Baseado em todos os documentos em `docs/`:**
> `ideacao-rapidrop.md`, `stack-completa.md`, `maquina-estados-pedido.md`,
> `integracao-whatsapp.md`, `fluxo-financeiro.md`, `onboarding-lojista.md`,
> `multi-tenancy.md`, `observabilidade.md`, `analise-dados.md`,
> `mapas-roteirizacao.md`, `pagamento-entregadores.md`, `assinatura-saas.md`,
> `experiencia-cliente.md`
