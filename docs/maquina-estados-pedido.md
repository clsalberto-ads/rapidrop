# RapiDrop — Máquina de Estados do Pedido

> Especificação formal dos estados, transições, regras e eventos do ciclo de vida
> do pedido. Este documento é a **fonte única da verdade** para o comportamento
> do pedido em todos os módulos (dashboard, notificações, billing, audit, analytics).

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Mapa Mestre de Estados](#2-mapa-mestre-de-estados)
3. [Tabela de Transições](#3-tabela-de-transições)
4. [Variações por Segmento](#4-variações-por-segmento)
5. [Estados Concorrentes](#5-estados-concorrentes)
6. [Timeouts e SLA](#6-timeouts-e-sla)
7. [Cancelamentos e Reembolsos](#7-cancelamentos-e-reembolsos)
8. [Tabela de Eventos](#8-tabela-de-eventos)
9. [Casos de Exceção](#9-casos-de-exceção)
10. [Estratégia de Implementação](#10-estratégia-de-implementação)
11. [Cobertura de Testes](#11-cobertura-de-testes)
12. [Glossário](#12-glossário)

---

## 1. Visão Geral

### 1.1 Propósito

A máquina de estados do pedido define **exatamente** como um pedido se comporta
em cada momento do seu ciclo de vida: o que pode acontecer, quem pode fazer
acontecer, e o que o sistema precisa fazer quando acontece.

Sem ela, cada desenvolvedor interpreta "confirmar pedido" de um jeito diferente,
notificações são esquecidas, billing erra valores, e o audit log fica incompleto.

### 1.2 Princípios

| Princípio | Implicação |
|-----------|------------|
| **Determinístico** | Dado um estado atual + transição, o resultado é sempre o mesmo. Não há decisão baseada em "estado atual do sistema" (ex: horário, fila). |
| **Transições explícitas** | Toda mudança de estado é uma transição registrada. Nunca se muda `order.status` diretamente no banco. Sempre via `transition(state_machine, event)`. |
| **Auditável** | Cada transição gera um registro imutável em `audit_log` com `from_status`, `to_status`, `who`, `when`, `why`. |
| **Testável** | Cada transição é um teste. Cada guarda é um teste. Cada exceção é um teste. |
| **Segment-aware** | Regras diferentes por segmento (farmácia, mercado, comida) são explícitas — não escondidas em ifs. |

### 1.3 Design Decisions

1. **Uma única máquina de estados** para o pedido, com variações por segmento.
   Não criar máquinas separadas para cada segmento — a manutenção não escala.

2. **Estados concorrentes separados** para entregador e pagamento.
   `order.status` reflete o estado do pedido. `order_rider.status` reflete a
   entrega. `order.payment_status` reflete o pagamento. São paralelos mas
   acoplados por regras de guarda.

3. **`cancelado` é um estado terminal único**, mas com metadados de motivo.
   O campo `order.cancellation_reason` enum explica por que foi cancelado
   (cliente, lojista, sistema, pagamento_recusado, timeout, etc.).
   As regras de reembolso dependem do **ponto onde foi cancelado**, não do motivo.

4. **Estados de transição automática são preferíveis a timers no frontend.**
   O backend é o dono do tempo. O frontend apenas reflete o estado atual.

---

## 2. Mapa Mestre de Estados

### 2.1 Diagrama — Fluxo Base (Todos os Segmentos)

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                     FLUXO BASE (TODOS)                       │
                    └─────────────────────────────────────────────────────────────┘

                       ┌──────────┐
                       │   NOVO   │
                       └────┬─────┘
                            │ (automático, após validação)
                            ▼
  ┌───────────────────────────────────┐
  │          PENDENTE                 │ ←── Aguardando confirmação do lojista
  └──────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│CONFIRMADO│    │CANCELADO │ ←── Se lojista recusar ou timeout
└────┬─────┘    └──────────┘
     │
     ▼
┌──────────┐
│EM PREPARO│
└────┬─────┘
     │
     ▼
┌──────────┐
│  PRONTO  │ ←── Pedido pronto para retirada
└────┬─────┘
     │
     ▼
┌──────────────────┐
│SAIU P/ ENTREGA   │ ←── Entregador saiu da loja
└─────────┬────────┘
          │
          ▼
┌──────────┐
│ ENTREGUE │ ←── Cliente recebeu
└────┬─────┘
     │ (processamento pós-entrega)
     ▼
┌────────────┐
│ FINALIZADO │ ←── Billing, analytics, notificações processados
└────────────┘

CANCELADO pode ocorrer de QUALQUER estado antes de ENTREGUE.
Cada ponto de cancelamento tem regras diferentes de reembolso e billing.
```

### 2.2 Definição dos Estados

| # | Estado | Descrição | É Terminal? | Tempo Máximo |
|---|--------|-----------|:-----------:|:------------:|
| 1 | `novo` | Pedido acabou de chegar no sistema. Validação inicial em andamento. | Não | Instantâneo (transição automática) |
| 2 | `pendente` | Pedido validado, aguardando o lojista confirmar. | Não | 30 min |
| 3 | `confirmado` | Lojista aceitou o pedido. Início do preparo iminente. | Não | — |
| 4 | `em_preparo` | Pedido sendo preparado (cozinha, separação de estoque). | Não | Configurável por lojista/produto |
| 5 | `pronto` | Pedido pronto, aguardando retirada pelo entregador. | Não | 15 min (alerta se demorar) |
| 6 | `saiu_para_entrega` | Entregador saiu com o pedido. Em rota. | Não | ETA + 30 min |
| 7 | `entregue` | Cliente recebeu o pedido. Entrega concluída. | Não | — |
| 8 | `finalizado` | Processamento pós-entrega completo (billing, analytics, audit). | **Sim** ✅ | Imediato após `entregue` |
| 9 | `cancelado` | Pedido cancelado. Estado terminal. | **Sim** ✅ | — |

### 2.3 Estados Específicos por Segmento

#### Farmácia — Estados Adicionais

```
                    NOVO
                     │
                     ▼
         ┌────────────────────┐
         │ AGUARDANDO RECEITA │ ←── Se produto requer prescrição
         └─────────┬──────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
  ┌──────────────┐   ┌──────────────┐
  │RECEITA       │   │RECEITA       │ ←── Rejeitada (ilegível,
  │VALIDADA      │   │REJEITADA     │     inválida, medicamento errado)
  └──────┬───────┘   └──────┬───────┘
         │                  │
         ▼                  ▼
    ┌──────────┐     ┌──────────────┐
    │ PENDENTE │     │AGUARDANDO    │ ←── Cliente pode reenviar
    └──────────┘     │REENVIO       │
                     └──────┬───────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
           ┌──────────────┐    ┌──────────┐
           │RECEITA       │    │CANCELADO │ ←── Se timeout sem reenvio
           │VALIDADA      │    └──────────┘
           └──────┬───────┘
                  │
                  ▼
             ┌──────────┐
             │ PENDENTE │
             └──────────┘
```

| Estado | Descrição | Aplica-se a |
|--------|-----------|:-----------:|
| `aguardando_receita` | Produto com tarja vermelha/preta — aguardando upload da receita | Farmácia |
| `receita_validada` | Receita verificada pelo farmacêutico — OK para prosseguir | Farmácia |
| `receita_rejeitada` | Receita rejeitada (ilegível, dados incorretos, medicamento não prescrito) | Farmácia |
| `aguardando_reenvio` | Cliente notificado para enviar nova receita | Farmácia |

#### Mercado — Estados Adicionais

```

            EM PREPARO
                │
                ▼
     ┌────────────────────┐
     │AGUARDANDO          │ ←── Item em falta, substituto pendente
     │SUBSTITUIÇÃO        │
     └─────────┬──────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐     ┌────────────────┐
│EM PREPARO│     │CANCELADO      │ ←── Se cliente rejeitar substituto
│(com item │     │PARCIAL        │     e não houver alternativa
│alternativo)    └────────────────┘
└──────────┘
```

| Estado | Descrição | Aplica-se a |
|--------|-----------|:-----------:|
| `aguardando_substituicao` | Item fora de estoque — aguardando cliente aprovar substituto | Mercado |
| `cancelado_parcial` | Item removido do pedido por falta/substituição rejeitada. Pedido continua. **Não é terminal** — o pedido prossegue sem o item. | Mercado |

> ⚠️ `cancelado_parcial` não é um estado terminal! O pedido continua com os
> demais itens. O valor é recalculado. A nomenclatura "cancelado" é
> infeliz mas mantida por clareza com o lojista (que diz "cancelou o item").

---

## 3. Tabela de Transições

Esta é a **especificação central**. Toda implementação deve refleti-la.

### Legenda

- **Guards (G):** Condições que DEVEM ser verdade para a transição ocorrer.
- **Ações (A):** Efeitos colaterais obrigatórios ao completar a transição.
- **Disparado por:** Quem ou o quê inicia a transição.
- **Segmento:** `T` = Todos, `F` = Farmácia, `M` = Mercado, `A` = Alimentação.

### 3.1 Tabela Mestra

| # | De | Para | Nome da Transição | Guards (G) | Ações (A) | Disparado por | Segmento |
|---|----|------|-------------------|-----------|-----------|---------------|:--------:|
| T1 | *(novo)* | `novo` | `order.created` | G1: Dados obrigatórios presentes (items, customer, merchant) | A1: Gerar ID sequencial por merchant. A2: Salvar no DB. A3: Audit log. | Sistema (qualquer canal) | T |
| T2 | `novo` | `pendente` | `order.pending` | G2: Pagamento pré-pago já confirmado (se aplicável). OU método de pagamento é pós-pago (dinheiro/cartão na entrega). | A4: Notificar lojista (som + push + WebSocket). A5: Disparar `order.new` via WebSocket. | Sistema (automático após criar) | T |
| T3 | `novo` | `aguardando_receita` | `order.awaiting_prescription` | G3: `segment_config.requires_prescription_check` = true. G4: Pelo menos 1 item com `tarja IN ('red','black')`. | A6: Notificar cliente via WhatsApp: "Envie a foto da receita". A7: Iniciar timer de timeout (2h). | Sistema (automático) | F |
| T4 | `aguardando_receita` | `receita_validada` | `prescription.validated` | G5: Farmacêutico validou receita. G6: Receita corresponde ao medicamento pedido. G7: Receita dentro do prazo de validade. | A8: Criptografar imagem da receita. A9: Salvar dados da validação (who, when). A10: Cancelar timer de timeout. A11: Mover para pendente. | Farmacêutico (dashboard) | F |
| T5 | `aguardando_receita` | `receita_rejeitada` | `prescription.rejected` | G8: Farmacêutico rejeitou. G9: Motivo informado (ilegível/incompleto/vencida/medicamento não corresponde). | A12: Notificar cliente via WhatsApp com motivo. A13: Solicitar reenvio. A14: Reset timer para 2h. | Farmacêutico (dashboard) | F |
| T6 | `receita_rejeitada` | `aguardando_reenvio` | `order.awaiting_retry` | G10: Cliente notificado. | A15: Iniciar timer de timeout (2h). | Sistema (automático) | F |
| T7 | `aguardando_reenvio` | `receita_validada` | `prescription.retry_validated` | Mesmos guards de T4. | Mesmas ações de T4. | Farmacêutico | F |
| T8 | `aguardando_reenvio` | `cancelado` | `prescription.timeout` | G11: Timer expirou (2h sem reenvio válido). | A16: Notificar cliente: "Pedido cancelado — receita não enviada". A17: Reembolso integral (se já pagou). | Sistema (timer) | F |
| T9 | `pendente` | `confirmado` | `order.confirmed` | G12: Lojista autenticado clica "Confirmar". | A18: WhatsApp cliente: "Seu pedido #X foi confirmado! 🎉". A19: WebSocket `order.confirmed`. A20: Audit log. A21: Se aplicável, imprimir pedido (cozinha/estoque). | Lojista (dashboard) | T |
| T10 | `pendente` | `cancelado` | `order.cancelled_by_merchant` | G13: Lojista autenticado clica "Cancelar". G14: Motivo informado. | A22: WhatsApp cliente: "Seu pedido #X foi cancelado". A23: Reembolso integral (se pagou). A24: Sem cobrança SaaS. A25: Audit log com motivo. | Lojista (dashboard) | T |
| T11 | `pendente` | `cancelado` | `order.cancelled_by_customer` | G15: Cliente solicita cancelamento (via WhatsApp/link). G16: Pedido ainda não está em preparo. | Mesmas ações de T10. | Cliente (whatsapp/link) | T |
| T12 | `pendente` | `cancelado` | `order.cancelled_timeout` | G17: Timer de 30 min expirou sem confirmação. | A26: WhatsApp cliente: "Seu pedido foi cancelado — lojista não confirmou". A27: Reembolso integral. A28: Notificar lojista: "Você perdeu um pedido por não confirmar a tempo". | Sistema (timer) | T |
| T13 | `pendente` | `cancelado` | `order.payment_expired` | G18: Método PIX: QR Code expirou sem pagamento. | A29: Notificar cliente: "Tempo de pagamento expirou". A30: Liberar estoque (itens reservados). | Sistema (timer/webhook) | T |
| T14 | `confirmado` | `em_preparo` | `order.preparation_started` | G19: Lojista (ou cozinha/estoque) clica "Iniciar Preparo". | A31: WebSocket `order.preparing`. A32: Iniciar timer de preparo. A33: Se farmácia: verificar refrigeração. A34: Se mercado: iniciar separação. | Lojista/Operador (dashboard ou tela de produção) | T |
| T15 | `confirmado` | `cancelado` | `order.cancelled_by_merchant_pre_prep` | G20: Lojista cancela antes de iniciar preparo. | A35: WhatsApp cliente: cancelamento. A36: Reembolso integral. A37: **Sem cobrança SaaS**. | Lojista | T |
| T16 | `em_preparo` | `pronto` | `order.ready` | G21: Lojista clica "Pronto". | A38: WebSocket `order.ready`. A39: Notificar sistema de atribuição de entregador. A40: Se entregador já atribuído: push "Pedido pronto para retirada". | Lojista/Operador | T |
| T17 | `em_preparo` | `aguardando_substituicao` | `order.substitution_needed` | G22: Item em falta. G23: Segmento = grocery. G24: Cliente precisa aprovar substituto. | A41: Notificar cliente via WhatsApp: "O item X está em falta. Aceita Y no lugar?". A42: Iniciar timer de substituição (30 min). A43: Pausar timer de preparo. | Sistema (lojista marca falta) | M |
| T18 | `aguardando_substituicao` | `em_preparo` | `order.substitution_accepted` | G25: Cliente aprovou substituto (ou sistema automático para regra "substituir automaticamente"). | A44: Atualizar item no pedido. A45: Se necessário, ajustar valor. A46: Retomar timer de preparo. | Cliente (WhatsApp) ou Sistema | M |
| T19 | `aguardando_substituicao` | `em_preparo` | `order.substitution_declined_removed` | G26: Cliente rejeitou substituto. G27: Item não é essencial (pedido prossegue sem ele). | A47: Remover item do pedido. A48: Recalcular valor total. A49: Registrar `cancelado_parcial` para o item. A50: Retomar timer de preparo. | Cliente (WhatsApp) | M |
| T20 | `aguardando_substituicao` | `cancelado` | `order.substitution_essential_declined` | G28: Cliente rejeitou substituto. G29: Item é essencial (pedido inteiro depende dele). | A51: WhatsApp cliente: "Pedido cancelado pois o item principal está em falta". A52: Reembolso integral. A53: **Sem cobrança SaaS** (cancelado antes de sair). | Sistema | M |
| T21 | `aguardando_substituicao` | `cancelado` | `order.substitution_timeout` | G30: Timer 30 min expirou sem resposta. | A54: Rejeitar automaticamente. A55: Se item essencial → cancelar pedido. Se não → remover item e prosseguir. | Sistema (timer) | M |
| T22 | `em_preparo` | `cancelado` | `order.cancelled_by_merchant_during_prep` | G31: Lojista cancela durante preparo. G32: Motivo informado. | A56: WhatsApp cliente: "Seu pedido foi cancelado". A57: **Reembolso integral.** A58: **Cobra taxa SaaS** 🔴 (preparo consumiu recursos). A59: Audit log. | Lojista | T |
| T23 | `pronto` | `saiu_para_entrega` | `order.out_for_delivery` | G33: Entregador registrou saída. G34: Entregador atribuído e na loja. | A60: GPS tracking do entregador começa a ser compartilhado. A61: WhatsApp cliente: "Seu pedido saiu para entrega! 🚗". A62: WebSocket `order.out_for_delivery`. A63: Iniciar timer de ETA. | Entregador (app) | T |
| T24 | `pronto` | `cancelado` | `order.cancelled_after_ready` | G35: Pedido pronto mas não saiu. G36: Lojista ou cliente solicita. | A64: Notificar cliente/lojista. A65: **Reembolso parcial** (política do lojista — mínimo 50%). A66: **Cobra taxa SaaS.** | Lojista ou Cliente | T |
| T25 | `saiu_para_entrega` | `entregue` | `order.delivered` | G37: Entregador clica "Entregue". G38: (Opcional) Prova de entrega (foto/assinatura) capturada. | A67: Parar timer. A68: WhatsApp cliente: "Pedido entregue! 🎉". A69: WebSocket `order.delivered`. A70: Iniciar processamento pós-entrega (billing, analytics, extrato entregador). A71: Transição automática para `finalizado` após processamento. | Entregador (app) | T |
| T26 | `saiu_para_entrega` | `entregue` | `order.delivered_customer_confirmed` | G39: Cliente confirma recebimento via link/WhatsApp. G40: (Fallback) Entregador não conseguiu marcar no app. | Mesmas ações de T25. | Cliente (link/WhatsApp) | T |
| T27 | `saiu_para_entrega` | `cancelado` | `order.cancelled_during_delivery` | G41: Entregador retornou (cliente não encontrado, endereço errado, recusou receber). G42: Lojista confirma retorno. | A72: WhatsApp cliente: "Pedido retornou ao estabelecimento". A73: **Reembolso parcial** (deduzir custo de entrega). A74: **Cobra taxa SaaS.** A75: Registrar motivo da falha de entrega. | Entregador + Lojista | T |
| T28 | `entregue` | `finalizado` | `order.finalized` | G43: Processamento pós-entrega completo (billing, analytics, atualização de rankings). | A76: Nenhuma ação visível ao usuário. A77: Registro de conclusão no audit log. | Sistema (automático) | T |
| T29 | `entregue` | `cancelado` | `order.cancelled_after_delivery` | G44: (Raro) Estorno por acordo lojista-cliente pós-entrega. G45: Aprovado por supervisor. | A78: **Reembolso ao cliente.** A79: **Estorno da taxa SaaS não é feito** (serviço foi prestado). A80: Pedido permanece como entregue para métricas, mas financeiro é estornado. | Lojista + Admin | T |

### 3.2 Transições Proibidas (Validações)

Algumas transições parecem óbvias mas precisam ser **explicitamente proibidas**:

| Transição | Por que é proibida |
|-----------|-------------------|
| `entregue` → `saiu_para_entrega` | Pedido entregue não pode voltar para rota. |
| `cancelado` → qualquer estado | Estado terminal. Imutável. |
| `finalizado` → qualquer estado | Estado terminal. Imutável. |
| `em_preparo` → `pendente` | Preparo não pode ser desfeito. |
| `em_preparo` → `confirmado` | Preparo não pode ser desfeito. |
| `saiu_para_entrega` → `pronto` | Entregador não pode voltar. |
| Pular `confirmado` (ex: `pendente` → `em_preparo`) | Lojista precisa confirmar antes de preparar. |
| Pular `saiu_para_entrega` (ex: `pronto` → `entregue`) | Entregador precisa registrar saída. |

---

## 4. Variações por Segmento

### 4.1 Alimentação (Fluxo Base)

O fluxo mais simples. Usa os estados base sem modificações.

```
novo → pendente → confirmado → em_preparo → pronto → saiu_para_entrega → entregue → finalizado
```

**Particularidades:**
- `em_preparo` mapeia para tela de **cozinha** (pedido vai para a produção)
- Tempo de preparo é estimado por produto (`product.prep_time_minutes`)
- Atraso crítico: pizza que queima, hambúrguer que esfria
- Impressão automática do pedido na cozinha ao `confirmado` (se houver impressora térmica)

### 4.2 Farmácia

Fluxo extendido com validação de receitas.

```
                    ┌──────────────────┐      ┌──────────────────┐
                    │  NOVO            │      │  CANCELADO       │
                    │  (com receita)   │───►  │  (receita não    │
                    └────────┬─────────┘      │  enviada/timeout)│
                             │                └──────────────────┘
                             ▼
                    ┌──────────────────┐
                    │  AGUARDANDO      │
                    │  RECEITA         │
                    └────────┬─────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  RECEITA         │  │  RECEITA         │
          │  VALIDADA        │  │  REJEITADA       │
          └────────┬─────────┘  └────────┬─────────┘
                   │                     │
                   ▼                     ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  PENDENTE        │  │  AGUARDANDO      │
          │  (segue fluxo    │  │  REENVIO         │
          │   base)          │  └────────┬─────────┘
          └──────────────────┘           │
                                  ┌──────┴──────┐
                                  │             │
                                  ▼             ▼
                          ┌────────────┐  ┌──────────┐
                          │  RECEITA   │  │CANCELADO │
                          │  VALIDADA  │  │(timeout) │
                          └─────┬──────┘  └──────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  PENDENTE        │
                       └──────────────────┘
```

**Particularidades:**
- **Validação de receita é obrigatória** para medicamentos de tarja vermelha e preta
- Medicamentos de tarja preta exigem validação **mais rigorosa** (receita especial, retenção)
- Medicamentos sem tarja (MIPs): seguem fluxo normal, sem `aguardando_receita`
- **Refrigeração**: itens com `requires_refrigeration = true` disparam alerta no `saiu_para_entrega`
- **Idade mínima**: verificação no checkout para medicamentos com restrição de idade
- **Registro de dispensação**: obrigatório para medicamentos controlados

### 4.3 Mercado

Fluxo extendido com substituição de itens e suporte a pedidos grandes.

```
em_preparo → (se item em falta) → aguardando_substituicao
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                          ▼           ▼           ▼
                    ┌──────────┐ ┌──────────┐ ┌──────────┐
                    │  Cliente │ │  Cliente │ │  Timeout │
                    │  aceitou │ │  rejeitou│ │  (30 min)│
                    └────┬─────┘ └────┬─────┘ └────┬─────┘
                         │            │            │
                         ▼            ▼            ▼
                    ┌──────────┐ ┌──────────┐ ┌──────────┐
                    │em_preparo│ │em_preparo│ │  Auto-   │
                    │(c/ subs) │ │(s/ item) │ │  rejeitar│
                    └──────────┘ └────┬─────┘ └────┬─────┘
                                      │            │
                                      ▼            ▼
                                ┌──────────┐ ┌──────────┐
                                │cancelado │ │em_preparo│
                                │_parcial  │ │(s/ item) │
                                └──────────┘ └──────────┘
```

**Particularidades:**
- **Substituição**: cada produto pode ter um `substitute_product_id` configurado pelo lojista
- **Item essencial**: campo `is_essential` no item do pedido. Se true e não há substituto → pedido cancela
- **Peso fracionado**: itens por peso (kg, g) podem ser ajustados no `em_preparo` (ex: "300g de queijo" → "só temos 250g")
- **Janela de entrega**: pedidos de mercado podem ter janela agendada (ex: "Hoje 14h-16h"). Nesse caso, o pedido pode ficar em `pronto` por mais tempo até a janela.
- **Múltiplas entregas**: pedidos grandes podem ser divididos em múltiplas saídas. Ver [Casos de Exceção](#9-casos-de-exceção).
- **Mínimo por pedido**: configurado pelo lojista. Verificado no checkout, mas pode ser relaxado no `confirmado`.

### 4.4 Resumo das Diferenças por Segmento

| Aspecto | Alimentação | Farmácia | Mercado |
|---------|:-----------:|:--------:|:-------:|
| Estados exclusivos | — | `aguardando_receita`, `receita_validada`, `receita_rejeitada`, `aguardando_reenvio` | `aguardando_substituicao`, `cancelado_parcial` |
| Validação extra no checkout | — | Receita para tarja vermelha/preta, idade | Valor mínimo, janela de entrega |
| Tela de produção | Cozinha | Farmácia (balcão) | Estoque/Expedição |
| Tempo de preparo | Por produto (min) | Instantâneo (separação) | Por produto + volume |
| Agendamento | Não | Não | Sim (janela de entrega) |
| Substituição de item | Não se aplica | Não se aplica | Sim (regra de negócio) |
| Múltiplas entregas | Raro | Não | Sim (pedidos grandes) |
| Impressão automática | Sim (cozinha) | Sim (balcão) | Sim (expedição) |

---

## 5. Estados Concorrentes

O `order.status` não conta a história completa. Dois processos paralelos afetam
o comportamento do pedido: a **atribuição do entregador** e o **pagamento**.

### 5.1 Atribuição do Entregador (`order_rider.status`)

O entregador tem seu próprio ciclo de vida, que corre em paralelo ao pedido.

```
 Estados do Pedido:                  Estados do Entregador:

 confirmado ──► em_preparo ──► pronto ──► saiu_para_entrega ──► entregue
                                  ▲            ▲                      ▲
                                  │            │                      │
                    ┌─────────────┘            │                      │
                    │                          │                      │
                    ▼                          │                      │
     ┌────────────────────────┐               │                      │
     │  não_atribuido          │               │                      │
     └─────────┬──────────────┘               │                      │
               │                              │                      │
               ▼                              │                      │
     ┌────────────────────────┐               │                      │
     │  atribuido              │               │                      │
     └─────────┬──────────────┘               │                      │
               │                              │                      │
               ▼                              │                      │
     ┌────────────────────────┐               │                      │
     │  a_caminho_da_loja    │               │                      │
     └─────────┬──────────────┘               │                      │
               │                              │                      │
               ▼                              │                      │
     ┌────────────────────────┐ ◄─────────────┘                      │
     │  na_loja               │  (pronto = pode retirar)              │
     └─────────┬──────────────┘                                      │
               │                                                      │
               ▼                                                      │
     ┌────────────────────────┐ ◄────────────────────────────────────┘
     │  saiu_para_entrega    │  (saiu_para_entrega = entregador saiu)
     └─────────┬──────────────┘
               │
               ▼
     ┌────────────────────────┐
     │  entregue              │
     └────────────────────────┘
```

**Transições do Entregador:**

| # | De | Para | Condição | Disparado por |
|---|----|------|----------|---------------|
| R1 | *(none)* | `nao_atribuido` | Pedido em `confirmado` ou `em_preparo` | Sistema (automático) |
| R2 | `nao_atribuido` | `atribuido` | Lojista seleciona entregador OU sistema atribui automaticamente | Lojista ou Sistema |
| R3 | `atribuido` | `a_caminho_da_loja` | Entregador aceitou a corrida e está vindo | Entregador (app) |
| R4 | `atribuido` | `nao_atribuido` | Entregador recusou ou não respondeu em 2 min | Sistema (timeout) |
| R5 | `a_caminho_da_loja` | `na_loja` | Entregador chegou (geofence + confirmação) | Sistema (geo) ou Entregador |
| R6 | `na_loja` | `saiu_para_entrega` | Pedido está `pronto` E entregador saiu | Entregador (app) |
| R7 | `saiu_para_entrega` | `entregue` | Entregador finalizou | Entregador (app) |
| R8 | `saiu_para_entrega` | `na_loja` | (Exceção) Cliente não encontrado — retornando | Entregador + Lojista |

**Regras de acoplamento Pedido × Entregador:**

| Regra | Descrição |
|-------|-----------|
| Pedido pode ser atribuído a partir de `confirmado` | Mais cedo = melhor para o entregador se programar |
| Pedido **não** sai sem entregador atribuído | `saiu_para_entrega` exige `order_rider.status = na_loja` |
| Se pedido está `pronto` e entregador não atribuído → **alerta de gargalo** | Dashboard mostra "Pedido pronto aguardando entregador" |
| Se entregador chegou (`na_loja`) e pedido não está `pronto` → **tempo de espera** | Registrado em métrica `rider_wait_time` |
| Troca de entregador: possível apenas se `order_rider.status IN ('nao_atribuido','atribuido')` | Após `a_caminho_da_loja`, só o lojista pode substituir |

### 5.2 Pagamento (`order.payment_status`)

O pagamento é um estado separado que corre em paralelo ao pedido.

```
Estados de Pagamento:

fluxo pré-pago (PIX / cartão online):
  aguardando_pagamento → autorizado → capturado → liquidado
       │                     │
       ▼                     ▼
  expirado               estornado

fluxo pós-pago (dinheiro / cartão na entrega):
  pendente_na_entrega → recebido_na_entrega → liquidado
                             │
                             ▼
                        estornado
```

**Tabela de Estados de Pagamento:**

| Estado | Descrição | Quando ocorre |
|--------|-----------|---------------|
| `nao_aplicavel` | Pedido sem cobrança (ex: pedido de teste, cortesia) | — |
| `aguardando_pagamento` | Cliente gerou PIX/card link mas não pagou ainda | Imediatamente após `novo` (métodos pré-pagos) |
| `autorizado` | Cartão autorizou (reserva, valor não capturado) | No checkout |
| `capturado` | Valor efetivamente cobrado | No `confirmado` ou no `saiu_para_entrega` (configurável) |
| `liquidado` | Valor disponível na conta (settled) | D+1 a D+30 (depende do gateway) |
| `recebido_na_entrega` | Dinheiro/cartão recebido pelo entregador | No `entregue` (entregador confirma) |
| `expirado` | PIX não pago dentro do tempo | Timeout (5-15 min) |
| `estornado` | Valor devolvido ao cliente | No `cancelado` |
| `falhou` | Transação recusada pelo gateway | No checkout |

**Regras de acoplamento Pedido × Pagamento:**

| Regra | Descrição |
|-------|-----------|
| Se método pré-pago: pedido só vai para `pendente` se `payment_status = capturado` | Evita processar pedido não pago |
| Se método pós-pago: pedido vai para `pendente` imediatamente | Pagamento acontece na entrega |
| PIX expirado (`expirado`): pedido vai para `cancelado` | T13 na tabela mestra |
| Cartão recusado (`falhou`): pedido nunca sai de `novo` | Cliente é notificado para tentar outro método |
| Reembolso em `cancelado` aciona `estornado` no gateway | Gatilho para gateway de pagamento |
| Pedidos com `payment_status = estornado` após `entregue` são raros | Requer aprovação do admin |

---

## 6. Timeouts e SLA

### 6.1 Tabela de Timeouts

Cada estado tem um tempo máximo permitido. Após esse tempo, uma ação automática ocorre.

| Estado | Timeout | Ação Automática | Severidade | Notificação |
|--------|:-------:|-----------------|:----------:|-------------|
| `pendente` | **15 min** | Alerta: "Pedidos pendentes exigem ação" | ⚠️ Warning | Push + Som no dashboard |
| `pendente` | **30 min** | Cancelamento automático (T12) | 🔴 Crítico | WhatsApp cliente + notificação lojista |
| `aguardando_receita` | **15 min** | Lembrete: "Não esqueça de enviar a receita" | ⚠️ Warning | WhatsApp cliente |
| `aguardando_receita` | **2 h** | Cancelamento automático (T8) | 🔴 Crítico | WhatsApp cliente |
| `aguardando_reenvio` | **2 h** | Cancelamento automático (T8) | 🔴 Crítico | WhatsApp cliente |
| `aguardando_substituicao` | **10 min** | Lembrete: "Aceite o substituto para não atrasar" | ⚠️ Warning | WhatsApp cliente |
| `aguardando_substituicao` | **30 min** | Rejeição automática (T21) | 🔴 Crítico | WhatsApp cliente |
| `em_preparo` | `tempo_médio × 1.5` | Alerta de atraso (T14 timer) | ⚠️ Warning | Push lojista |
| `em_preparo` | `tempo_médio × 2` | Notificação de atraso crítico | 🔴 Crítico | WhatsApp cliente + Push lojista |
| `pronto` | **15 min** | Alerta: "Pedido pronto mas não saiu" | ⚠️ Warning | Push lojista |
| `saiu_para_entrega` | ETA + 15 min | Verificar posição GPS do entregador | ⚠️ Warning | Push lojista |
| `saiu_para_entrega` | ETA + 30 min | Escalar: contatar entregador | 🔴 Crítico | Push lojista + Ligação? |
| `aguardando_pagamento` (PIX) | **15 min** | Cancelamento automático (T13) | 🔴 Crítico | WhatsApp cliente |

### 6.2 Cálculo de ETA

O tempo estimado de entrega (ETA) é calculado no `confirmado` e atualizado no
`saiu_para_entrega`.

```
ETA = tempo_preparo + tempo_roteirizacao + tempo_deslocamento

tempo_preparo:
  Alimentação: MAX(prep_time de cada item) × fator_fila
  Farmácia:    tempo_fixo (5 min para separação)
  Mercado:     SQRT(qtde_itens) × 2 min × fator_fila

tempo_roteirizacao:
  OSRM estima com base na distória loja → cliente

fator_fila:
  Número de pedidos na fila do entregador × tempo_médio_entrega
```

### 6.3 SLA Mínimo por Segmento

| Segmento | Meta do restaurante ao cliente | Meta do confirmado ao saiu |
|----------|:------------------------------:|:--------------------------:|
| Alimentação (pizzaria) | 45 min | 25 min |
| Alimentação (restaurante) | 35 min | 20 min |
| Farmácia | 25 min | 10 min |
| Mercado (até 10 itens) | 40 min | 25 min |
| Mercado (10+ itens) | 60 min | 40 min |

---

## 7. Cancelamentos e Reembolsos

### 7.1 Matriz de Cancelamento

O impacto do cancelamento depende de **quando** ele ocorre no ciclo de vida.

| Ponto de Cancelamento | Reembolso ao Cliente | Cobrança SaaS | Quem pode cancelar |
|-----------------------|:--------------------:|:-------------:|:------------------:|
| Antes de `confirmado` | **100%** | **Não cobra** ✅ | Lojista, Cliente, Sistema |
| Entre `confirmado` e `em_preparo` | **100%** | **Não cobra** ✅ | Lojista, Cliente |
| Durante `em_preparo` | **100%** | **Cobra** 🔴 | Lojista (motivado) |
| Em `pronto` (não saiu) | **≥ 80%** (definido pelo lojista) | **Cobra** 🔴 | Lojista |
| Em `saiu_para_entrega` | **≥ 50%** (deduz custo de entrega) | **Cobra** 🔴 | Lojista (com suporte) |
| Após `entregue` (estorno) | **100%** (caso excepcional) | **Mantido** 🔴 | Admin RapiDrop |

### 7.2 Política de Reembolso

| Método de Pagamento | Como reembolsar | Prazo |
|---------------------|-----------------|:-----:|
| PIX | Estorno via gateway (Asaas/Stripe) | Instantâneo a D+1 |
| Cartão (online) | Estorno via gateway | Até 2 faturas |
| Dinheiro | Lojista devolve presencialmente | Combinado com cliente |
| Cartão (na entrega) | Lojista estorna presencialmente ou RapiDrop media | Combinado |

### 7.3 Regras para o Cancelamento do Cliente

O cliente pode cancelar **sem custo** apenas até o pedido ser confirmado.
Após `confirmado`, o cancelamento fica a critério do lojista.

```
Cliente solicita cancelamento:
  ├── Pedido em pendente → ✅ Automático (reembolso integral)
  ├── Pedido em confirmado → ✅ Automático (reembolso integral)
  ├── Pedido em em_preparo → ❌ A critério do lojista
  ├── Pedido em pronto → ❌ A critério do lojista
  └── Pedido em saiu_para_entrega → ❌ Não permitido (contatar suporte)
```

Para o cliente, a interface mostra opções conforme o estado:
- Até `confirmado`: botão "Cancelar Pedido" visível
- Após `confirmado`: botão muda para "Solicitar Cancelamento" (envia pedido ao lojista)

### 7.4 Regras para Cancelamento do Lojista

O lojista pode cancelar a qualquer momento, mas com consequências diferentes:

```
Cancelamento pelo lojista:
  ├── Até confirmado → ✅ Sem custo, reembolso integral
  ├── Durante preparo → ⚠️ Cobrado SaaS + reembolso integral
  └── Após pronto → 🔴 Cobrado SaaS + reembolso parcial + possível penalidade
```

**Penalidade para lojista com alto índice de cancelamento pós-preparo:**
- > 5% no mês → Alerta automático
- > 10% no mês → Revisão de conta (possível suspensão)

### 7.5 Fluxo de Reembolso Automático

```
[Pedido cancelado em estado X]
        │
        ▼
[Determinar valor do reembolso baseado na matriz]
        │
        ▼
[Se pagamento foi PIX/cartão → acionar estorno via gateway]
        │
        ▼
[Se pagamento foi dinheiro/cartão na entrega → notificar lojista]
        │
        ▼
[Registrar em payment_transaction: tipo=refund, valor, motivo]
        │
        ▼
[Notificar cliente: "Seu reembolso de R$ X foi processado"]
```

---

## 8. Tabela de Eventos

Cada transição dispara eventos em **múltiplos sistemas**. Esta tabela consolida
tudo que acontece em cada mudança de estado.

| Transição | Notificações | WebSocket | Billing | Audit | Analytics | Integrações |
|-----------|:-----------:|:---------:|:-------:|:-----:|:---------:|:-----------:|
| `order.created` → `novo` | — | — | — | `order.created` | `order_created` | — |
| `novo` → `pendente` | Push lojista + Som dashboard | `order.new` | — | `order.status_changed` | `order_pending` | — |
| `novo` → `aguardando_receita` | WhatsApp cliente (solicitar receita) | — | — | `prescription.requested` | — | — |
| `aguardando_receita` → `receita_validada` | WhatsApp cliente (receita ok) | — | — | `prescription.validated` | — | — |
| `aguardando_receita` → `receita_rejeitada` | WhatsApp cliente (motivo) | — | — | `prescription.rejected` | — | — |
| `pendente` → `confirmado` | WhatsApp cliente (confirmado 🎉) | `order.confirmed` | — | `order.confirmed` | `order_confirmed` | Imprimir pedido |
| `pendente` → `cancelado` | WhatsApp cliente (cancelado) | `order.cancelled` | Estorno se pago | `order.cancelled` | `order_cancelled` | — |
| `pendente` → `cancelado` (timeout) | WhatsApp cliente + Alerta lojista | `order.cancelled` | Estorno se pago | `order.cancelled_timeout` | `order_cancelled_timeout` | — |
| `confirmado` → `em_preparo` | — | `order.preparing` | — | `order.preparation_started` | `order_preparing` | — |
| `em_preparo` → `aguardando_substituicao` | WhatsApp cliente (substituto) | — | — | `substitution.requested` | — | — |
| `aguardando_substituicao` → `em_preparo` | — | — | Recalcular valor | `substitution.resolved` | — | — |
| `em_preparo` → `pronto` | Push entregador (se atribuído) | `order.ready` | — | `order.ready` | `order_ready` | — |
| `em_preparo` → `cancelado` | WhatsApp cliente + Lojista | `order.cancelled` | **Cobra SaaS** + Estorno | `order.cancelled_in_prep` | `order_cancelled_in_prep` | — |
| `pronto` → `saiu_para_entrega` | WhatsApp cliente (saiu 🚗) | `order.out_for_delivery` | — | `order.out_for_delivery` | `delivery_started` | Iniciar GPS share |
| `saiu_para_entrega` → `entregue` | WhatsApp cliente (entregue 🎉) | `order.delivered` | **Gera cobrança SaaS** | `order.delivered` | `delivery_completed` | Sincronizar extrato |
| `entregue` → `finalizado` | — | — | Processar billing | `order.finalized` | `order_finalized` | Sincronizar ERP? |
| `saiu_para_entrega` → `cancelado` | WhatsApp cliente + Lojista | `order.cancelled` | **Cobra SaaS** + Estorno parcial | `order.failed_delivery` | `delivery_failed` | — |

### 8.1 WebSocket — Mapa Completo de Eventos

```
Cliente (site/app do cliente):
  order.confirmed          → "Pedido confirmado"
  order.preparing          → "Em preparo"
  order.ready              → "Saiu para entrega (em breve)"
  order.out_for_delivery   → "Saiu para entrega 🚗"
  rider.location_update    → Posição do entregador no mapa
  order.delivered          → "Pedido entregue! 🎉"
  order.cancelled          → "Pedido cancelado"
  order.substitution       → "Item X precisa de substituto"

Lojista (dashboard):
  order.new                → Novo pedido (com som)
  order.status_changed     → Qualquer mudança no pedido
  rider.location_update    → Posição de cada entregador
  rider.status_changed     → Entregador online/offline
  substitution.requested   → Item em falta → substituto pendente
  alert.delay              → Atraso detectado (preparo ou entrega)

Entregador (app):
  order.assigned           → Novo pedido para você
  order.ready              → Pedido pronto para retirada
  order.cancelled          → Pedido cancelado
  order.priority_update    → Reordenamento da fila
```

---

## 9. Casos de Exceção

### 9.1 Pedido Dividido em Múltiplas Entregas

**Cenário:** Pedido de mercado grande demais para um único entregador (ex: 50 itens).

**Como funciona:**
- Um pedido é dividido em **entregas parciais**, cada uma com seu próprio `order_rider`
- O `order.status` do pedido **mãe** só vai para `entregue` quando todas as entregas forem concluídas
- Entregas parciais têm um `delivery_number` (1 de 2, 2 de 2)

```
                ┌─────────────────────────────┐
                │      PEDIDO MÃE #1234        │
                │  status: em_preparo          │
                │  split: true                 │
                └─────────────┬───────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ ENTREGA 1/3  │ │ ENTREGA 2/3  │ │ ENTREGA 3/3  │
     │ 8 itens      │ │ 7 itens      │ │ 5 itens      │
     │ rider: João  │ │ rider: Maria │ │ rider: João  │
     │ frágil: não  │ │ frágil: ovos │ │ refrig: sim  │
     │ status: saiu │ │ status: prep │ │ status: prep │
     └──────────────┘ └──────────────┘ └──────────────┘
```

**Transições especiais:**
| Evento | Ação |
|--------|------|
| Todas entregas `entregue` | Pedido mãe → `entregue` |
| Uma entrega `cancelado` | Pedido mãe → `cancelado_parcial` (as outras entregas seguem) |
| Todas entregas canceladas | Pedido mãe → `cancelado` |

### 9.2 Cliente Não Encontrado no Endereço

**Cenário:** Entregador chega no endereço e cliente não atende.

**Fluxo:**
```
1. Entregador tenta contato (app → botão "Ligar para o cliente")
2. Aguarda 5 minutos no local
3. Se não conseguir:
   a. Marca "Cliente não encontrado" no app
   b. Sistema notifica lojista
   c. Lojista decide: retornar pedido ou tentar novamente
4. Se retornar: pedido vai para cancelado (T27)
5. Pedido fica disponível para retirada presencial (cliente pode buscar depois)
```

**Regras:**
- Lojista pode definir política: "tentar X vezes" ou "retornar imediatamente"
- Cliente paga taxa de entrega mesmo se não receber (recurso foi consumido)
- Se cliente reclamar: lojista decide sobre reembolso da taxa

### 9.3 Item em Falta Após Confirmação (Mercado)

**Cenário:** Lojista confirma o pedido, mas ao separar o estoque descobre que um item está em falta.

**Fluxo:**
```
1. Lojista marca o item como "em falta" no dashboard
2. Sistema verifica se há substitute_product_id configurado
   a. Se sim: entra em aguardando_substituicao com substituto sugerido
   b. Se não: entra em aguardando_substituicao sem sugestão (cliente pode sugerir)
3. Cliente responde via WhatsApp:
   a. Aceita substituto → pedido segue
   b. Rejeita → item removido (cancelado_parcial) ou pedido cancelado (se essencial)
```

### 9.4 Gateway de Pagamento Recusa Após Confirmação

**Cenário:** Raro. Cartão autorizou no checkout, mas a captura falhou.

**Fluxo:**
```
1. Sistema tenta capturar o valor
2. Gateway retorna erro (limite insuficiente, cartão bloqueado, etc.)
3. Pedido em confirmado ou em_preparo:
   a. Sistema notifica lojista e cliente
   b. Cliente tem X horas para trocar forma de pagamento
   c. Se não trocar: cancelamento automático
```

**Nota:** Este cenário é mais comum em cartão com autorização + captura posterior.
Para PIX, o pagamento é confirmado antes do pedido ser criado.

### 9.5 Entregador Desiste Após Atribuição

**Cenário:** Entregador aceita o pedido mas depois desiste.

**Fluxo:**
```
1. Entregador clica "Recusar" no app (ou não responde em 2 min)
2. Sistema:
   a. Registra recusa (afeta ranking do entregador)
   b. Marca order_rider como nao_atribuido
   c. Se pedido está pronto: alerta crítico no dashboard
   d. Atribui para próximo entregador disponível
```

**Regra de ranking:** Cada recusa diminui o score do entregador.
Muitas recusas → menor prioridade na atribuição.

### 9.6 Cliente Quer Alterar Pedido Após Confirmação

**Cenário:** Cliente liga e quer adicionar/remover um item.

**Política:**
| Estado | Alteração permitida? |
|--------|:--------------------:|
| `pendente` | ✅ Sim (cliente ou lojista) |
| `confirmado` | ✅ Sim (lojista aprova) |
| `em_preparo` | ❌ Não (já está sendo produzido) |
| `pronto` ou depois | ❌ Não |

**Nota sobre alteração:** Alterar pedido gera um **novo registro de auditoria**.
Não se sobrescreve o pedido original — cria-se uma "alteração" vinculada ao pedido.

### 9.7 Falha de Sistema Durante Transição

**Cenário:** O servidor cai no meio de uma transição de estado.

**Estratégia:**
- Transições devem ser **idempotentes**: executar duas vezes produz o mesmo resultado
- Usar `SAVEPOINT` + `ROLLBACK` no PostgreSQL se algo falhar
- Transições críticas (pagamento, billing) usam **saga pattern** com compensação
- Se a transição falha: `order.status` permanece inalterado, um alerta é disparado
- Um worker de reconciliação verifica transições pendentes a cada 5 minutos

```
Transitions devem ser wrapped em:
  BEGIN;
    SAVEPOINT transition;
    UPDATE order SET status = 'novo_status', updated_at = NOW();
    INSERT INTO audit_log (...);
    -- disparar eventos externos (se falhar, rollback to SAVEPOINT)
  COMMIT;
```

### 9.8 Múltiplos Canais Concorrentes

**Cenário:** O cliente pede pelo WhatsApp, mas o atendente já cadastrou o pedido manualmente no dashboard.

**Proteção:**
- Depulicação por telefone + itens + horário próximos (janela de 5 min)
- Se detectado como duplicata: o segundo pedido é marcado como `suspeito_duplicata`
- Lojista vê no dashboard: "⚠️ Pedido similar já recebido. Confirmar mesmo assim?"
- Se confirmar: ambos seguem. Se não: um vai para `cancelado` com motivo `duplicata`

---

## 10. Estratégia de Implementação

### 10.1 Arquitetura Recomendada

```python
# Implementação como tabela de transições no código
# NÃO usar if/else espalhados

# Estrutura:
#   transitions = [
#       Transition(from_state, to_state, event, guards, actions),
#       ...
#   ]
#
#   order.transition(event_name, who, reason)
#       → valida se transição existe para estado atual
#       → executa guards
#       → se passar: executa actions e muda o estado
#       → se falhar: levanta exceção
```

**Padrão: State Machine + Chain of Responsibility.**

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Optional

class OrderStatus(str, Enum):
    NOVO = "novo"
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    EM_PREPARO = "em_preparo"
    PRONTO = "pronto"
    SAIU_PARA_ENTREGA = "saiu_para_entrega"
    ENTREGUE = "entregue"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

    # Farmácia
    AGUARDANDO_RECEITA = "aguardando_receita"
    RECEITA_VALIDADA = "receita_validada"
    RECEITA_REJEITADA = "receita_rejeitada"
    AGUARDANDO_REENVIO = "aguardando_reenvio"

    # Mercado
    AGUARDANDO_SUBSTITUICAO = "aguardando_substituicao"
    CANCELADO_PARCIAL = "cancelado_parcial"


@dataclass
class Transition:
    name: str
    from_state: OrderStatus | list[OrderStatus] | None  # None = qualquer estado
    to_state: OrderStatus
    guards: list[Callable] = field(default_factory=list)
    actions: list[Callable] = field(default_factory=list)
    allowed_roles: list[str] | None = None  # None = qualquer role
    segments: list[str] | None = None  # None = todos

    def matches(self, order_status: OrderStatus, role: str, segment: str) -> bool:
        if self.from_state is not None:
            if isinstance(self.from_state, list):
                if order_status not in self.from_state:
                    return False
            elif order_status != self.from_state:
                return False
        if self.allowed_roles and role not in self.allowed_roles:
            return False
        if self.segments and segment not in self.segments:
            return False
        return True
```

### 10.2 Tabela de Transições como Código

```python
TRANSITIONS: list[Transition] = [
    # === Fluxo Base ===
    Transition(
        name="order.pending",
        from_state=OrderStatus.NOVO,
        to_state=OrderStatus.PENDENTE,
        guards=[guard_prepaid_paid_or_postpaid],
        actions=[notify_merchant_new_order, websocket_order_new],
        allowed_roles=["system"],
    ),
    Transition(
        name="order.confirmed",
        from_state=OrderStatus.PENDENTE,
        to_state=OrderStatus.CONFIRMADO,
        guards=[guard_merchant_can_confirm],
        actions=[notify_customer_confirmed, websocket_order_confirmed, audit_log],
        allowed_roles=["merchant", "operator"],
    ),
    Transition(
        name="order.preparation_started",
        from_state=OrderStatus.CONFIRMADO,
        to_state=OrderStatus.EM_PREPARO,
        guards=[guard_merchant_can_start_prep],
        actions=[websocket_order_preparing, start_prep_timer],
        allowed_roles=["merchant", "operator", "kitchen"],
    ),
    # ... (todas as transições da tabela mestra)

    # === Farmácia ===
    Transition(
        name="prescription.validated",
        from_state=OrderStatus.AGUARDANDO_RECEITA,
        to_state=OrderStatus.PENDENTE,
        guards=[guard_prescription_valid],
        actions=[encrypt_prescription, save_validation, cancel_timeout],
        allowed_roles=["pharmacist"],
        segments=["pharmacy"],
    ),
    # ...

    # === Cancelamentos ===
    Transition(
        name="order.cancelled_by_merchant",
        from_state=[OrderStatus.PENDENTE, OrderStatus.CONFIRMADO],
        to_state=OrderStatus.CANCELADO,
        guards=[guard_cancellation_reason_provided],
        actions=[notify_customer_cancelled, process_refund, audit_log],
        allowed_roles=["merchant", "operator"],
    ),
    Transition(
        name="order.cancelled_in_prep",
        from_state=OrderStatus.EM_PREPARO,
        to_state=OrderStatus.CANCELADO,
        guards=[guard_cancellation_reason_provided, guard_merchant_accepts_charge],
        actions=[notify_customer_cancelled, process_refund, charge_saas_fee, audit_log],
        allowed_roles=["merchant"],
    ),
    # ...

    # === Novos estados concorrentes não-mutuamente exclusivos ===
    Transition(
        name="rider.assigned",
        from_state=None,  # estado do pedido não muda
        to_state=None,    # quem muda é order_rider.status
        # ... lida separadamente
    ),
]
```

### 10.3 Função Central de Transição

```python
# Core function — ÚNICO lugar onde order.status muda
from datetime import datetime, timezone
from sqlalchemy import update
from .audit import create_audit_log

async def transition_order(
    db_session,
    order_id: int,
    event_name: str,
    who: str,
    who_id: int,
    reason: str | None = None,
    metadata: dict | None = None,
) -> Order:
    """
    Aplica uma transição de estado a um pedido.
    Esta é a ÚNICA função que altera order.status em TODO o sistema.

    Args:
        db_session: Sessão do banco
        order_id: ID do pedido
        event_name: Nome do evento (ex: "order.confirmed")
        who: Role de quem disparou (merchant, system, rider, etc.)
        who_id: ID do usuário/sistema que disparou
        reason: Motivo (obrigatório para cancelamentos)
        metadata: Dados adicionais para audit log

    Returns:
        Order atualizado

    Raises:
        InvalidTransitionError: Se a transição não é permitida
        GuardViolationError: Se um guard não passou
    """
    # 1. Buscar pedido
    order = await db_session.get(Order, order_id)
    if not order:
        raise OrderNotFoundError(order_id)

    # 2. Encontrar transição que corresponde
    matching = [
        t for t in TRANSITIONS
        if t.name == event_name and t.matches(order.status, who, order.segment)
    ]
    if not matching:
        raise InvalidTransitionError(
            f"Transição '{event_name}' não permitida "
            f"para pedido {order_id} no estado '{order.status}'"
        )

    transition = matching[0]

    # 3. Executar guards
    for guard in transition.guards:
        guard_result = await guard(db_session, order, who_id, reason)
        if guard_result is not True:
            raise GuardViolationError(
                f"Guard '{guard.__name__}' falhou: {guard_result}"
            )

    # 4. Executar a transição (DB + audit)
    old_status = order.status
    now = datetime.now(timezone.utc)

    # Atualizar o pedido
    stmt = (
        update(Order)
        .where(Order.id == order_id)
        .values(
            status=transition.to_state.value,
            updated_at=now,
            **status_timestamp_field(transition.to_state, now),
        )
    )
    await db_session.execute(stmt)

    # Registrar audit log
    audit_entry = {
        "entity_type": "order",
        "entity_id": order_id,
        "action": event_name,
        "from_status": old_status,
        "to_status": transition.to_state.value,
        "who": who,
        "who_id": who_id,
        "reason": reason,
        "metadata": metadata or {},
        "created_at": now,
    }
    await create_audit_log(db_session, audit_entry)
    await db_session.commit()

    # 5. Disparar ações (fora da transação DB)
    # Ações são disparadas assincronamente para não travar a transição
    # Usar Celery/BackgroundTasks para notificações, WebSocket, analytics
    for action in transition.actions:
        await action(db_session, order, who_id, reason)

    # Recarregar pedido atualizado
    updated_order = await db_session.get(Order, order_id)
    return updated_order


def status_timestamp_field(status: OrderStatus, timestamp: datetime) -> dict:
    """Mapeia cada estado ao campo de timestamp correspondente no banco."""
    mapping = {
        OrderStatus.PENDENTE: {"pending_at": timestamp},
        OrderStatus.CONFIRMADO: {"confirmed_at": timestamp},
        OrderStatus.EM_PREPARO: {"preparing_at": timestamp},
        OrderStatus.PRONTO: {"ready_at": timestamp},
        OrderStatus.SAIU_PARA_ENTREGA: {"out_for_delivery_at": timestamp},
        OrderStatus.ENTREGUE: {"delivered_at": timestamp},
        OrderStatus.FINALIZADO: {"finalized_at": timestamp},
        OrderStatus.CANCELADO: {"cancelled_at": timestamp},
    }
    return mapping.get(status, {})
```

### 10.4 Exemplo de Guard

```python
async def guard_merchant_can_confirm(db_session, order, who_id, reason) -> bool | str:
    """"Retorna True se OK, ou string com motivo da recusa."""
    if not order.items:
        return "Pedido sem itens não pode ser confirmado"
    merchant = await db_session.get(Merchant, order.merchant_id)
    if merchant.is_blocked:
        return "Lojista bloqueado"
    if merchant.plan_status not in ("active", "trial"):
        return "Plano do lojista não está ativo"
    return True
```

### 10.5 Exemplo de Ação

```python
async def notify_customer_confirmed(db_session, order, who_id, reason):
    """Dispara notificação de confirmação ao cliente."""
    customer = await db_session.get(Customer, order.customer_id)
    merchant = await db_session.get(Merchant, order.merchant_id)
    template = NotificationTemplate.get("order.confirmed", merchant.segment)
    message = template.render(
        order_id=order.id,
        merchant_name=merchant.name,
        estimated_time=order.calculated_eta,
    )
    await dispatch_notification.delay(
        channel="whatsapp",
        to=customer.phone,
        message=message,
        template_name="order_confirmed",
        metadata={"order_id": order.id, "merchant_id": order.merchant_id},
    )
```

---

## 11. Cobertura de Testes

### 11.1 Testes por Transição

Cada transição na tabela mestra (T1-T29) deve ter no mínimo:

```python
# Template para cada transição:
def test_{transition_name}_happy_path():
    """Transição ocorre quando todas as condições são satisfeitas."""
    ...

def test_{transition_name}_guard_fails():
    """Transição é bloqueada quando um guard não passa."""
    ...

def test_{transition_name}_wrong_role():
    """Transição é bloqueada quando role não autorizada."""
    ...
```

**Total estimado:** ~80-100 testes para cobertura completa das transições.

### 11.2 Testes de Estados Proibidos

```python
def test_cannot_go_back_from_cancelled():
    """Cancelado é terminal — nenhuma transição é permitida."""
    order = OrderFactory(status="cancelled")
    for transition in ALL_TRANSITIONS:
        with pytest.raises(InvalidTransitionError):
            order.transition(transition.name, ...)

def test_cannot_skip_confirmed():
    """Pendente não pode ir direto para em_preparo."""
    order = OrderFactory(status="pendente")
    with pytest.raises(InvalidTransitionError):
        order.transition("order.preparation_started", ...)
```

### 11.3 Testes de Timeout

```python
def test_pending_timeout_after_30min():
    """Pedido sem confirmação após 30 min é cancelado automaticamente."""
    order = OrderFactory(status="pendente", pending_at=now() - timedelta(minutes=31))
    result = await process_timeouts()
    assert order.status == "cancelado"
    assert order.cancellation_reason == "timeout"

def test_pending_warning_at_15min():
    """Alerta é disparado aos 15 min de pendente."""
    order = OrderFactory(status="pendente", pending_at=now() - timedelta(minutes=16))
    result = await process_timeout_warnings()
    assert alert_sent_to_merchant(order.merchant_id)
```

### 11.4 Testes de Reembolso

```python
def test_cancel_before_confirmation_full_refund():
    """Cancelado antes da confirmação → reembolso integral, sem taxa SaaS."""
    order = OrderFactory(status="pendente", payment_status="captured")
    await transition_order(db, order.id, "order.cancelled_by_merchant", ...)
    assert refund_processed(order.id, amount=order.total_cents)
    assert not saas_fee_charged(order.id)

def test_cancel_during_prep_charges_saas_fee():
    """Cancelado durante preparo → reembolso integral + taxa SaaS."""
    order = OrderFactory(status="em_preparo", payment_status="captured")
    await transition_order(db, order.id, "order.cancelled_by_merchant_during_prep", ...)
    assert refund_processed(order.id, amount=order.total_cents)
    assert saas_fee_charged(order.id)
```

### 11.5 Testes de Idempotência

```python
def test_double_transition_is_safe():
    """Chamar a mesma transição duas vezes é seguro (idempotente)."""
    order = OrderFactory(status="pendente")
    await transition_order(db, order.id, "order.confirmed", ...)
    with pytest.raises(InvalidTransitionError):
        await transition_order(db, order.id, "order.confirmed", ...)
    assert order.status == "confirmado"
```

### 11.6 Testes de Concorrência

```python
def test_concurrent_transitions_are_serialized():
    """Duas transições simultâneas no mesmo pedido não causam race condition."""
    order = OrderFactory(status="pendente")
    # Disparar duas confirmações ao mesmo tempo
    results = await asyncio.gather(
        transition_order(db, order.id, "order.confirmed", ...),
        transition_order(db, order.id, "order.confirmed", ...),
        return_exceptions=True,
    )
    assert one_succeeded and one_failed
    assert order.status == "confirmado"
```

---

## 12. Glossário

| Termo | Definição |
|-------|-----------|
| **Estado (state)** | Situação atual do pedido no seu ciclo de vida (ex: `pendente`, `em_preparo`). |
| **Transição (transition)** | Movimento de um estado para outro, com guards e actions. |
| **Guard (guarda)** | Condição que deve ser verdade para a transição ocorrer. |
| **Action (ação)** | Efeito colateral disparado ao completar uma transição (notificação, billing, etc.). |
| **Estado terminal** | Estado que não permite mais transições (`cancelado`, `finalizado`). |
| **Estado concorrente** | Estado de uma dimensão paralela (entregador, pagamento) que corre junto com `order.status`. |
| **Timeout** | Tempo máximo em um estado antes de ação automática. |
| **SLA** | Acordo de nível de serviço — tempo esperado para cada etapa. |
| **ETA** | Tempo estimado para conclusão da entrega. |
| **Segmento** | Categoria do lojista (alimentação, farmácia, mercado). Afeta regras da máquina. |
| **Reembolso integral** | Devolução de 100% do valor pago pelo cliente. |
| **Reembolso parcial** | Devolução parcial (política do lojista ou do RapiDrop). |
| **Estorno** | Devolução do dinheiro via gateway de pagamento. |
| **Idempotente** | Propriedade de produzir o mesmo resultado se executado múltiplas vezes. |
| **Saga pattern** | Padrão de transações distribuídas com compensação em caso de falha. |

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Baseado nos documentos:** `docs/ideacao-rapidrop.md`, `docs/pagamento-entregadores.md`,
> `docs/assinatura-saas.md`, `docs/experiencia-cliente.md`
> **Próximo documento sugerido:** `docs/integracao-whatsapp.md`
