# RapiDrop — Multi-tenancy e Isolamento de Dados

> Como garantimos que cada lojista vê **apenas seus próprios dados**,
> como gerenciamos o ciclo de vida de tenants, e como a arquitetura
> escala de 1 a 10.000 lojistas sem quebrar o isolamento.

---

## Índice

1. [Filosofia de Isolamento](#1-filosofia-de-isolamento)
2. [Modelo Escolhido: Shared Database](#2-modelo-escolhido-shared-database)
3. [Identificação do Tenant](#3-identificação-do-tenant)
4. [Application-Level Filtering](#4-application-level-filtering)
5. [Row-Level Security (RLS) — Defesa em Profundidade](#5-row-level-security-rls--defesa-em-profundidade)
6. [Admin SaaS — Acesso Cross-Tenant](#6-admin-saas--acesso-cross-tenant)
7. [Dados Compartilhados vs Dados por Tenant](#7-dados-compartilhados-vs-dados-por-tenant)
8. [Esquemas por Tenant para Dados Sensíveis](#8-esquemas-por-tenant-para-dados-sensíveis)
9. [Ciclo de Vida do Tenant](#9-ciclo-de-vida-do-tenant)
10. [LGPD — Direito ao Esquecimento](#10-lgpd--direito-ao-esquecimento)
11. [Backup e Restore por Tenant](#11-backup-e-restore-por-tenant)
12. [Monitoramento de Isolamento](#12-monitoramento-de-isolamento)
13. [Performance e Escalabilidade](#13-performance-e-escalabilidade)
14. [Modelo de Dados](#14-modelo-de-dados)
15. [Estratégia de Implementação](#15-estratégia-de-implementação)
16. [Cobertura de Testes](#16-cobertura-de-testes)

---

## 1. Filosofia de Isolamento

### 1.1 Princípios

| Princípio | Implicação |
|-----------|------------|
| **Isolamento por padrão, compartilhamento por exceção** | Toda query já nasce com filtro de tenant. Dados compartilhados (planos, configurações globais) são explicitamente marcados. |
| **Defesa em profundidade** | Duas camadas de proteção: (1) aplicação sempre filtra por `merchant_id`, (2) banco de dados tem RLS como fallback. Se uma falhar, a outra segura. |
| **Nunca confiar no cliente** | O `merchant_id` nunca vem do frontend como dado confiável. É extraído do token JWT autenticado. |
| **Audit trail cross-tenant** | Qualquer acesso do admin SaaS a dados de lojistas é registrado com `admin_id`, `merchant_id`, `reason`. |
| **LGPD nativo** | Exclusão de tenant = anonimização de todos os dados pessoais + retenção de dados financeiros por 5 anos (obrigação legal). |

### 1.2 Modelos Considerados

| Modelo | Descrição | Vantagens | Desvantagens | Escolha? |
|--------|-----------|-----------|--------------|:--------:|
| **A — Shared Database + merchant_id** | Todas as tabelas com coluna `merchant_id`, filtro em toda query | ✅ Simples, barato, fácil de gerenciar | ❌ Risco de vazamento se esquecer filtro, backup único | **✅ MVP + Escala** |
| **B — Shared Database + Schema por Tenant** | PostgreSQL schemas separados (`tenant_42.orders`, `tenant_57.orders`) | ✅ Isolamento lógico, backup por schema, migração individual | ❌ Complexo de gerenciar, 10.000 schemas = pesado | ⚠️ **Híbrido para dados sensíveis** |
| **C — Database por Tenant** | Um banco PostgreSQL por lojista | ✅ Isolamento total, backup individual, sem risco de vazamento | ❌ Caro (1 banco x 10.000 = ~R$ 500k/mês), complexo | ❌ **Descartado** |
| **D — Híbrido (A+B)** | Shared database + schemas separados apenas para dados sensíveis (farmácia) | ✅ Melhor dos dois mundos | ⚠️ Complexidade moderada | **✅ Recomendado** |

### 1.3 Decisão: Modelo D — Híbrido

```
FASE 1 (MVP — 1 a 100 lojistas):
  Shared Database + merchant_id em todas as queries
  RLS ativado como segurança extra
  ✅ Simples, seguro, baixo custo

FASE 2 (ESCALA — 100 a 1.000 lojistas):
  Mantém shared database
  Adiciona schema separado (tenant_{id}) para dados sensíveis:
    ─ Farmácia: prescriptions, prescription_images
    ─ Pagamento: gateway_tokens, refund_reasons
  ✅ Isolamento onde realmente importa

FASE 3 (ENTERPRISE — 1.000+ lojistas):
  Read replicas para analytics (sem impacto nos tenants)
  Opção de dedicated database para lojistas enterprise
  Sharding por grupo de tenants (ex: por região)
```

---

## 2. Modelo Escolhido: Shared Database

### 2.1 Arquitetura

```
┌────────────────────────────────────────────────────────────┐
│                    POSTGRESQL (16)                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DATABASE: rapidrop                                   │  │
│  │                                                       │  │
│  │  ┌─ public (dados compartilhados)                   │  │
│  │  │   ├─ plans, plan_features                        │  │
│  │  │   ├─ onboarding_content                          │  │
│  │  │   ├─ notification_templates                      │  │
│  │  │   └─ system_config                               │  │
│  │  │                                                   │  │
│  │  ├─ merchants (FK references)                       │  │
│  │  ├─ orders (merchant_id)                            │  │
│  │  ├─ products (merchant_id)                          │  │
│  │  ├─ customers (merchant_id)                         │  │
│  │  ├─ riders (merchant_id)                            │  │
│  │  ├─ invoices (merchant_id)                          │  │
│  │  ├─ ... (merchant_id em todas)                      │  │
│  │                                                   │  │
│  │  ┌─ tenant_42 (schema de dados sensíveis)         │  │
│  │  │   ├─ prescriptions                             │  │
│  │  │   ├─ prescription_images                       │  │
│  │  │   └─ payment_tokens                            │  │
│  │  │                                                   │  │
│  │  └─ tenant_57 (...)                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  RLS POLICIES ativas em todas as tabelas com merchant_id    │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Justificativa

| Por que Shared Database? | Explicação |
|--------------------------|------------|
| **Custo** | Um PostgreSQL 16 bem configurado roda 1.000+ lojistas sem suar. Database separada para cada um multiplicaria o custo por 1.000. |
| **Manutenção** | Uma migração (Alembic) para todos. Backup único. Monitoramento único. |
| **Consultas cross-tenant** | Admin SaaS precisa de "quantos pedidos todos os lojistas fizeram hoje?" — em shared DB é `SELECT count(*)`. Em DB separado seriam 1.000 queries. |
| **Simplicidade** | Toda a equipe entende. Sem ORM complexo. Sem roteamento de queries. |

| Por que schemas separados para dados sensíveis? | Explicação |
|--------------------------------------------------|------------|
| **Farmácia: receitas médicas** | Imagens de receita são dados de saúde (LGPD categoria especial). Isolamento extra justifica a complexidade. |
| **Tokens de pagamento** | Chaves de gateway criptografadas por tenant. Schema separado = camada extra de segurança. |
| **Escalabilidade seletiva** | Só isolar onde a lei exige. Dados comuns (pedidos, produtos) ficam no shared. |

---

## 3. Identificação do Tenant

### 3.1 Como o Sistema Sabe Quem é o Tenant

O tenant é identificado em **cada request** através do token JWT:

```
Request HTTP
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ MIDDLEWARE DE AUTENTICAÇÃO                                    │
│                                                               │
│  1. Extrair JWT do header Authorization: Bearer <token>      │
│  2. Validar assinatura + expiração                           │
│  3. Decodificar payload:                                     │
│       {                                                      │
│         "user_id": 42,                                       │
│         "merchant_id": 57,         ← DONO DO TENANT         │
│         "role": "merchant_owner",                            │
│         "iat": ...,                                          │
│         "exp": ...                                           │
│       }                                                      │
│  4. Injeta no request context: request.state.merchant_id      │
│                                                               │
│  🔴 NUNCA confiar em merchant_id vindo do body/query/header   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Regras de Tenant por Role

| Role | merchant_id no JWT | Acesso a dados |
|------|:------------------:|----------------|
| `merchant_owner` | O próprio | Apenas seus dados |
| `merchant_operator` | O próprio | Apenas dados do merchant (sem financeiro) |
| `rider` | Do merchant que contratou | Apenas entregas do merchant |
| `saas_admin` | `null` (acesso global) | Todos os tenants (com audit log) |
| `customer` | `null` (acesso via customer_id) | Apenas seus próprios pedidos |

### 3.3 Fluxo de Requests

```python
# Middleware: FastAPI dependency
async def get_current_merchant_id(request: Request) -> int:
    """
    Extrai o merchant_id do token JWT autenticado.

    Esta é a ÚNICA fonte confiável de merchant_id.
    NUNCA usar merchant_id enviado pelo cliente no body/query.
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    merchant_id = payload.get("merchant_id")
    role = payload.get("role")

    # Admin não tem merchant_id (acesso global)
    if role == "saas_admin":
        return None  # Acesso liberado para todos os tenants

    if not merchant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return merchant_id
```

```python
# Repository pattern — toda query de dados de tenant passa por aqui
class MerchantRepository:
    """
    Base para todos os repositórios que acessam dados de tenant.
    Garante que TODA query tenha filtro de merchant_id.
    """

    def __init__(self, db_session: AsyncSession, merchant_id: int | None):
        self.db = db_session
        self.merchant_id = merchant_id  # None = admin (acesso global)

    async def get_orders(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        query = select(Order)

        # 🔴 FILTRO OBRIGATÓRIO — aplicação nunca esquece
        if self.merchant_id is not None:
            query = query.where(Order.merchant_id == self.merchant_id)

        if status:
            query = query.where(Order.status == status)

        query = query.order_by(Order.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()
```

---

## 4. Application-Level Filtering

### 4.1 Padrão Obrigatório

Toda consulta a dados de tenant **DEVE** seguir este padrão:

```python
# ✅ CERTO — filtro explícito de merchant_id
query = select(Order).where(Order.merchant_id == current_merchant_id)

# ✅ CERTO — usando repositório com tenant
orders = await repo.get_orders(status="pendente")

# ❌ ERRADO — sem filtro de tenant (vaza dados!)
query = select(Order)

# ❌ ERRADO — confiando no merchant_id vindo do cliente
merchant_id = request.query_params.get("merchant_id")
query = select(Order).where(Order.merchant_id == merchant_id)
```

### 4.2 Campos Obrigatórios em Todas as Tabelas de Tenant

Toda tabela que armazena dados de/para um lojista DEVE ter:

```sql
merchant_id INTEGER NOT NULL REFERENCES merchants(id)

-- E DEVE ter índice:
CREATE INDEX idx_{tabela}_merchant ON {tabela}(merchant_id);
```

**Tabelas que SEMPRE têm `merchant_id`:**
```
orders, products, product_categories, product_variations,
customers, customer_addresses, customer_consent,
riders, rider_payment_config, rider_payment_period,
invoices, invoice_transactions, payment_transactions,
prescriptions (no schema do tenant),
whatsapp_conversations, whatsapp_message_log,
merchant_onboarding, onboarding_event,
reports, report_schedules
```

**Tabelas que NÃO têm `merchant_id` (dados compartilhados):**
```
saas_admins, plans, plan_features, system_config,
onboarding_content, notification_templates
```

### 4.3 Checklist de Code Review

```markdown
## Checklist de Revisão — Proteção de Tenant

Antes de aprovar qualquer PR com query no banco:

- [ ] A query filtra por `merchant_id`?
- [ ] O `merchant_id` veio do token JWT, não do cliente?
- [ ] A rota/mutation tem proteção de autenticação?
- [ ] Se é admin: o acesso cross-tenant está registrado em audit log?
- [ ] Se é uma nova tabela: ela tem `merchant_id NOT NULL`?
- [ ] Se é uma nova tabela: tem índice em `merchant_id`?
- [ ] Os testes incluem cenário de "tentar acessar dados de outro tenant"?
```

### 4.4 Tratamento de Exceções

```python
# Se por algum motivo o merchant_id não está disponível:
if current_merchant_id is None and role != "saas_admin":
    raise HTTPException(
        status_code=403,
        detail="Tenant não identificado. Acesso negado.",
    )

# Se uma query sem filtro retornar dados de múltiplos tenants
# (possível bug de implementação):
if len(results) > 0 and any(
    r.merchant_id != current_merchant_id for r in results
):
    # Log imediato + alerta de segurança
    security_alert(
        event="potential_data_leak",
        merchant_id=current_merchant_id,
        endpoint=request.url.path,
        user_id=current_user_id,
    )
    raise HTTPException(status_code=500, detail="Erro de isolamento de dados")
```

---

## 5. Row-Level Security (RLS) — Defesa em Profundidade

### 5.1 Políticas RLS no PostgreSQL

Além do filtro na aplicação, o PostgreSQL tem **Row-Level Security** como
camada extra. Se a aplicação esquecer um filtro, o RLS barra.

```sql
-- Habilitar RLS no banco
ALTER DATABASE rapidrop SET row_security = ON;

-- Para cada tabela de tenant:
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE riders ENABLE ROW LEVEL SECURITY;
-- ... (todas as tabelas com merchant_id)

-- Política: usuário só vê registros do seu merchant_id
CREATE POLICY tenant_isolation_policy ON orders
    FOR ALL
    USING (merchant_id = current_setting('app.current_merchant_id')::INTEGER);

CREATE POLICY tenant_isolation_policy ON products
    FOR ALL
    USING (merchant_id = current_setting('app.current_merchant_id')::INTEGER);

-- ... (uma policy por tabela)
```

### 5.2 Configuração da Sessão

A cada request, a aplicação configura o `merchant_id` na sessão do PostgreSQL:

```python
async def configure_rls_session(
    db_session: AsyncSession,
    merchant_id: int | None,
    role: str,
):
    """
    Configura a sessão do PostgreSQL com o tenant atual para RLS.
    Chama no início de cada request.
    """
    if role == "saas_admin":
        # Admin: desabilita RLS para acesso global
        await db_session.execute(
            text("SET app.current_merchant_id = 0")
        )
        await db_session.execute(
            text("SET app.is_admin = true")
        )
    else:
        # Tenant: ativa RLS com o merchant_id
        await db_session.execute(
            text(f"SET app.current_merchant_id = {merchant_id}")
        )
        await db_session.execute(
            text("SET app.is_admin = false")
        )

    # Aplicação usa ROLE dedicada que respeita RLS
    await db_session.execute(
        text("SET ROLE rapidrop_app")
    )
```

### 5.3 Roles do PostgreSQL

```sql
-- Role da aplicação (com RLS ativo)
CREATE ROLE rapidrop_app WITH LOGIN;
ALTER ROLE rapidrop_app SET row_security TO on;

-- Role do admin (sem RLS — acesso total)
CREATE ROLE rapidrop_admin WITH LOGIN;
ALTER ROLE rapidrop_admin SET row_security TO off;

-- Política especial: admin vê tudo
CREATE POLICY admin_bypass ON orders
    FOR ALL
    USING (
        current_setting('app.is_admin')::BOOLEAN = true
        OR
        merchant_id = current_setting('app.current_merchant_id')::INTEGER
    );
```

### 5.4 Teste Manual de RLS

```sql
-- Simular lojista 42
SET app.current_merchant_id = 42;
SET app.is_admin = false;
SET ROLE rapidrop_app;

-- Deve retornar apenas pedidos do lojista 42
SELECT * FROM orders LIMIT 5;

-- Simular admin
SET app.current_merchant_id = 0;
SET app.is_admin = true;
SET ROLE rapidrop_app;

-- Deve retornar pedidos de todos os lojistas
SELECT * FROM orders LIMIT 5;
```

---

## 6. Admin SaaS — Acesso Cross-Tenant

### 6.1 Quando o Admin Precisa Acessar Dados de Lojistas

O admin do RapiDrop precisa ver dados de todos os lojistas para:

```
✅ Dashboard de métricas do SaaS (MRR, churn, pedidos totais)
✅ Suporte: ver pedidos, fatura, configurações de um lojista específico
✅ Auditoria: verificar suspeita de fraude
✅ Cobrança: gerenciar faturas inadimplentes

❌ NUNCA: modificar dados sem registro em audit log
❌ NUNCA: acessar dados de clientes finais sem justificativa
❌ NUNCA: exportar dados de múltiplos lojistas sem registro
```

### 6.2 Audit Log de Acesso Admin

Todo acesso do admin a dados de tenant é registrado:

```python
@router.get("/admin/merchants/{merchant_id}/orders")
async def admin_get_merchant_orders(
    merchant_id: int,
    admin_user: SaasAdmin = Depends(get_admin_user),
    db_session: AsyncSession = Depends(get_session),
):
    """
    Admin visualiza pedidos de um lojista específico.
    TODO acesso é logado com motivo.
    """

    # Registrar acesso no audit log
    await create_audit_log(db_session, {
        "entity_type": "admin_access",
        "entity_id": merchant_id,
        "action": "admin.view_merchant_orders",
        "who": "saas_admin",
        "who_id": admin_user.id,
        "reason": request.headers.get("X-Access-Reason", "Suporte"),  # OBRIGATÓRIO
        "metadata": {
            "ip_address": request.client.host,
            "endpoint": request.url.path,
            "merchant_id": merchant_id,
        },
    })

    # Acessar dados do tenant
    repo = OrderRepository(db_session, merchant_id=None)  # admin: sem filtro
    orders = await repo.get_merchant_orders(merchant_id)

    return orders
```

### 6.3 Interface do Admin — Seleção de Tenant

```
┌────────────────────────────────────────────────────────────┐
│  🔍 Admin RapiDrop                                         │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Buscar lojista: [ Pizzaria do Norte          ] 🔍          │
│                                                              │
│  ┌──────────────┬──────────┬────────┬────────────────────┐  │
│  │ Lojista      │ Segmento │ Status │ Ações              │  │
│  ├──────────────┼──────────┼────────┼────────────────────┤  │
│  │ Pizzaria do  │ Comida   │ 🟢 Ativo│ [Pedidos] [Fatura] │  │
│  │ Norte (#42)  │          │        │ [Config]            │  │
│  ├──────────────┼──────────┼────────┼────────────────────┤  │
│  │ Farmácia     │ Farmácia │ 🟡     │ [Pedidos] [Fatura] │  │
│  │ São João     │          │ Trial  │ [Config]            │  │
│  └──────────────┴──────────┴────────┴────────────────────┘  │
│                                                              │
│  ⚠️  Você está acessando dados de um lojista.               │
│     Motivo: [Suporte ▼]                                      │
│     Todo acesso é registrado.                                │
└────────────────────────────────────────────────────────────┘
```

---

## 7. Dados Compartilhados vs Dados por Tenant

### 7.1 Matriz Completa

| Entidade | Tipo | merchant_id? | Observação |
|----------|:----:|:------------:|------------|
| `saas_admins` | Compartilhado | ❌ | Administradores do RapiDrop |
| `plans` | Compartilhado | ❌ | Planos de assinatura (Básico, Pro, Enterprise) |
| `plan_features` | Compartilhado | ❌ | Features por plano |
| `onboarding_content` | Compartilhado | ❌ | Templates de onboarding por segmento |
| `notification_templates` | Compartilhado | ❌ | Templates aprovados no WhatsApp |
| `system_config` | Compartilhado | ❌ | Configurações globais do sistema |
| `merchants` | Tenant | ✅ (PK) | A própria entidade "lojista" é o tenant |
| `orders` | Tenant | ✅ | Pedidos |
| `products` | Tenant | ✅ | Catálogo de produtos |
| `product_categories` | Tenant | ✅ | Categorias do catálogo |
| `product_variations` | Tenant | ✅ | Variações (tamanho, sabor) |
| `customers` | Tenant | ✅ | Clientes do lojista |
| `customer_addresses` | Tenant | ✅ | Endereços dos clientes |
| `riders` | Tenant | ✅ | Entregadores |
| `rider_payment_config` | Tenant | ✅ | Config de pagamento |
| `rider_payment_period` | Tenant | ✅ | Períodos de pagamento |
| `invoices` | Tenant | ✅ | Faturas mensais |
| `payment_transactions` | Tenant | ✅ | Transações financeiras |
| `whatsapp_conversations` | Tenant | ✅ | Conversas WhatsApp |
| `whatsapp_message_log` | Tenant | ✅ | Log de mensagens |
| `merchant_onboarding` | Tenant | ✅ | Progresso do onboarding |
| `onboarding_event` | Tenant | ✅ | Eventos de onboarding |
| `prescriptions` | **Schema do tenant** | ✅ | Receitas (dados sensíveis) |
| `prescription_images` | **Schema do tenant** | ✅ | Imagens criptografadas |
| `gateway_tokens` | **Schema do tenant** | ✅ | Tokens do gateway |

### 7.2 Exceções: Quando um Registro Não Tem merchant_id

Algumas entidades são **do cliente final**, não do lojista:

```sql
-- Tabela de clientes (global) — usada para login unificado
-- Mesmo cliente pode comprar de múltiplos lojistas
CREATE TABLE customer_account (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,  -- login por WhatsApp
    name VARCHAR(200),
    email VARCHAR(200),
    password_hash VARCHAR(200),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ponte: cliente → lojista (dados específicos do relacionamento)
CREATE TABLE customer_merchant (
    id UUID PRIMARY KEY,
    customer_account_id UUID REFERENCES customer_account(id),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    -- dados específicos deste cliente com este lojista
    total_orders INTEGER DEFAULT 0,
    total_spent_cents INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (customer_account_id, merchant_id)
);
```

---

## 8. Esquemas por Tenant para Dados Sensíveis

### 8.1 Quando Usar Schema Separado

Apenas para dados que a lei ou a segurança exige isolamento extra:

| Dado | Por que schema separado? | Risco se vazar |
|------|--------------------------|----------------|
| Imagens de receitas médicas | LGPD: dados de saúde são categoria especial | 🔴 Multa, dano reputacional, processo |
| Dados de pagamento (tokens) | PCI-DSS: tokens de cartão | 🔴 Multa, bloqueio do gateway |
| Histórico de localização dos entregadores | LGPD: dados de localização | 🟡 Exposição de privacidade |

### 8.2 Criação Automática de Schema

```python
async def create_tenant_schema(merchant_id: int):
    """
    Cria schema separado para dados sensíveis de um tenant.
    Chamado quando o lojista completa o onboarding.

    Schema: tenant_{merchant_id}
    """
    schema_name = f"tenant_{merchant_id}"

    # Criar schema
    await db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

    # Criar tabelas dentro do schema
    await db_session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.prescriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            order_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            image_path VARCHAR(500) NOT NULL,
            image_hash VARCHAR(64) NOT NULL,
            validated_by INTEGER,
            validated_at TIMESTAMPTZ,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            rejection_reason TEXT,
            expires_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMPTZ  -- soft delete para LGPD
        );
    """))

    # Configurar RLS no schema
    await db_session.execute(text(f"""
        ALTER TABLE {schema_name}.prescriptions ENABLE ROW LEVEL SECURITY;
    """))

    await db_session.commit()
```

### 8.3 Acesso aos Schemas por Tenant

```python
class SensitiveDataRepository:
    """
    Acesso a dados sensíveis em schema separado.
    """

    def __init__(self, db_session: AsyncSession, merchant_id: int):
        self.db = db_session
        self.schema = f"tenant_{merchant_id}"

    async def get_prescription(self, prescription_id: UUID) -> dict | None:
        query = text(f"""
            SELECT * FROM {self.schema}.prescriptions
            WHERE id = :id AND deleted_at IS NULL
        """)
        result = await self.db.execute(query, {"id": prescription_id})
        return result.one_or_none()

    async def get_active_prescriptions(self, customer_id: int) -> list[dict]:
        query = text(f"""
            SELECT * FROM {self.schema}.prescriptions
            WHERE customer_id = :cid
              AND status = 'validated'
              AND deleted_at IS NULL
              AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY created_at DESC
        """)
        result = await self.db.execute(query, {"cid": customer_id})
        return result.all()
```

### 8.4 Migrações em Schemas por Tenant

Para aplicar migrações em todos os schemas de tenant:

```python
@celery.task
async def migrate_all_tenant_schemas():
    """
    Aplica migrações pendentes em TODOS os schemas de tenant.
    Roda após cada deploy com nova migração.
    """
    # Listar todos os merchants ativos
    merchants = await db_session.execute(
        text("SELECT id FROM merchants WHERE is_active = true")
    )

    for (merchant_id,) in merchants:
        schema = f"tenant_{merchant_id}"
        try:
            # Aplicar migração no schema
            await db_session.execute(text(f"SET search_path TO {schema}"))
            await run_migrations_up()  # função de migração
            logger.info("Migração aplicada", schema=schema)
        except Exception as e:
            logger.error("Falha na migração", schema=schema, error=str(e))
            # Falha em um tenant não bloqueia os outros
            continue
```

---

## 9. Ciclo de Vida do Tenant

### 9.1 Estados do Tenant

```
                    ┌──────────┐
                    │ LEAN     │ (cadastro iniciado)
                    └────┬─────┘
                         │
                         ▼
                    ┌──────────┐
                    │ ACTIVE   │ (em operação, pagando ou trial)
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ SUSPENDED│ │ CANCELLED│ │ EXPIRED  │
       │          │ │          │ │ (dados   │
       │  (inadi- │ │ (pediu   │ │  retidos)│
       │  plente) │ │  sair)   │ │          │
       └────┬─────┘ └────┬─────┘ └────┬─────┘
            │            │            │
            ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ REACTIVE │ │ PENDING  │ │ ANONYMI- │
       │ (pagou)  │ │ DELETE   │ │ ZED (90  │
       └──────────┘ │ (90 dias)│ │  dias)   │
                    └──────────┘ └──────────┘
                         │
                         ▼
                    ┌──────────┐
                    │ DELETED  │ (dados anonimizados)
                    └──────────┘
```

### 9.2 Ações em Cada Transição

| Transição | Ações do Sistema |
|-----------|------------------|
| `lead → active` | Schema criado (`tenant_{id}`). Onboarding inicia. Timer do trial começa. |
| `active → suspended` | Dashboard bloqueado. Pedidos novos bloqueados. Entregas ativas continuam. |
| `suspended → active` | Dashboard reativado. Pedidos novos liberados. Imediato após pagamento. |
| `active → cancelled` | Lojista solicita. Dashboard bloqueado. Inicia contagem de 90 dias. |
| `cancelled → pending_delete` | 90 dias se passaram. Dados marcados para anonimização. |
| `pending_delete → anonymized` | Job roda: anonimiza dados pessoais, mantém dados financeiros (obrigação legal). Schema do tenant deletado. |
| `cancelled → active` | Reativação dentro de 90 dias: dados recuperados integralmente. |

### 9.3 Cancelamento de Tenant (Fluxo Completo)

```python
async def cancel_merchant(merchant_id: int, reason: str, requested_by: str):
    """
    Cancela um lojista e inicia o processo de retenção/exclusão de dados.
    """
    merchant = await db.get(Merchant, merchant_id)
    merchant.plan_status = "cancelled"
    merchant.cancelled_at = datetime.now()
    merchant.cancellation_reason = reason
    merchant.cancellation_requested_by = requested_by

    # Bloquear acesso imediatamente
    merchant.is_active = False

    # Agendar anonimização para 90 dias
    merchant.scheduled_deletion_at = datetime.now() + timedelta(days=90)

    # Notificar lojista
    await send_email(
        merchant.email,
        "Conta cancelada",
        f"Seus dados serão mantidos por 90 dias. "
        f"Para reativar, acesse o link: ..."
    )

    await db.commit()

    # Agendar job de anonimização
    schedule_anonymization.apply_async(
        args=[merchant_id],
        eta=datetime.now() + timedelta(days=90),
    )
```

---

## 10. LGPD — Direito ao Esquecimento

### 10.1 O Que é Anonimizado vs Mantido

Quando um tenant é cancelado e o prazo de 90 dias expira:

| Tipo de Dado | Ação | Prazo Legal | Justificativa |
|-------------|------|:-----------:|---------------|
| Nome do lojista | Anonimizar | — | LGPD |
| Email do lojista | Anonimizar | — | LGPD |
| Telefone do lojista | Anonimizar | — | LGPD |
| Endereço do lojista | Anonimizar | — | LGPD |
| Dados dos clientes finais | Anonimizar | — | LGPD |
| Nome do entregador | Anonimizar | — | LGPD |
| **Faturas pagas** | **Manter** | **5 anos** | **Obrigação fiscal** |
| **Transações financeiras** | **Manter** | **5 anos** | **Obrigação fiscal** |
| **Contratos aceitos** | **Manter** | **5 anos** | **Obrigação legal** |
| Logs de auditoria | Manter (anonimizar PII) | 5 anos | Segurança jurídica |
| Métricas agregadas | Manter | Indeterminado | Anonimizado (não identifica) |

### 10.2 Job de Anonimização

```python
@celery.task
async def anonymize_merchant_data(merchant_id: int):
    """
    Anonimiza dados pessoais de um lojista e seus clientes.
    Roda 90 dias após o cancelamento.
    """
    logger.info("Anonimizando dados", merchant_id=merchant_id)

    # 1. Anonimizar dados do lojista
    await db.execute(
        update(Merchant)
        .where(Merchant.id == merchant_id)
        .values(
            business_name=f"Lojista {merchant_id}",  # anonimizado
            email=f"deleted_{merchant_id}@rapidrop.com",
            phone=f"+55 11 00000-0000",
            address_street="[removido]",
            address_number="0",
            document="000.000.000-00",  # CPF/CNPJ anonimizado
            is_anonymized=True,
            anonymized_at=datetime.now(),
        )
    )

    # 2. Anonimizar dados dos clientes deste lojista
    await db.execute(f"""
        UPDATE customers
        SET
            name = 'Cliente #' || id,
            phone = '+55 11 00000-0000',
            email = NULL,
            notes = NULL,
            health_notes = NULL,
            is_anonymized = TRUE,
            anonymized_at = NOW()
        WHERE merchant_id = {merchant_id}
    """)

    # 3. Anonimizar dados dos entregadores
    await db.execute(f"""
        UPDATE riders
        SET
            name = 'Entregador #' || id,
            phone = '+55 11 00000-0000',
            document = '000.000.000-00',
            is_anonymized = TRUE,
            anonymized_at = NOW()
        WHERE merchant_id = {merchant_id}
    """)

    # 4. Deletar schema de dados sensíveis
    await db.execute(text(f"DROP SCHEMA IF EXISTS tenant_{merchant_id} CASCADE"))

    # 5. Deletar arquivos (receitas, comprovantes)
    await delete_merchant_files(merchant_id)

    # 6. Registrar conclusão
    merchant = await db.get(Merchant, merchant_id)
    merchant.data_deleted_at = datetime.now()
    await db.commit()

    logger.info("Anonimização concluída", merchant_id=merchant_id)
```

### 10.3 Exportação de Dados (Solicitação do Lojista)

O lojista pode solicitar a exportação de todos os seus dados a qualquer momento:

```
1. Lojista acessa "Configurações → Privacidade → Exportar dados"
2. Sistema gera um pacote ZIP com:
   ─ Pedidos (CSV)
   ─ Produtos (CSV)
   ─ Clientes (CSV, com dados de contato)
   ─ Entregadores (CSV)
   ─ Faturas (CSV)
   ─ Log de acesso (CSV, últimos 12 meses)
3. Link para download enviado por email
4. Link expira em 7 dias
```

---

## 11. Backup e Restore por Tenant

### 11.1 Estratégia de Backup

| Tipo | Frequência | Retenção | Cobertura |
|------|:----------:|:--------:|-----------|
| Full database | Diária (00:00 UTC) | 30 dias | Todo o banco |
| WAL (Write-Ahead Log) | Contínuo | 7 dias | Point-in-time recovery |
| Schema por tenant | Semanal | 3 meses | Schemas de dados sensíveis |
| Arquivos (imagens) | Diária | 30 dias | Bucket S3/MinIO |

### 11.2 Restore de Tenant Específico

```bash
# Backup full do banco
pg_dump -Fc -d rapidrop > rapidrop_full_$(date +%Y%m%d).dump

# Restore de um tenant específico a partir do full dump
pg_restore -d rapidrop \
    --schema=tenant_42 \
    --data-only \
    --table=merchants \
    --table=orders \
    --table=products \
    --table=customers \
    rapidrop_full_20260601.dump

# Ou: extrair apenas dados de um merchant_id
pg_dump -d rapidrop \
    --data-only \
    --table=orders \
    --schema=tenant_42 \
    --schema=public \
    --column-inserts \
    --where="merchant_id=42" \
    > tenant_42_restore.sql
```

### 11.3 Teste de Restore

Mensalmente, um job automatizado testa o restore:

```
1. Cria database de teste: rapidrop_restore_test
2. Restaura o último backup full
3. Executa queries de verificação:
   ─ Contagem de merchants, orders, products
   ─ Verifica merchant_id = 42 tem dados
   ─ Verifica merchant_id = 9999 NÃO tem dados (não existe)
4. Deleta database de teste
5. Envia relatório: "✅ Restore testado com sucesso"
```

---

## 12. Monitoramento de Isolamento

### 12.1 Alertas de Segurança

| Evento | Severidade | Ação |
|--------|:----------:|------|
| Query sem `merchant_id` retorna dados de múltiplos tenants | 🔴 Crítico | Alerta imediato no Slack + bloqueio da query |
| Tentativa de acesso cross-tenant não autorizada | 🔴 Crítico | Log + bloquear IP + notificar admin |
| Admin acessa tenant sem motivo registrado | 🟡 Médio | Log + notificação semanal |
| RLS policy desabilitada em tabela de tenant | 🔴 Crítico | Alerta + reabilitação automática |
| Mais de 1.000 conexões simultâneas (aquecimento) | 🟡 Médio | Escalar pool de conexões |

### 12.2 Queries de Auditoria

```sql
-- Detectar possíveis vazamentos: queries que retornaram dados de múltiplos tenants
-- (executar periodicamente nos logs do banco)

-- Verificar se todas as tabelas de tenant têm RLS ativo
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE tablename IN (
    'orders', 'products', 'customers', 'riders',
    'invoices', 'payment_transactions'
)
ORDER BY tablename;
```

### 12.3 Dashboard de Isolamento (Admin)

```
┌────────────────────────────────────────────────────────────┐
│  🔒 ISOLAMENTO DE DADOS — Status                           │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ RLS ativo: 32/32 tabelas de tenant                      │
│  ✅ Schemas de tenant: 42 ativos                            │
│  ✅ Último restore testado: 01/06/2026 (OK)                 │
│                                                              │
│  Acessos admin nas últimas 24h:                             │
│  ┌───┬────────────┬────────────┬──────────┬──────────────┐ │
│  │ # │ Admin      │ Lojista    │ Motivo   │ Data         │ │
│  ├───┼────────────┼────────────┼──────────┼──────────────┤ │
│  │ 1 │ victor@... │ Pizzaria   │ Suporte  │ 15/06 14:23  │ │
│  │ 2 │ maya@...   │ Farmácia   │ Auditoria│ 15/06 10:05  │ │
│  │   │            │ São João   │          │              │ │
│  └───┴────────────┴────────────┴──────────┴──────────────┘ │
│                                                              │
│  ⚠️  0 tentativas de acesso cross-tenant suspeitas          │
└────────────────────────────────────────────────────────────┘
```

---

## 13. Performance e Escalabilidade

### 13.1 Índices Obrigatórios

Toda tabela de tenant DEVE ter:

```sql
-- Índice primário: busca por tenant + data
CREATE INDEX idx_{tabela}_merchant_created
    ON {tabela}(merchant_id, created_at DESC);

-- Índices adicionais por caso de uso:
CREATE INDEX idx_orders_merchant_status
    ON orders(merchant_id, status, created_at DESC);

CREATE INDEX idx_products_merchant_available
    ON products(merchant_id, is_available)
    WHERE is_available = true;
```

### 13.2 Pool de Conexões

Cada request usa uma conexão do pool. O `merchant_id` é configurado por conexão:

```python
# Configuração do pool de conexões (SQLAlchemy async)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,        # conexões mantidas abertas
    max_overflow=10,     # conexões extras sob demanda
    pool_pre_ping=True,  # verifica se conexão está viva
    pool_recycle=3600,   # recicla conexões a cada 1h
)

# A cada request: pega conexão do pool, configura tenant
async with db_session.begin():
    await configure_rls_session(db_session, merchant_id, role)
    # ... executa queries com RLS ativo
```

### 13.3 Estratégia de Escala

| Nível | Lojistas | PostgreSQL | Estratégia |
|:-----:|:--------:|:-----------|------------|
| 🟢 **Início** | 1-100 | 1 instância (4GB RAM, 2 vCPU) | Shared DB + RLS + índices |
| 🟡 **Crescimento** | 100-500 | 1 instância (16GB RAM, 4 vCPU) | + read replica para analytics + partition por mês (orders) |
| 🟠 **Escala** | 500-2.000 | 1 primária + 2 réplicas | + connection pooling (PgBouncer) + cache pesado (Redis) |
| 🔴 **Maturidade** | 2.000+ | Cluster (Citus/PostgreSQL distribuído) | + sharding por grupo de merchants + dedicated para enterprise |

### 13.4 Considerações de Performance

| Problema | Solução |
|----------|---------|
| `merchant_id` em toda query satura o cache de planos | Índices compostos começando com `merchant_id` |
| Muitos tenants = muitas partitions = lentidão | Só particionar tabelas grandes (`orders`, `payment_transactions`) |
| RLS overhead (avalia policy em cada row) | Negligenciável (< 5%) para tabelas com índice em `merchant_id` |
| Admin queries cross-tenant são lentas (sem RLS, sem índice específico) | Admin usa queries diferentes, otimizadas para agregação |

---

## 14. Modelo de Dados

```sql
-- Tabela principal de merchants (o tenant)
CREATE TABLE merchants (
    id SERIAL PRIMARY KEY,
    -- Dados de identificação
    business_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    phone VARCHAR(20),
    document VARCHAR(20),  -- CPF/CNPJ
    segment VARCHAR(20) NOT NULL,  -- 'food' | 'pharmacy' | 'grocery'

    -- Plano e status
    plan_id INTEGER REFERENCES plans(id),
    plan_status VARCHAR(20) NOT NULL DEFAULT 'trial',
    -- 'lead' | 'trial' | 'active' | 'suspended' | 'cancelled' | 'anonymized'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamps de ciclo de vida
    trial_ends_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    scheduled_deletion_at TIMESTAMPTZ,
    data_deleted_at TIMESTAMPTZ,
    is_anonymized BOOLEAN NOT NULL DEFAULT FALSE,
    anonymized_at TIMESTAMPTZ,

    -- Endereço
    address_street VARCHAR(200),
    address_number VARCHAR(20),
    address_city VARCHAR(100),
    address_state VARCHAR(2),
    address_zip VARCHAR(10),
    lat NUMERIC(10, 7),
    lng NUMERIC(10, 7),

    -- Configurações
    settings JSONB,  -- delivery_fee_config, working_hours, etc.

    -- Chaves Asaas
    asaas_subaccount VARCHAR(100),  -- ID da subconta
    asaas_wallet_id VARCHAR(100),   -- wallet para split

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Log de ações do tenant (para compliance)
CREATE TABLE tenant_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    -- 'suspended' | 'reactivated' | 'cancelled' | 'data_exported'
    -- 'admin_accessed' | 'plan_changed' | 'payment_method_changed'
    performed_by VARCHAR(50) NOT NULL,  -- 'system' | 'merchant' | 'admin'
    performed_by_id INTEGER,
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Schema de dados sensíveis (criado dinamicamente)
-- CREATE SCHEMA tenant_{merchant_id};
-- CREATE TABLE tenant_{merchant_id}.prescriptions ( ... );

-- Índices
CREATE INDEX idx_merchants_status ON merchants(plan_status) WHERE is_active = true;
CREATE INDEX idx_merchants_deletion ON merchants(scheduled_deletion_at)
    WHERE scheduled_deletion_at IS NOT NULL AND data_deleted_at IS NULL;
CREATE INDEX idx_tenant_audit ON tenant_audit_log(merchant_id, created_at DESC);
```

---

## 15. Estratégia de Implementação

### 15.1 Fase 1 — MVP (Semanas 1-2)

```
[ ] Todas as tabelas de tenant com merchant_id NOT NULL
[ ] Middleware de autenticação com extração de merchant_id
[ ] Repository pattern com filtro obrigatório de merchant_id
[ ] RLS ativado nas tabelas principais (orders, products, customers, riders)
[ ] Testes de isolamento: tenant A não vê dados de tenant B
[ ] Code review checklist incluído no processo de PR

⚠️ Não criar schemas por tenant ainda (MVP usa apenas shared DB)
⚠️ Não implementar anonimização ainda (só cancelamento simples)
```

### 15.2 Fase 2 — Pós-MVP (Mês 2-3)

```
[ ] Schema por tenant para farmácia (prescriptions)
[ ] Anonimização de dados (job com 90 dias)
[ ] Exportação de dados para o lojista
[ ] Dashboard de isolamento para admin
[ ] Alertas de segurança (query sem merchant_id)
[ ] Backup e restore testado mensalmente
```

### 15.3 Fase 3 — Escala (Mês 4+)

```
[ ] Read replicas para analytics
[ ] Partitioning de tabelas grandes (orders por mês)
[ ] PgBouncer para pool de conexões
[ ] Sharding (se necessário)
[ ] Opção de dedicated database para enterprise
```

---

## 16. Cobertura de Testes

### 16.1 Testes de Isolamento (Críticos)

```python
# Estes testes são OBRIGATÓRIOS e bloqueiam deploy se falharem.

async def test_merchant_a_cannot_see_merchant_b_orders():
    """Lojista A não vê pedidos do lojista B."""
    # Arrange
    merchant_a = await create_merchant()
    merchant_b = await create_merchant()
    order_b = await create_order(merchant_b)

    # Act
    repo = OrderRepository(db, merchant_id=merchant_a.id)
    orders = await repo.get_orders()

    # Assert
    assert order_b.id not in [o.id for o in orders]

async def test_merchant_a_cannot_see_merchant_b_products():
    """Lojista A não vê produtos do lojista B."""
    ...

async def test_merchant_a_cannot_see_merchant_b_customers():
    """Lojista A não vê clientes do lojista B."""
    ...

async def test_merchant_a_cannot_see_merchant_b_riders():
    """Lojista A não vê entregadores do lojista B."""
    ...

async def test_merchant_a_cannot_see_merchant_b_invoices():
    """Lojista A não vê faturas do lojista B."""
    ...
```

### 16.2 Testes de Autenticação

```python
async def test_merchant_id_from_jwt_not_from_body():
    """merchant_id no body/query é ignorado — o do JWT prevalece."""
    # Tenta enviar merchant_id de outro lojista no body
    response = await client.post(
        "/api/v1/orders",
        json={"merchant_id": 9999, "product": "pizza"},
        headers={"Authorization": f"Bearer {token_lojista_42}"},
    )
    # O pedido deve ser criado para o lojista 42, não 9999
    order = response.json()
    assert order["merchant_id"] == 42

async def test_admin_can_access_all_tenants():
    """Admin consegue acessar dados de qualquer lojista."""
    ...

async def test_admin_access_is_logged():
    """Acesso de admin a dados de tenant fica registrado no audit log."""
    ...
```

### 16.3 Testes de RLS

```python
async def test_rls_blocks_cross_tenant_query():
    """RLS bloqueia query que não filtra por merchant_id."""
    # Simular conexão sem configurar merchant_id
    async with db_session as conn:
        await conn.execute(text("SET app.current_merchant_id = 0"))
        await conn.execute(text("SET app.is_admin = false"))
        await conn.execute(text("SET ROLE rapidrop_app"))

        # Tentar buscar todos os pedidos (sem where)
        with pytest.raises(Exception):  # RLS deve bloquear ou retornar vazio
            result = await conn.execute(text("SELECT * FROM orders"))

async def test_rls_allows_own_tenant():
    """RLS permite acesso do próprio tenant."""
    ...

async def test_rls_bypass_for_admin():
    """Admin consegue bypassar RLS (role rapidrop_admin)."""
    ...
```

### 16.4 Testes de LGPD

```python
async def test_anonymization_removes_pii():
    """Anonimização remove dados pessoais mas mantém registros financeiros."""
    merchant_id = 42
    await anonymize_merchant_data(merchant_id)

    merchant = await db.get(Merchant, merchant_id)
    assert merchant.business_name != "Pizzaria do Norte"
    assert merchant.email != "contato@pizzaria.com"
    assert merchant.is_anonymized == True

    # Dados financeiros ainda existem
    invoices = await db.execute(
        text(f"SELECT * FROM invoices WHERE merchant_id = {merchant_id}")
    )
    assert invoices.rowcount > 0  # faturas mantidas

async def test_cancelled_merchant_cannot_login():
    """Lojista cancelado não consegue fazer login."""
    ...

async def test_data_export_contains_all_categories():
    """Exportação de dados inclui todas as categorias obrigatórias."""
    ...
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Baseado nos documentos:** `docs/stack-completa.md`, `docs/analise-dados.md`,
> `docs/maquina-estados-pedido.md`, `docs/fluxo-financeiro.md`
