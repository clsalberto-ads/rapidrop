# RapiDrop — Fluxo Financeiro

> Como o dinheiro se move no RapiDrop: recebimento de clientes, split de
> pagamentos, cobrança da taxa SaaS, pagamento de entregadores, conciliação
> e implicações legais/fiscais.

---

## Índice

1. [Filosofia Financeira](#1-filosofia-financeira)
2. [Diagrama Geral do Fluxo de Dinheiro](#2-diagrama-geral-do-fluxo-de-dinheiro)
3. [Modalidades de Pagamento](#3-modalidades-de-pagamento)
4. [Modelo de Cobrança da Taxa SaaS](#4-modelo-de-cobrança-da-taxa-saas)
5. [Fluxo por Método de Pagamento](#5-fluxo-por-método-de-pagamento)
6. [Split de Pagamentos (Asaas)](#6-split-de-pagamentos-asaas)
7. [Cobrança por Fatura (Fallback)](#7-cobrança-por-fatura-fallback)
8. [Pagamento de Entregadores](#8-pagamento-de-entregadores)
9. [Ciclo de Settlement](#9-ciclo-de-settlement)
10. [Reembolsos e Chargebacks](#10-reembolsos-e-chargebacks)
11. [Conciliação](#11-conciliação)
12. [Inadimplência e Dunning](#12-inadimplência-e-dunning)
13. [Implicações Fiscais](#13-implicações-fiscais)
14. [Modelo de Dados (Tabelas Financeiras)](#14-modelo-de-dados-tabelas-financeiras)
15. [Estratégia de Implementação](#15-estratégia-de-implementação)
16. [Cobertura de Testes](#16-cobertura-de-testes)

---

## 1. Filosofia Financeira

### 1.1 Princípios

| Princípio | Implicação |
|-----------|------------|
| **RapiDrop não segura dinheiro de terceiros** | Todo dinheiro de clientes ou lojistas transita por gateway de pagamento com split automático. RapiDrop nunca mantém saldo de merchant em conta própria. |
| **Taxa é cobrada no momento do pedido, não no fim do mês** | Para pagamentos online, a taxa é deduzida automaticamente no split. Para dinheiro/cartão na entrega, a fatura é gerada automaticamente. |
| **Rastreabilidade total** | Cada centavo tem origem conhecida: `payment_transaction` → `order` → `customer`. Nada é "caixa preta". |
| **Conciliação diária automatizada** | Todo dia o sistema compara pedidos do dia com transações do gateway. Divergências viram alerta. |
| **LGPD e regulação BCB** | Dados financeiros são tratados com nível máximo de segurança. Split payments via instituição autorizada pelo Banco Central (Asaas). |

### 1.2 Abordagem em Fases

```
FASE 1 (MVP) — FATURA MENSAL
┌─────────────────────────────────────────────────────────┐
│ Cliente paga o lojista direto (PIX, dinheiro, cartão)   │
│ RapiDrop calcula a taxa e emite fatura no fim do mês    │
│ Lojista paga a fatura (PIX ou boleto, via Asaas)        │
│                                                          │
│ ✅ Mais simples de implementar                           │
│ ✅ Sem necessidade de split payment                     │
│ ❌ Risco de inadimplência (precisa cobrar)              │
│ ❌ Fricção no onboarding (lojista precisa pagar depois) │
└─────────────────────────────────────────────────────────┘

FASE 2 (ESCALA) — SPLIT AUTOMÁTICO
┌─────────────────────────────────────────────────────────┐
│ Cliente paga via gateway do RapiDrop (Asaas)             │
│ Asaas split: taxa RapiDrop + repasse ao lojista         │
│ RapiDrop recebe a taxa instantaneamente                 │
│                                                          │
│ ✅ Risco de inadimplência ZERO                          │
│ ✅ Experiência integrada (cliente paga no checkout)     │
│ ✅ Lojista recebe líquido direto na conta               │
│ ❌ Lojista precisa ter conta Asaas (subconta)          │
│ ❌ Mais complexidade técnica                             │
└─────────────────────────────────────────────────────────┘

FASE 3 (MATURIDADE) — ANTECIPAÇÃO + WALLET
┌─────────────────────────────────────────────────────────┐
│ RapiDrop oferece antecipação de recebíveis              │
│ Wallet digital para o lojista (saldo, saques)           │
│ Programa de fidelidade financeira (desconto por volume) │
└─────────────────────────────────────────────────────────┘

O MVP começa com a Fase 1. A Fase 2 é o destino final desejado.
```

---

## 2. Diagrama Geral do Fluxo de Dinheiro

### 2.1 Fase 1 — Fatura Mensal

```
                    ┌──────────┐
                    │ CLIENTE  │
                    └────┬─────┘
                         │  R$ 100,00 (PIX para o lojista)
                         ▼
                    ┌──────────┐
                    │ LOJISTA  │
                    │          │
                    │ Conta:   │
                    │ +R$ 100  │
                    └────┬─────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Produto  │  │ Custo    │  │ RapiDrop │
    │ (insumos)│  │ entrega  │  │ Taxa 2%  │
    │ -R$ 40   │  │ -R$ 15   │  │ = R$ 2   │
    └──────────┘  └──────────┘  └──────────┘
                                   │
                                   │ Fatura no fim do mês
                                   ▼
                              ┌──────────┐
                              │ LOJISTA  │
                              │ paga R$ 2│
                              └──────────┘

 Fluxo de caixa do lojista:
   +R$ 100  (cliente)
   -R$ 40   (custo produto)
   -R$ 15   (entregador)
   -R$ 2    (taxa RapiDrop — paga depois)
   ─────────
   =R$ 43   (margem do lojista)

 Risco: RapiDrop precisa cobrar os R$ 2 depois.
```

### 2.2 Fase 2 — Split Automático

```
                    ┌──────────┐
                    │ CLIENTE  │
                    └────┬─────┘
                         │  R$ 100,00 (PIX para Asaas)
                         ▼
                    ┌──────────┐
                    │  ASAAS   │  (gateway de pagamento)
                    │          │
                    │ Split:   │
                    └────┬─────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ RapiDrop         │  │ LOJISTA          │
    │ Recebe:          │  │ Recebe:           │
    │ R$ 2,00 (taxa)   │  │ R$ 98,00 (líquido)│
    │ Já é nosso! 🎉   │  │ Na conta bancária │
    └──────────────────┘  └──────────────────┘

 Risco: ZERO para o RapiDrop.
 Lojista recebe o líquido automaticamente.
```

### 2.3 Fluxo do Dinheiro no Tempo

```
Evento:           Pedido         Delivery      Settlement      Fim do mês
                  criado         concluído     (D+0 a D+30)
                  │              │             │               │
Timeline:         ├──────────────┼─────────────┼───────────────┤
                  │              │             │               │
No split:         │              │             │               │
 Cliente ▶ Asaas  ●──────────────●─────────────●───────────────┤
 RapiDrop (taxa)  │              │             ● (instantâneo) │
 Lojista          │              │             ● (D+0 a D+30)  │
                  │              │             │               │
Na fatura:        │              │             │               │
 Cliente ▶ Lojista●──────────────●─────────────●───────────────┤
 Fatura RapiDrop  │              │             │               ●
 Lojista paga     │              │             │               ● (D+30)
```

---

## 3. Modalidades de Pagamento

### 3.1 Tabela de Modalidades

| # | Método | Tipo | Settlement | Split Possível? | Fluxo no MVP |
|---|--------|:----:|:----------:|:---------------:|--------------|
| 1 | **PIX** | Pré-pago | Instantâneo (D+0) | ✅ Sim | Cliente → Asaas → Split |
| 2 | **Cartão crédito (online)** | Pré-pago | D+1 a D+30 | ✅ Sim | Cliente → Asaas → Split |
| 3 | **Cartão débito (online)** | Pré-pago | D+0 a D+1 | ✅ Sim | Cliente → Asaas → Split |
| 4 | **Dinheiro** | Pós-pago | Na entrega | ❌ Não | Cliente → Entregador → Lojista. Fatura no fim do mês. |
| 5 | **Cartão na entrega** | Pós-pago | Na entrega | ❌ Não | Cliente → Maquininha do lojista. Fatura no fim do mês. |
| 6 | **Boleto** | Pré-pago | D+1 a D+3 | ✅ Sim | Cliente → Asaas → Split |

**Regra de decisão:**
- Métodos pré-pagos (PIX, cartão online, boleto): **split automático via Asaas** (Fase 2+)
- Métodos pós-pagos (dinheiro, cartão na entrega): **fatura mensal** (sempre)
- No MVP (Fase 1): **todos por fatura mensal**, inclusive os pré-pagos

### 3.2 Métodos Disponíveis por Segmento

| Segmento | PIX | Cartão online | Dinheiro | Cartão entrega | Boleto |
|----------|:---:|:-------------:|:--------:|:--------------:|:------:|
| Alimentação | ✅ | ✅ | ✅ | ✅ | ❌ |
| Farmácia | ✅ | ✅ | ✅ | ✅ | ❌ |
| Mercado | ✅ | ✅ | ✅ | ✅ | ✅ (pedidos grandes) |

### 3.3 Regras por Método

**PIX:**
- QR Code dinâmico gerado pelo Asaas (válido por 15 min)
- Após pagamento: webhook confirma → pedido segue
- Se expirar: `order.payment_expired` → cancelamento automático

**Cartão crédito (online):**
- Tokenização: cartão é tokenizado no Asaas (RapiDrop nunca vê o número)
- Autorização no checkout + captura automática
- Parcelamento: lojista decide se aceita (1x a 12x)
- Lojista absorve custo do parcelamento (ou repassa ao cliente — configurável)

**Dinheiro:**
- Entregador recebe o valor na entrega
- Entregador acerta com o lojista no fim do dia/semana
- RapiDrop fatura a taxa no fim do mês

**Cartão na entrega:**
- Entregador leva maquininha do lojista
- Valor é processado na maquininha normalmente
- RapiDrop fatura a taxa no fim do mês

---

## 4. Modelo de Cobrança da Taxa SaaS

### 4.1 Como a Taxa é Calculada

A taxa segue a especificação de [`docs/assinatura-saas.md`](assinatura-saas.md):

| Segmento | Taxa | Aplicação |
|----------|:----:|-----------|
| Alimentação | **2,0%** | Sobre o total do pedido (itens + taxa de entrega) |
| Farmácia | **1,5%** | Sobre o total do pedido |
| Mercado | **1,5%** | Sobre o total do pedido |

**Regras:**
- A taxa incide sobre o valor **total** do pedido (itens + taxa de entrega)
- Pedidos **cancelados antes de `em_preparo`** não geram cobrança
- Pedidos **cancelados durante ou após `em_preparo`** geram cobrança normal
- Pedidos com `cancelado_parcial` (mercado): taxa incide sobre o valor final (após remoção dos itens)

### 4.2 Momento da Cobrança

```
FASE 1 (Fatura):
  taxas são acumuladas mensalmente
  fatura gerada no D+1 do mês seguinte
  lojista tem 7 dias para pagar

FASE 2 (Split):
  taxa é deduzida no momento do pagamento
  RapiDrop recebe instantaneamente junto com o split
  sem fatura, sem cobrança, sem inadimplência
```

### 4.3 Cálculo na Fatura Mensal

```python
def calculate_monthly_invoice(merchant_id: int, year: int, month: int) -> Invoice:
    """
    Calcula a fatura mensal de um lojista.

    Acumula todos os pedidos do mês que geram cobrança e aplica a taxa.
    """
    orders = await db.query(Order).filter(
        Order.merchant_id == merchant_id,
        Order.delivered_at.between(
            date(year, month, 1),
            date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1),
        ),
        Order.status.in_(["entregue", "finalizado"]),
    ).all()

    # Incluir pedidos cancelados que geram cobrança
    cancelled_charged = await db.query(Order).filter(
        Order.merchant_id == merchant_id,
        Order.status == "cancelado",
        Order.cancelled_at >= order.created_at,  # cancelado após preparo
        Order.cancelled_at.between(...)
    ).all()

    total_orders_value = sum(order.total_cents for order in orders)
    total_cancelled_value = sum(order.total_cents for order in cancelled_charged)

    # Aplica a taxa do segmento
    merchant = await db.get(Merchant, merchant_id)
    rate = SEGMENT_RATES[merchant.segment]  # 0.02 ou 0.015

    amount_cents = int((total_orders_value + total_cancelled_value) * rate)

    return Invoice(
        merchant_id=merchant_id,
        period_start=date(year, month, 1),
        period_end=date(year, month + 1, 1),
        amount_cents=amount_cents,
        total_orders=len(orders),
        total_orders_value=total_orders_value,
        total_cancelled_charged_value=total_cancelled_value,
        rate=rate,
    )
```

### 4.4 Descontos e Isenções

| Situação | Regra |
|----------|-------|
| Trial (meses 1-2) | **Isento** — taxa ZERO |
| Primeiro mês pago | Taxa normal a partir do mês 3 |
| Pedido cancelado antes do preparo | **Isento** — não entra na fatura |
| Pedido cancelado após preparo | **Cobra** — entra na fatura |
| Estorno pós-entrega | Taxa **não é estornada** (serviço foi prestado) |

---

## 5. Fluxo por Método de Pagamento

### 5.1 PIX — Fluxo Completo

```
[Cliente finaliza checkout — seleciona PIX]
        │
        ▼
[RapiDrop → Asaas: criar cobrança PIX]
  │  POST /v3/pix/cob
  │  ├── value: 10000 (R$ 100,00 em centavos)
  │  ├── split: (Fase 2) [{"merchant": 9800}, {"rapidrop": 200}]
  │  └── expiration: 15 min
        │
        ▼
[Asaas → RapiDrop: QR Code + copia-cola]
        │
        ▼
[Cliente vê QR Code na tela (ou recebe por WhatsApp)]
        │
        ▼
┌──────────────────────────────────────────────────┐
│  [Cliente paga]  ─── ou ───  [Tempo expira]     │
│         │                            │            │
│         ▼                            ▼            │
│  Webhook Asaas:                 Webhook Asaas:    │
│  PAYMENT_CONFIRMED              PAYMENT_EXPIRED  │
│         │                            │            │
│         ▼                            ▼            │
│  pedido → pendente            pedido → cancelado  │
│  (segue fluxo normal)          notificar cliente  │
└──────────────────────────────────────────────────┘
```

### 5.2 Cartão Crédito — Fluxo Completo

```
[Cliente finaliza checkout — insere dados do cartão]
        │
        ▼
[Asaas: tokenizar cartão]
  │  POST /v3/payments/tokenize
  │  RapiDrop NUNCA vê o número do cartão
        │
        ▼
[Asaas: autorizar pagamento]
  │  POST /v3/payments
  │  ├── customer: id no Asaas
  │  ├── billingType: CREDIT_CARD
  │  ├── value: 10000
  │  └── creditCardToken: tok_xxxx
        │
        ▼
┌──────────────────────────────┐
│  AUTORIZADO      RECUSADO   │
│       │               │      │
│       ▼               ▼      │
│  pedido → pendente   notificar cliente
│  cartão CAPTURADO    "tente outro cartão"
│  após delivery       │
│       │              ▼      │
│       ▼         pedido não  │
│  (segue fluxo)   é criado   │
└──────────────────────────────┘

⚠️ Momento da captura:
  ─ PIX: captura instantânea (não tem como reverter)
  ─ Cartão: autoriza no checkout, CAPTURA após delivery
    (evita pagar taxa de cancelamento se pedido for cancelado)
```

### 5.3 Dinheiro — Fluxo Completo

```
[Cliente finaliza checkout — seleciona "Dinheiro"]
  │  informa: "troco para R$ 120,00"
        │
        ▼
[Pedido segue fluxo normal → delivery]
        │
        ▼
[Entregador chega no local]
  │  Cliente paga R$ 100,00 em dinheiro
  │  Entregador dá troco (se necessário)
        │
        ▼
[Entregador marca "Entregue" no app]
  │  Confirma recebimento: "💰 Dinheiro recebido"
        │
        ▼
[Lojista acerta com entregador no fim do dia]
  │  Extrato do dia mostra: dinheiro recebido vs entregas feitas
        │
        ▼
[Fim do mês: fatura RapiDrop inclui esse pedido]
```

### 5.4 Cartão na Entrega — Fluxo Completo

```
[Cliente finaliza checkout — seleciona "Cartão na entrega"]
        │
        ▼
[Pedido segue fluxo normal → delivery]
        │
        ▼
[Entregador chega com maquininha do lojista]
  │  Cliente passa o cartão
  │  Maquininha processa normalmente
        │
        ▼
[Entregador marca "Entregue" no app]
  │  Confirma pagamento: "💳 Cartão processado"
        │
        ▼
[Lojista recebe na conta dele (via maquininha)]
  │  R$ 97,00 (R$ 100 - 3% da maquininha)
        │
        ▼
[Fim do mês: fatura RapiDrop inclui esse pedido]
```

---

## 6. Split de Pagamentos (Asaas)

### 6.1 Arquitetura do Split

O Asaas oferece split de pagamentos via **Subcontas**:

```
┌────────────────────────────────────────────────────────────┐
│                     ASAAS PLATFORM                          │
│                                                             │
│  ┌─────────────────────┐   ┌────────────────────────────┐  │
│  │ Conta RapiDrop      │   │ Subconta Lojista A         │  │
│  │ (Plataforma)        │   │ (merchant_id: 42)          │  │
│  │                     │   │                            │  │
│  │ ● Gerencia splits   │   │ ● Recebe repasses          │  │
│  │ ● Recebe taxa SaaS  │   │ ● Dados bancários próprios │  │
│  │ ● Onboarding        │   │ ● Token de acesso próprio  │  │
│  │   de subcontas      │   │                            │  │
│  └─────────────────────┘   └────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────┐   ┌────────────────────────────┐  │
│  │ Subconta Lojista B  │   │ Subconta Lojista C         │  │
│  │ (merchant_id: 57)   │   │ (merchant_id: 89)          │  │
│  └─────────────────────┘   └────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Cada lojista precisa:**
1. Criar uma **Subconta** no Asaas (via embedded onboarding)
2. Fornecer dados cadastrais (CPF/CNPJ, dados bancários)
3. Aceitar os termos de uso

### 6.2 Chamada de Split

```python
async def create_split_payment(
    order: Order,
    customer: Customer,
    payment_method: str,
) -> dict:
    """
    Cria um pagamento no Asaas com split automático.

    A taxa do RapiDrop é deduzida automaticamente no split.
    O lojista recebe o valor líquido na conta bancária dele.
    """
    total_cents = order.total_cents
    rate = SEGMENT_RATES[order.merchant.segment]  # 0.02 ou 0.015
    rapidrop_fee_cents = int(total_cents * rate)
    merchant_net_cents = total_cents - rapidrop_fee_cents

    # Buscar IDs no Asaas
    merchant = await db.get(Merchant, order.merchant_id)
    asaas_customer_id = customer.asaas_customer_id

    payment_data = {
        "customer": asaas_customer_id,
        "billingType": payment_method.upper(),  # PIX, CREDIT_CARD, BOLETO
        "value": total_cents / 100,  # Asaas aceita em reais (float)
        "dueDate": date.today().isoformat(),
        "description": f"Pedido #{order.id} - {merchant.business_name}",
        "split": [
            {
                "walletId": MERCHANT_WALLET_ID,  # wallet do lojista no Asaas
                "percentualValue": 0,  # valor fixo, não percentual
                "fixedValue": merchant_net_cents / 100,
            },
            {
                "walletId": RAPIDROP_WALLET_ID,  # wallet do RapiDrop
                "percentualValue": 0,
                "fixedValue": rapidrop_fee_cents / 100,
            },
        ],
    }

    # Em vez de percentual, split por valor fixo.
    # Isso garante que o valor exato da taxa seja cobrado,
    # sem arredondamentos que podem dar diferença de centavos.

    response = await asaas_client.post("/v3/payments", json=payment_data)
    return response.json()

# Resposta:
# {
#   "id": "pay_12345",
#   "status": "PENDING",  # ou RECEIVED (PIX é instantâneo)
#   "value": 100.00,
#   "split": [
#     {"walletId": "xxx", "value": 98.00, "status": "PENDING"},
#     {"walletId": "yyy", "value": 2.00, "status": "PENDING"},
#   ]
# }
```

### 6.3 Onboarding de Subcontas (Embedded)

Para criar a subconta do lojista no Asaas sem ele sair do RapiDrop:

```
1. Lojista vai em "Configurações → Financeiro" no dashboard
2. Clica em "Conectar conta Asaas para recebimento"
3. RapiDrop redireciona para o Asaas Account:
   ─ Lojista preenche dados (CPF/CNPJ, RG, endereço, dados bancários)
   ─ Documentos são verificados automaticamente
   ─ Conta criada em 1-2 minutos
4. RapiDrop recebe o `account_id` da subconta
5. Pronto! Lojista pode receber splits

Dados armazenados em merchant.asaas_subaccount:
  ├── account_id: "sub_xxxx"
  ├── wallet_id: "wallet_xxxx"
  ├── account_status: "pending" | "active" | "blocked"
  └── onboarded_at: datetime
```

---

## 7. Cobrança por Fatura (Fallback)

Para pedidos em dinheiro/cartão na entrega (e para toda a Fase 1), a taxa
é cobrada via **fatura mensal**.

### 7.1 Geração da Fatura

```
Todo dia 1º do mês:
  1. Sistema calcula todas as taxas do mês anterior
  2. Gera fatura no Asaas
  3. Envia para o lojista (WhatsApp + Email)
  4. Lojista tem 7 dias para pagar (PIX ou boleto)

Estrutura da fatura:
  ┌──────────────────────────────────────────────┐
  │  FATURA RapiDrop — Pizzaria do Norte          │
  │  Período: Junho/2026                         │
  │                                              │
  │  Total de pedidos: 142                       │
  │  Valor total pedidos: R$ 7.352,00            │
  │  Taxa aplicada: 2,0%                        │
  │  ─────────────────────────────────────      │
  │  VALOR DA FATURA: R$ 147,04                  │
  │  Vencimento: 07/07/2026                      │
  │                                              │
  │  📄 Detalhamento por pedido disponível       │
  │  💳 Pagar com PIX (QR Code abaixo)           │
  └──────────────────────────────────────────────┘
```

### 7.2 Webhook de Pagamento da Fatura

```python
@router.post("/api/v1/asaas/webhook")
async def asaas_webhook(request: Request):
    """
    Webhook do Asaas para eventos de pagamento.
    Atualiza o status da fatura quando paga.
    """
    payload = await request.json()
    event = payload.get("event")

    if event == "PAYMENT_RECEIVED":
        payment_id = payload["payment"]["id"]
        invoice = await db.query(Invoice).filter(
            Invoice.asaas_payment_id == payment_id
        ).first()
        if invoice:
            invoice.status = "paid"
            invoice.paid_at = datetime.now()
            invoice.payment_method = payload["payment"].get("billingType")
            await db.commit()
            await notify_merchant_invoice_paid(invoice)

    elif event == "PAYMENT_OVERDUE":
        # Ativar fluxo de cobrança (dunning)
        payment_id = payload["payment"]["id"]
        invoice = await db.query(Invoice).filter(
            Invoice.asaas_payment_id == payment_id
        ).first()
        if invoice:
            invoice.status = "overdue"
            await db.commit()
            await start_dunning_flow(invoice)
```

### 7.3 Detalhamento da Fatura

Cada fatura tem um breakdown por pedido para transparência total:

```json
{
  "invoice_id": 42,
  "merchant": "Pizzaria do Norte",
  "period": "2026-06",
  "total_amount_cents": 14704,
  "rate": 0.02,
  "total_orders": 142,
  "total_orders_value_cents": 735200,
  "orders": [
    {
      "order_id": 1234,
      "date": "2026-06-01",
      "value_cents": 5200,
      "fee_cents": 104,
      "status": "entregue"
    },
    {
      "order_id": 1235,
      "date": "2026-06-01",
      "value_cents": 3800,
      "fee_cents": 76,
      "status": "entregue"
    }
  ],
  "cancelled_charged": [
    {
      "order_id": 1240,
      "date": "2026-06-02",
      "value_cents": 4500,
      "fee_cents": 90,
      "reason": "cancelado_durante_preparo"
    }
  ]
}
```

---

## 8. Pagamento de Entregadores

### 8.1 Quem Paga o Entregador?

**O lojista paga o entregador diretamente.** O RapiDrop apenas:

1. **Calcula** o valor a pagar (por diária, por entrega, híbrido, ranking)
2. **Gera o extrato** com detalhamento completo
3. **Registra** no sistema para auditoria e conciliação

```
RapiDrop: calcula ▶ extrato ▶ registra
                                    │
                                    ▼
Lojista:  confirma ▶ paga ▶ marca como pago no sistema
                                    │
                                    ▼
Entregador: recebe ▶ confirma recebimento (app)
```

### 8.2 Fluxo de Pagamento

Ver especificação completa em [`docs/pagamento-entregadores.md`](pagamento-entregadores.md).

Este documento apenas define **como o dinheiro se move**:

```
1. RapiDrop gera extrato do período (ex: 01-07/jun)
   ├── base_amount: R$ 350,00 (7 diárias × R$ 50)
   ├── additional: R$ 42,00 (entregas extras)
   ├── ranking_bonus: R$ 30,00 (2º lugar no ranking)
   └── total: R$ 422,00

2. Lojista visualiza, ajusta se necessário, aprova

3. Lojista paga:
   ├── PIX direto pro entregador (recomendado)
   └── Dinheiro (no fim do expediente)

4. Lojista marca como pago no sistema

5. Entregador confirma recebimento no app
```

### 8.3 Acordo com Entregador

O RapiDrop **não** tem vínculo empregatício com o entregador.
O vínculo é **exclusivamente do lojista**.

- O RapiDrop é uma ferramenta de gestão e cálculo
- O lojista é o contratante do entregador
- O extrato gerado pelo RapiDrop é uma **recomendação de pagamento**
- O lojista pode ajustar valores (para cima ou para baixo) antes de pagar
- O lojista assume toda responsabilidade trabalhista e previdenciária

---

## 9. Ciclo de Settlement

### 9.1 Prazos por Gateway e Método

| Método | Gateway | Settlement Lojista | Settlement RapiDrop |
|--------|---------|:------------------:|:-------------------:|
| PIX | Asaas | D+0 (instantâneo) | D+0 (split instantâneo) |
| Cartão crédito | Asaas | D+14 a D+30* | D+14 a D+30* |
| Cartão débito | Asaas | D+1 | D+1 |
| Boleto | Asaas | D+3 (após pagamento) | D+3 |
| Dinheiro | — | Na entrega | Fim do mês (fatura) |
| Cartão entrega | Maquininha do lojista | D+0 a D+30 (maquininha) | Fim do mês (fatura) |

\* Cartão de crédito: o prazo depende do número de parcelas e do acordo com
a adquirente. Asaas repassa ao lojista em D+14 para 1x, e em parcelas mensais
para parcelado.

### 9.2 Impacto no Fluxo de Caixa do Lojista

```
Exemplo: Pedido de R$ 100,00 pago com cartão crédito 1x

  Lojista recebe:   R$ 98,00 (após taxa RapiDrop de 2%)
  Asaas repassa:    D+14 (média)
  Custo maquininha: incluso no acordo Asaas (~1,99% + R$ 0,50)

  ─ Lojista vê no dashboard:
    "💰 R$ 98,00 a receber em ~14 dias"
```

### 9.3 Múltiplos Recebíveis no Dashboard

O lojista vê um resumo financeiro unificado:

```
┌─────────────────────────────────────────────────────┐
│  📊 RESUMO FINANCEIRO — Pizzaria do Norte           │
│  Período: Junho/2026                                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  A RECEBER                   RECEBIDO               │
│  ──────────                   ────────              │
│  Cartão (D+14)   R$ 850,00   PIX      R$ 2.300,00  │
│  Dinheiro        R$ 120,00   (entregue, pendente    │
│  (faturamento)               de acerto c/ entreg.)  │
│                                                      │
│  TOTAL           R$ 970,00   TOTAL   R$ 2.300,00    │
│                                                      │
│  ─────────────────────────────────────────────       │
│  Taxa RapiDrop (2%): R$ 97,00                       │
│  Status: ✅ Fatura #42 — Paga em 05/07               │
└─────────────────────────────────────────────────────┘
```

---

## 10. Reembolsos e Chargebacks

### 10.1 Matriz de Reembolso

(Conforme especificado em [`docs/maquina-estados-pedido.md`](maquina-estados-pedido.md#7-cancelamentos-e-reembolsos))

| Ponto de Cancelamento | Reembolso ao Cliente | Taxa SaaS | Quem arca com custo do gateway |
|-----------------------|:--------------------:|:---------:|:------------------------------:|
| Antes de `confirmado` | **100%** | Não cobra | RapiDrop (estorno gratuito) |
| Durante `em_preparo` | **100%** | Cobra | Lojista (via split negativo) |
| Após `pronto` | **≥ 80%** | Cobra | Lojista |
| Após `saiu_para_entrega` | **≥ 50%** | Cobra | Lojista |

### 10.2 Fluxo de Estorno (PIX/Cartão)

```python
async def process_refund(order: Order, reason: str, amount_cents: int):
    """
    Processa estorno de um pedido pago via gateway.
    """
    # 1. Buscar transação original
    transaction = await db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == order.id,
        PaymentTransaction.type == "charge",
    ).first()

    if not transaction:
        raise RefundError("Transação original não encontrada")

    # 2. Se foi split, precisa estornar das duas wallets
    if transaction.split:
        # Asaas: estorno proporcional ao split
        refund = await asaas_client.post(f"/v3/payments/{transaction.gateway_id}/refund", {
            "value": amount_cents / 100,
        })
    else:
        # Fatura: estorno não se aplica (dinheiro já foi do lojista)
        # Notificar lojista para devolver ao cliente
        await notify_merchant_refund_needed(order, amount_cents)
        return

    # 3. Registrar transação de estorno
    refund_txn = PaymentTransaction(
        order_id=order.id,
        merchant_id=order.merchant_id,
        type="refund",
        gateway="asaas",
        gateway_transaction_id=refund["id"],
        amount_cents=-amount_cents,
        fee_cents=refund.get("fee", 0),
        status="completed",
        paid_at=datetime.now(),
    )
    await db.add(refund_txn)
    await db.commit()

    # 4. Notificar cliente
    await notify_refund_processed(order, amount_cents)
```

### 10.3 Chargeback (Cartão)

Chargeback é quando o cliente contesta a cobrança no cartão junto ao banco.

```
Fluxo de chargeback:
  1. Banco do cliente contesta a cobrança
  2. Asaas notifica RapiDrop via webhook
  3. RapiDrop notifica lojista:
     "⚠️ Pedido #42 — Chargeback de R$ 100,00
      Motivo: Cliente não reconhece a compra
      Prazo para defesa: 7 dias"
  4. Lojista pode:
     a. Aceitar: RapiDrop estorna, lojista perde o valor
     b. Contestar: enviar comprovantes para defesa
  5. Se perder: RapiDrop debita do lojista (próxima fatura ou split futuro)
  6. Se ganhar: chargeback revertido, nada acontece
```

**Política de chargeback:**
- Lojista é responsável pelo chargeback (foi o cliente dele)
- Se lojista estiver no split: próximo split é reduzido
- Se lojista estiver na fatura: próximo mês vem com acréscimo
- Chargeback frequente (> 1% dos pedidos) → revisão de conta

---

## 11. Conciliação

### 11.1 Conciliação Diária Automatizada

Todo dia às 06:00, um job de conciliação roda:

```python
@celery.task
async def daily_reconciliation(date: date = None):
    """
    Concilia pedidos do dia com transações do gateway.
    Roda todo dia às 06:00.
    """
    date = date or date.today() - timedelta(days=1)

    # 1. Buscar todos os pedidos ENTREGUES do dia
    orders = await db.query(Order).filter(
        Order.delivered_at.between(date, date + timedelta(days=1)),
        Order.status.in_(["entregue", "finalizado"]),
    ).all()

    # 2. Buscar transações do gateway no mesmo período
    gateway_txns = await asaas_client.get_payments(
        date_start=date.isoformat(),
        date_end=(date + timedelta(days=1)).isoformat(),
    )

    # 3. Matching: order.id ↔ gateway payment.description
    matched = []
    unmatched_orders = []
    unmatched_txns = []

    for order in orders:
        txn = find_matching_transaction(order, gateway_txns)
        if txn:
            matched.append((order, txn))
        else:
            unmatched_orders.append(order)

    for txn in gateway_txns:
        if not any(txn["id"] == m[1]["id"] for m in matched):
            unmatched_txns.append(txn)

    # 4. Registrar resultados
    reconciliation = Reconciliation(
        date=date,
        total_orders=len(orders),
        matched=len(matched),
        unmatched_orders=unmatched_orders,
        unmatched_transactions=unmatched_txns,
        total_value_cents=sum(o.total_cents for o in orders),
        total_gateway_cents=sum(t["value"] * 100 for t in gateway_txns),
        discrepancy_cents=abs(
            sum(o.total_cents for o in orders) -
            sum(t["value"] * 100 for t in gateway_txns)
        ),
    )

    # 5. Se houver divergência, alertar
    if reconciliation.discrepancy_cents > 0:
        alerts.send(
            channel="slack",
            severity="warning",
            title="⚠️ Divergência na conciliação",
            message=f"{len(unmatched_orders)} pedidos sem transação, "
                    f"{len(unmatched_txns)} transações sem pedido",
        )

    return reconciliation
```

### 11.2 Regras de Matching

| Critério | Como |
|----------|------|
| Pedido pago via gateway | `payment_transaction.gateway_id` = Asaas payment ID |
| Pedido em dinheiro | Sem transação no gateway. Match manual (conferência do lojista) |
| Fatura paga | `invoice.asaas_payment_id` = Asaas payment ID |
| Estorno | `payment_transaction.type = 'refund'` + valor negativo |

### 11.3 Dashboard de Conciliação (Admin)

```
┌────────────────────────────────────────────────────────┐
│  CONCILIAÇÃO — 15/06/2026                               │
├────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ 142 pedidos conciliados                              │
│  ⚠️  3 pedidos sem transação (dinheiro/cartão entrega)  │
│  ℹ️  0 transações sem pedido                            │
│                                                          │
│  Valor total pedidos:  R$ 7.352,00                      │
│  Valor total gateway:  R$ 5.800,00                      │
│  Diferença:           R$ 1.552,00 (💰 dinheiro)        │
│                                                          │
│  Pendências:                                             │
│  ┌───┬────────────┬──────────┬──────────────────────┐   │
│  │ # │ Pedido     │ Valor    │ Situação             │   │
│  ├───┼────────────┼──────────┼──────────────────────┤   │
│  │ 1 │ #1289      │ R$ 45,00 │ Dinheiro — OK        │   │
│  │ 2 │ #1292      │ R$ 78,00 │ Dinheiro — OK        │   │
│  │ 3 │ #1295      │ R$ 32,00 │ Dinheiro — OK        │   │
│  └───┴────────────┴──────────┴──────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

## 12. Inadimplência e Dunning

### 12.1 Ciclo de Cobrança (Fase 1 — Fatura)

```
DIA 1:  Fatura gerada e enviada (WhatsApp + Email)
        ─ Status: "pending"

DIA 7:  Vencimento
        ─ Se não pago: status → "overdue"
        ─ Disparar notificação: "Fatura #42 venceu! Pague agora"

DIA 10: Reenvio da fatura + tom mais firme
        ─ "Seu plano pode ser suspenso em 5 dias"

DIA 15: Suspensão do plano
        ─ merchant.plan_status → "suspended"
        ─ Dashboard bloqueado (lojista não acessa)
        ─ Pedidos NOVOS não são aceitos
        ─ Entregas em andamento continuam (para não prejudicar clientes)
        ─ WhatsApp: "Seu acesso foi suspenso. Regularize para reativar."

DIA 30: Cancelamento
        ─ merchant.plan_status → "cancelled"
        ─ Todos os dados mantidos por 90 dias (LGPD)
        ─ Após 90 dias: dados anonimizados
```

### 12.2 Regras de Suspensão

| O que acontece | Antes da suspensão | Durante suspensão | Após cancelamento |
|----------------|:------------------:|:-----------------:|:-----------------:|
| Dashboard lojista | ✅ Normal | ❌ Bloqueado | ❌ Bloqueado |
| Pedidos novos | ✅ Normal | ❌ Bloqueado | ❌ Removido |
| Entregas em andamento | ✅ Normal | ✅ Continuam | ✅ Continuam |
| Página white-label | ✅ Online | ❌ Offline | ❌ Offline |
| App entregador | ✅ Normal | ❌ Apenas entregas ativas | ❌ Bloqueado |
| Dados do lojista | — | Mantidos | 90 dias |
| Reativação | — | ✅ Automática após pagamento | ❌ Novo cadastro |

### 12.3 Dunning Automático

```python
@celery.task
async def dunning_check():
    """
    Roda todo dia. Verifica faturas vencidas e executa ações.
    """
    overdue = await db.query(Invoice).filter(
        Invoice.status == "overdue",
        Invoice.due_date < datetime.now(),
    ).all()

    for invoice in overdue:
        days_overdue = (datetime.now() - invoice.due_date).days
        merchant = await db.get(Merchant, invoice.merchant_id)

        match days_overdue:
            case 0 | 1 | 2:
                # Apenas lembrete
                await send_whatsapp(
                    merchant.phone,
                    "invoice_reminder",
                    {"invoice_id": invoice.id, "amount": invoice.display_amount},
                )
            case 3 | 4 | 5 | 6:
                # Lembrete + urgência
                await send_whatsapp(
                    merchant.phone,
                    "invoice_urgent",
                    {"invoice_id": invoice.id, "days": 7 - days_overdue},
                )
            case 7 | 8:
                # Alerta de suspensão
                await send_whatsapp(
                    merchant.phone,
                    "invoice_suspension_warning",
                    {"invoice_id": invoice.id, "suspension_date": ...},
                )
            case 9:
                # Suspender
                merchant.plan_status = "suspended"
                await db.commit()
                await send_whatsapp(
                    merchant.phone,
                    "account_suspended",
                    {"invoice_id": invoice.id},
                )
```

---

## 13. Implicações Fiscais

### 13.1 Modelo Tributário

| Cenário | Impostos | Observação |
|---------|----------|------------|
| **Fatura mensal (Fase 1)** | RapiDrop emite NF para o lojista | Simples: RapiDrop presta serviço ao lojista |
| **Split (Fase 2)** | RapiDrop emite NF para o lojista sobre a taxa | Asaas emite NF para o lojista sobre o repasse |
| **Repasse ao lojista** | Não tributável pelo RapiDrop | Dinheiro não passa pelo RapiDrop |
| **Taxa de pagamento (gateway)** | Asaas emite NF para o lojista | Custa do lojista |

### 13.2 Regime Tributário do RapiDrop

- **Recomendação:** Simples Nacional (anexo III ou IV, dependendo da atividade)
- **Atividade principal:** "Desenvolvimento e licenciamento de software SaaS"
- **CNAE sugerido:** 6201-5/01 (Desenvolvimento de programas de computador)
- **ISS:** 2-5% sobre o faturamento (depende do município)

### 13.3 Nota Fiscal

| Evento | NF emitida por | Para | Quando |
|--------|---------------|------|--------|
| Taxa SaaS (split) | RapiDrop | Lojista | Mensal (nota consolidada) |
| Taxa SaaS (fatura) | RapiDrop | Lojista | Junto com a fatura |
| Taxa de gateway | Asaas | Lojista | A cada transação |
| Repasse ao lojista | Asaas | Lojista | A cada repasse |

---

## 14. Modelo de Dados (Tabelas Financeiras)

```sql
-- Transação financeira (cobrança de pedido ou estorno)
CREATE TABLE payment_transaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id INTEGER REFERENCES orders(id),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    type VARCHAR(20) NOT NULL,           -- 'charge' | 'refund' | 'chargeback'
    gateway VARCHAR(30) NOT NULL,        -- 'asaas' | 'stripe'
    gateway_id VARCHAR(100),
    gateway_split_id VARCHAR(100),
    method VARCHAR(20) NOT NULL,         -- 'pix' | 'credit_card' | 'debit_card' | 'cash' | 'boleto'
    amount_cents INTEGER NOT NULL,       -- positivo para charge, negativo para refund
    fee_cents INTEGER DEFAULT 0,         -- taxa do gateway
    rapidrop_fee_cents INTEGER DEFAULT 0, -- nossa taxa (para split)
    merchant_net_cents INTEGER,          -- líquido do lojista (para split)
    installments INTEGER DEFAULT 1,      -- parcelamento
    status VARCHAR(20) NOT NULL,         -- 'pending' | 'completed' | 'failed' | 'refunded'
    paid_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Fatura mensal do lojista (Fase 1 e fallback para dinheiro)
CREATE TABLE invoice (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    amount_cents INTEGER NOT NULL,
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_orders_value_cents INTEGER NOT NULL DEFAULT 0,
    rate NUMERIC(4,3) NOT NULL,          -- 0.020 ou 0.015
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 'pending' | 'paid' | 'overdue' | 'cancelled'
    asaas_payment_id VARCHAR(100),       -- ID do pagamento no Asaas
    payment_method VARCHAR(20),
    paid_at TIMESTAMPTZ,
    due_date DATE NOT NULL,
    overdue_days INTEGER DEFAULT 0,
    dunning_stage INTEGER DEFAULT 0,    -- 0 = nenhuma, 1-5 = estágios
    details JSONB,                       -- breakdown por pedido
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conciliação diária
CREATE TABLE reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    total_orders INTEGER NOT NULL,
    total_orders_value_cents INTEGER NOT NULL,
    total_gateway_transactions INTEGER NOT NULL,
    total_gateway_value_cents INTEGER NOT NULL,
    matched INTEGER NOT NULL,
    unmatched_orders INTEGER NOT NULL,
    unmatched_transactions INTEGER NOT NULL,
    discrepancy_cents INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ok',
    -- 'ok' | 'discrepancy' | 'investigating'
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conciliação manual (para dinheiro/cartão na entrega)
CREATE TABLE manual_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    date DATE NOT NULL,
    order_id INTEGER REFERENCES orders(id),
    amount_cents INTEGER NOT NULL,
    method VARCHAR(20) NOT NULL,         -- 'cash' | 'card_on_delivery'
    confirmed_by INTEGER,                -- who_id do lojista
    confirmed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Subconta Asaas do lojista
CREATE TABLE merchant_gateway_account (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER NOT NULL UNIQUE REFERENCES merchants(id),
    gateway VARCHAR(30) NOT NULL DEFAULT 'asaas',
    account_id VARCHAR(100) NOT NULL,    -- ID da subconta no Asaas
    wallet_id VARCHAR(100),              -- wallet para split
    account_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 'pending' | 'active' | 'blocked' | 'rejected'
    onboarding_url VARCHAR(500),
    onboarded_at TIMESTAMPTZ,
    blocked_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_payment_txn_order ON payment_transaction(order_id);
CREATE INDEX idx_payment_txn_merchant ON payment_transaction(merchant_id, created_at DESC);
CREATE INDEX idx_payment_txn_gateway ON payment_transaction(gateway_id);
CREATE INDEX idx_invoice_merchant ON invoice(merchant_id, period_start DESC);
CREATE INDEX idx_invoice_status ON invoice(status) WHERE status IN ('pending', 'overdue');
CREATE INDEX idx_reconciliation_date ON reconciliation(date DESC);
```

---

## 15. Estratégia de Implementação

### 15.1 Fase 1 — MVP (Fatura Mensal)

```
Semanas 1-2:
  [ ] Criar tabelas: payment_transaction, invoice
  [ ] Implementar cálculo da fatura mensal
  [ ] Gerar fatura no Asaas (cobrança avulsa)
  [ ] Webhook de pagamento da fatura
  [ ] Dashboard do lojista: resumo financeiro básico

Semanas 3-4:
  [ ] Fluxo de dunning (lembretes automáticos)
  [ ] Suspensão automática por inadimplência
  [ ] Conciliação manual para dinheiro/cartão entrega
  [ ] Extrato do entregador (apenas cálculo, pagamento pelo lojista)
```

### 15.2 Fase 2 — Split Automático

```
  [ ] Registrar RapiDrop como plataforma Asaas
  [ ] Implementar embedded onboarding de subcontas
  [ ] Criar pagamentos com split no Asaas
  [ ] Tratar estorno em pagamentos splitados
  [ ] Conciliação automática (match pedido × transação)
  [ ] Dashboard financeiro completo do lojista
```

### 15.3 Integração com Asaas

```python
# Cliente Asaas
class AsaasClient:
    def __init__(self, api_key: str, environment: str = "sandbox"):
        self.base_url = (
            "https://sandbox.asaas.com/api/v3"
            if environment == "sandbox"
            else "https://api.asaas.com/v3"
        )
        self.api_key = api_key

    async def create_customer(self, data: dict) -> dict:
        """Cria/consulta cliente no Asaas."""
        ...

    async def create_payment(self, data: dict) -> dict:
        """Cria cobrança (PIX, cartão, boleto)."""
        ...

    async def create_subaccount(self, data: dict) -> dict:
        """Cria subconta para lojista receber splits."""
        ...

    async def refund_payment(self, payment_id: str, value: float | None = None) -> dict:
        """Estorna pagamento total ou parcial."""
        ...

    async def get_payments(
        self,
        date_start: str,
        date_end: str,
        status: str | None = None,
    ) -> list[dict]:
        """Lista pagamentos para conciliação."""
        ...
```

---

## 16. Cobertura de Testes

### 16.1 Testes de Unidade

```python
# Cálculo de fatura
def test_invoice_calculates_correct_rate():
    """Fatura aplica taxa correta do segmento."""
    ...

def test_invoice_skips_cancelled_before_prep():
    """Pedidos cancelados antes do preparo não entram na fatura."""
    ...

def test_invoice_includes_cancelled_during_prep():
    """Pedidos cancelados durante preparo entram na fatura."""
    ...

def test_invoice_free_trial_no_charge():
    """Meses de trial (1-2) não geram cobrança."""
    ...

# Split
def test_split_calculates_exact_values():
    """Split calcula valores corretos sem arredondamento."""
    ...

def test_split_handles_1_cent_orders():
    """Pedidos de R$ 1,00: 2 centavos de taxa, 98 centavos pro lojista."""
    ...

# Reembolso
def test_refund_full_before_confirmation():
    """Cancelado antes da confirmação: reembolso integral, sem taxa."""
    ...

def test_refund_partial_after_delivery():
    """Cancelado após saída: reembolso parcial, taxa cobrada."""
    ...

# Conciliação
def test_daily_reconciliation_matches_all():
    """Conciliação diária encontra match para todos os pedidos pagos."""
    ...

def test_daily_reconciliation_alerts_discrepancy():
    """Conciliação alerta se houver divergência de valores."""
    ...

# Dunning
def test_dunning_suspends_after_9_days():
    """Lojista é suspenso após 9 dias de inadimplência."""
    ...

def test_dunning_reactivates_on_payment():
    """Lojista é reativado automaticamente ao pagar fatura."""
    ...
```

### 16.2 Testes de Integração

```python
# Asaas webhook
def test_asaas_webhook_payment_confirmed():
    """Webhook de confirmação de pagamento atualiza fatura."""
    ...

def test_asaas_webhook_payment_refunded():
    """Webhook de estorno registra transação de reembolso."""
    ...

# Fluxo completo
def test_customer_pays_with_pix_order_flow():
    """Cliente paga com PIX → split → lojista recebe líquido."""
    ...

def test_customer_pays_with_cash_invoice_flow():
    """Cliente paga com dinheiro → fatura no fim do mês."""
    ...
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Baseado nos documentos:** `docs/assinatura-saas.md`, `docs/pagamento-entregadores.md`,
> `docs/maquina-estados-pedido.md`, `docs/stack-completa.md`
> **Próximo documento sugerido:** `docs/onboarding-lojista.md`
