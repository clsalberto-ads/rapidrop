# RapiDrop — Integração WhatsApp

> Especificação completa da integração com WhatsApp Cloud API.
> O WhatsApp é o **canal primário de comunicação** com o cliente final e o
> **segundo maior canal de pedidos** (depois do site white-label) no MVP.

---

## Índice

1. [Filosofia e Abordagem](#1-filosofia-e-abordagem)
2. [Arquitetura Geral](#2-arquitetura-geral)
3. [Modelo de Números e Contas](#3-modelo-de-números-e-contas)
4. [Outbound — Notificações](#4-outbound--notificações)
5. [Inbound — Recebimento de Mensagens](#5-inbound--recebimento-de-mensagens)
6. [Fluxos Conversacionais](#6-fluxos-conversacionais)
7. [Conexão do Lojista (Onboarding WhatsApp)](#7-conexão-do-lojista-onboarding-whatsapp)
8. [Gerenciamento de Templates](#8-gerenciamento-de-templates)
9. [Message Logging e Compliance](#9-message-logging-e-compliance)
10. [Casos de Exceção](#10-casos-de-exceção)
11. [Estratégia de Implementação](#11-estratégia-de-implementação)
12. [Cobertura de Testes](#12-cobertura-de-testes)

---

## 1. Filosofia e Abordagem

### 1.1 Princípios

| Princípio | Implicação |
|-----------|------------|
| **WhatsApp é o canal primário** | Cliente não precisa baixar app. Onde o cliente já está (WhatsApp) é onde o sistema conversa com ele. |
| **O lojista não perde o próprio número** | O cliente continua mandando mensagem pro número de sempre. O RapiDrop **aumenta** a capacidade, não **substitui** o número. |
| **Notificações são templates aprovados** | Toda mensagem enviada pro cliente usa um template aprovado pelo Meta. Sem mensagens "inventadas" que possam ser bloqueadas. |
| **Humano no loop** | O sistema tenta interpretar e responder automaticamente, mas **sempre** cede pro atendente humano se não tiver certeza. |
| **LGPD nativo** | Consentimento é registrado antes do primeiro disparo. Cliente pode opt-out a qualquer momento. |

### 1.2 Abordagem em Fases

O WhatsApp não será implementado de uma vez. A abordagem é progressiva:

```
FASE 1 (MVP) — Notificações Outbound
  └── RapiDrop envia mensagens usando seu próprio WABA
  └── Templates aprovados pelo Meta
  └── Cliente recebe: "Pedido confirmado", "Saiu para entrega", etc.
  └── Inbound: apenas manual (cliente responde e cai no WhatsApp do lojista)

FASE 2 (Pós-MVP) — Inbound + Conexão do Lojista
  └── Lojista conecta seu número WhatsApp Business ao RapiDrop
  └── Mensagens dos clientes aparecem no dashboard
  └── Sistema tenta interpretar intenção automaticamente
  └── Atendente humano assume quando necessário

FASE 3 (Escala) — IA Conversacional
  └── AI interpreta pedidos em linguagem natural
  └── "Quero 2 pizzas grandes e uma coca" → cria pedido automaticamente
  └── Substituição, reclamação, suporte com IA + fallback humano
  └── Campanhas de marketing segmentadas via WhatsApp
```

**Este documento cobre as 3 fases**, mas a implementação deve começar pela Fase 1.

---

## 2. Arquitetura Geral

### 2.1 Diagrama de Componentes

```
                        ┌──────────────────────────────────┐
                        │        META WHATSAPP CLOUD API    │
                        │  (graph.facebook.com/v22.0)      │
                        │                                  │
                        │  ┌────────────────────────────┐  │
                        │  │  WABA RapiDrop             │  │
                        │  │  Phone: +55 XX XXXXX-XXXX  │  │
                        │  │  (notificações outbound)    │  │
                        │  └────────────────────────────┘  │
                        │                                  │
                        │  ┌────────────────────────────┐  │
                        │  │  WABA do Lojista (fase 2)  │  │
                        │  │  Phone: número do lojista  │  │
                        │  │  (inbound + outbound)      │  │
                        │  └────────────────────────────┘  │
                        └──────────┬───────────────────────┘
                                   │ HTTPS (Webhook + API)
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                     RAPIDROP BACKEND (FastAPI)                     │
│                                                                   │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ WhatsApp   │  │ Template     │  │ Conversation Manager       │ │
│  │ Webhook    │  │ Manager      │  │ (state machine por chat)   │ │
│  │ Handler    │  │              │  │                            │ │
│  │  ├─verify  │  │  ├─CRUD      │  │  ├─Intent detection       │ │
│  │  ├─receive │  │  ├─submit    │  │  ├─Flow routing            │ │
│  │  └─send    │  │  └─status    │  │  └─Human handoff           │ │
│  └────────────┘  └──────────────┘  └───────────────────────────┘ │
│                                         │                          │
│                    ┌────────────────────┴────────────────────┐    │
│                    │           Celery Workers                │    │
│                    │  ┌──────────┐ ┌──────────┐              │    │
│                    │  │ Send     │ │ Template │              │    │
│                    │  │ Message  │ │ Sync     │              │    │
│                    │  └──────────┘ └──────────┘              │    │
│                    └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                         BANCO DE DADOS                           │
│                                                                   │
│  whatsapp_templates  ─  templates aprovados + pendentes          │
│  whatsapp_webhook_log ─  registro de todas as mensagens          │
│  whatsapp_conversations ─ estado da conversa por chat            │
│  merchant_waba       ─  conexão WABA do lojista                  │
│  customer_consent    ─  opt-in/opt-out do cliente                │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Duas Contas WhatsApp

O RapiDrop opera com **dois tipos de conta WhatsApp**:

| Conta | Titular | Uso | Quando |
|-------|---------|-----|--------|
| **WABA RapiDrop** | RapiDrop (CNPJ do SaaS) | Notificações outbound para clientes de **todos** os lojistas | Fase 1 (MVP) |
| **WABA do Lojista** | Próprio lojista (CNPJ dele) | Receber mensagens dos clientes, responder, gerenciar conversas | Fase 2+ |

**IMPORTANTE:** Na Fase 1, o cliente recebe notificações de um número do RapiDrop
(identificado como "RapiDrop — [Nome da Loja]"). O cliente pode responder, mas
a resposta cai no WhatsApp pessoal do lojista (não no sistema). Isso é aceitável
para o MVP porque o lojista continua usando o WhatsApp dele normalmente.

Na Fase 2, quando o lojista conecta o próprio número, tudo fica centralizado no dashboard.

### 2.3 Stack Técnica

| Componente | Tecnologia |
|------------|------------|
| **WhatsApp Cloud API** | Meta Graph API v22.0 |
| **SDK/Client** | `whatsapp-cloud-api` (Python) ou request direto |
| **Webhook** | FastAPI endpoint público (`POST /api/v1/whatsapp/webhook`) |
| **Fila de envio** | Celery + RabbitMQ (evitar rate limit) |
| **Webhook log** | Tabela separada no PostgreSQL |
| **State machine** | Por conversation_id (telefone do cliente) |
| **Templates** | Gerenciados via Meta Business API + cache local |

---

## 3. Modelo de Números e Contas

### 3.1 WABA RapiDrop (Fase 1)

Uma única conta WhatsApp Business Account registrada no CNPJ do RapiDrop.

```
WABA RapiDrop
├── Phone: +55 XX 9XXXX-XXXX (número único)
├── Display Name: "RapiDrop — [Nome do Lojista]"
│   (muda dinamicamente via API por mensagem)
├── Business Profile: Logo RapiDrop, site rapidrop.com.br
├── Status: VERIFIED (Meta Business Verification concluída)
└── Templates: 15+ templates aprovados (ver seção 8)
```

**Limitações conhecidas:**
- Um novo número WhatsApp tem limite de 1.000 conversas/dia nos primeiros dias
- O limite cresce com o volume e tempo de conta (até 100.000+/dia)
- Para o MVP (dezenas de lojistas, centenas de mensagens/dia), o limite inicial é suficiente
- O nome do remetente muda por mensagem usando o parâmetro `display_name` no header

### 3.2 WABA do Lojista (Fase 2)

Cada lojista precisa ter uma WhatsApp Business Account própria para usar o recurso de inbound.

**Perfil do lojista típico:**
- Já usa WhatsApp Business (gratuito) no celular da loja
- Tem um número comercial que os clientes conhecem
- **Não** tem WABA registrada no Meta (a maioria não tem)
- Precisa passar por um fluxo de embedded signup

**Fluxo de conexão:** Ver [seção 7 — Conexão do Lojista](#7-conexão-do-lojista-onboarding-whatsapp).

### 3.3 Mapeamento: Número → Merchant

No banco de dados, o mapeamento é:

```
whatsapp_phone_numbers
├── id
├── merchant_id (FK, nullable → null = número do RapiDrop)
├── phone_number (E.164: +5511999999999)
├── waba_id (ID da WABA no Meta)
├── waba_phone_id (ID do telefone na WABA)
├── is_rapidrop_owned (boolean — true = nosso, false = do lojista)
├── status (active / pending / disconnected / revoked)
├── connected_at
├── disconnected_at
├── config: jsonb
│   ├── business_name: "Pizzaria do Norte"
│   ├── display_name: "Pizzaria do Norte"
│   ├── greeting: "Olá! Aqui é da Pizzaria do Norte. Como posso ajudar?"
│   └── working_hours: {"weekday": "08:00-23:00", "weekend": "10:00-23:00"}
└── created_at, updated_at
```

---

## 4. Outbound — Notificações

### 4.1 Arquitetura de Envio

Toda notificação WhatsApp segue este fluxo:

```
[Transição de estado do pedido]
        │
        ▼
[Determinar template + variáveis]
        │
        ▼
[Verificar consentimento do cliente]
   ┌───┴───┐
   │       │
   ▼       ▼
  Sim     Não → Pular (ou SMS fallback)
   │
   ▼
[Enfileirar no Celery: send_whatsapp.delay()]
        │
        ▼
[Worker consulta API do Meta]
        │
        ▼
[Registrar em whatsapp_webhook_log]
        │
        ▼
[Meta envia mensagem para o cliente]
```

### 4.2 Catálogo de Templates (Outbound)

Todos os templates abaixo precisam ser **submetidos e aprovados pelo Meta**
antes de serem usados. A aprovação leva de 1 a 5 dias úteis.

#### Templates de Transação (UTILITY)

São templates que informam o cliente sobre uma transação em andamento.
Categoria `UTILITY` — podem ser enviados mesmo fora da janela de 24h.

| ID | Nome | Conteúdo | Variáveis | Disparo |
|----|------|----------|-----------|---------|
| T1 | `order_confirmed` | `Olá {{name}}! Seu pedido #{{order_id}} no *{{merchant_name}}* foi confirmado! 🎉 Tempo estimado: {{eta}}.` | `name`, `order_id`, `merchant_name`, `eta` | Transição para `confirmado` |
| T2 | `order_out_for_delivery` | `{{name}}, seu pedido #{{order_id}} saiu para entrega! 🚗 Previsão: {{eta}}. Acompanhe ao vivo: {{tracking_link}}` | `name`, `order_id`, `eta`, `tracking_link` | Transição para `saiu_para_entrega` |
| T3 | `order_delivered` | `{{name}}, seu pedido #{{order_id}} do *{{merchant_name}}* foi entregue! 🎉 Obrigado pela preferência! 💛` | `name`, `order_id`, `merchant_name` | Transição para `entregue` |
| T4 | `order_cancelled` | `{{name}}, o pedido #{{order_id}} no *{{merchant_name}}* foi cancelado. Motivo: {{reason}}. Seu pagamento será reembolsado em até {{refund_days}} dias úteis.` | `name`, `order_id`, `merchant_name`, `reason`, `refund_days` | Transição para `cancelado` |
| T5 | `order_cancelled_refunded` | `{{name}}, o reembolso do pedido #{{order_id}} foi processado com sucesso! O valor de R$ {{amount}} será creditado em até {{days}} dias.` | `name`, `order_id`, `amount`, `days` | Reembolso processado |
| T6 | `prescription_request` | `{{name}}, o medicamento *{{product_name}}* precisa de receita. Envie a foto da receita aqui mesmo para prosseguirmos com o pedido 📸` | `name`, `product_name` | Transição para `aguardando_receita` | F |
| T7 | `prescription_rejected` | `{{name}}, a receita enviada não foi aprovada. Motivo: {{reason}}. Por favor, envie uma nova foto da receita válida.` | `name`, `reason` | Transição para `receita_rejeitada` | F |
| T8 | `substitution_offer` | `{{name}}, o item *{{product_name}}* está em falta. Aceita *{{substitute_name}}* como substituto? 💚 Sim / ❌ Não (responda aqui)` | `name`, `product_name`, `substitute_name` | Transição para `aguardando_substituicao` | M |
| T9 | `order_delay` | `{{name}}, seu pedido #{{order_id}} está com um pequeno atraso. Pedimos desculpas! 🙏 Nova previsão: {{new_eta}}.` | `name`, `order_id`, `new_eta` | Timer de atraso no `em_preparo` |
| T10 | `payment_pix` | `{{name}}, aqui está o PIX para pagar seu pedido #{{order_id}}: Código: {{pix_code}} Valor: R$ {{amount}} Válido até: {{expires_at}}` | `name`, `order_id`, `pix_code`, `amount`, `expires_at` | Checkout (PIX) |

#### Templates de Marketing (MARKETING)

Categoria `MARKETING` — só podem ser enviados dentro da janela de 24h desde
a última interação do cliente com o negócio. Para clientes inativos, é
necessário opt-in explícito.

| ID | Nome | Conteúdo | Disparo |
|----|------|----------|---------|
| M1 | `welcome` | `Olá {{name}}! Seja bem-vindo(a) ao *{{merchant_name}}* 🎉 Peça pelo link: {{store_link}}` | Primeiro pedido |
| M2 | `back_active` | `{{name}}, sentimos sua falta! 🥺 Use o cupom **{{coupon}}** e ganhe {{discount}}% de desconto no seu próximo pedido no *{{merchant_name}}* 🎉` | Cliente inativo > 30 dias |
| M3 | `referral` | `{{name}}, indique um amigo e ganhe {{reward}}! 🎉 Seu amigo ganha {{friend_reward}} também. Compartilhe: {{referral_link}}` | Após entrega |

### 4.3 Lógica de Envio

```python
# Regras de quando enviar cada template:

WHATSAPP_NOTIFICATION_RULES = {
    "order.confirmed": {
        "template": "order_confirmed",
        "segment": "all",
        "condition": lambda order: True,  # sempre envia
        "priority": "high",
    },
    "order.out_for_delivery": {
        "template": "order_out_for_delivery",
        "segment": "all",
        "condition": lambda order: True,
        "priority": "high",
    },
    "order.delivered": {
        "template": "order_delivered",
        "segment": "all",
        "condition": lambda order: True,
        "priority": "high",
    },
    "order.cancelled": {
        "template": "order_cancelled",
        "segment": "all",
        "condition": lambda order: True,
        "priority": "high",
    },
    "prescription.requested": {
        "template": "prescription_request",
        "segment": "pharmacy",
        "condition": lambda order: any(
            item.get("tarja") in ("red", "black")
            for item in order.items
        ),
        "priority": "high",
    },
    "substitution.needed": {
        "template": "substitution_offer",
        "segment": "grocery",
        "condition": lambda order: order.substitution_needed,
        "priority": "medium",
    },
}

# Worker de envio
@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,  # não perder mensagens se worker crashar
)
def send_whatsapp(
    self,
    to_phone: str,
    template_name: str,
    template_vars: dict,
    merchant_id: int,
    order_id: int | None = None,
):
    """
    Envia uma mensagem WhatsApp usando template aprovado.
    """
    # 1. Verificar consentimento
    if not has_consent(to_phone, merchant_id):
        logger.warning("Sem consentimento", to=to_phone, merchant=merchant_id)
        return

    # 2. Buscar template
    template = get_template(template_name)
    if not template or template.status != "approved":
        raise TemplateNotApprovedError(template_name)

    # 3. Escolher número de envio
    # Na Fase 1: sempre o número do RapiDrop
    # Na Fase 2: o número do lojista (se conectado), senão o do RapiDrop
    source_phone = get_outbound_phone(merchant_id)

    # 4. Enviar via Meta API
    try:
        response = whatsapp_client.send_template(
            from_phone=source_phone,
            to_phone=to_phone,
            template_name=template.meta_name,
            template_vars=template_vars,
            language="pt_BR",
        )
    except RateLimitError:
        # Respeitar rate limit — retentar com backoff exponencial
        raise self.retry(exc=RateLimitError, countdown=2 ** self.request.retries * 60)
    except WhatsAppAPIError as e:
        logger.error("Falha ao enviar WhatsApp", error=str(e))
        raise self.retry(exc=e)

    # 5. Registrar
    log_whatsapp_message(
        to_phone=to_phone,
        from_phone=source_phone,
        template_name=template_name,
        status="sent",
        meta_message_id=response.get("messages", [{}])[0].get("id"),
        merchant_id=merchant_id,
        order_id=order_id,
    )
```

### 4.4 Consentimento (Opt-in)

Nenhuma mensagem WhatsApp pode ser enviada sem consentimento explícito.

```
Fluxo de consentimento:
  1. Cliente faz primeiro pedido → no checkout, check-box:
     "☑️ Aceito receber notificações do pedido por WhatsApp"
  2. Cliente clica "Sim" → registrado em customer_consent
  3. A cada novo pedido, o consentimento é verificado
  4. Cliente pode revogar a qualquer momento:
     - Respondendo "PARE" ou "SAIR" para qualquer mensagem
     - No link de tracking do pedido
     - Falando com o lojista

Tabela:
  customer_consent
  ├── id
  ├── customer_id (FK)
  ├── merchant_id (FK)
  ├── channel (whatsapp / sms / push)
  ├── consent_granted_at
  ├── consent_revoked_at (nullable)
  ├── source (checkout / onboarding / link)
  └── ip_address, user_agent
```

---

## 5. Inbound — Recebimento de Mensagens

### 5.1 Webhook de Mensagens Recebidas

O Meta envia um `POST` para o webhook do RapiDrop sempre que uma mensagem é
enviada para um dos números gerenciados.

```
POST /api/v1/whatsapp/webhook
  Headers:
    X-Hub-Signature-256: sha256=<assinatura>
    Content-Type: application/json

  Body (exemplo):
  {
    "object": "whatsapp_business_account",
    "entry": [{
      "id": "WABA_ID",
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {
            "display_phone_number": "+5511999999999",
            "phone_number_id": "PHONE_ID"
          },
          "contacts": [{
            "profile": {"name": "Ana Silva"},
            "wa_id": "+5511988888888"
          }],
          "messages": [{
            "from": "+5511988888888",
            "id": "MESSAGE_ID",
            "timestamp": "1717000000",
            "type": "text",
            "text": {"body": "Quero fazer um pedido"}
          }]
        }
      }]
    }]
  }
```

### 5.2 Handler de Webhook

```python
@router.post("/api/v1/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Endpoint público para receber webhooks do WhatsApp Cloud API.
    """
    # 1. Verificar assinatura
    signature = request.headers.get("X-Hub-Signature-256", "")
    raw_body = await request.body()
    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 2. Processar payload
    payload = await request.json()
    for entry in payload.get("entry", []):
        waba_id = entry.get("id")
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "messages" in value:
                await process_inbound_messages(waba_id, value)
            if "statuses" in value:
                await process_status_updates(waba_id, value)

    # 3. Meta espera 200 OK rápido
    return {"status": "ok"}


async def process_inbound_messages(waba_id: str, payload: dict):
    """
    Processa mensagens recebidas e roteia para o fluxo correto.
    """
    # Descobrir qual merchant é dono deste número
    phone_number_id = payload["metadata"]["phone_number_id"]
    phone = await get_phone_by_meta_id(phone_number_id)

    for msg in payload.get("messages", []):
        # Registrar no log (imutável)
        await log_inbound_message(waba_id, phone, msg)

        from_wa_id = msg["from"]  # telefone do cliente
        msg_type = msg["type"]     # text, image, interactive, etc.

        # Buscar ou criar sessão de conversa
        conversation = await get_or_create_conversation(
            merchant_id=phone.merchant_id,
            customer_phone=from_wa_id,
        )

        # Rotear por tipo de mensagem
        match msg_type:
            case "text":
                await handle_text_message(conversation, msg["text"]["body"])
            case "image":
                await handle_image_message(conversation, msg["image"])
            case "interactive":
                await handle_interactive_reply(conversation, msg["interactive"])
            case "button":
                await handle_button_reply(conversation, msg["button"])
            case "location":
                await handle_location_message(conversation, msg["location"])
            case _:
                await handle_unknown_message(conversation, msg_type)
```

### 5.3 Roteamento de Intenção

Quando uma mensagem de texto chega, o sistema tenta identificar a intenção:

```python
INTENT_PATTERNS = {
    # Pedidos
    "new_order": [
        r"quero (pedir|fazer um pedido|comprar|encomendar)",
        r"gostaria de (pedir|encomendar|comprar)",
        r"pode (trazer|enviar|entregar)",
        r"tem (disponível|como faço para pedir)",
        r"card[áa]pio",
    ],
    # Status
    "track_order": [
        r"(cadê|onde está|status|andr[ao]) (meu pedido|pedido)",
        r"quanto tempo (falta|vai demorar)",
        r"j[aá] (saiu|foi|enviou)",
    ],
    # Cancelamento
    "cancel_order": [
        r"(quero|gostaria de) cancelar",
        r"pode cancelar",
        r"cancela (aí|por favor|meu pedido)",
    ],
    # Suporte
    "support": [
        r"(preciso de|quero) (falar|falar com) (com|)(atendente|suporte|gerente|humano)",
        r"reclamar|reclamação|problema",
        r"não (recebi|chegou|entregou)",
    ],
    # Substituto
    "substitution_response": [
        r"sim|pode|ok|aceito|pode ser|manda|tudo bem|claro|sim pode|sim aceito",
        r"não|nao|não quero|nao quero|recuso|não obrigado|sem esse",
    ],
    # Horário
    "business_hours": [
        r"(que horas|horário|funciona|abre|fecha|até que horas)",
    ],
}
```

**IMPORTANTE:** Na Fase 1, o roteamento de intenção é **mínimo**. Apenas
identifica `track_order` e `cancel_order`. Mensagens não identificadas são
encaminhadas para o WhatsApp do lojista.

Na Fase 3, o roteamento usa IA (LLM) para interpretar mensagens complexas.

### 5.4 Conversation Manager

Cada cliente × lojista tem uma **sessão de conversa** que mantém o estado:

```python
@dataclass
class ConversationState:
    """
    Estado de uma conversa WhatsApp entre cliente e lojista.
    """
    merchant_id: int
    customer_phone: str
    customer_name: str

    # Estado atual
    current_flow: str | None  # None = neutro, "ordering", "substitution", "support"
    current_step: str | None  # passo dentro do fluxo

    # Contexto
    active_order_id: int | None
    pending_substitution: dict | None  # {product, substitute}
    last_intent: str | None

    # Timers
    last_message_at: datetime
    expires_at: datetime  # 24h desde última mensagem

    # Flag
    needs_human: bool = False  # True = transferir para atendente
```

```
Ciclo de vida de uma conversa:
  [Mensagem recebida] → [Criar/retomar sessão] → [Detectar intenção]
       → [Executar fluxo] → [Responder ou transferir] → [Aguardar próximo input]

  Expira após 24h de inatividade.
  Se expirar: apenas templates UTILITY podem ser enviados.
```

### 5.5 Human Handoff (Transferência para Humano)

Quando o sistema não consegue atender o cliente adequadamente:

| Situação | Ação |
|----------|------|
| Intenção não identificada | "Não entendi. Vou transferir para o [Nome da Loja] te atender!" + encaminha pro WhatsApp do lojista |
| Cliente pede "falar com atendente" | Transfere imediatamente |
| Fluxo de pedido complexo | Após 3 tentativas frustradas, transfere |
| Reclamação / problema | Transfere + abre ticket de suporte |

Na transferência, o sistema envia uma mensagem de contexto para o lojista:
```
📩 Cliente Ana Silva (11 98888-8888) precisa de atendimento.
Contexto:
  - Pedido #42 (Pendente)
  - Última mensagem: "Quero trocar o refrigerante por suco"
  - Cliente já pediu 5 vezes (R$ 212 em pedidos)
```

---

## 6. Fluxos Conversacionais

### 6.1 Fluxo de Acompanhamento de Pedido

```
Cliente: "Cadê meu pedido?"

Sistema: [Detecta intenção: track_order]
         [Busca pedido mais recente do cliente]
         [Se tem pedido ativo → mostra status]
         [Se não tem → informa]

Respostas possíveis:
  ├── Pedido em preparo:
  │   "Seu pedido #42 já está sendo preparado! 🍕
  │    Previsão: 20 min"
  │
  ├── Pedido saiu para entrega:
  │   "Seu pedido #42 saiu para entrega! 🚗
  │    Acompanhe ao vivo: [tracking link]
  │    Previsão: 10 min"
  │
  ├── Pedido entregue:
  │   "Seu pedido #42 foi entregue às 20:15! 🎉
  │    Ficou tudo certo? Responda se precisar de algo."
  │
  └── Nenhum pedido ativo:
      "Não encontrei nenhum pedido em andamento.
       Quer fazer um novo pedido? 😊
       Acesse: [store link]"
```

### 6.2 Fluxo de Substituição (Mercado — Fase 2/3)

```
Sistema envia:  "O item Arroz Tipo 1 (marca A) está em falta.
                 Aceita Arroz Tipo 1 (marca B) como substituto?
                 💚 Sim / ❌ Não"

Cliente responde:
  ├── "Sim" / "Pode ser" / "💚" → Atualiza pedido, notifica confirmação
  ├── "Não" / "Não quero" / "❌" → Remove item (ou pergunta se quer outro)
  ├── "Quero o marca C" → Interpreta e sugere marca C
  └── (não responde em 30 min) → Timeout: rejeita substituto automaticamente
```

### 6.3 Fluxo de Cancelamento (Cliente)

```
Cliente: "Quero cancelar meu pedido"

Sistema: [Detecta intenção: cancel_order]
         [Verifica estado do pedido]

Respostas possíveis:
  ├── Pedido em PENDENTE:
  │   "Seu pedido #42 ainda não foi confirmado.
  │    Tem certeza que deseja cancelar? 💔
  │    🔴 Sim, cancelar / 🔵 Não, manter"
  │   [Se Sim → cancelamento automático + reembolso]
  │
  ├── Pedido em CONFIRMADO (antes do preparo):
  │   "Seu pedido #42 pode ser cancelado sem custo.
  │    Confirmar cancelamento?
  │    🔴 Sim, cancelar / 🔵 Não, manter"
  │   [Se Sim → cancelamento automático + reembolso]
  │
  ├── Pedido em EM_PREPARO ou PRONTO:
  │   "Seu pedido #42 já está sendo preparado.
  │    Vou avisar o [Nome da Loja] sobre seu pedido de cancelamento.
  │    Entraremos em contato em breve! 🙏"
  │   [Notifica lojista → lojista decide]
  │
  └── Pedido já SAIU_PARA_ENTREGA:
      "Seu pedido #42 já saiu para entrega! 🚗
       Infelizmente não podemos cancelar agora.
       Se precisar, ligue para o [Nome da Loja]: [telefone]"
```

### 6.4 Fluxo de Novo Pedido (Fase 3 — IA Conversacional)

```
Cliente: "Quero pedir uma pizza"

Sistema: [Detecta intenção: new_order]
         [Inicia fluxo de pedido]

Sistema: "Ótimo! 🍕 Vou anotar seu pedido.
          Qual pizza você quer?"

Cliente: "Portuguesa grande"

Sistema: "Portuguesa grande (R$ 45,90) anotada!
          Algo mais?
          (Ex: borda, bebida, sobremesa)"

Cliente: "Borda de catupiry e uma coca 2L"

Sistema: "Fechou! 🎉
          • Pizza Portuguesa (grande) — R$ 45,90
          • Borda Catupiry — R$ 6,00
          • Coca-Cola 2L — R$ 9,50
          ─────────────────
          Total: R$ 61,40

          Endereço: Rua das Flores, 123 (casa)?
          Pagamento: PIX?"

Cliente: "Sim, PIX"

Sistema: "Perfeito! Gerando PIX para pagamento..."
         [Envia template payment_pix]
         [Quando pago: pedido criado no sistema]
```

---

## 7. Conexão do Lojista (Onboarding WhatsApp)

### 7.1 Fluxo de Conexão — Fase 2

Quando o lojista decide conectar o WhatsApp Business ao RapiDrop:

```
1. Lojista acessa "Configurações → WhatsApp" no dashboard
2. Clica em "Conectar WhatsApp Business"
3. Sistema redireciona para o Embedded Signup do Meta:
   - Lojista faz login na conta Facebook Business
   - Aceita os termos
   - Escolhe o número de telefone
   - Verifica o número (código SMS/chamada)
4. Meta retorna um access token para a WABA
5. RapiDrop armazena o token (criptografado) no banco
6. Sistema testa o webhook configurando a URL de callback
7. Pronto! Número do lojista agora está integrado
```

### 7.2 Embedded Signup

O Meta oferece um fluxo de **Embedded Signup** que permite ao lojista
conectar a WABA sem sair do RapiDrop.

```
URL de embedded signup:
  https://business.facebook.com/embedded/signup
    ?business_verification=optional  (não exigir verificação imediata)
    &permissions=whatsapp_business_messaging,whatsapp_business_phone_number
    &state=<state_token> (para validação de retorno)
    &redirect_uri=https://rapidrop.com.br/merchant/whatsapp/callback

No retorno, recebemos:
  - waba_id
  - phone_number_id
  - display_phone_number
  - access_token (validade: 60 dias, renovável)
```

### 7.3 QR Code para Conexão Rápida (Múltiplos Dispositivos)

Para lojistas que não querem passar pelo Embedded Signup completo,
o WhatsApp Business suporta o recurso **Multi-Device** que permite
conectar via QR Code:

```
1. Lojista abre o WhatsApp Business no celular
2. Vai em "Aparelhos conectados" → "Conectar dispositivo"
3. Escaneia o QR Code gerado pelo RapiDrop
4. Pronto! Mensagens aparecem no dashboard

⚠️ Limitação: Funciona apenas com WhatsApp Business (não WhatsApp comum).
⚠️ Escala: Cada QR Code é válido por 60 segundos.
⚠️ Recomendado apenas para testes iniciais ou lojistas com baixo volume.
```

### 7.4 Estados da Conexão

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  NOT     │───►│PENDING   │───►│ ACTIVE   │───►│DISCON-   │
│CONNECTED │    │(signup   │    │          │    │NECTED    │
│          │    │ iniciado)│    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                      │
                                                      ▼
                                                ┌──────────┐
                                                │  EXPIRED │
                                                │(token    │
                                                │ venceu)  │
                                                └──────────┘
```

---

## 8. Gerenciamento de Templates

### 8.1 Ciclo de Vida do Template

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  DRAFT   │───►│PENDING   │───►│ APPROVED │───►│  ACTIVE  │
│(criação) │    │(revisão  │    │          │    │(em uso)  │
│          │    │ Meta)    │    │          │    │          │
└──────────┘    └──────────┘    └────┬─────┘    └──────────┘
                                      │
                                      ▼
                                ┌──────────┐
                                │ REJECTED │
                                │(motivo)  │
                                └──────────┘
                                  │ (ajustar e reenviar)
                                  ▼
                               ┌──────────┐
                               │  DRAFT   │
                               └──────────┘
```

### 8.2 Boas Práticas para Aprovação

| Requisito do Meta | Como o RapiDrop atende |
|-------------------|------------------------|
| Template não pode ser enganoso | Usamos nome do lojista real + informações factuais |
| Template de UTILITY deve ter ação clara | "Seu pedido foi confirmado", "Saiu para entrega" — utilitário puro |
| Template não pode solicitar ação do usuário em UTILITY | Substituição usa INTERACTIVE, não UTILITY |
| Variáveis não podem ser usadas para conteúdo proibido | Variáveis só para nome, número, link, valor |
| Template de MARKETING exige opt-in | Opt-in registrado em `customer_consent` |
| Idioma português brasileiro | `language: "pt_BR"` |

### 8.3 Cache Local de Templates

```python
class TemplateManager:
    """
    Gerencia templates do WhatsApp.
    Mantém cache local sincronizado com o Meta.
    """

    async def get_template(self, name: str) -> Template | None:
        """Busca template no cache local."""
        cached = await redis.get(f"whatsapp:template:{name}")
        if cached:
            return Template.model_validate_json(cached)
        # Se não está em cache, busca no banco
        db_template = await db.query(WhatsAppTemplate).filter_by(name=name).first()
        if db_template and db_template.status == "approved":
            await redis.set(f"whatsapp:template:{name}", db_template.json(), ex=3600)
            return db_template
        return None

    async def sync_templates(self):
        """
        Sincroniza templates do Meta para o cache local.
        Roda a cada 15 minutos via Celery Beat.
        """
        templates = await whatsapp_client.get_templates()
        for t in templates:
            await db.merge(WhatsAppTemplate(
                meta_template_id=t["id"],
                name=t["name"],
                status=t["status"],
                category=t["category"],
                meta_name=t["name"],
                body=t["components"][0]["text"] if t["components"] else "",
                last_synced_at=datetime.now(),
            ))
        await db.commit()
```

---

## 9. Message Logging e Compliance

### 9.1 Registro Imutável de Mensagens

Toda mensagem enviada e recebida é registrada em uma tabela de auditoria:

```
whatsapp_message_log
├── id (UUID)
├── direction (outbound / inbound)
├── merchant_id (FK)
├── customer_phone (E.164)
├── message_type (text / template / image / interactive / etc.)
├── template_name (nullable — se for template)
├── message_body (texto da mensagem)
├── meta_message_id (ID da mensagem no Meta)
├── meta_conversation_id (ID da conversa no Meta)
├── status (sent / delivered / read / failed / received)
├── status_updated_at
├── pricing: jsonb
│   └── {"billable": true, "category": "utility", "amount": 0.005}
├── metadata: jsonb
│   ├── order_id (nullable)
│   ├── error_code (nullable)
│   └── error_message (nullable)
├── created_at (NOT NULL — imutável após inserção)
```

**Regras:**
- `message_body` nunca é editado após inserção (imutável)
- Log é retido por **5 anos** (LGPD + regulação financeira)
- Cliente pode solicitar exportação dos seus dados a qualquer momento
- Cliente pode solicitar exclusão (anonymization do telefone)

### 9.2 Opt-Out (Direito de Revogar Consentimento)

O cliente pode revogar o consentimento a qualquer momento:

```
Palavras-chave que disparam opt-out:
  ─ "PARE" (ou "STOP", "SAIR", "CANCELAR", "NÃO ENVIAR MAIS")
  ─ Detectado no webhook → registra revogação
  ─ A partir desse momento, NENHUMA mensagem é enviada
  ─ Exceção: mensagens transacionais de pedidos ATIVOS ainda são enviadas
    (para concluir a entrega). Após o pedido finalizar, silêncio total.
```

### 9.3 Rate Limits

| Limite | Valor | Estratégia |
|--------|:-----:|------------|
| Mensagens por segundo | **50 msg/s** por número | Queue no Celery, batch processing |
| Conversas paralelas | **400** ativas por número | Abrir nova conversa apenas se necessário |
| Templates por dia | **1.000** (início) a **100.000+** (maduro) | Crescimento gradual com histórico |
| Mensagens marketing na janela 24h | **Ilimitadas** | Dentro da janela, sem restrição |
| Mensagens fora da janela 24h | **Apenas templates UTILITY** | Toda notificação é template UTILITY |

---

## 10. Casos de Exceção

### 10.1 Mensagem Não Entregue

| Motivo | Código Meta | Ação do Sistema |
|--------|:-----------:|-----------------|
| Número inválido/excluído | 1006 | Marcar cliente como `whatsapp_invalid`, tentar SMS |
| Cliente bloqueou o número | 130472 | Marcar `consent_revoked`, parar envios |
| Cliente está fora da área de serviço | 131026 | Retentar em 1h, depois tentar SMS |
| Número não é WhatsApp | 1008 | Marcar cliente como `no_whatsapp`, enviar apenas SMS |
| Template rejeitado pelo Meta | 132015 | Alertar equipe de operações |

### 10.2 Cliente Envia Localização

O cliente pode enviar a localização atual como endereço de entrega:

```
Cliente envia 📍 (localização do GPS)

Sistema:
  1. Extrai lat/lng da mensagem
  2. Reversa para endereço (via Nominatim)
  3. Confirma com o cliente:
     "O endereço é [rua, número, bairro]?
      🔵 Sim / 🔴 Não"
  4. Se confirmado → usa como endereço de entrega
```

### 10.3 Cliente Envia Áudio

Meta Cloud API suporta recebimento de áudio. O sistema pode:

```
1. Baixar o áudio via API do Meta (Media Download)
2. Transcrever usando Whisper/ASR
3. Processar o texto transcrito como mensagem normal

⚠️ Fase 2+: apenas para clientes com histórico de compras.
⚠️ Não transcrever para clientes novos (privacidade).
```

### 10.4 Template Rejeitado pelo Meta

| Situação | Ação |
|----------|------|
| Template rejeitado por "conteúdo genérico" | Adicionar contexto específico do segmento |
| Template rejeitado por "falta de personalização" | Incluir nome do lojista + nome do cliente |
| Template rejeitado por "categoria incorreta" | Revisar classificação (UTILITY vs MARKETING) |
| Template rejeitado por "excesso de emojis" | Remover emojis ou reduzir |

### 10.5 Webhook Fora do Ar

O Meta espera resposta `200 OK` no webhook em até **5 segundos**.
Se exceder, o Meta marca o webhook como falho e para de enviar.

```
Proteções:
  1. Processamento assíncrono: webhook só registra e enfileira
  2. Resposta 200 imediata (antes de processar)
  3. Se webhook cair: Meta retenta por até 72h
  4. Ao voltar: processar mensagens acumuladas na fila
  5. Alerta se webhook ficar 5 min sem resposta
```

### 10.6 Duplicidade de Mensagem

O Meta pode reenviar a mesma mensagem em caso de timeout no webhook.

```
Proteção:
  - Campo `meta_message_id` é UNIQUE na tabela de log
  - Mensagens duplicadas são ignoradas na inserção (ON CONFLICT DO NOTHING)
```

---

## 11. Estratégia de Implementação

### 11.1 Por Onde Começar (Fase 1 — MVP)

```
MVP — O essencial para o lançamento:

  Semana 1:
    [ ] Registrar WABA RapiDrop no Meta Business
    [ ] Configurar webhook endpoint básico (POST /api/v1/whatsapp/webhook)
    [ ] Implementar verificação de webhook (GET, hub.challenge)
    [ ] Criar tabelas: whatsapp_message_log, customer_consent
  
  Semana 2:
    [ ] Implementar envio de templates (Celery worker)
    [ ] Template order_confirmed (submeter e aguardar aprovação)
    [ ] Template order_out_for_delivery (submeter e aguardar aprovação)
    [ ] Template order_delivered (submeter e aguardar aprovação)
    [ ] Template order_cancelled (submeter e aguardar aprovação)
    [ ] Integrar envio com as transições da máquina de estados
  
  Semana 3:
    [ ] Template prescription_request (farmácia — opcional no MVP)
    [ ] Template substitution_offer (mercado — opcional no MVP)
    [ ] Template payment_pix
    [ ] Implementar consentimento no checkout
    [ ] Implementar opt-out (PARE/SAIR)
  
  Semana 4:
    [ ] Dashboard: log de mensagens enviadas
    [ ] Tratamento de erros (número inválido, bloqueado)
    [ ] Fallback SMS para notificações críticas
    [ ] Testes E2E com número real sandbox
```

### 11.2 Configuração do WABA no Meta

```yaml
# Passos administrativos necessários (fora do código):

1. Criar Facebook Business Manager
   └── business.facebook.com/overview

2. Solicitar verificação do negócio (Meta Business Verification)
   └── Necessário: CNPJ, comprovante de endereço, documentos dos sócios
   └── Prazo: 1-2 semanas

3. Criar WhatsApp Business Account (WABA)
   └── business.facebook.com/wa/manage
   └── Associar ao Business Manager

4. Solicitar número de telefone
   └── Número novo (não pode ser usado no WhatsApp pessoal)
   └── Verificar com código SMS

5. Configurar webhook
   └── URL: https://api.rapidrop.com.br/api/v1/whatsapp/webhook
   └── Token de verificação: configurado via env var
   └── Inscrição nos eventos: messages, message_deliveries, message_reads

6. Criar e submeter templates
   └── business.facebook.com/wa/manage/message-templates/
   └── Submeter UTILITY templates primeiro (aprovação mais rápida)

7. Configurar phone number profile
   └── About: "Sistema de pedidos RapiDrop"
   └── Profile picture: logo RapiDrop
```

### 11.3 Modelo de Dados (Tabelas)

```sql
-- Templates WhatsApp
CREATE TABLE whatsapp_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(20) NOT NULL, -- 'utility' | 'marketing'
    status VARCHAR(20) NOT NULL,   -- 'draft' | 'pending' | 'approved' | 'rejected'
    meta_template_id VARCHAR(100),
    meta_name VARCHAR(100),
    body_template TEXT NOT NULL,
    variables JSONB,               -- ["name", "order_id", "merchant_name"]
    rejection_reason TEXT,
    segment VARCHAR(20),           -- 'all' | 'food' | 'pharmacy' | 'grocery'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_synced_at TIMESTAMPTZ
);

-- Mensagens logadas (imutável)
CREATE TABLE whatsapp_message_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    direction VARCHAR(10) NOT NULL,         -- 'inbound' | 'outbound'
    merchant_id INTEGER REFERENCES merchants(id),
    customer_phone VARCHAR(20) NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    template_name VARCHAR(100),
    message_body TEXT,
    meta_message_id VARCHAR(100) UNIQUE,
    meta_conversation_id VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    status_updated_at TIMESTAMPTZ,
    pricing JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Consentimento do cliente
CREATE TABLE customer_consent (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id INTEGER REFERENCES customers(id),
    merchant_id INTEGER REFERENCES merchants(id),
    channel VARCHAR(20) NOT NULL,           -- 'whatsapp' | 'sms' | 'push'
    consent_granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    consent_revoked_at TIMESTAMPTZ,
    source VARCHAR(50) NOT NULL,            -- 'checkout' | 'onboarding' | 'link'
    ip_address INET,
    user_agent TEXT,
    UNIQUE (customer_id, merchant_id, channel)
);

-- Conversas ativas
CREATE TABLE whatsapp_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    customer_phone VARCHAR(20) NOT NULL,
    customer_name VARCHAR(200),
    current_flow VARCHAR(50),
    current_step VARCHAR(50),
    active_order_id INTEGER REFERENCES orders(id),
    context JSONB,
    needs_human BOOLEAN NOT NULL DEFAULT FALSE,
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (merchant_id, customer_phone)
);

-- Telefones WhatsApp gerenciados
CREATE TABLE whatsapp_phone_numbers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER REFERENCES merchants(id),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    waba_id VARCHAR(100),
    waba_phone_id VARCHAR(100),
    is_rapidrop_owned BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    config JSONB,
    connected_at TIMESTAMPTZ,
    disconnected_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_wa_log_merchant ON whatsapp_message_log(merchant_id, created_at DESC);
CREATE INDEX idx_wa_log_customer ON whatsapp_message_log(customer_phone, created_at DESC);
CREATE INDEX idx_wa_log_meta_id ON whatsapp_message_log(meta_message_id);
CREATE INDEX idx_wa_consent_lookup ON customer_consent(customer_id, merchant_id, channel);
CREATE INDEX idx_wa_conversations_active ON whatsapp_conversations(merchant_id, expires_at)
    WHERE expires_at > NOW();
```

---

## 12. Cobertura de Testes

### 12.1 Testes de Unidade

```python
# Envio de template
def test_send_template_success():
    """Template é enviado com sucesso via API do Meta."""
    ...

def test_send_template_no_consent_skips():
    """Sem consentimento, mensagem não é enviada."""
    ...

def test_send_template_rate_limit_retries():
    """Rate limit do Meta dispara retry com backoff."""
    ...

def test_send_template_invalid_number():
    """Número inválido é registrado e fallback SMS é acionado."""
    ...

# Webhook
def test_webhook_verification():
    """GET /webhook responde com hub.challenge."""
    ...

def test_webhook_invalid_signature_403():
    """Assinatura inválida retorna 403."""
    ...

def test_webhook_duplicate_message_ignored():
    """Mensagem duplicada (mesmo meta_message_id) é ignorada."""
    ...

# Consentimento
def test_opt_out_stops_messages():
    """Cliente que enviou PARE não recebe mais mensagens."""
    ...

def test_opt_out_still_receives_active_order():
    """Cliente que enviou PARE ainda recebe updates de pedido ativo."""
    ...

# Intent detection
def test_detect_track_order():
    """'Cadê meu pedido' é detectado como track_order."""
    ...

def test_detect_cancel_order():
    """'Quero cancelar' é detectado como cancel_order."""
    ...

def test_unknown_intent_has_fallback():
    """Intenção não reconhecida tem fallback para atendente."""
    ...
```

### 12.2 Testes de Integração

```python
# Webhook → processamento
def test_inbound_message_creates_conversation():
    """Mensagem recebida cria sessão de conversa."""
    ...

def test_conversation_expires_after_24h():
    """Conversa expira após 24h de inatividade."""
    ...

# Fila de envio
def test_celery_queue_processes_messages():
    """Worker processa fila de mensagens corretamente."""
    ...

# Templates
def test_template_cache_hit():
    """Template em cache é usado sem chamar Meta API."""
    ...

def test_template_sync_updates_local():
    """Sincronização atualiza templates locais com Meta."""
    ...
```

### 12.3 Testes E2E

```python
# Fluxo completo de notificação
def test_order_confirmed_sends_whatsapp():
    """Transição para confirmado dispara template order_confirmed."""
    # Arrange: pedido em "pendente"
    # Act: confirmar pedido
    # Assert: worker de WhatsApp foi chamado com template correto
    ...

# Fluxo de resposta do cliente
def test_customer_replies_substitution():
    """Cliente responde 'Sim' para substituição → pedido atualizado."""
    ...
```

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Baseado nos documentos:** `docs/ideacao-rapidrop.md`, `docs/maquina-estados-pedido.md`,
> `docs/experiencia-cliente.md`
> **Próximo documento sugerido:** `docs/fluxo-financeiro.md`
