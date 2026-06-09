# RapiDrop — Sistema de Pagamento de Entregadores

> Modelo de remuneração configurável por dia trabalhado ou por entrega realizada,
> com estratégias de ranqueamento para bonificação por performance.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Métodos de Pagamento](#2-métodos-de-pagamento)
3. [Estratégias por Método](#3-estratégias-por-método)
4. [Sistema de Ranqueamento](#4-sistema-de-ranqueamento)
5. [Regras de Acumulação e Conflito](#5-regras-de-acumulação-e-conflito)
6. [Fluxos de Usuário](#6-fluxos-de-usuário)
7. [Modelagem de Dados](#7-modelagem-de-dados)
8. [Extrato e Pagamento](#8-extrato-e-pagamento)

---

## 1. Visão Geral

O lojista precisa de flexibilidade para remunerar seus entregadores de forma justa e estratégica. O sistema de pagamento do RapiDrop permite:

- **Escolher o método**: por dia trabalhado, por entrega realizada, ou híbrido
- **Configurar a estratégia**: regras de cálculo dentro de cada método
- **Ranquear por performance**: bônus baseados em métricas reais
- **Automatizar o cálculo**: extrato gerado automaticamente para acerto de contas

### 1.1 Conceitos-Chave

| Conceito | Definição |
|----------|-----------|
| **Método de Pagamento** | A forma base de remuneração (diária ou por entrega) |
| **Estratégia** | As regras de cálculo dentro de cada método |
| **Ranqueamento** | Classificação periódica dos entregadores por métricas de performance |
| **Bônus** | Valor extra distribuído com base na posição do ranking |
| **Período de Cálculo** | Intervalo de tempo para fechamento (semanal, quinzenal, mensal) |

---

## 2. Métodos de Pagamento

O lojista configura **um método principal** para seu estabelecimento.
Os métodos são mutuamente exclusivos como base, mas podem ter complementos.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MÉTODOS DE PAGAMENTO                         │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │   POR DIA        │  │  POR ENTREGA     │  │   HÍBRIDO     │  │
│  │   TRABALHADO     │  │  REALIZADA       │  │               │  │
│  ├──────────────────┤  ├──────────────────┤  ├───────────────┤  │
│  │ R$ X por dia     │  │ R$ Y por entrega │  │ Diária + taxa │  │
│  │ + bônus ranking  │  │ + bônus ranking  │  │ por entrega   │  │
│  └──────────────────┘  └──────────────────┘  └───────────────┘  │
│                                                                 │
│  Em todos os métodos:                                           │
│  - Bônus de ranqueamento (opcional, configurável)               │
│  - Adicional noturno / fim de semana (opcional)                 │
│  - Taxa mínima por período (opcional)                           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Por Dia Trabalhado

O entregador recebe um valor fixo por cada dia que trabalha, independente do número de entregas.

**Quando usar:**
- Lojista quer fidelizar entregadores com renda previsível
- Períodos de baixo movimento (o entregador não é prejudicado)
- Entregadores em regime de dedicação exclusiva

**Regras base:**
- Valor fixo por dia (ex: R$ 80,00/dia)
- Vinculado à presença: entregador precisa ficar online por X horas
- Mínimo de entregas para garantir a diária (ex: mínimo 5 entregas)
- Se não atingir o mínimo, recebe proporcional ou por entrega

### 2.2 Por Entrega Realizada

O entregador recebe por cada entrega concluída.

**Quando usar:**
- Lojista com volume alto e variável de pedidos
- Entregadores que preferem ser remunerados por produtividade
- Entregadores de meio-período ou horário flexível

### 2.3 Híbrido (Diária + Taxa por Entrega)

Combina os dois métodos: uma base fixa por dia + um valor variável por entrega.

**Quando usar:**
- Lojista quer garantir uma renda mínima ao entregador
- Mas também incentivar produtividade com taxa extra por entrega

---

## 3. Estratégias por Método

Cada método de pagamento possui estratégias de cálculo configuráveis.

### 3.1 Estratégias para "Por Dia Trabalhado"

| Estratégia | Descrição | Exemplo |
|------------|-----------|---------|
| **Diária Fixa** | Valor fixo independente do número de entregas | R$ 80/dia |
| **Diária com Meta Mínima** | Valor fixo, mas exige entregas mínimas para receber | R$ 80/dia (mín. 8 entregas) |
| **Diária Progressiva** | Aumenta conforme dias consecutivos trabalhados | 1º dia: R$ 60, 2º: R$ 70, 5º+: R$ 100 |
| **Diária por Turno** | Valor diferente para cada turno (manhã/tarde/noite) | Manhã: R$ 50, Noite: R$ 80 |
| **Diária + Adicional por Hora Extra** | Diária fixa + adicional por hora além da jornada | R$ 70/dia + R$ 10/h extra |

**Exemplo de configuração no sistema:**

```json
{
  "method": "daily_rate",
  "strategy": "fixed_with_minimum",
  "daily_rate_cents": 8000,
  "currency": "BRL",
  "minimum_deliveries": 8,
  "minimum_hours_online": 6,
  "weekend_bonus_cents": 2000,
  "night_shift_bonus_cents": 1500,
  "night_shift_start": "20:00",
  "night_shift_end": "06:00",
  "consecutive_day_bonus": {
    "enabled": true,
    "day_2_cents": 500,
    "day_3_cents": 1000,
    "day_5_cents": 2000,
    "day_7_cents": 3000
  }
}
```

### 3.2 Estratégias para "Por Entrega Realizada"

| Estratégia | Descrição | Exemplo |
|------------|-----------|---------|
| **Taxa Fixa por Entrega** | Mesmo valor para qualquer entrega | R$ 5,00/entrega |
| **Taxa por Distância** | Valor base + adicional por km rodado | R$ 4,00 + R$ 0,50/km |
| **Taxa por Valor do Pedido** | Percentual sobre o valor total do pedido | 5% do valor do pedido |
| **Taxa por Faixa de Entregas** | Valor aumenta conforme o entregador faz mais entregas no período | 1-10 entregas: R$ 4,00. 11-20: R$ 5,00. 21+: R$ 6,00 |
| **Taxa por Complexidade** | Valor maior para entregas especiais | Normal: R$ 5,00. Refrigeração: R$ 7,00. Frágil: R$ 6,00 |
| **Taxa por Região** | Valor diferente por bairro/região | Bairro A: R$ 5,00. Bairro B (distante): R$ 8,00 |

**Exemplo de configuração no sistema:**

```json
{
  "method": "per_delivery",
  "strategy": "tiered_by_volume",
  "base_rate_cents": 500,
  "tiers": [
    { "min_deliveries": 0,  "rate_cents": 400 },
    { "min_deliveries": 10, "rate_cents": 500 },
    { "min_deliveries": 30, "rate_cents": 600 },
    { "min_deliveries": 50, "rate_cents": 750 }
  ],
  "distance_rate_cents_per_km": 50,
  "distance_rate_enabled": true,
  "percentage_rate_enabled": false,
  "percentage_rate": 0.0,
  "complexity_bonus": {
    "refrigeration_cents": 200,
    "heavy_cents": 150,
    "fragile_cents": 100,
    "pharmacy_prescription_cents": 300
  },
  "region_bonus": [
    { "region": "zona_norte", "additional_cents": 300 },
    { "region": "zona_sul",   "additional_cents": 200 },
    { "region": "centro",     "additional_cents": 0 }
  ],
  "weekend_bonus_cents": 200,
  "night_shift_bonus_cents": 150,
  "tier_reset": "weekly"
}
```

### 3.3 Configuração Híbrida

```json
{
  "method": "hybrid",
  "daily_rate_cents": 4000,
  "per_delivery_rate_cents": 300,
  "minimum_deliveries_for_daily": 5,
  "daily_rate_weekend_bonus_cents": 1000,
  "per_delivery_weekend_bonus_cents": 100,
  "ranking_bonus_enabled": true
}
```

---

## 4. Sistema de Ranqueamento

O ranking é uma camada opcional que incentiva a competição saudável e recompensa os melhores entregadores.

### 4.1 Como Funciona

```
┌─────────────────────────────────────────────────────────────────┐
│  PERÍODO DE RANQUEAMENTO (ex: semanal)                          │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Entrega │  │ Entrega │  │ Entrega │  │ Entrega │  ...       │
│  │  #1     │  │  #2     │  │  #3     │  │  #4     │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       └────────────┴────────────┴────────────┘                  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              CÁLCULO DO RANKING                           │   │
│  │                                                           │   │
│  │  Score = (entregas × 0.4) + (pontualidade × 0.3)         │   │
│  │        + (avaliação × 0.2) + (aceitação × 0.1)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  RANKING SEMANAL                                          │   │
│  │  🥇 1º → R$ 150 de bônus                                  │   │
│  │  🥈 2º → R$ 100 de bônus                                  │   │
│  │  🥉 3º → R$ 50 de bônus                                   │   │
│  │  4º-10º → R$ 20 de bônus                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Métricas de Ranqueamento

O lojista escolhe quais métricas entram no cálculo e seus pesos.

| Métrica | Descrição | Peso sugerido |
|---------|-----------|---------------|
| **Entregas Realizadas** | Número total de entregas no período | 40% |
| **Pontualidade** | % de entregas feitas dentro do prazo estimado | 30% |
| **Avaliação Média** | Nota média recebida dos clientes (1-5) | 20% |
| **Taxa de Aceitação** | % de pedidos aceitos vs. recebidos | 10% |
| **Distância Percorrida** | Km totais rodados (para quem faz entregas mais longas) | Peso extra |
| **Horas Online** | Tempo total disponível para entregas | Peso extra |
| **Reclamações** | Quantidade de reclamações recebidas (dedução) | Redutor |

**Fórmula de Cálculo:**

```
Score = (entregas_normalizadas × peso_entregas)
      + (pontualidade × peso_pontualidade)
      + (avaliacao_normalizada × peso_avaliacao)
      + (aceitacao × peso_aceitacao)
      - (reclamacoes × peso_reclamacao)
```

> Onde `entregas_normalizadas` = entregas_do_rider / maior_entrega_do_periodo
> e `avaliacao_normalizada` = (avaliacao_do_rider - 1) / 4

### 4.3 Distribuição de Bônus

O lojista pode escolher entre dois modelos de distribuição:

#### A) Bônus Fixo por Posição

| Posição | Bônus |
|---------|-------|
| 🥇 1º lugar | R$ 200,00 |
| 🥈 2º lugar | R$ 120,00 |
| 🥉 3º lugar | R$ 80,00 |
| 4º ao 10º | R$ 30,00 |
| 11º ao 20º | R$ 15,00 |

#### B) Pool de Bônus Rateado

O lojista define um valor total do pool (ex: R$ 1.000,00/semana) e o sistema distribui proporcionalmente ao score:

```
Entregador A: score 85 → recebe (85 / soma_dos_scores) × pool_total
Entregador B: score 62 → recebe (62 / soma_dos_scores) × pool_total
Entregador C: score 41 → recebe (41 / soma_dos_scores) × pool_total
```

#### C) Bônus por Meta (Individual)

Cada entregador ganha um bônus se atingir metas individuais, independente dos outros:

| Meta | Bônus |
|------|-------|
| Fazer 50+ entregas na semana | R$ 40,00 |
| Manter avaliação ≥ 4.8 | R$ 30,00 |
| 0 reclamações na semana | R$ 20,00 |
| 100% de pontualidade | R$ 25,00 |

### 4.4 Períodos de Ranqueamento

| Período | Quando calcular | Quando pagar |
|---------|----------------|--------------|
| **Semanal** | Segunda-feira 00h | Junto com o acerto semanal |
| **Quinzenal** | Dias 1 e 16 | Acerto quinzenal |
| **Mensal** | Dia 1 de cada mês | Acerto mensal |
| **Personalizado** | Configurado pelo lojista | Conforme configurado |

### 4.5 Dashboard do Ranking (Lojista)

O lojista vê em tempo real a classificação dos entregadores:

```
┌─────────────────────────────────────────────────────────────────┐
│  RANKING DE ENTREGADORES — Esta Semana                          │
│  Período: 01/06 a 07/06     🏆 Pool de bônus: R$ 500,00        │
├─────────────────────────────────────────────────────────────────┤
│  #  Entregador    Entrega  Pontual  Aval  Aceit  Score   Bônus  │
│  ─────────────────────────────────────────────────────────────  │
│  1  🥇 Jefferson    42      97%     4.9    95%    92.3   R$ 200 │
│  2  🥈 Marcio       38      95%     4.8    92%    86.1   R$ 120 │
│  3  🥉 Luana        35      100%    4.7    98%    83.5   R$ 80  │
│  4  Rodrigo         30      92%     4.6    90%    72.4   R$ 30  │
│  5  Pedro           28      88%     4.5    85%    65.8   R$ 30  │
│  6  Amanda          25      90%     4.8    88%    62.1   R$ 30  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Regras de Acumulação e Conflito

### 5.1 O que acumula?

| Combinação | Acumula? | Regra |
|------------|----------|-------|
| Diária + bônus de ranking | ✅ Sim | Bônus é extra, independente do método |
| Taxa por entrega + bônus de ranking | ✅ Sim | Bônus é extra |
| Diária + adicional noturno | ✅ Sim | Adicional é somado à diária |
| Taxa por entrega + adicional noturno | ✅ Sim | Adicional por entrega em horário noturno |
| Taxa por distância + taxa por valor | ✅ Sim | Ambas são somadas por entrega |
| Taxa por faixa + bônus de complexidade | ✅ Sim | Bônus de complexidade é extra |
| Diária + taxa por entrega (híbrido) | ✅ Sim | Recebe ambos |
| Mínimo de entregas não atingido + diária | ❌ Não | Se não atingiu mínimo, pode perder diária |

### 5.2 Regras de Transição

- Se o lojista **mudar o método** (ex: de "por dia" para "por entrega"), a mudança vale apenas para o próximo período de cálculo
- Entregadores são **notificados** da mudança com 7 dias de antecedência
- O histórico de períodos anteriores é preservado com o método vigente na época

### 5.3 Regras de Elegibilidade para Ranking

- Mínimo de 10 entregas no período para entrar no ranking
- Se o entregador teve reclamação grave (definido pelo lojista), é desclassificado
- Entregador precisa ter trabalhado pelo menos 3 dias no período

---

## 6. Fluxos de Usuário

### 6.1 Fluxo do Lojista — Configuração Inicial

```
[Menu: Entregadores > Configurar Pagamento]
    │
    ▼
[Escolhe método principal]
    ├── 💰 Por dia trabalhado
    ├── 📦 Por entrega realizada
    └── 🔀 Híbrido (diária + taxa por entrega)
    │
    ▼
[Configura estratégia do método escolhido]
    │
    ▼
[Define valores, faixas, bônus, adicionais]
    │
    ▼
[Configura ranking]
    ├── Ativar ranking? Sim/Não
    ├── Período: Semanal / Quinzenal / Mensal
    ├── Métricas e pesos
    └── Modelo de bônus: Fixo / Pool / Metas
    │
    ▼
[Revisa resumo da configuração]
    │
    ▼
[Salva → Notifica entregadores via WhatsApp]
```

### 6.2 Fluxo do Entregador — Visualização

```
[App do entregador > Menu > Meus Ganhos]
    │
    ▼
[Resumo do período atual]
    ├── Método: Por entrega + bônus ranking
    ├── Entregas no período: 38
    ├── Posição no ranking: 🥇 1º
    ├── Ganho base estimado: R$ 190,00
    ├── Bônus ranking estimado: R$ 200,00
    └── Total estimado: R$ 390,00
    │
    ▼
[Detalhamento por entrega]
    ├── #42 - Pizza - 3km - R$ 5,00 + R$ 0,50 (dist) = R$ 5,50
    ├── #43 - Remédio - 2km - R$ 5,00 + R$ 2,00 (refrig) = R$ 7,00
    └── ...
    │
    ▼
[Detalhamento da diária (se aplicável)]
    ├── Seg: R$ 80,00 (8 entregas) ✅
    ├── Ter: R$ 60,00 (5 entregas - mínimo não atingido) ⚠️
    └── ...
```

### 6.3 Fluxo de Fechamento e Acerto

```
[Fim do período de cálculo]
    │
    ▼
[Sistema calcula automaticamente:
    - Ganho base por método
    - Adicionais (noturno, fds, complexidade)
    - Bônus de ranking
    - Total por entregador]
    │
    ▼
[Sistema gera extrato para cada entregador]
    │
    ▼
[Lojista revisa e aprova (ou ajusta manualmente)]
    │
    ▼
[Extrato é enviado para o entregador via WhatsApp/App]
    │
    ▼
[Lojista realiza pagamento (PIX, dinheiro, transferência)]
    │
    ▼
[Lojista marca como "Pago" no sistema]
```

---

## 7. Modelagem de Dados

### 7.1 Tabelas Principais

```sql
-- Configuração de pagamento do estabelecimento
rider_payment_config
├── id: uuid PK
├── merchant_id: uuid FK NOT NULL
├── method: enum('daily_rate', 'per_delivery', 'hybrid') NOT NULL
├── strategy: varchar(50) NOT NULL  -- ex: 'fixed_with_minimum', 'tiered_by_volume'
├── config: jsonb NOT NULL  -- configuração completa (ver exemplos na seção 3)
├── ranking_enabled: boolean DEFAULT false
├── ranking_period: enum('weekly', 'biweekly', 'monthly') DEFAULT 'weekly'
├── ranking_metrics_config: jsonb  -- pesos e métricas
│   └── [
│         {"metric": "deliveries", "weight": 0.4},
│         {"metric": "on_time_rate", "weight": 0.3},
│         {"metric": "rating", "weight": 0.2},
│         {"metric": "acceptance_rate", "weight": 0.1}
│       ]
├── ranking_bonus_model: enum('fixed_position', 'pool', 'individual_goals')
├── ranking_bonus_config: jsonb
│   └── "fixed_position": { "1": 20000, "2": 12000, "3": 8000, "4-10": 3000 }
│   └── "pool": { "total_pool_cents": 100000 }
│   └── "individual_goals": { "deliveries_50": 4000, "rating_48": 3000, "no_complaints": 2000 }
├── min_deliveries_for_ranking: int DEFAULT 10
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Extrato individual do entregador por período
rider_payment_period
├── id: uuid PK
├── merchant_id: uuid FK
├── rider_id: uuid FK NOT NULL
├── period_start: date NOT NULL
├── period_end: date NOT NULL
├── method: enum('daily_rate', 'per_delivery', 'hybrid') NOT NULL
├── status: enum('calculating', 'pending_approval', 'approved', 'paid', 'cancelled')
│
├── base_amount_cents: int  -- ganho base do método
├── additional_cents: int  -- adicionais noturno/fds/complexidade
├── ranking_bonus_cents: int  -- bônus de ranking
├── ranking_position: int  -- posição no ranking (nullable)
├── total_cents: int  -- soma total
│
├── metrics_snapshot: jsonb  -- métricas congeladas no momento do cálculo
│   └── { "deliveries": 42, "on_time_rate": 0.97, "rating": 4.9, "aceptance_rate": 0.95 }
│
├── delivery_breakdown: jsonb  -- detalhamento por entrega
│   └── [
│         { "order_id": 42, "amount_cents": 550, "note": "Pizza - 3km" },
│         { "order_id": 43, "amount_cents": 700, "note": "Remédio - 2km + refrig" }
│       ]
│
├── paid_at: timestamptz
├── payment_method: varchar(50)  -- pix, dinheiro, transferência
├── payment_proof: text  -- comprovante (opcional)
│
├── approved_by: uuid FK (merchant_user)
├── approved_at: timestamptz
├── created_at: timestamptz
└── notes: text

-- Histórico de alterações na configuração (audit trail)
rider_payment_config_log
├── id: uuid PK
├── merchant_id: uuid FK
├── changed_by: uuid FK (merchant_user)
├── old_config: jsonb
├── new_config: jsonb
├── change_reason: text
└── created_at: timestamptz

-- Eventos de pagamento (cada lançamento individual)
rider_payment_event
├── id: uuid PK
├── rider_payment_period_id: uuid FK
├── rider_id: uuid FK
├── type: enum('delivery', 'daily_rate', 'additional', 'ranking_bonus', 'adjustment')
├── reference_id: varchar(100)  -- order_id, period_id, etc
├── amount_cents: int
├── description: text
└── created_at: timestamptz
```

### 7.2 Índices Recomendados

```sql
-- Consulta principal: extrato do entregador
CREATE INDEX idx_rider_period_rider_dates ON rider_payment_period (rider_id, period_start DESC);

-- Consulta do lojista: fechamento por período
CREATE INDEX idx_rider_period_merchant_dates ON rider_payment_period (merchant_id, period_start DESC);

-- Ranking: buscar todos os entregadores de um período ordenados
CREATE INDEX idx_rider_period_merchant_ranking ON rider_payment_period (merchant_id, period_start, total_cents DESC)
  WHERE status = 'approved';

-- Única config ativa por merchant
CREATE UNIQUE INDEX idx_one_active_config ON rider_payment_config (merchant_id) WHERE is_active = true;
```

---

## 8. Extrato e Pagamento

### 8.1 Exemplo de Extrato (WhatsApp / App)

```
═══════════════════════════════════════
  RapiDrop — Extrato de Pagamento
  🏪 Pizzaria do Ricardo
═══════════════════════════════════════
  Entregador: Jefferson
  Período: 01/06 a 07/06
  Método: Por entrega + ranqueamento
─────────────────────────────────────
  📦 Entregas realizadas:  42
  💰 Taxa base (42 × R$5):  R$ 210,00
  🚗 Taxa de distância:      R$ 42,00
  🌙 Adicional noturno:      R$ 12,00
  ─────────────────────────────────────
  ✅ Total base:             R$ 264,00
─────────────────────────────────────
  🏆 RANKING SEMANAL
  🥇 1º lugar de 6 entregadores
  ─────────────────────────────────────
  🎯 Bônus 1º lugar:        R$ 200,00
  ⭐ Bônus avaliação 4.9:   R$ 30,00
─────────────────────────────────────
  💵 TOTAL DO PERÍODO:      R$ 494,00
═══════════════════════════════════════
```

### 8.2 Funcionalidades do Módulo de Pagamento

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Configuração de Método** | Escolher entre diária, por entrega, ou híbrido | P0 |
| **Estratégias de Cálculo** | Fixa, faixa, distância, percentual, complexidade | P0 |
| **Cálculo Automático** | Sistema calcula automaticamente ao final do período | P0 |
| **Extrato para Entregador** | Detalhamento visível no app e enviado por WhatsApp | P0 |
| **Aprovação do Lojista** | Lojista revisa e aprova antes de finalizar | P1 |
| **Ranking Automático** | Cálculo do score e distribuição de bônus | P1 |
| **Dashboard do Ranking** | Visualização ao vivo da classificação | P1 |
| **Notificação de Mudança** | Avisar entregadores quando config mudar | P1 |
| **Pagamento por PIX** | Integração com gateway para pagamento automático | P2 |
| **Relatório Fiscal** | Exportação dos valores pagos para contabilidade | P2 |
| **Histórico de Configurações** | Audit trail de todas as mudanças | P2 |
| **Múltiplos Métodos por Estabelecimento** | Diferentes grupos de entregadores com métodos diferentes | P2 |

---

## 9. Regras de Negócio — Resumo

1. **Cada lojista tem uma configuração de pagamento ativa**
2. **Todo entregador do mesmo lojista segue a mesma regra** (simplifica gestão)
3. **Mudanças de método só valem para o próximo período** (nunca retroativo)
4. **Entregador precisa de no mínimo X entregas para entrar no ranking**
5. **Bônus de ranking é sempre extra** — nunca substitui o ganho base
6. **Extrato precisa ser aprovado pelo lojista** antes de virar débito
7. **Histórico de configurações é preservado** para auditoria
8. **Entregador vê seu ganho em tempo real** no app (estimado até o fechamento)

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Nota:** Este documento especifica o sistema de pagamento de entregadores do RapiDrop.
> Deve ser usado como referência para implementação dos módulos de `riders` e `payments`.
