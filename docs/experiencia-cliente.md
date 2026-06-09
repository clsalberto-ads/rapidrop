# RapiDrop — Experiência do Cliente Final

> Como o consumidor se cadastra, descobre lojas, pede, paga e fideliza.
> Estratégia de aquisição de clientes com o lojista como protagonista.

---

## Índice

1. [Visão Estratégica](#1-visão-estratégica)
2. [Canais do Cliente](#2-canais-do-cliente)
3. [Cadastro e Conta Única](#3-cadastro-e-conta-única)
4. [Catálogo e Navegação](#4-catálogo-e-navegação)
5. [Carrinho e Checkout](#5-carrinho-e-checkout)
6. [Favoritos — Lojas e Pratos](#6-favoritos--lojas-e-pratos)
7. [Distância e Taxa de Entrega](#7-distância-e-taxa-de-entrega)
8. [Promoções e Cupons](#8-promoções-e-cupons)
9. [Acompanhamento do Pedido](#9-acompanhamento-do-pedido)
10. [Estratégia de Aquisição de Clientes](#10-estratégia-de-aquisição-de-clientes)
11. [Fluxos Completos](#11-fluxos-completos)
12. [Modelagem de Dados](#12-modelagem-de-dados)
13. [Comparativo com Concorrentes](#13-comparativo-com-concorrentes)

---

## 1. Visão Estratégica

### 1.1 Princípios

| Princípio | Implicação |
|-----------|------------|
| **O lojista é o dono da relação com o cliente** | O cliente é do lojista, não do RapiDrop. Dados de pedidos pertencem ao lojista. |
| **Conta única do cliente** | Um cadastro funciona em **todas as lojas** que usam RapiDrop. O cliente não recadastra dados a cada loja. |
| **Experiência white label** | Cada loja tem sua própria cara (cores, logo, domínio) — o cliente não precisa saber que é RapiDrop por trás. |
| **Descoberta opcional** | O cliente pode descobrir lojas próximas no app RapiDrop, mas a relação é sempre com a loja. |
| **Cadastro assistido pelo lojista** | O lojista promove ativamente o cadastro dos seus clientes dentro da própria loja (física e digital). |

### 1.2 A Grande Ideia

Diferente do iFood (marketplace que **intermedia** a relação loja-cliente), o RapiDrop é uma **infraestrutura branca**:

```
iFood:                RapiDrop:
──────                ────────
Cliente é do iFood    Cliente é do lojista
Lojista não tem       Lojista tem dados completos
contato direto         do cliente
iFood decide          Lojista decide preços,
preços e entregas      promoções e operação
Comissão 12-27%       Taxa fixa de 1,5-2%
```

O cliente final se cadastra **uma vez** e pode pedir de **qualquer loja** que use RapiDrop. A loja pode **promover seu próprio canal** (site + app) dentro do seu estabelecimento físico, criando uma relação direta com o cliente.

---

## 2. Canais do Cliente

O cliente pode interagir com as lojas por **três canais**, todos alimentados pelo mesmo backend:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE FINAL                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Site da Loja    │ │  App RapiDrop    │ │  WhatsApp        │
│  (White Label)   │ │  (Cliente)       │ │  (via link)      │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ pizzaria.minha-  │ │ App iOS/Android  │ │ Link comparti-   │
│ loja.com.br      │ │ com TODAS as     │ │ lhado que abre   │
│                  │ │ lojas da região  │ │ o site da loja   │
│ Com a cara da    │ │                  │ │ com o item já    │
│ loja (cores,     │ │ Descoberta:      │ │ selecionado      │
│ logo)            │ │ "Lojas perto     │ │                  │
│                  │ │ de mim"          │ │                  │
│ Funciona como    │ │                  │ │                  │
│ site próprio     │ │ Favoritos,       │ │                  │
│                  │ │ histórico,       │ │                  │
│                  │ │ endereços        │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 2.1 Site White Label da Loja

Cada loja tem seu próprio site com domínio personalizado:

```
pizzariadonorte.com.br        → Restaurante
drogariasaovicente.com.br     → Farmácia
mercadoramos.com.br           → Mercado
```

**Características:**
- Domínio próprio do lojista (ou subdomínio `loja.rapidrop.com.br` se não tiver)
- Cores, logo e identidade visual da loja
- Catálogo completo com fotos e preços
- Checkout integrado com mesmo login do cliente RapiDrop
- SEO próprio (cada loja ranqueia no Google separadamente)
- A loja divulga esse link no Instagram, WhatsApp e cardápio físico

### 2.2 App RapiDrop (Cliente)

Um aplicativo unificado (iOS + Android) onde o cliente:

- Vê **todas as lojas** que usam RapiDrop na sua região
- Filtra por segmento (comida, farmácia, mercado)
- Busca por nome de loja ou produto
- Acessa seus **favoritos** (lojas e pratos)
- Vê **pedidos anteriores** e **status em tempo real**
- Gerencia endereços e pagamentos

> ⚠️ **Importante:** O app RapiDrop é um **facilitador de descoberta**, não um marketplace. A comissão continua sendo apenas o percentual do SaaS — não há taxa extra por pedido vindo do app.

### 2.3 Links Compartilháveis (WhatsApp, Redes Sociais)

Qualquer página de produto, loja ou promoção gera um **link único** que:
- Abre o site da loja se o cliente não tem o app
- Abre o app se o cliente já tem instalado (deep link)
- Pode conter **parâmetros de rastreio** (ex: `?ref=instagram`)

---

## 3. Cadastro e Conta Única

### 3.1 Como o Cliente se Cadastra

| Método | Onde | Experiência |
|--------|------|-------------|
| **Celular + OTP** | Site, app ou QR code físico | Cliente digita o celular, recebe SMS com código de 4 dígitos. Pronto. |
| **Google/Apple** | App | Login social com um toque. |
| **Email + senha** | Site | Método tradicional. |
| **QR Code na loja** | Balcão, mesa ou sacola | Cliente aponta a câmera → abre a loja no navegador com um link que já inicia o pedido. Ao fechar o pedido, se não tiver conta, cadastra em 2 toques. |

**Dados mínimos do cadastro:**

| Campo | Obrigatório? | Uso |
|-------|:-----------:|-----|
| Nome | ✅ | Identificação |
| Celular | ✅ | Login OTP + contato do entregador |
| Email | ❌ | Opcional — recuperação de conta e notificações |
| CEP | ✅ | Verificar lojas que entregam no endereço |
| Endereço completo | Na primeira compra | Entrega |

### 3.2 Conta Única — O Diferencial

O cliente se cadastra **uma vez** e usa a mesma conta em **todas as lojas** RapiDrop:

```
Exemplo de jornada:
  1. Cliente pede pizza na Pizzaria do Norte (site dela)
     → Faz cadastro com celular + endereço + cartão
  2. No dia seguinte, abre o app RapiDrop e descobre
     uma farmácia perto de casa
     → Já está logado. Já tem endereço e cartão salvos.
     → Pede em 30 segundos.
  3. Na semana seguinte, a mãe manda um link do WhatsApp
     do Mercado Ramos
     → Abre o site, já logado, já com endereço.
     → Adiciona itens e finaliza.
```

**Benefício para o cliente:** Nunca mais precisa cadastrar dados em loja nova.
**Benefício para o lojista:** Cliente novo chega pré-cadastrado (se já tem conta RapiDrop).

### 3.3 Endereços

O cliente pode salvar **múltiplos endereços** com etiquetas:

```
🏠 Casa     Rua das Flores, 123 — Casa
💼 Trabalho Av. Paulista, 1000 — Ap 52
🏡 Outro    Rua dos Pinheiros, 50 — Casa 2
```

- Cada endereço tem: CEP, logradouro, número, complemento, bairro, cidade, UF
- Ponto de referência (opcional): "Próximo ao mercado"

### 3.4 Formas de Pagamento

| Método | Como funciona |
|--------|--------------|
| **Cartão de crédito** | Salvo com token (nunca armazenamos número completo). Múltiplos cartões. |
| **PIX** | Gera QR Code na finalização. Confirmação instantânea. |
| **Dinheiro** | Pagamento na entrega (troco calculado no checkout). |
| **Cartão na entrega** | Maquininha na porta. |

### 3.5 Privacidade e Dados

- O lojista vê **apenas os dados dos clientes que pediram na sua loja**
- O cliente pode exportar ou excluir seus dados a qualquer momento (LGPD)
- Nenhum dado é vendido a terceiros
- O cliente pode desativar notificações por loja

---

## 4. Catálogo e Navegação

### 4.1 Página da Loja

Cada loja tem uma página com:

```
┌─────────────────────────────────────────────────┐
│  🍕 PIZZARIA DO NORTE                   4.8 ★  │
│  Aberto • 18:00-23:00                    │
│  Entrega: R$ 5,00 • Mínimo: R$ 25,00     │
│  📍 Entrega para: Seu endereço aqui      │
├─────────────────────────────────────────────────┤
│  [Buscar nesta loja...]                         │
├─────────────────────────────────────────────────┤
│  🍕 PIZZAS                    (Ver tudo →)      │
│  ┌────────────────────────────────────────┐     │
│  │ Calabresa       ─── R$ 39,90  [ + ]   │     │
│  │ Mussarela       ─── R$ 35,90  [ + ]   │     │
│  │ Portuguesa      ─── R$ 44,90  [ + ]   │     │
│  └────────────────────────────────────────┘     │
│                                                  │
│  🥤 BEBIDAS                   (Ver tudo →)      │
│  ┌────────────────────────────────────────┐     │
│  │ Coca-Cola  2L   ─── R$ 10,90  [ + ]   │     │
│  │ Guaraná 2L      ─── R$ 9,90   [ + ]   │     │
│  └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

**Elementos da página:**

| Elemento | Descrição |
|----------|-----------|
| **Capa/Foto da loja** | Imagem principal (ambiente, prato principal) |
| **Avaliação** | Média de estrelas + número de avaliações |
| **Status** | Aberto/Fechado + horário de funcionamento |
| **Taxa de entrega** | Valor calculado pela distância (seção 7) |
| **Valor mínimo** | Pedido mínimo exigido pela loja |
| **Endereço de entrega** | Cliente informa ou confirma o CEP |
| **Busca** | Busca por nome do produto dentro da loja |
| **Categorias** | Seções do catálogo (Pizzas, Bebidas, Sobremesas) |
| **Produtos** | Nome, descrição curta, preço, foto, botão de adicionar |
| **Variações** | Tamanhos (P/M/G), sabores (se aplicável) |

### 4.2 Catálogo de Produtos

Cada produto pode ter:

| Atributo | Descrição | Exemplo |
|----------|-----------|---------|
| Nome | Título visível | "Pizza Calabresa" |
| Descrição | Breve descrição | "Molho, mussarela, calabresa, cebola e azeitona" |
| Fotos | 1-3 imagens | Foto do prato |
| Preço | Valor atual | R$ 39,90 |
| Preço promocional | Opcional | R$ 29,90 (ver seção 8) |
| Variações | Tamanhos, sabores | P R$ 29,90 / M R$ 39,90 / G R$ 49,90 |
| Adicionais | Itens extras | "Adicionar borda recheada + R$ 6,00" |
| Categoria | Agrupamento | "Pizzas Salgadas" |
| Disponibilidade | Ativo/inativo | Controlado pelo estoque da loja |
| Selos | 🥇 Mais pedido, 🌱 Vegano, 🔥 Picante | Destaques visuais |

### 4.3 Busca e Descoberta (App RapiDrop)

No app unificado, o cliente pode:

```
Busca:           [ "pizza" ───────────────────────── ]
                 Resultados mostram lojas + produtos

Filtros:         ┌─ Categoria: ──┐  ┌─ Distância: ─┐
                 │ ■ Comida      │  │ ■ Até 1 km   │
                 │ □ Farmácia    │  │ ■ Até 3 km   │
                 │ □ Mercado     │  │ ■ Até 5 km   │
                 └───────────────┘  └──────────────┘
                 ┌─ Ordenar: ─────┐
                 │ ● Distância   │
                 │ ○ Avaliação   │
                 │ ○ Tempo de    │
                 │   entrega     │
                 └───────────────┘
```

**Seções do app:**
- **Perto de você** — lojas que entregam no seu endereço, ordenadas por distância
- **Favoritos** — suas lojas e pratos favoritos
- **Pedindo de novo?** — lojas onde você já pediu
- **Aberto agora** — lojas abertas no momento
- **Promoções** — lojas com ofertas ativas

---

## 5. Carrinho e Checkout

### 5.1 Carrinho

```
┌─────────────────────────────────────────────────┐
│  CARRINHO                              🛒       │
│  Loja: Pizzaria do Norte                         │
├─────────────────────────────────────────────────┤
│  Pizza Calabresa (G)        R$ 49,90  [ - 2 + ] │
│    Borda recheada           R$ 6,00              │
│                                                  │
│  Coca-Cola 2L               R$ 10,90  [ - 1 + ] │
│                                                  │
│  Subtotal:                         R$ 116,70     │
│  Taxa de entrega:                  R$ 5,00       │
│  Desconto:                        -R$ 10,00      │
│  ─────────────────────────────────────────────   │
│  Total:                            R$ 111,70     │
│                                                  │
│  [ 🎟️ Cupom de desconto ]                       │
│  [ 📝 Observações: "Sem cebola na pizza" ]      │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │        [ FINALIZAR PEDIDO ]              │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 5.2 Fluxo de Checkout

```mermaid
Cart → Confirmar endereço → Pagamento → Revisar → Finalizar
  │          │                  │          │
  ▼          ▼                  ▼          ▼
  Revisa    Seleciona          Escolhe    Confirma tudo
  itens     entre os           cartão,    + forma de
            endereços          PIX ou     pagamento
            salvos             dinheiro
```

**Etapas detalhadas:**

1. **Carrinho** — Revisa itens, quantidades, observações
2. **Endereço** — Confirma/local de entrega (se múltiplos endereços salvos)
3. **Pagamento** — Seleciona forma de pagamento salva ou adiciona nova
4. **Revisão** — Resumo completo: itens, endereço, pagamento, valor
5. **Finalizar** — Botão "Finalizar Pedido" → pedido enviado para a loja

### 5.3 Regras de Checkout

- **Valor mínimo:** Se não atingiu, bloqueia e mostra "Faltam R$ X para o pedido mínimo"
- **Disponibilidade:** Produtos fora de estoque são removidos com aviso
- **Horário:** Se a loja fechar antes da entrega estimada, avisa antes de finalizar
- **Troco:** Se for dinheiro, cliente informa para quanto precisa de troco

---

## 6. Favoritos — Lojas e Pratos

### 6.1 Conceito

O cliente pode **favoritar** lojas e produtos para acesso rápido. É o principal mecanismo de **retenção e recorrência**.

### 6.2 Tipos de Favorito

| Tipo | O que é | Onde aparece |
|------|---------|--------------|
| **⭐ Loja favorita** | Loja que o cliente marcou como favorita | Seção "Favoritos" no app, destaque na lista |
| **❤️ Prato favorito** | Produto específico favoritado | Acesso rápido na página da loja + "Pedir de novo" |
| **🔄 Pedir de novo** | Últimos pedidos com 1 clique | Botão "Pedir de novo" no histórico |

### 6.3 Funcionalidades de Favoritos

```
┌─────────────────────────────────────────────────┐
│  ⭐ MINHAS LOJAS FAVORITES                      │
│                                                  │
│  🍕 Pizzaria do Norte         4.8 ★  Aberta     │
│     Pedido mínimo: R$ 25  ·  Entrega: R$ 5      │
│                                                  │
│  💊 Drogaria São Vicente      4.5 ★  Aberta     │
│     Pedido mínimo: R$ 15  ·  Entrega: R$ 7      │
│                                                  │
│  🛒 Mercado Ramos             4.7 ★  Fechada    │
│     Pedido mínimo: R$ 30  ·  Entrega: Grátis    │
└─────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────┐
│  ❤️ PRATOS FAVORITOS                            │
│                                                  │
│  🍕 Pizza Calabresa (Pizzaria do Norte)  R$39,90│
│     [ + Adicionar ao carrinho ]                 │
│                                                  │
│  🥤 Coca-Cola 2L (Mercado Ramos)        R$10,90 │
│     [ + Adicionar ao carrinho ]                 │
│                                                  │
│  💊 Dorflex 10 comp (Drogaria São Vicente)R$8,50│
│     [ + Adicionar ao carrinho ]                 │
└─────────────────────────────────────────────────┘
```

### 6.4 Notificações de Favoritos

O cliente pode ativar notificações **por loja favorita**:

> 🔔 "Pizzaria do Norte está com promoção: Pizza Grande por R$ 39,90 hoje!"
> 🔔 "Mercado Ramos abriu — já pode fazer seu pedido da semana"

- O cliente opta por receber ou não (opt-in por loja)
- Máximo de 2 notificações por loja por semana (anti-spam)

### 6.5 "Pedir de Novo" em 1 Clique

No histórico de pedidos:

```
┌─────────────────────────────────────────────────┐
│  SEUS ÚLTIMOS PEDIDOS                            │
│                                                  │
│  🍕 Pizzaria do Norte — Ontem                    │
│     Pizza Calabresa (G), Coca-Cola 2L            │
│     R$ 62,80  [ 🔁 Pedir de novo ]              │
│                                                  │
│  💊 Drogaria São Vicente — 3 dias atrás          │
│     Dorflex, Band-aid, Álcool gel               │
│     R$ 32,50  [ 🔁 Pedir de novo ]              │
└─────────────────────────────────────────────────┘
```

"Pedir de novo" **recria o carrinho exatamente igual** ao pedido anterior, com os mesmos itens, variações e observações. O cliente só confirma e finaliza.

---

## 7. Distância e Taxa de Entrega

### 7.1 Raio de Entrega

Cada loja define seu **raio de entrega**:

| Forma | Descrição | Exemplo |
|-------|-----------|---------|
| **Raio fixo** | Entrega até X km do centro da loja | 5 km |
| **Raio por CEP** | Lista de CEPs atendidos | CEPs 59000-000 a 59100-000 |
| **Raio por bairro** | Lista de bairros atendidos | "Petrópolis, Tirol, Lagoa Nova" |

**Regras:**
- O cliente informa o CEP antes de ver o cardápio
- Se o CEP está fora do raio: "Essa loja não entrega no seu endereço"
- Se está dentro: mostra cardápio + taxa calculada

### 7.2 Cálculo da Taxa de Entrega

| Método | Cálculo | Exemplo |
|--------|---------|---------|
| **Taxa fixa** | Valor único para todo o raio | R$ 5,00 |
| **Por faixa de distância** | Tabela por km | Até 2 km: R$ 3,00 · 2-5 km: R$ 7,00 · 5-10 km: R$ 12,00 |
| **Por km rodado** | R$ X por km | R$ 1,50/km → 5 km = R$ 7,50 |
| **Grátis acima de X** | Frete grátis para pedidos acima de Y | Grátis acima de R$ 50,00 |
| **Taxa dinâmica** | Varia por horário/dia | Seg-sex: R$ 5,00 · Sáb-dom: R$ 8,00 |

> O lojista escolhe o método no painel de administração. Pode combinar (ex: taxa fixa + grátis acima de R$ 50).

### 7.3 Distância no App de Descoberta

No app RapiDrop, as lojas são filtradas por **distância real**:

```
📍 Seu endereço: Rua das Flores, 123 — Petrópolis

🟢 Lojas que entregam no seu endereço:
   🍕 Pizzaria do Norte      1,2 km  ~30 min
   💊 Drogaria São Vicente   2,1 km  ~40 min
   🛒 Mercado Ramos          4,5 km  ~55 min

🔴 Lojas que NÃO entregam (fora do raio):
   🥗 Restaurante Saúde      8 km    (não atende sua região)
```

---

## 8. Promoções e Cupons

### 8.1 Tipos de Promoção

| Tipo | Quem cria | Exemplo |
|------|-----------|---------|
| **Desconto em produto** | Lojista | "Pizza Calabresa de R$ 39,90 por R$ 29,90" |
| **Leve X pague Y** | Lojista | "Compre 2 pizzas, leve 3" |
| **Frete grátis** | Lojista | "Frete grátis acima de R$ 50" |
| **Desconto por valor mínimo** | Lojista | "R$ 10 off em pedidos acima de R$ 80" |
| **Cupom único** | Lojista | "PIZZA10" — 10% off |
| **Cupom por cliente** | Lojista | "Bem-vindo! R$ 15 de desconto no primeiro pedido" |
| **Happy Hour** | Lojista | "Todas as pizzas com 20% off das 18h às 20h" |
| **Programa de fidelidade** | Lojista | "A cada 10 pizzas, uma grátis" |
| **Indique um amigo** | Lojista + Sistema | "Você ganha R$ 10, seu amigo ganha R$ 10" |
| **Primeira compra** | Plataforma (opcional) | RapiDrop cobre o desconto para atrair novos clientes |

### 8.2 Mecânica de Cupons

```
Cupom = código alfanumérico + regras de uso

Regras possíveis:
  - Valor mínimo do pedido: R$ 50,00
  - Válido para: toda a loja / categoria específica / produto específico
  - Tipo: percentual (%) / valor fixo (R$) / frete grátis
  - Limite de usos: 100 usos / 1 uso por cliente
  - Validade: data início + data fim
  - Horário: válido apenas das 18h às 22h
  - Cliente específico: cupom nominal para cliente selecionado
```

### 8.3 Exibição de Promoções

```
Na página da loja:

  ⚡ PROMOÇÕES ATIVAS
  ┌────────────────────────────────────────────┐
  │ 🎉 Pizza Grande (R$ 49,90 → R$ 39,90)     │
  │    Válida até domingo                      │
  │                                            │
  │ 🚚 Frete grátis acima de R$ 50            │
  │                                            │
  │ 🎟️ Use o cupom: PIZZA10                   │
  │    (10% off na primeira compra)            │
  └────────────────────────────────────────────┘
```

**Badges nos produtos:**

```
🍕 Calabresa       R$ 39,90   R$ 29,90  🔥 -25%
                                        [Promoção do dia]
```

### 8.4 Programa de Fidelidade

O lojista pode ativar um programa de fidelidade simples:

```
🃏 CARTÃO FIDELIDADE — Pizzaria do Norte

  🍕🍕🍕🍕🍕🍕🍕🍕__   8/10 pizzas
  ⭐ Faltam 2 pizzas para ganhar uma grátis!
```

| Modelo | Como funciona |
|--------|--------------|
| **A cada X, ganhe 1** | "A cada 10 pizzas, a 11ª é grátis" |
| **Acúmulo de pontos** | "R$ 1 = 1 ponto. 100 pontos = R$ 10 de desconto" |
| **Aniversário** | "Mês do seu aniversário: 20% off" |

---

## 9. Acompanhamento do Pedido

### 9.1 Status do Pedido

Após finalizar, o cliente vê o progresso em tempo real:

```
🟢 Pedido confirmado     18:32  │ Já estamos preparando!
🟡 Em preparo            18:35  │ Sua pizza está no forno
🟡 Saiu para entrega     19:05  │ 🛵 Entregador a caminho
🔴 Entregue!             19:22  │ ✅ Bom apetite!
```

### 9.2 Mapa ao Vivo (GPS)

Quando o pedido sai para entrega, o cliente vê:

```
┌─────────────────────────────────────────────────┐
│ 🛵 ENTREGADOR A CAMINHO                         │
│                                                  │
│  [ Mapa com rota em tempo real ]                 │
│                                                  │
│  👤 João (entregador) — ★ 4.9                    │
│  📍 A 3 minutos do seu endereço                   │
│  📱 (84) 99999-0000 (ligar para o entregador)    │
└─────────────────────────────────────────────────┘
```

### 9.3 Notificações

| Momento | Canal | Mensagem |
|---------|-------|----------|
| Pedido confirmado | Push / WhatsApp | "Seu pedido na Pizzaria do Norte foi confirmado! 🍕" |
| Saiu para entrega | Push / WhatsApp | "Seu pedido saiu para entrega! 🛵" |
| Entregador chegou | Push | "Entregador chegou! 🛵" |
| Promoção da loja favorita | Push (opt-in) | "Pizzaria do Norte: 20% off hoje! 🎉" |
| Carrinho abandonado | Push (1h depois) | "Seu carrinho ainda está aqui →" |

---

## 10. Estratégia de Aquisição de Clientes

### 10.1 O Lojista como Protagonista

Diferente do iFood, onde o marketplace atrai o cliente **para a plataforma**, no RapiDrop o **lojista atrai o cliente para a sua loja**. O RapiDrop fornece as ferramentas.

### 10.2 Materiais de Divulgação (Para o Lojista)

O RapiDrop fornece ao lojista **materiais prontos** para divulgar seu canal próprio:

```
┌─────────────────────────────────────────────────┐
│           KIT DE DIVULGAÇÃO DO LOJISTA          │
├─────────────────────────────────────────────────┤
│                                                   │
│  📱 QR CODE PARA BALCÃO                          │
│  ┌──────────────────────┐                        │
│  │   Peça pelo nosso    │                        │
│  │   delivery direto!   │                        │
│  │                      │                        │
│  │   [QR CODE]          │                        │
│  │                      │                        │
│  │   📲 Aponte a câmera │                        │
│  │   🎉 1º pedido com   │                        │
│  │      10% de desconto │                        │
│  └──────────────────────┘                        │
│                                                   │
│  📲 WALLPAPER PARA WHATSAPP                      │
│  ├─ "Peça pelo link: bit.ly/pizzariadonorte"     │
│                                                   │
│  📸 POST PARA INSTAGRAM                          │
│  ├─ Arte pronta com imagem + link na bio          │
│                                                   │
│  🧾 IMPRESSO PARA SACOLA                         │
│  ├─ Adesivo/panfleto dentro da sacola:           │
│  │  "Na próxima, peça pelo nosso site e ganhe    │
│  │   frete grátis! → pizzariadonorte.com.br"     │
│                                                   │
│  🔗 LINK DE INDICAÇÃO                            │
│  ├─ Link único: "Indique um amigo e ganhe R$ 10" │
└─────────────────────────────────────────────────┘
```

### 10.3 Estratégias de Crescimento

#### Estratégia 1: QR Code no Balcão / Mesa

O lojista imprime um QR code que leva direto ao **site da loja já com cadastro facilitado**:

```
Jornada:
  Cliente está na loja → Vê placa "Peça delivery pelo nosso site"
  → Escaneia QR code → Abre página da loja
  → "Primeira compra? Clique para pedir"
  → Informa celular → Recebe código SMS
  → Pronto! Já pode pedir.
  
  🎁 Bônus da primeira compra: R$ 10 de desconto
```

**Taxa de conversão esperada:** 15-25% dos clientes presenciais que escaneiam o QR code fazem o primeiro pedido online em até 7 dias.

#### Estratégia 2: Indicação de Amigos

```
"Indique um amigo e vocês dois ganham R$ 10!"

Fluxo:
  1. Cliente entra no app → "Indicar amigos"
  2. Compartilha link único via WhatsApp
  3. Amigo clica, se cadastra e faz primeiro pedido
  4. Ambos recebem R$ 10 de desconto no próximo pedido

Custo: R$ 20 por novo cliente ativo (R$ 10 para quem indicou + R$ 10 para o novo)
Quem paga: O lojista decide se arca com o custo ou compartilha com o RapiDrop
```

#### Estratégia 3: Primeira Compra com Desconto

O lojista **cria um cupom automático** para primeira compra de cada cliente:

```
🎫 CUPOM: BEMVINDO
  - R$ 15 de desconto na primeira compra (ou 15%, o que for menor)
  - Válido apenas para clientes novos (nunca pediram antes)
  - Expira em 30 dias após criar a conta
```

#### Estratégia 4: Sacola Inteligente

Dentro de cada delivery, o lojista coloca um **panfleto/adesivo**:

```
"Gostou? Na próxima, peça direto pelo nosso site
 e ganhe frete grátis na sua volta!

 📲 pizzariadonorte.com.br
 🎟️ Use o cupom: VOLTEI (frete grátis na próxima)
```

#### Estratégia 5: Cardápio Digital via QR Code

O QR code na mesa pode ser **dual-purpose**:

```
📱 Cardápio digital → Cliente vê o cardápio no celular
                     → Se quiser pedir, clica "Quero delivery"
                     → Já está na página da loja
                     → Se cadastra em 2 toques
```

### 10.4 Métricas de Aquisição

| Métrica | Definição | Benchmark inicial |
|---------|-----------|:-----------------:|
| **QR code → cadastro** | % que escaneou e criou conta | > 10% |
| **Cadastro → primeira compra** | % que fez o primeiro pedido | > 40% em 7 dias |
| **Primeira compra → segunda** | % que repetiu | > 30% em 30 dias |
| **CAC** | Custo por novo cliente ativo | < R$ 15 (via QR code) |
| **Cliques em link de indicação** | % de clientes que compartilham | > 5% dos ativos |
| **Taxa de cadastro assistido** | % de pedidos de clientes novos vindos de ação do lojista | > 60% |

### 10.5 Funil Completo de Aquisição

```
            ┌─────────────────────────┐
            │   CLIENTE DESCOBRE      │
            │   A LOJA (física,       │
            │   Instagram, amigo)      │
            └───────────┬─────────────┘
                        ▼
            ┌─────────────────────────┐
            │   ESCANEIA QR / CLICA   │
            │   NO LINK               │
            │   → Abre site da loja   │
            └───────────┬─────────────┘
                        ▼
            ┌─────────────────────────┐
            │   CADASTRO RÁPIDO       │
            │   (celular + OTP)       │
            │   🎁 Já ganha desconto  │
            │      de primeira compra │
            └───────────┬─────────────┘
                        ▼
            ┌─────────────────────────┐
            │   PRIMEIRO PEDIDO       │
            │   → Endereço            │
            │   → Pagamento           │
            │   → Finalizar           │
            └───────────┬─────────────┘
                        ▼
            ┌─────────────────────────┐
            │   EXPERIÊNCIA POSITIVA  │
            │   → Acompanhamento      │
            │   → Entrega no prazo    │
            │   → Produto correto     │
            └───────────┬─────────────┘
                        ▼
            ┌─────────────────────────┐
            │   RETENÇÃO              │
            │   → Favoritou a loja    │
            │   → Salvou prato fav.   │
            │   → "Pedir de novo"     │
            │   → Indicou amigo       │
            └─────────────────────────┘
```

### 10.6 O Papel do RapiDrop na Aquisição

| O que o RapiDrop faz | O que o lojista faz |
|----------------------|---------------------|
| Gera QR code único por loja | Imprime e cola no balcão/mesa/sacola |
| Cria link de indicação | Compartilha no WhatsApp com clientes |
| Fornece posts prontos para redes sociais | Publica no Instagram/Facebook |
| Envia notificação de "carrinho abandonado" | Cria campanhas de desconto |
| Gerencia cupons e promoções | Define regras e valores |
| App de descoberta (opcional) | Atrai clientes novos na região |

---

## 11. Fluxos Completos

### 11.1 Primeiro Pedido — Cliente Novo

```
1. Cliente vê QR code no balcão da Pizzaria do Norte
2. Escaneia → abre pizzariadonorte.com.br
3. Vê cardápio, escolhe Pizza Calabresa G + Coca-Cola
4. Clica "Finalizar Pedido"
5. Sistema: "Você é novo por aqui! Informe seu celular"
6. Cliente digita celular → recebe SMS com código
7. Confirma → já está logado
8. Informa endereço de entrega (CEP + rua + número)
9. Escolhe pagamento: cartão de crédito
10. Sistema: "🎉 Primeira compra: R$ 10 de desconto!"
11. Confirma → pedido enviado para a pizzaria
12. Cliente vê: "Pedido confirmado! 🍕"
```

**Tempo total: ~90 segundos** (do clique até finalizar)

### 11.2 Segunda Compra — Mesma Loja

```
1. Cliente abre o app RapiDrop
2. Página inicial: "Pedir de novo 🍕" com último pedido
3. Clica → carrinho já está montado (Pizza G + Coca)
4. Confirma endereço e pagamento (já salvos)
5. Clica "Finalizar"
```

**Tempo total: ~10 segundos**

### 11.3 Compra em Nova Loja

```
1. Cliente abre app RapiDrop
2. Vê "Lojas perto de você" — encontra "Drogaria São Vicente"
3. Entra na página da farmácia
4. Busca "Dorflex" → adiciona ao carrinho
5. Finaliza
```

**Tempo total: ~30 segundos** (cadastro e pagamento já existem)

### 11.4 Loja Faz Promoção para Favoritos

```
1. Pizzaria do Norte cria cupom: "Segunda da Pizza" — 20% off
2. Ativa notificação para favoritos
3. Clientes que favoritaram a loja recebem push:
   "🍕 Pizzaria do Norte: 20% off hoje! Só clicar"
4. Cliente clica → abre a loja com desconto aplicado
5. Pede e finaliza
```

---

## 12. Modelagem de Dados

### 12.1 Tabelas

```sql
-- Conta do cliente final (funciona em todas as lojas)
customer
├── id: uuid PK
├── name: varchar(120) NOT NULL
├── phone: varchar(20) UNIQUE NOT NULL        -- login via OTP
├── phone_verified_at: timestamptz
├── email: varchar(200) UNIQUE                -- opcional
├── email_verified_at: timestamptz
├── password_hash: varchar(200)               -- para login email+senha
├── avatar_url: text                          -- opcional
├── cpf: varchar(14)                          -- opcional, para nota fiscal
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Provedores de identidade social (Google, Apple)
customer_social_login
├── id: uuid PK
├── customer_id: uuid FK
├── provider: enum('google', 'apple') NOT NULL
├── provider_user_id: varchar(200) NOT NULL
├── created_at: timestamptz
└── UNIQUE (provider, provider_user_id)

-- Endereços do cliente
customer_address
├── id: uuid PK
├── customer_id: uuid FK
├── label: varchar(50)                        -- "Casa", "Trabalho"
├── zipcode: varchar(9) NOT NULL
├── street: varchar(200) NOT NULL
├── number: varchar(20) NOT NULL
├── complement: varchar(100)
├── neighborhood: varchar(100) NOT NULL
├── city: varchar(100) NOT NULL
├── state: varchar(2) NOT NULL
├── latitude: decimal(10,7)                   -- geocodificado
├── longitude: decimal(10,7)                  -- geocodificado
├── reference_point: varchar(200)             -- "Próximo ao mercado"
├── is_default: boolean DEFAULT false
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Formas de pagamento salvas
customer_payment_method
├── id: uuid PK
├── customer_id: uuid FK
├── type: enum('credit_card', 'pix', 'cash', 'card_on_delivery') NOT NULL
├── gateway: varchar(50)                      -- 'stripe', 'asaas'
├── gateway_payment_method_id: varchar(200)   -- token do gateway
├── card_last_four: varchar(4)                -- últimos dígitos (credit_card)
├── card_brand: varchar(50)                   -- 'visa', 'mastercard'
├── card_holder_name: varchar(200)
├── card_expiry_month: int
├── card_expiry_year: int
├── is_default: boolean DEFAULT false
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Favoritar loja
customer_favorite_store
├── id: uuid PK
├── customer_id: uuid FK
├── store_id: uuid FK
├── notify_promotions: boolean DEFAULT true   -- receber notificações?
├── notify_open: boolean DEFAULT false        -- avisar quando abrir?
├── created_at: timestamptz
└── UNIQUE (customer_id, store_id)

-- Favoritar produto
customer_favorite_product
├── id: uuid PK
├── customer_id: uuid FK
├── product_id: uuid FK                       -- produto específico
├── store_id: uuid FK                         -- loja do produto
├── created_at: timestamptz
└── UNIQUE (customer_id, product_id)

-- Cupons de desconto
coupon
├── id: uuid PK
├── store_id: uuid FK                         -- loja que criou o cupom
├── code: varchar(50) NOT NULL UNIQUE         -- ex: "PIZZA10"
├── type: enum('percentage', 'fixed_amount', 'free_delivery')
├── value_cents: int                          -- 1000 = R$ 10,00
├── min_order_cents: int                      -- pedido mínimo para usar
├── usage_limit: int                          -- limite total de usos
├── usage_per_customer: int DEFAULT 1         -- quantas vezes por cliente
├── max_discount_cents: int                   -- teto para % off
├── applies_to: enum('all', 'category', 'product')
├── applies_to_id: uuid                       -- categoria ou produto
├── valid_from: timestamptz
├── valid_until: timestamptz
├── weekday_only: int[]                       -- 0=domingo, 1=segunda...
├── time_from: time                           -- horário início (ex: 18:00)
├── time_until: time                          -- horário fim (ex: 22:00)
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Cupom nominal (para cliente específico)
coupon_assignment
├── id: uuid PK
├── coupon_id: uuid FK
├── customer_id: uuid FK
├── reason: varchar(50)                       -- 'welcome', 'referral', 'birthday'
├── used_at: timestamptz
├── expires_at: timestamptz
├── created_at: timestamptz
└── UNIQUE (coupon_id, customer_id)

-- Programa de fidelidade (configuração por loja)
loyalty_program
├── id: uuid PK
├── store_id: uuid FK
├── type: enum('stamp', 'points') NOT NULL   -- carimbo ou pontos
├── is_active: boolean DEFAULT false
├── stamp_goal: int                           -- "A cada 10, ganhe 1"
├── stamp_reward_type: enum('product', 'discount')
├── stamp_reward_value_cents: int             -- valor do prêmio
├── points_per_reais_cents: int               -- R$ 1 = X pontos
├── points_redeem_cents: int                  -- X pontos = R$ 1
├── created_at: timestamptz
└── updated_at: timestamptz

-- Selos de fidelidade do cliente
loyalty_stamp
├── id: uuid PK
├── customer_id: uuid FK
├── store_id: uuid FK
├── loyalty_program_id: uuid FK
├── stamps_count: int DEFAULT 0              -- selos acumulados
├── points_balance: int DEFAULT 0            -- saldo de pontos
├── created_at: timestamptz
└── updated_at: timestamptz

-- Histórico de uso de selos/pontos
loyalty_transaction
├── id: uuid PK
├── loyalty_stamp_id: uuid FK
├── type: enum('earn', 'redeem', 'expire')
├── amount: int                               -- +1 selo, -50 pontos, etc
├── description: varchar(200)                 -- "Compra #1234", "Resgatou pizza"
├── order_id: uuid FK
├── created_at: timestamptz

-- Notificações push do cliente
customer_push_token
├── id: uuid PK
├── customer_id: uuid FK
├── platform: enum('ios', 'android', 'web') NOT NULL
├── token: varchar(500) NOT NULL
├── is_active: boolean DEFAULT true
├── created_at: timestamptz
└── updated_at: timestamptz

-- Preferências de notificação por loja favorita
customer_notification_preference
├── id: uuid PK
├── customer_id: uuid FK
├── store_id: uuid FK
├── promotions: boolean DEFAULT true          -- receber promoções?
├── order_updates: boolean DEFAULT true       -- status do pedido?
├── reorder_reminders: boolean DEFAULT false  -- "já pediu esse mês?"
├── created_at: timestamptz
└── UNIQUE (customer_id, store_id)

-- Sessão de login (para refresh token)
customer_session
├── id: uuid PK
├── customer_id: uuid FK
├── refresh_token_hash: varchar(200) NOT NULL
├── device_info: jsonb                        -- { platform, os, browser }
├── ip_address: varchar(45)
├── last_active_at: timestamptz
├── expires_at: timestamptz
├── created_at: timestamptz

-- Evento de indicação
referral
├── id: uuid PK
├── store_id: uuid FK
├── referrer_customer_id: uuid FK             -- quem indicou
├── referred_customer_id: uuid FK             -- quem foi indicado (NULL até cadastrar)
├── referral_code: varchar(20) UNIQUE         -- código único do link
├── status: enum('sent', 'clicked', 'registered', 'first_order', 'rewarded')
├── referrer_reward_cents: int                -- R$ 10 para quem indicou
├── referred_reward_cents: int                -- R$ 10 para o indicado
├── referrer_rewarded_at: timestamptz
├── referred_rewarded_at: timestamptz
├── created_at: timestamptz
└── updated_at: timestamptz
```

### 12.2 Índices

```sql
-- Buscar cliente por telefone (login)
CREATE UNIQUE INDEX idx_customer_phone ON customer (phone) WHERE is_active = true;

-- Endereços do cliente
CREATE INDEX idx_customer_address_customer ON customer_address (customer_id, is_default DESC);

-- Favoritos do cliente
CREATE INDEX idx_fav_store_customer ON customer_favorite_store (customer_id, created_at DESC);
CREATE INDEX idx_fav_product_customer ON customer_favorite_product (customer_id);
CREATE INDEX idx_fav_product_store ON customer_favorite_product (store_id, product_id);

-- Cupons ativos por loja
CREATE INDEX idx_coupon_active ON coupon (store_id, is_active, valid_from, valid_until);

-- Buscar cupom por código
CREATE UNIQUE INDEX idx_coupon_code ON coupon (code);

-- Indicações por cliente
CREATE INDEX idx_referral_referrer ON referral (referrer_customer_id);
CREATE INDEX idx_referral_code ON referral (referral_code);
```

---

## 13. Comparativo com Concorrentes

| Funcionalidade | iFood | RapiDrop (cliente) | Vantagem RapiDrop |
|---------------|:-----:|:-----------------:|:-----------------:|
| **Quem é dono da relação com o cliente** | iFood | **Lojista** | Lojista tem dados e pode se relacionar diretamente |
| **Conta única entre lojas** | ✅ Sim | ✅ Sim | Empata |
| **Site white label da loja** | ❌ Não | ✅ Sim | Lojista tem seu próprio canal |
| **Favoritar loja** | ✅ Sim | ✅ Sim | Empata |
| **Favoritar prato específico** | ❌ Não | ✅ **Sim** | Diferencial |
| "Pedir de novo" em 1 clique | ✅ Sim | ✅ Sim | Empata |
| **QR code físico para cadastro** | ❌ Limitado | ✅ **Nativo** | Lojista captura cliente dentro da loja |
| **Link de indicação** | ✅ Sim | ✅ Sim | Empata |
| **Programa de fidelidade** | ❌ Não (parceiros) | ✅ **Nativo** | Diferencial |
| **Notificações por loja favorita** | ❌ Genérica | ✅ **Por loja** | Cliente controla o que recebe |
| **Descoberta de lojas** | ✅ Principal | ✅ Opcional | RapiDrop não depende disso |
| **Taxa sobre o pedido** | 12-27% | **1,5-2%** | Muito mais barato |

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Nota:** Este documento descreve a experiência do cliente final (consumidor).
> A experiência do lojista (painel de administração) está em documentos separados.
