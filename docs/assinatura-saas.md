# RapiDrop — Modelo de Assinatura SaaS

> Modelo de cobrança por percentual sobre cada pedido, com opção de migração
> para mensalidade fixa após 12 meses, calculada pelo histórico de vendas.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Fase 1 — Percentual por Pedido](#2-fase-1--percentual-por-pedido)
3. [Fase 2 — Escolha: Percentual ou Mensalidade Fixa](#3-fase-2--escolha-percentual-ou-mensalidade-fixa)
4. [Cálculo da Mensalidade Fixa](#4-cálculo-da-mensalidade-fixa)
5. [Regras de Transição e Reversão](#5-regras-de-transição-e-reversão)
6. [Fluxo de Cobrança](#6-fluxo-de-cobrança)
7. [Modelagem de Dados](#7-modelagem-de-dados)
8. [Comparativo de Cenários](#8-comparativo-de-cenários)
9. [Summary para o Lojista](#9-summary-para-o-lojista)

---

## 1. Visão Geral

O RapiDrop adota um modelo de cobrança em **duas fases** que equilibra baixa barreira de entrada com receita previsível para o SaaS.

```
LINHA DO TEMPO DA ASSINATURA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  MÊS 0                          MÊS 12                     MÊS 13+
  ┌──────────────────────────────┬──────────────────────────────┐
  │                              │                              │
  │   FASE 1                     │   FASE 2 (ESCOLHA)          │
  │                              │                              │
  │   % sobre cada pedido        │   ┌─ Opção A: continuar %   │
  │   Sem mensalidade fixa       │   ├─ Opção B: mensalidade   │
  │   Sem fidelidade             │   │   fixa calculada pelo   │
  │                              │   │   histórico             │
  │   ─────────────────────      │   └──────────────────────────│
  │   • 0% meses 1-2 (cortesia)  │                              │
  │   • % cheia a partir mês 3   │   Reajuste anual: IPCA/IGPM │
  │                              │   + revisão a cada 12 meses │
  └──────────────────────────────┴──────────────────────────────┘
```

### 1.1 Princípios do Modelo

| Princípio | Por quê? |
|-----------|----------|
| **Barreira zero de entrada** | Lojista começa sem custo fixo — paga apenas quando vende. Reduz atrito no trial. |
| **Alinhamento de incentivos** | RapiDrop ganha quando o lojista vende. Se o lojista cresce, nós crescemos juntos. |
| **Previsibilidade futura** | Após 12 meses, o lojista pode optar por custo previsível (mensalidade fixa). |
| **Proteção ao SaaS** | A mensalidade fixa é calculada para que o RapiDrop não perda receita com a migração. |
| **Simplicidade** | Uma única métrica (percentual por pedido) durante o primeiro ano. Sem planos, sem limites. |

---

## 2. Fase 1 — Percentual por Pedido

### 2.1 Como Funciona

O lojista paga **um percentual sobre o valor total de cada pedido** processado pelo RapiDrop.

```
Exemplo:
  Pedido: R$ 100,00
  Taxa:   2%
  ─────────────────
  Cobrado: R$ 2,00 por pedido
```

### 2.2 Tabela de Percentuais por Segmento

| Segmento | Taxa por Pedido | Justificativa |
|----------|----------------:|---------------|
| **Alimentação** | 2,0% | Ticket médio mais baixo (~R$ 35-50), maior volume |
| **Farmácia** | 1,5% | Ticket médio mais alto (~R$ 60-90), menor volume |
| **Mercado** | 1,5% | Ticket médio alto (~R$ 80-150), margem menor do lojista |

### 2.3 Isenção Inicial (Cortesia)

Os primeiros **2 meses** são isentos de taxa para incentivar a adoção:

| Mês | Taxa | Motivo |
|-----|:----:|--------|
| Mês 1 | 0% | Cortesia — lojista aprende o sistema |
| Mês 2 | 0% | Cortesia — lojista valida o sistema com clientes reais |
| Mês 3+ | % cheia | Início da cobrança normal |

> **Nota:** Pedidos cancelados ou reembolsados **não** geram cobrança.

### 2.4 Limites por Conta (Anti-abuso)

Para evitar uso abusivo do período de taxa zero:

- Máximo de **500 pedidos** no período de cortesia (mêses 1-2)
- Após 500 pedidos, a taxa passa a valer mesmo antes de completar 2 meses
- Lojistas com CNPJ diferente não podem criar múltiplas contas para perpetuar o trial

### 2.5 Cálculo da Cobrança

```
Valor a cobrar = Σ (valor_total_do_pedido × percentual_do_segmento)

Onde:
  - valor_total_do_pedido = subtotal + taxa_de_entrega - descontos
  - gorjetas NÃO entram no cálculo (são 100% do entregador)
  - pedidos cancelados NÃO entram no cálculo
  - pedidos reembolsados geram crédito na próxima fatura
```

### 2.6 Faturamento na Fase 1

A cobrança é **mensal**, consolidando todos os pedidos do mês anterior:

```
Fatura do mês (ex: Julho)
  ┌──────────────────────────────────────────────┐
  │  Período: 01/07 a 31/07                       │
  │                                               │
  │  Total de pedidos: 142                        │
  │  Valor total dos pedidos: R$ 7.835,00        │
  │  Taxa aplicada: 2,0%                          │
  │                                               │
  │  Total a pagar: R$ 156,70                    │
  │                                               │
  │  Vencimento: 10/08                            │
  └──────────────────────────────────────────────┘
```

---

## 3. Fase 2 — Escolha: Percentual ou Mensalidade Fixa

Ao completar **12 meses**, o lojista recebe uma notificação para escolher seu regime de cobrança para os próximos 12 meses.

### 3.1 Opção A — Continuar no Percentual

O lojista **continua pagando o mesmo percentual por pedido** (2% / 1,5%) indefinidamente.

**Vantagem para o lojista:** Se o volume de pedidos cair, ele paga menos.
**Vantagem para o SaaS:** Se o volume subir, a receita acompanha.

### 3.2 Opção B — Migrar para Mensalidade Fixa

O lojista passa a pagar **um valor fixo por mês**, calculado com base no histórico do último ano.

**Vantagem para o lojista:** Previsibilidade de custos. Ideal para quem tem sazonalidade e quer planejar fluxo de caixa.
**Vantagem para o SaaS:** Receita recorrente previsível. Reduz a variabilidade mensal.

**Flexibilidade total:** O lojista pode **voltar ao modelo percentual a qualquer momento** — sem multa, sem período mínimo, sem burocracia. A mudança entra em vigor no mês seguinte.

### 3.3 Quando a Opção é Apresentada

```
[Mês 11]  ─── Sistema envia notificação: "Em 30 dias você poderá escolher seu plano!"
[Mês 12]  ─── Lojista acessa painel e vê as duas opções com simulação
           ─── Tem 30 dias para decidir (até mês 13)
[Mês 13]  ─── Se não escolher, continua no percentual (default)
```

### 3.4 Simulação Apresentada ao Lojista

```
═══════════════════════════════════════════════════════
  🎉 Parabéns por 1 ano de RapiDrop!
═══════════════════════════════════════════════════════
  Seu restaurante processou 1.680 pedidos no último ano.
  Seus dados de cobrança:

  Total de taxas pagas no ano:     R$ 1.876,00
  Média mensal:                    R$ 156,33
  Média dos últimos 6 meses:       R$ 182,40

  ─────────────────────────────────────────────────────
  📊 Opção 1 — Continuar no percentual
     Pagará 2% sobre cada pedido (sem mensalidade)
     ⚠️ Valor varia conforme suas vendas

  📊 Opção 2 — Mensalidade Fixa
     R$ 182,40/mês (valor dos últimos 6 meses)
     ✅ Previsível — mesmo valor todo mês
     ✅ Reajuste anual por IPCA
     🔒 Fixo por 12 meses

  Sua escolha: [ Continuar no percentual ] [ Migrar para Fixa ]
═══════════════════════════════════════════════════════
```

---

## 4. Cálculo da Mensalidade Fixa

### 4.1 Cálculo Inicial (Mês 13)

Quando o lojista opta pela mensalidade fixa no mês 13, o valor é calculado com base no **histórico real de pedidos dos últimos 12 meses** (mêses 1 a 12).

```
Mensalidade Fixa = max(
    média_12_meses,
    média_6_meses_mais_recentes
)

Onde:
  média_12_meses = Σ (taxas_que_teriam_sido_cobradas_no_ano) / 12
  média_6_meses_mais_recentes = Σ (taxas_meses_7_a_12) / 6
```

> **Não há buffer adicional.** A proteção ao SaaS está na própria fórmula: a mensalidade usa a maior média e cobre exatamente o que o modelo percentual teria gerado.

### 4.2 Por que Usar a Maior das Duas Médias?

Usar `max(média_12_meses, média_6_meses)` protege o SaaS em dois cenários:

| Cenário | Média 12 meses | Média 6 meses | Usada | Motivo |
|---------|:--------------:|:-------------:|:-----:|--------|
| **Crescimento** (lojista que cresceu) | R$ 100 | **R$ 150** | R$ 150 | O lojista cresceu — usar a média mais recente |
| **Estabilidade** (vendas constantes) | **R$ 120** | R$ 118 | R$ 120 | Praticamente iguais — usar a maior |
| **Queda recente** (lojista que caiu) | **R$ 130** | R$ 90 | R$ 130 | Usar a média do ano completo (mais justa) |

Isso garante que:
- Se o lojista **cresceu** no período recente, a mensalidade reflete o volume atual
- Se o lojista **caiu** recentemente, não penalizamos o SaaS com uma queda abrupta
- Em ambos os casos, o SaaS **não perde receita** com a migração

### 4.3 Revisão Anual Obrigatória — A Garantia do SaaS

A cada **12 meses** (sempre no mês de aniversário da migração para o fixo), o valor é **automaticamente recalculado** usando os **pedidos reais dos últimos 12 meses**.

```
Novo valor = max(
    média_12_meses_do_percentual_simulado,
    média_6_meses_mais_recentes_do_percentual_simulado
)
```

Isto é: mesmo que o lojista esteja no regime fixo, olhamos para **todos os pedidos que ele processou nos últimos 12 meses** e calculamos **quanto o RapiDrop teria faturado se ele estivesse no percentual**. A mensalidade do próximo ano será no mínimo esse valor.

**Isso garante que o dono do SaaS nunca perde** — porque mesmo que o lojista tenha crescido muito durante o ano no fixo, o reajuste anual captura esse crescimento e ajusta a mensalidade para o próximo período.

> ⚠️ **Importante:** Todos os pedidos são registrados no sistema, independente do regime de cobrança. Isso permite calcular o "contrafactual" — o que seria cobrado no percentual — a qualquer momento.

### 4.4 Reajuste pela Inflação (IPCA)

Além da revisão anual pelo volume de pedidos, o valor também é corrigido pela inflação:

```
Reajuste Anual = IPCA (ou IGPM) acumulado dos últimos 12 meses
```

O reajuste pela inflação é aplicado **separadamente** da revisão por volume:
1. Primeiro calcula-se o novo valor base pelo histórico de pedidos (seção 4.3)
2. Depois aplica-se o IPCA sobre esse novo valor

- Limitado ao teto de **15%** (para proteger o lojista em anos de inflação alta)
- O lojista é notificado com 30 dias de antecedência

### 4.5 Exemplos Completos

#### Exemplo 1: Pizzaria em Crescimento — Migração no Mês 13

| Mês | Pedidos | Ticket Médio | Taxa 2% | Receita RapiDrop |
|-----|:-------:|:------------:|:-------:|:----------------:|
| Jan | 80 | R$ 45 | R$ 2,00 | R$ 72,00 |
| Fev | 85 | R$ 48 | R$ 2,00 | R$ 81,60 |
| Mar | 90 | R$ 50 | R$ 2,00 | R$ 90,00 |
| Abr | 95 | R$ 47 | R$ 2,00 | R$ 89,30 |
| Mai | 100 | R$ 52 | R$ 2,00 | R$ 104,00 |
| Jun | 110 | R$ 49 | R$ 2,00 | R$ 107,80 |
| Jul | 115 | R$ 53 | R$ 2,00 | R$ 121,90 |
| Ago | 120 | R$ 55 | R$ 2,00 | R$ 132,00 |
| Set | 130 | R$ 51 | R$ 2,00 | R$ 132,60 |
| Out | 140 | R$ 54 | R$ 2,00 | R$ 151,20 |
| Nov | 150 | R$ 58 | R$ 2,00 | R$ 174,00 |
| Dez | 160 | R$ 62 | R$ 2,00 | R$ 198,40 |

```
Média 12 meses:  R$ 121,23
Média 6 meses:   R$ 151,68 (Jul a Dez)

Mensalidade Fixa Ano 2 = max(121.23, 151.68) = R$ 151,68/mês
```

#### Exemplo 2: Farmácia Estável — Migração no Mês 13

| Métrica | Valor |
|---------|-------|
| Média 12 meses de taxa (1,5%) | R$ 230,00 |
| Média 6 meses | R$ 225,00 |
| Mensalidade Fixa Ano 2 = max(230, 225) | **R$ 230,00/mês** |

#### Exemplo 3: Revisão Anual — Lojista que Cresceu no Fixo

```
Ano 2 (regime fixo):
  Mensalidade fixa: R$ 151,68/mês
  Pedidos processados no Ano 2: cresceram 20% vs Ano 1
  
  Cálculo da revisão para o Ano 3:
    Pedidos totais Ano 2: 2.016 pedidos
    Valor total dos pedidos Ano 2: R$ 120.960,00
    Taxa simulada (2%): R$ 2.419,20
    Média mensal simulada: R$ 201,60
  
  Mensalidade Fixa Ano 3 = R$ 201,60 (capturou o crescimento)
  
  Resultado: SaaS ganhou R$ 151,68/mês durante o Ano 2,
  e no Ano 3 passa a ganhar R$ 201,60 — mesmo valor que
  teria recebido se o lojista estivesse no percentual.
  
  ✅ SaaS não perdeu.
```

---

## 5. Regras de Transição e Reversão

### 5.1 Regras Gerais

| Regra | Descrição |
|-------|-----------|
| **Default** | Se o lojista não escolher até o mês 13, **continua no percentual** |
| **Retorno ao percentual** | Pode voltar ao percentual **a qualquer momento** (sem multa, sem período mínimo) |
| **Prazo da mudança** | A alteração entra em vigor no **mês seguinte** à solicitação |
| **Nova migração para fixo** | Se voltou ao percentual, só pode migrar para o fixo novamente após **12 meses** no percentual |
| **Cancelamento** | A qualquer momento, sem multa (mas o processamento de pedidos para) |

> **A lógica é simples:** o fixo é um benefício de previsibilidade para o lojista. Se ele não quer mais, pode sair. Mas para evitar "turbinar" (entrar no fixo só em meses altos e sair nos baixos), a reentrada no fixo exige 12 meses de percentual.

### 5.2 Durante o Período Fixo — O que Acontece se o Lojista Crescer?

O lojista no fixo **continua pagando o mesmo valor** mesmo que suas vendas cresçam. Essa é a vantagem para ele. O SaaS captura esse crescimento na **revisão anual obrigatória** (seção 4.3).

Simultaneamente, se o lojista achar que o fixo está baixo demais para o seu novo volume (improvável, mas possível), ele pode voluntariamente **migrar para o percentual** a qualquer momento.

### 5.3 E se o Lojista Quiser Voltar do Fixo para o Percentual no Meio do Ano?

**Pode, sem custo.** Basta solicitar no painel e a mudança vale para o mês seguinte.

```
Exemplo:
  Mês 6 do Ano 2 — Lojista no fixo (R$ 200/mês)
  Vendas caíram — ele quer pagar só o que vende
  Solicita: "Voltar para percentual"
  Mês 7 — Já está no percentual (2% por pedido)
```

Para migrar de volta para o fixo, precisa de 12 meses no percentual (regra anti-turbina).

### 5.4 E se o Lojista Quiser Fazer Upgrade de Segmento?

Se o lojista muda de segmento (ex: abre uma farmácia junto com o restaurante), o percentual segue o segmento principal. Se quiser separar, precisa de uma segunda conta.

---

## 6. Fluxo de Cobrança

### 6.1 Ciclo Mensal

```
[Dia 1 do mês] ─── Fatura anterior vence
                       ├── Cobrança via gateway (cartão/PIX/boleto)
                       └── Se falhar → re-tentativas D+3, D+7, D+14
                            └── Após D+21 → bloqueio parcial (dashboard readonly)
                                 └── Após D+30 → bloqueio total
                                           └── Após D+60 → cancelamento + perda de dados

[Dia 5] ─── Fatura do mês anterior é gerada
            (pedidos processados no mês anterior)

[Dia 5-10] ─── Lojista recebe notificação: "Sua fatura de R$ X está disponível"

[Dia 10] ─── Vencimento da fatura
```

### 6.2 Gateway de Pagamento

| Característica | Especificação |
|----------------|---------------|
| **Gateway primário** | Stripe (cartão) / Asaas (PIX + boleto) |
| **Pagamento automático** | Preferencialmente cartão de crédito (recorrência) |
| **Boleto** | Disponível, mas sem garantia de pagamento no vencimento |
| **PIX** | Disponível, confirmação instantânea |
| **Fatura em atraso** | Multa 2% + juros 1% ao mês |

### 6.3 Bloqueio por Inadimplência

| Estágio | Ações do Lojista | Ações do Sistema |
|---------|-----------------|------------------|
| **D+0 a D+3** | Normal | Notificação de vencimento |
| **D+4 a D+7** | Normal | Notificação de atraso + 2ª tentativa de cobrança |
| **D+8 a D+14** | Normal | 3ª tentativa de cobrança. WhatsApp do admin. |
| **D+15 a D+21** | Dashboard readonly. Pode ver, não pode alterar | Aviso de bloqueio iminente |
| **D+22 a D+30** | Dashboard bloqueado. Pedidos não são processados | Bloqueio total. Notificação ao lojista |
| **D+31 a D+60** | Acesso apenas para baixar dados | Aviso de exclusão iminente de dados |
| **D+61** | Conta cancelada. Dados excluídos após 30 dias | Cancelamento definitivo |

### 6.4 Regras de Cobrança na Fase 1 (Percentual)

```
Para cada pedido processado no mês M:
  1. Calcula taxa = valor_do_pedido × percentual_do_segmento
  2. Acumula no "saldo a pagar" do lojista

No dia 5 do mês M+1:
  1. Gera fatura com saldo acumulado
  2. Envia notificação
  3. Cobra no vencimento (dia 10)
```

### 6.5 Regras de Cobrança na Fase 2 (Mensalidade Fixa)

```
Valor fixo, cobrado no mesmo dia todo mês:
  Dia 10 de cada mês

Exceção no mês da migração (mês 13):
  - Se migrou no meio do mês, cobra proporcional
  - Próxima cobrança: dia 10 do mês seguinte (valor cheio)
```

---

## 7. Modelagem de Dados

### 7.1 Tabelas

```sql
-- Plano de precificação por segmento
pricing_plan
├── id: uuid PK
├── segment: enum('food', 'pharmacy', 'grocery') NOT NULL
├── name: varchar(100)  -- ex: "Alimentação - 2%"
├── percentage_rate: decimal(5,4) NOT NULL  -- ex: 0.0200 = 2%
├── trial_months: int DEFAULT 2
├── trial_max_orders: int DEFAULT 500
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Contrato de assinatura do lojista (evolui com o tempo)
merchant_subscription
├── id: uuid PK
├── merchant_id: uuid FK NOT NULL
├── pricing_plan_id: uuid FK
├── status: enum('trial', 'active_percentage', 'active_fixed', 'suspended', 'cancelled')
│
├── current_phase: enum('phase_1_percentage', 'phase_2_percentage', 'phase_2_fixed') NOT NULL
├── phase_started_at: timestamptz
├── phase_1_ended_at: timestamptz  -- quando completou 12 meses
│
├── percentage_rate: decimal(5,4)  -- taxa vigente (pode mudar se mudar de segmento)
│
├── fixed_monthly_cents: int  -- valor da mensalidade fixa (se phase_2_fixed)
├── fixed_monthly_calculated_at: date
├── fixed_monthly_next_review: date
├── fixed_monthly_buffer_percent: decimal(5,4) DEFAULT 0.05
│
├── trial_ends_at: date
├── trial_orders_count: int DEFAULT 0
│
├── billing_day: int DEFAULT 10  -- dia de vencimento
├── payment_gateway: varchar(50)
├── payment_gateway_customer_id: varchar(200)  -- id no gateway
│
├── cancellation_reason: text
├── cancelled_at: timestamptz
├── created_at: timestamptz
└── updated_at: timestamptz

-- Histórico de mudanças de fase
merchant_subscription_phase_log
├── id: uuid PK
├── merchant_subscription_id: uuid FK
├── previous_phase: varchar(50)
├── new_phase: varchar(50)
├── changed_by: varchar(50)  -- 'system', 'merchant', 'admin'
├── metadata: jsonb  -- dados usados no cálculo (médias, buffers, etc)
│   └── { "avg_12_months_cents": 15633, "avg_6_months_cents": 18240, "buffer": 0.05 }
├── created_at: timestamptz
└── notes: text

-- Fatura mensal
invoice
├── id: uuid PK
├── merchant_id: uuid FK
├── merchant_subscription_id: uuid FK
├── type: enum('percentage', 'fixed', 'adjustment', 'credit', 'debit')
│
├── period_start: date
├── period_end: date
├── due_date: date
│
├── amount_cents: int  -- valor total
├── percentage_amount_cents: int  -- valor referente ao percentual (se aplicável)
├── fixed_amount_cents: int  -- valor da mensalidade fixa (se aplicável)
├── adjustments_cents: int  -- créditos ou débitos extras
│
├── payment_status: enum('pending', 'paid', 'overdue', 'cancelled', 'refunded')
├── paid_at: timestamptz
├── payment_method: varchar(50)
├── gateway_invoice_id: varchar(200)
│
├── invoice_pdf_url: text
├── created_at: timestamptz
└── payment_attempts: int DEFAULT 0

-- Transação individual (para rateio detalhado na fase de percentual)
invoice_transaction
├── id: uuid PK
├── invoice_id: uuid FK
├── order_id: uuid FK  -- pedido que gerou a transação
├── order_amount_cents: int  -- valor do pedido
├── percentage_rate: decimal(5,4)
├── amount_cents: int  -- taxa calculada
├── created_at: timestamptz
```

### 7.2 Índices

```sql
-- Buscar assinatura ativa do lojista
CREATE UNIQUE INDEX idx_one_active_subscription
  ON merchant_subscription (merchant_id) WHERE status IN ('trial', 'active_percentage', 'active_fixed');

-- Faturas do lojista
CREATE INDEX idx_invoice_merchant_dates ON invoice (merchant_id, period_start DESC);

-- Lojistas em trial próximo do vencimento
CREATE INDEX idx_subscription_trial_ending ON merchant_subscription (trial_ends_at)
  WHERE status = 'trial';

-- Lojistas aptos a migrar para fase 2
CREATE INDEX idx_subscription_phase1_ending ON merchant_subscription (phase_1_ended_at)
  WHERE current_phase = 'phase_1_percentage' AND phase_1_ended_at IS NOT NULL;
```

---

## 8. Comparativo de Cenários

### 8.1 Para o Lojista

| Cenário | Percentual (sempre) | Mensalidade Fixa |
|---------|:-------------------:|:-----------------:|
| Mês de vendas baixas | ✅ Paga menos | ❌ Paga o mesmo |
| Mês de vendas altas | ❌ Paga mais | ✅ Paga o mesmo |
| Sazonalidade forte | ❌ Imprevisível | ✅ Previsível |
| Planejamento financeiro | ❌ Variável | ✅ Fixo |
| Crescimento acelerado | ❌ Custo sobe | ✅ Custo estável (até revisão) |
| Queda nas vendas | ✅ Custo cai | ❌ Custo não cai |
| Inflação | ✅ Ajuste automático | ❌ Reajuste anual |

### 8.2 Para o SaaS (RapiDrop)

| Cenário | Percentual (sempre) | Mensalidade Fixa |
|---------|:-------------------:|:-----------------:|
| Receita previsível | ❌ Variável | ✅ Previsível |
| Alinhamento com crescimento | ✅ Acompanha | ❌ Defasado (até revisão) |
| Safe para valuation | ❌ Menos atraente | ✅ MRR previsível |
| Risco de churn | ❌ Maior (surpresa na fatura) | ✅ Menor (acostumou com o valor) |
| Complexidade operacional | ✅ Simples ( % fixa) | ❌ Cálculo + reajuste |

### 8.3 Projeção de Receita do SaaS — Loja Típica (Pizzaria)

```
Cenário: Pizzaria com ticket médio R$ 50, crescendo 5% ao mês nos primeiros 12 meses

Mês   Pedidos   Receita Lojista   Taxa 2%   Receita RapiDrop
─────────────────────────────────────────────────────────────
 1     50        R$ 2.500         0%        R$ 0       (cortesia)
 2     60        R$ 3.000         0%        R$ 0       (cortesia)
 3     70        R$ 3.500         2%        R$ 70
 4     80        R$ 4.000         2%        R$ 80
 5     90        R$ 4.500         2%        R$ 90
 6     100       R$ 5.000         2%        R$ 100
 7     105       R$ 5.250         2%        R$ 105
 8     110       R$ 5.500         2%        R$ 110
 9     115       R$ 5.750         2%        R$ 115
10     120       R$ 6.000         2%        R$ 120
11     125       R$ 6.250         2%        R$ 125
12     130       R$ 6.500         2%        R$ 130
─────────────────────────────────────────────────────────────
Total 1º ano: R$ 1.045 (média: R$ 104,50/mês nos meses pagos)

Mês 13 — Se migrar para fixo:
  Média 12 meses:           R$ 87,08  (R$ 1.045 / 12)
  Média 6 meses (Jul-Dez):  R$ 117,50 (R$ 705 / 6)
  Mensalidade Fixa (5%):    R$ 123,38/mês
```

---

## 9. Summary para o Lojista

```
╔══════════════════════════════════════════════════════════════╗
║              🚚 RapiDrop — Planos de Assinatura             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📅 PRIMEIRO ANO — Pague apenas quando vender               ║
║                                                              ║
║     • 2% sobre cada pedido (alimentação)                     ║
║     • 1,5% sobre cada pedido (farmácia/mercado)              ║
║     • 🎁 2 primeiros meses sem taxa                          ║
║     • Sem mensalidade, sem fidelidade                        ║
║                                                              ║
║  📅 APÓS 12 MESES — Escolha seu regime                       ║
║                                                              ║
║     ┌─ Opção A: Continuar no percentual                      ║
║     │  (paga % sobre cada pedido)                            ║
║     │                                                        ║
║     └─ Opção B: Mensalidade Fixa                             ║
║        (valor calculado pelo seu histórico)                  ║
║        • Previsível: mesmo valor todo mês                    ║
║        • Justo: calculado pela sua média real                ║
║        • 🔄 Pode voltar ao percentual a qualquer momento     ║
║                                                              ║
║  💳 Pagamento: Cartão, PIX ou Boleto                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 10. Regras de Negócio — Resumo

1. **Fase 1 (mêses 1-12)**: Percentual por pedido, sem mensalidade fixa
2. **Cortesia**: 2 primeiros meses sem taxa (limitado a 500 pedidos)
3. **Percentuais por segmento**: 2% alimentação, 1,5% farmácia/mercado
4. **Fase 2 (após 12 meses)**: Lojista escolhe entre continuar % ou migrar para fixo
5. **Cálculo inicial do fixo**: `max(média_12_meses, média_6_meses)` — sem buffer
6. **Revisão anual obrigatória**: Recalcula usando pedidos reais dos últimos 12 meses, simulando o percentual — garante que o SaaS nunca perca
7. **Reajuste anual**: IPCA acumulado (limitado a 15%)
8. **Retorno ao percentual**: A qualquer momento, sem multa, sem período mínimo
9. **Reentrada no fixo**: Só após 12 meses no percentual (anti-turbina)
10. **Inadimplência**: Bloqueio progressivo com D+15 (readonly), D+22 (total), D+60 (cancelamento)

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Nota:** Este documento substitui a precificação por planos fixos da versão anterior.
> O modelo de percentual + mensalidade opcional alinha incentivos e reduz barreira de entrada.
