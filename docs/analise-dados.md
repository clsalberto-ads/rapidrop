# RapiDrop — Análise de Dados e Governança

> Como tratamos dados com qualidade, rastreabilidade e confiabilidade.
> Um diferencial estratégico para o SaaS e para os lojistas.

---

## Índice

1. [Filosofia de Dados](#1-filosofia-de-dados)
2. [Camadas de Dados](#2-camadas-de-dados)
3. [Data Quality Framework](#3-data-quality-framework)
4. [Data Lineage e Rastreabilidade](#4-data-lineage-e-rastreabilidade)
5. [Governança de Dados](#5-governança-de-dados)
6. [Audit Trail](#6-audit-trail)
7. [Testes de Dados](#7-testes-de-dados)
8. [Análise e BI](#8-análise-e-bi)
9. [Eventos de Negócio](#9-eventos-de-negócio)
10. [Diferenciais Estratégicos](#10-diferenciais-estratégicos)

---

## 1. Filosofia de Dados

### 1.1 Nossos Princípios

```
┌─────────────────────────────────────────────────────────────┐
│                   FILOSOFIA DE DADOS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📐  PRECISÃO                                               │
│       "Dado errado é pior que dado nenhum."                │
│       Toda informação armazenada passa por validação        │
│       na entrada. Nunca confiamos no usuário cegamente.    │
│                                                             │
│  🔗  RASTREABILIDADE                                        │
│       "Todo dado tem uma origem conhecida."                │
│       Sabemos quem criou, quando, por quê e como            │
│       cada registro foi parar no banco.                     │
│                                                             │
│  🧪  TESTABILIDADE                                           │
│       "Se não pode testar, não pode confiar."              │
│       Dados têm testes automatizados como código tem.       │
│                                                             │
│  📊  ANALYTICS-READY                                         │
│       "Dado de produção é dado de análise."                │
│       Não transformamos dados para relatórios —             │
│       eles já nascem prontos para serem analisados.        │
│                                                             │
│  🔒  PRIVACIDADE                                             │
│       "Confiança não se deleta."                            │
│       LGPD não é checklist, é arquitetura.                  │
│       Dados sensíveis são protegidos por padrão.            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 O Diferencial Estratégico

```
Para o LOJISTA:                                                   
  ┌─ Dados confiáveis sobre seus pedidos, clientes e financeiro  
  ├─ Relatórios que refletem a realidade, não aproximações       
  └─ Auditoria completa: sabe exatamente o que aconteceu         

Para o SAAS:                                                      
  ┌─ Decisões baseadas em dados consistentes (MRR, churn, CAC)   
  ├─ Confiança do investidor: números auditáveis                 
  └─ Vantagem competitiva: dados de qualidade = produto superior 

Para o CLIENTE:                                                   
  ┌─ Histórico de pedidos preciso                                
  ├─ Fidelidade que realmente funciona (selos contados certos)   
  └─ Privacidade respeitada (LGPD nativa)                        
```

---

## 2. Camadas de Dados

### 2.1 Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADAS DE DADOS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  🎯  CAMADA DE APRESENTAÇÃO                              │   │
│  │  Grafana, Relatórios CSV, API de exports, Webhooks       │   │
│  │  Dados agregados, prontos para consumo                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ▲                                        │
│                          │ consultas                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  📊  CAMADA ANALÍTICA (DATA MART)                        │   │
│  │  Materialized views, tabelas de agregação, métricas      │   │
│  │  Próprias para BI sem precisar de JOINs complexos        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ▲                                        │
│                          │ ETL / transformação                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  📦  CAMADA DE NEGÓCIO (DOMAIN)                          │   │
│  │  Tabelas normalizadas do domínio: orders, products,      │   │
│  │  customers, riders, invoices, subscriptions              │   │
│  │  Dados consistentes, integridade referencial             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ▲                                        │
│                          │ ingestão                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  📥  CAMADA BRUTA (RAW)                                  │   │
│  │  Eventos, webhooks, logs de integração, importações      │   │
│  │  Dados como chegaram — sem transformação                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 O que Cada Camada Armazena

| Camada | Tabelas/Exemplos | Quem usa |
|--------|-----------------|----------|
| **RAW** | `webhook_logs`, `import_errors`, `event_stream` | Backend, Debug |
| **DOMAIN** | `order`, `product`, `customer`, `rider`, `invoice` | API, Lojista |
| **ANALYTIC** | `mv_daily_orders`, `mv_merchant_monthly`, `mv_rider_performance` | Dashboards, Relatórios |
| **PRESENTATION** | CSVs exportados, Webhooks, APIs públicas | Lojista, Cliente, Parceiros |

### 2.3 Materialized Views (Camada Analítica)

```sql
-- Exemplo: Vendas diárias por lojista
CREATE MATERIALIZED VIEW mv_daily_orders AS
SELECT
    o.merchant_id,
    DATE(o.created_at) AS date,
    COUNT(*) AS total_orders,
    SUM(o.total_cents) / 100.0 AS revenue_brl,
    AVG(o.total_cents) / 100.0 AS avg_ticket_brl,
    COUNT(*) FILTER (WHERE o.status = 'cancelled') AS cancelled_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    o.channel
FROM order o
GROUP BY o.merchant_id, DATE(o.created_at), o.channel;

-- Refresh programado (via Celery, a cada 1h)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_orders;
```

```sql
-- Exemplo: Performance mensal do entregador
CREATE MATERIALIZED VIEW mv_rider_monthly AS
SELECT
    r.merchant_id,
    r.id AS rider_id,
    r.name AS rider_name,
    DATE_TRUNC('month', or2.delivered_at) AS month,
    COUNT(*) AS total_deliveries,
    AVG(or2.delivered_at - or2.assigned_at) AS avg_delivery_time,
    SUM(COALESCE(rpp.total_cents, 0)) / 100.0 AS total_earnings_brl,
    AVG(COALESCE(rpp.ranking_position, 0)) AS avg_ranking_position
FROM rider r
JOIN order_rider or2 ON r.id = or2.rider_id
LEFT JOIN rider_payment_period rpp ON r.id = rpp.rider_id
WHERE or2.delivered_at IS NOT NULL
GROUP BY r.merchant_id, r.id, r.name, DATE_TRUNC('month', or2.delivered_at);
```

### 2.4 Por Que Isso É Diferencial

| Sem camadas | Com camadas |
|-------------|-------------|
| Relatório demora porque faz JOIN em milhões de pedidos | Relatório consulta materialized view — instantâneo |
| Dado bruto exposto para usuário final | Dado tratado, agregado, consistente |
| Cada relatório reinventa a lógica | Lógica centralizada na MV |
| Cascata de queries lentas no horário comercial | Refresh programado em horário de baixa |

---

## 3. Data Quality Framework

### 3.1 Validation na Entrada (Backend)

Todo dado que entra no sistema passa por **validação em 3 níveis**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDAÇÃO DE DADOS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SCHEMA VALIDATION (Pydantic / Zod)                          │
│     ├─ Tipos corretos? (int, string, enum, uuid)                │
│     ├─ Campos obrigatórios presentes?                           │
│     ├─ Tamanhos respeitados? (string max_length, array max_items)│
│     └─ Formato válido? (email, phone, CEP, CPF, CNPJ)           │
│                                                                  │
│  2. BUSINESS VALIDATION (Regras de negócio)                     │
│     ├─ Pedido mínimo?                                           │
│     ├─ Produto disponível?                                      │
│     ├─ CEP dentro do raio de entrega?                           │
│     ├─ Horário de funcionamento?                                │
│     └─ Cupom válido? (não expirou, não excedeu limite)          │
│                                                                  │
│  3. CONSISTENCY VALIDATION (Integridade)                        │
│     ├─ FK existe? (loja existe, cliente existe)                 │
│     ├─ Valores consistentes? (total = subtotal + frete - desc)  │
│     └─ Estado válido? (transição de status permitida)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Exemplo: Validação de Pedido no Código

```python
# src/modules/orders/schemas.py

from pydantic import BaseModel, Field, model_validator
from decimal import Decimal
from typing import List, Optional
from enum import Enum

class OrderItem(BaseModel):
    product_id: str = Field(..., description="UUID do produto")
    quantity: int = Field(..., ge=1, le=100, description="Quantidade (1-100)")
    variation_id: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class OrderCreate(BaseModel):
    """Schema de criação de pedido com validação em 3 níveis."""
    merchant_id: str = Field(..., description="UUID do lojista")
    customer_id: str = Field(..., description="UUID do cliente")
    items: List[OrderItem] = Field(..., min_length=1, max_length=50)
    delivery_address_id: str = Field(...)
    payment_method: str = Field(..., pattern="^(credit_card|pix|cash|card_on_delivery)$")
    coupon_code: Optional[str] = Field(None, max_length=20)
    customer_notes: Optional[str] = Field(None, max_length=1000)

    # Nível 2: Business validation
    @model_validator(mode="after")
    def validate_business_rules(self) -> "OrderCreate":
        if len(self.items) > 50:
            raise ValueError("Pedido excede limite de 50 itens")
        return self

    # Nível 3: Consistency validation (executado no service)
    # Ex: verificar se merchant existe, se produtos existem, se estoque OK
```

### 3.3 Validação de Dados no Banco (Constraints)

```sql
-- Constraints que garantem qualidade dos dados no banco

-- 1. CHECK constraints (valores dentro do esperado)
ALTER TABLE "order"
    ADD CONSTRAINT chk_order_positive_values
    CHECK (subtotal_cents >= 0 AND total_cents >= 0 AND delivery_fee_cents >= 0);

ALTER TABLE "order"
    ADD CONSTRAINT chk_order_total_matches
    CHECK (total_cents = subtotal_cents + delivery_fee_cents - COALESCE(discount_cents, 0));

-- 2. ENUMs (valores controlados, sem string solta)
CREATE TYPE order_status AS ENUM (
    'pending', 'confirmed', 'preparing',
    'out_for_delivery', 'delivered', 'cancelled'
);

ALTER TABLE "order"
    ALTER COLUMN status TYPE order_status USING status::order_status;

-- 3. UNIQUE constraints (sem duplicatas)
ALTER TABLE merchant
    ADD CONSTRAINT uq_merchant_document UNIQUE (document);

ALTER TABLE customer
    ADD CONSTRAINT uq_customer_phone UNIQUE (phone);

-- 4. NOT NULL (campos obrigatórios)
ALTER TABLE "order"
    ALTER COLUMN merchant_id SET NOT NULL,
    ALTER COLUMN customer_id SET NOT NULL,
    ALTER COLUMN total_cents SET NOT NULL;

-- 5. Timestamps automáticos (nunca confie no app para isso)
ALTER TABLE "order"
    ALTER COLUMN created_at SET DEFAULT NOW(),
    ALTER COLUMN updated_at SET DEFAULT NOW();
```

### 3.4 Data Quality Checks Automatizados (Great Expectations)

```python
# tests/data_quality/test_orders_quality.py

"""
Testes de qualidade que rodam no CI e em produção (agendado).
Usa a biblioteca Great Expectations para validação declarativa.
"""

# Expectativa 1: Nenhum pedido com valor negativo
expect_column_values_to_be_between(
    column="total_cents",
    min_value=0,
    max_value=10000000,  # R$ 100.000,00 — teto seguro
)

# Expectativa 2: Todo pedido tem um lojista válido
expect_column_values_to_not_be_null("merchant_id")

# Expectativa 3: Status sempre pertence ao enum
expect_column_values_to_be_in_set(
    column="status",
    value_set=["pending", "confirmed", "preparing",
               "out_for_delivery", "delivered", "cancelled"],
)

# Expectativa 4: Pedidos entregues têm data de entrega
expect_compound_columns_to_be_unique(
    column_list=["merchant_id", "sequential_id"],
)

# Expectativa 5: Ticket médio dentro do esperado
expect_column_mean_to_be_between(
    column="total_cents",
    min_value=500,    # R$ 5,00
    max_value=50000,  # R$ 500,00
)
```

### 3.5 Detecção de Anomalias em Tempo Real

```python
# src/shared/data_quality/monitor.py

"""
Monitor que detecta anomalias nos dados em tempo real
e alerta se algo foge do padrão esperado.
"""

from prometheus_client import Counter, Gauge
import structlog

logger = structlog.get_logger()

# Métricas de qualidade
data_quality_errors = Counter(
    "data_quality_errors_total",
    "Erros de qualidade de dados",
    ["table", "check_type"],
)

data_quality_score = Gauge(
    "data_quality_score",
    "Pontuação de qualidade dos dados (0-100%)",
    ["table"],
)

class DataQualityMonitor:
    """Monitora a qualidade dos dados e alerta em caso de anomalia."""

    ANOMALY_RULES = {
        "order": {
            "max_cancellation_rate": 0.15,     # Máx 15% de cancelamento
            "max_empty_fields_pct": 0.01,      # Máx 1% de campos nulos
            "min_orders_per_hour": 1,          # Mín 1 pedido/hora (loja ativa)
        },
        "product": {
            "max_zero_price_pct": 0.02,        # Máx 2% de produtos com preço zero
            "max_without_category_pct": 0.01,  # Máx 1% sem categoria
        },
        "customer": {
            "max_without_address_pct": 0.05,   # Máx 5% sem endereço
            "max_invalid_phone_pct": 0.02,     # Máx 2% com telefone inválido
        },
    }

    async def check_table_quality(self, table: str):
        """
        Executa checagens de qualidade em uma tabela.
        Chamado por um scheduler Celery a cada hora.
        """
        rules = self.ANOMALY_RULES.get(table, {})

        for check_name, threshold in rules.items():
            result = await self._run_check(table, check_name)

            if result["value"] > threshold:
                data_quality_errors.labels(
                    table=table, check_type=check_name
                ).inc()

                logger.warning(
                    "data_quality.anomaly_detected",
                    table=table,
                    check=check_name,
                    value=result["value"],
                    threshold=threshold,
                )

                # Se for crítico, notificar no Slack
                if result["severity"] == "critical":
                    await self._notify_slack(table, check_name, result)

        # Atualiza score geral
        score = await self._calculate_score(table, rules, threshold)
        data_quality_score.labels(table=table).set(score)
```

---

## 4. Data Lineage e Rastreabilidade

### 4.1 O Que é Lineage e Por Que Precisamos

**Data Lineage** é saber de onde cada dado veio, por quem foi criado, e por quais transformações passou.

```
SEM LINEAGE:                           COM LINEAGE:
"Essa métrica de MRR           "O MRR de R$ 47.320 veio de:
 está diferente, por quê?"        → Tabela invoice
                                  → Filtro: payment_status = 'paid'
                                  → Filtro: MONTH(created_at) = '2026-06'
                                  → Agregação: SUM(amount_cents)
                                  → Última atualização: 10/06 14:30"
```

### 4.2 Campos de Rastreabilidade (Toda Tabela)

Toda tabela no RapiDrop tem **campos obrigatórios de rastreabilidade**:

```sql
-- Toda tabela DEVE ter:
created_at      timestamptz NOT NULL DEFAULT NOW()
updated_at      timestamptz NOT NULL DEFAULT NOW()
created_by      uuid          -- quem criou (FK para user, customer ou system)
updated_by      uuid          -- quem atualizou

-- Tabelas financeiras e sensíveis TAMBÉM devem ter:
source          varchar(50)   -- de onde veio: 'api', 'webhook', 'import', 'migration'
source_id       varchar(200)  -- ID original na origem
version         int DEFAULT 1 -- versão do registro (para reconciliar)
```

### 4.3 Exemplo Prático

```sql
-- Ordem com lineage completa
SELECT
    o.id,
    o.total_cents,
    o.status,
    o.created_at,
    o.created_by,      -- UUID do cliente que fez o pedido
    o.source,          -- 'api'
    o.source_id,       -- ID original no sistema de origem
    o.version,         -- 1 (primeira versão)
    o.updated_at,
    o.updated_by       -- UUID de quem atualizou (ou sistema)
FROM "order" o
WHERE o.id = 'abc-123';
```

### 4.4 dbt — Transformações com Rastreabilidade

Para transformações analíticas, usamos **dbt (data build tool)**:

```yaml
# dbt_project.yml

name: 'rapidrop'
version: '1.0'
profile: 'rapidrop'

models:
  +materialized: table
  +tags: ['rapidrop']
  +docs:
    node_color: '#4A90D9'

  staging:       # Cópia fiel da produção
    +materialized: view
    +schema: stg

  intermediate:  # Limpeza e tipagem
    +materialized: ephemeral

  marts:         # Agregações de negócio
    +schema: analytics
    +tags: ['business']
```

```sql
-- models/marts/merchant_monthly.sql

/*
  Modelo: merchant_monthly
  Descrição: Métricas mensais consolidadas por lojista
  Fonte: staging.stg_orders, staging.stg_merchants
  Mantenedor: @leo
*/

WITH orders_aggregated AS (
    SELECT
        merchant_id,
        DATE_TRUNC('month', created_at) AS month,
        COUNT(*) AS total_orders,
        SUM(total_cents) AS revenue_cents,
        COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_orders,
        COUNT(DISTINCT customer_id) AS unique_customers
    FROM {{ ref('stg_orders') }}
    WHERE created_at >= '2025-01-01'
    GROUP BY 1, 2
)

SELECT
    o.merchant_id,
    m.name AS merchant_name,
    m.segment,
    o.month,
    o.total_orders,
    o.revenue_cents / 100.0 AS revenue_brl,
    o.cancelled_orders,
    ROUND(o.cancelled_orders * 100.0 / NULLIF(o.total_orders, 0), 2) AS cancellation_pct,
    o.unique_customers,
    CURRENT_TIMESTAMP AS _loaded_at
FROM orders_aggregated o
JOIN {{ ref('stg_merchants') }} m ON o.merchant_id = m.id
```

### 4.5 Rastreabilidade com dbt

```bash
# dbt fornece automaticamente:
#   - Lineage graph (quem depende de quem)
#   - Documentação das colunas
#   - Testes de qualidade
#   - Histórico de execução

dbt docs generate  →  Gera site com lineage completo
dbt test           →  Roda testes de qualidade
dbt run            →  Executa transformações na ordem certa
```

---

## 5. Governança de Dados

### 5.1 Matriz de Acesso

| Dado | Lojista vê | Cliente vê | Admin vê | Entregador vê |
|------|:----------:|:----------:|:--------:|:-------------:|
| Pedidos da própria loja | ✅ | ❌ | ✅ | ✅ (só os seus) |
| Clientes da própria loja | ✅ | ❌ | ❌ | ❌ |
| Nome do cliente | ✅ | ✅ (só o seu) | ❌ | ✅ (para entrega) |
| Endereço do cliente | ✅ | ✅ | ❌ | ✅ (para entrega) |
| Telefone do cliente | ✅ | ✅ | ❌ | ✅ (para entrega) |
| Financeiro da loja | ✅ | ❌ | ✅ | ✅ (só seus ganhos) |
| Dados de outras lojas | ❌ | ❌ | ❌ | ❌ |
| Cartão de crédito | ❌ (token) | ✅ | ❌ | ❌ |

### 5.2 Política de Retenção

| Dado | Retenção | Exclusão |
|------|----------|----------|
| Pedidos finalizados | 5 anos | Após 5 anos, anonimizados |
| Clientes inativos | 24 meses sem pedido | Anonimizado (mantém apenas CEP para métrica) |
| Logs de evento | 12 meses | Excluído |
| Dados de pagamento | 5 anos (fiscal) | Conforme LGPD |
| Receitas médicas | 2 anos após validade | Criptografia removida |
| Sessões de login | 7 dias após expirar | Excluído |

### 5.3 Responsabilidades

```
Dono dos Dados (Data Owner):
  └─ Quem? O Lojista (para dados da loja)
  └─ Decide: o que coletar, por quanto tempo reter

Curador dos Dados (Data Steward):
  └─ Quem? @leo (Data Engineer)
  └─ Garante: qualidade, definições, consistência

Guardião dos Dados (Data Custodian):
  └─ Quem? @theo (DevOps)
  └─ Garante: backup, criptografia, acesso físico

Usuário dos Dados:
  └─ Quem? Time RapiDrop, Lojistas
  └─ Usa: conforme política de acesso
```

### 5.4 Processo de Criação de Tabelas

```
Qualquer nova tabela no banco de dados DEVE passar por:

  [1] Definição no schema.sql
  [2] Revisão: índices, constraints, lineage fields
  [3] Migração Alembic gerada
  [4] Testes de qualidade (Great Expectations)
  [5] Materialized view (se for para relatório)
  [6] Documentação no dbt
  [7] Aprovação do @backend (@kira) + @data-engineer (@leo)
```

---

## 6. Audit Trail

### 6.1 Quem Fez o Quê e Quando?

Toda ação financeira e administrativa tem **registro imutável de auditoria**.

```sql
-- Tabela de audit trail (imutável)
audit_log
├── id: uuid PK
├── table_name: varchar(100) NOT NULL     -- tabela afetada
├── record_id: uuid NOT NULL              -- ID do registro
├── action: enum('create', 'update', 'delete', 'soft_delete') NOT NULL
├── old_values: jsonb                     -- snapshot antes
├── new_values: jsonb                     -- snapshot depois
├── changed_by: uuid NOT NULL             -- quem fez
├── changed_by_type: enum('merchant', 'customer', 'admin', 'rider', 'system')
├── ip_address: varchar(45)
├── user_agent: text
├── trace_id: varchar(100)                -- correlation ID (OpenTelemetry)
├── reason: varchar(200)                  -- motivo da alteração
└── created_at: timestamptz DEFAULT NOW() -- imutável
```

### 6.2 O que é Auditado

| Tabela | Ações auditadas | Motivo |
|--------|:--------------:|--------|
| `order` | create, update, cancel, delete | Financeiro, LGPD |
| `invoice` | create, payment, cancel | Financeiro |
| `merchant_subscription` | create, phase_change, cancel | Financeiro |
| `rider_payment_period` | create, approve, pay | Financeiro |
| `merchant` | create, update, delete | Administrativo |
| `product` | create, update, delete | Catálogo |
| `customer` | create, update, delete_exercise | LGPD |
| `coupon` | create, update, delete | Financeiro |
| `prescription` | create, validate, reject | Regulatório (farmácia) |

### 6.3 Implementação com SQLAlchemy

```python
# src/shared/audit.py

"""
Audit trail automático usando SQLAlchemy event listeners.
Toda alteração em tabelas monitoradas gera um registro de auditoria.
"""

from sqlalchemy import event
from sqlalchemy.orm import Session
from src.models.audit import AuditLog
import json
import structlog

logger = structlog.get_logger()

AUDITED_TABLES = {
    "order", "invoice", "merchant_subscription",
    "rider_payment_period", "merchant", "product",
    "customer", "coupon", "prescription",
}

def before_update_listener(mapper, connection, target):
    """Disparado antes de qualquer UPDATE em tabelas monitoradas."""
    table_name = target.__tablename__
    if table_name not in AUDITED_TABLES:
        return

    # Obtém valores antigos (antes da mudança)
    state = target._sa_instance_state
    old_values = {}
    for attr in target.__table__.columns.keys():
        if hasattr(target, attr):
            # Histórico: valor ANTES da mudança
            history = state.get_history(attr, False)
            if history.has_changes():
                old_values[attr] = history.deleted[0] if history.deleted else None

    if not old_values:
        return  # nada mudou

    new_values = {k: getattr(target, k) for k in old_values.keys()}

    # Cria registro de auditoria (em nova sessão para não rolar back)
    # O registro é INSERTed diretamente, fora da transação principal
    connection.execute(
        AuditLog.__table__.insert().values(
            table_name=table_name,
            record_id=target.id,
            action="update",
            old_values=json.dumps(old_values, default=str),
            new_values=json.dumps(new_values, default=str),
            changed_by=getattr(target, '_changed_by', None),
            changed_by_type=getattr(target, '_changed_by_type', 'system'),
            trace_id=getattr(target, '_trace_id', None),
        )
    )

# Registrar listener em todas as sessões
event.listen(Session, 'before_flush', before_update_listener)
```

### 6.4 Exemplo de Consulta de Auditoria

```sql
-- Quem alterou o status do pedido #1234 e quando?
SELECT
    created_at,
    action,
    old_values->>'status' AS status_anterior,
    new_values->>'status' AS status_novo,
    changed_by,
    changed_by_type,
    reason
FROM audit_log
WHERE table_name = 'order'
    AND record_id = '1234'
    AND action = 'update'
ORDER BY created_at;

-- Resultado:
-- created_at          | action | anterior       | novo           | changed_by | reason
-- 2026-06-09 18:30:00 | update | 'preparing'    | 'out_for_delivery' | uuid_joao  | 'Entregador saiu'
-- 2026-06-09 18:32:00 | update | 'out_for_delivery' | 'delivered'  | uuid_joao  | 'Entregue'
```

---

## 7. Testes de Dados

### 7.1 Pirâmide de Testes de Dados

```
          ┌──────────┐
          │  E2E     │  Testes de BI: "O dashboard mostra
          │  DATA    │  o valor esperado para um cenário
          │  TESTS   │  conhecido?"
          └────┬─────┘
               │
          ┌────▼─────┐
          │  INTEGRAÇÃO│  Testes de pipeline: "A materialized
          │  DATA    │  view foi atualizada corretamente?"
          └────┬─────┘
               │
          ┌────▼─────┐
          │  UNIT    │  Testes de schema: "O campo X existe?
          │  DATA    │  É NOT NULL? Tem o tipo certo?"
          └──────────┘
```

### 7.2 Testes Automatizados no CI

```yaml
# .github/workflows/data-tests.yml

name: Data Quality Tests

on:
  pull_request:
    paths:
      - 'apps/api/**'
      - 'packages/shared/**'

jobs:
  data-quality:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: rapidrop_test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run migrations
        run: alembic upgrade head

      - name: Run data quality tests
        run: pytest tests/data_quality/ -v --tb=short

      - name: Run schema validation
        run: pytest tests/schemas/ -v --tb=short

      - name: Check constraints
        run: python scripts/validate_constraints.py
```

### 7.3 Testes de Schema no CI

```python
# tests/schemas/test_order_schema.py

"""
Testes de schema: garantem que as tabelas têm a estrutura esperada.
Esses testes falham se alguém alterar o banco sem atualizar as definições.
"""

def test_order_table_has_required_columns(db_session):
    """A tabela 'order' deve ter todas as colunas obrigatórias."""
    required = {
        "id", "merchant_id", "customer_id", "status",
        "subtotal_cents", "delivery_fee_cents", "total_cents",
        "created_at", "updated_at",
    }
    actual = get_table_columns(db_session, "order")
    missing = required - actual
    assert not missing, f"Colunas faltando em 'order': {missing}"

def test_order_table_constraints(db_session):
    """Verifica constraints da tabela order."""
    constraints = get_table_constraints(db_session, "order")
    assert "chk_order_positive_values" in constraints
    assert "chk_order_total_matches" in constraints

def test_all_tables_have_lineage_fields(db_session):
    """Toda tabela deve ter created_at, updated_at."""
    tables = get_all_tables(db_session)
    for table in tables:
        if table.startswith("pg_") or table.startswith("_") or table == "alembic_version":
            continue
        columns = get_table_columns(db_session, table)
        assert "created_at" in columns, f"{table} não tem created_at"
        assert "updated_at" in columns, f"{table} não tem updated_at"
```

### 7.4 Teste de Propagação (Novo Pedido → MV)

```python
# tests/data_quality/test_order_propagation.py

"""
Teste de propagação: verifica se um pedido criado na API
aparece corretamente na materialized view de análise.
"""

async def test_new_order_appears_in_mv(async_client, db_session):
    # Arrange: criar um pedido via API
    order_data = {
        "merchant_id": str(uuid4()),
        "customer_id": str(uuid4()),
        "items": [{"product_id": str(uuid4()), "quantity": 1}],
        "delivery_address_id": str(uuid4()),
        "payment_method": "pix",
    }

    # Act: chamar a API
    response = await async_client.post("/api/v1/orders", json=order_data)
    assert response.status_code == 201

    # Act: refresh da materialized view
    await db_session.execute("REFRESH MATERIALIZED VIEW mv_daily_orders")

    # Assert: pedido aparece na MV
    result = await db_session.execute("""
        SELECT COUNT(*) FROM mv_daily_orders
        WHERE merchant_id = :mid
    """, {"mid": order_data["merchant_id"]})
    count = result.scalar()
    assert count == 1, "Pedido não propagou para a MV"
```

---

## 8. Análise e BI

### 8.1 Ferramentas

```
Visualização:    Grafana (dashboards operacionais)
                 Metabase (self-serve para o time)

Data Warehouse:  PostgreSQL (camada analítica com MVs)
                 Futuro: ClickHouse / DuckDB para volumes maiores

ETL:             dbt (transformações versionadas)
                 Celery (refresh programado de MVs)

Exportação:      CSV (para o lojista baixar)
                 API (integrações)
                 Webhook (dados em tempo real)
```

### 8.2 Self-Service para o Time

```sql
-- Qualquer pessoa do time pode consultar os dados analíticos
-- via Metabase ou Grafana Explore.

-- Exemplo: "Quanto faturamos ontem?"
SELECT
    DATE(created_at) AS day,
    COUNT(*) AS orders,
    SUM(total_cents) / 100.0 AS revenue_brl
FROM "order"
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
    AND created_at < CURRENT_DATE
    AND status != 'cancelled';

-- Exemplo: "Top 10 lojistas por receita no mês"
SELECT
    m.name,
    m.segment,
    SUM(o.total_cents) / 100.0 AS revenue_brl,
    COUNT(*) AS total_orders
FROM "order" o
JOIN merchant m ON o.merchant_id = m.id
WHERE DATE_TRUNC('month', o.created_at) = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY m.name, m.segment
ORDER BY revenue_brl DESC
LIMIT 10;
```

### 8.3 Métricas que Acompanhamos em Tempo Real

```
📈 DASHBOARD DE NEGÓCIO (Grafana + SQL)

  ┌─ Lojistas ativos hoje
  ├─ Pedidos na última hora
  ├─ Receita do dia vs ontem
  ├─ Ticket médio do dia
  ├─ Cancelamentos %
  ├─ Tempo médio de entrega
  ├─ Lojistas com maior volume
  └─ Clientes que mais pedem
```

---

## 9. Eventos de Negócio

### 9.1 Schema Único de Eventos

Todo evento de negócio segue um schema padronizado:

```json
{
    "event": "order.created",
    "version": 1,
    "id": "evt_abc123",
    "timestamp": "2026-06-09T14:30:00.123Z",
    "source": "api",
    "trace_id": "trace_xyz",
    "merchant_id": "m_42",
    "data": {
        "order_id": "ord_789",
        "total_cents": 4990,
        "channel": "site",
        "segment": "food"
    }
}
```

### 9.2 Catálogo de Eventos

| Evento | Quando | Dados enviados |
|--------|--------|---------------|
| `order.created` | Novo pedido | order_id, total, channel, items_count |
| `order.status_changed` | Status mudou | order_id, from_status, to_status |
| `order.cancelled` | Pedido cancelado | order_id, reason, who |
| `payment.completed` | Pagamento confirmado | order_id, method, amount |
| `payment.failed` | Pagamento recusado | order_id, method, reason |
| `rider.assigned` | Entregador atribuído | order_id, rider_id |
| `rider.delivered` | Entrega concluída | order_id, rider_id, duration_min |
| `customer.created` | Novo cliente | customer_id, segment |
| `customer.first_order` | Primeiro pedido | customer_id, merchant_id |
| `coupon.used` | Cupom aplicado | coupon_code, customer_id, discount_cents |
| `merchant.subscription_phase_changed` | Migrou de fase | merchant_id, from_phase, to_phase |

### 9.3 Implementação

```python
# src/shared/events.py

"""
Sistema de eventos de negócio padronizados.
Cada evento é emitido para:
  1. Redis PubSub (tempo real — WebSocket)
  2. Kafka / RabbitMQ (futuro — stream processing)
  3. Audit log (persistência)
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from uuid import uuid4
import structlog
import json

logger = structlog.get_logger()


@dataclass
class BusinessEvent:
    """Schema único de evento de negócio."""
    event: str                          # "order.created"
    version: int = 1
    id: str = field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "api"
    trace_id: str = None
    merchant_id: str = None
    data: dict = field(default_factory=dict)


class EventBus:
    """
    Central de eventos. Emite para todos os canais configurados.
    """

    def __init__(self, redis=None, rabbit=None):
        self._redis = redis
        self._rabbit = rabbit

    async def emit(self, event: BusinessEvent):
        """Emite um evento para todos os canais."""
        payload = json.dumps(asdict(event))

        # 1. Redis PubSub (WebSocket em tempo real)
        if self._redis:
            await self._redis.publish("events", payload)

        # 2. RabbitMQ (stream processing)
        if self._rabbit:
            await self._rabbit.publish("business_events", payload)

        # 3. Log estruturado
        logger.info(f"event.{event.event}", **asdict(event))

        return event.id


# Uso no código:
event_bus = EventBus(redis=redis_client)

async def create_order(data):
    order = await order_service.create(data)

    await event_bus.emit(BusinessEvent(
        event="order.created",
        merchant_id=order.merchant_id,
        data={
            "order_id": str(order.id),
            "total_cents": order.total_cents,
            "channel": order.channel,
            "items_count": len(order.items),
        },
    ))

    return order
```

---

## 10. Diferenciais Estratégicos

### 10.1 O Que Nos Torna Únicos

| Aspecto | Concorrentes (iFood, etc.) | RapiDrop |
|---------|---------------------------|----------|
| **Qualidade de dados** | Dados do lojista limitados ao que o marketplace libera | Dados completos, validados e auditados |
| **Rastreabilidade** | Caixa-preta — lojista não sabe o que aconteceu | Lineage completa — todo dado tem origem conhecida |
| **Privacidade** | LGPD reativa | LGPD nativa — dados protegidos por arquitetura |
| **Analytics** | Relatórios básicos pré-definidos | Self-service: qualquer pergunta respondida com SQL |
| **Propagação** | Dados podem levar dias para aparecer em relatórios | Materialized views atualizadas a cada hora |
| **Confiança** | "O relatório do iFood estava errado" | Testes automatizados garantem consistência |

### 10.2 Para o Lojista

```
O lojista do RapiDrop tem:
  ┌─ Dados confiáveis sobre seus pedidos, clientes e entregadores
  ├─ Relatórios que batem com o financeiro (nunca "tem diferença")
  ├─ Saber exatamente quem fez o quê (audit trail)
  ├─ Dados dos seus clientes (não escondidos pelo marketplace)
  └─ Privacidade garantida (LGPD)

Isso é um argumento de venda:
  "No iFood, você não sabe quem são seus clientes.
   No RapiDrop, você tem nome, telefone, endereço e histórico
   de cada um — e tudo auditado."
```

### 10.3 Para o SaaS

```
O RapiDrop como negócio tem:
  ┌─ MRR calculado com precisão (nunca "achismo")
  ├─ Churn real, não estimado
  ├─ Dados para convencer investidores
  ├─ Precificação baseada em dados reais de uso
  └─ Decisões de produto baseadas em dados consistentes

Dado de qualidade = decisão de qualidade.
```

### 10.4 Resumo — Os 5 Mandamentos dos Dados

```
╔══════════════════════════════════════════════════════════════╗
║             OS 5 MANDAMENTOS DOS DADOS                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. VALIDE NA ENTRADA                                        ║
║     Nenhum dado entra sem validação (Pydantic + constraints) ║
║                                                              ║
║  2. RASTREIE DA ORIGEM AO DESTINO                            ║
║     Toda tabela tem created_at, created_by, source           ║
║                                                              ║
║  3. TESTE AUTOMATICAMENTE                                    ║
║     Dados têm testes no CI — se falhar, não deploya          ║
║                                                              ║
║  4. PROTEJA POR PADRÃO                                       ║
║     LGPD é arquitetura, não checklist                        ║
║                                                              ║
║  5. ANALYSE SEM TRANSFORMAR                                  ║
║     Materialized views prontas para consulta                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Principais responsáveis:** @leo (Data Engineer), @kira (Backend)
> **Ferramentas:** dbt, Great Expectations, PostgreSQL, Grafana, Metabase
