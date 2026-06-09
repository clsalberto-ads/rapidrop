# RapiDrop — Onboarding do Lojista

> A jornada completa do lojista, do primeiro clique ao primeiro pedido.
> O onboarding é o momento mais crítico do ciclo de vida — se for
> frustrante, o lojista nunca experimenta o valor do produto.

---

## Índice

1. [Filosofia de Onboarding](#1-filosofia-de-onboarding)
2. [Jornada do Lojista (Mapa)](#2-jornada-do-lojista-mapa)
3. [Fluxo de Cadastro](#3-fluxo-de-cadastro)
4. [Setup do Estabelecimento](#4-setup-do-estabelecimento)
5. [Setup do Catálogo](#5-setup-do-catálogo)
6. [Setup de Entregadores](#6-setup-de-entregadores)
7. [Conexão WhatsApp](#7-conexão-whatsapp)
8. [Setup Financeiro](#8-setup-financeiro)
9. [Primeiro Pedido (Sandbox → Real)](#9-primeiro-pedido-sandbox--real)
10. [Onboarding Adaptativo por Segmento](#10-onboarding-adaptativo-por-segmento)
11. [Gamificação e Progresso](#11-gamificação-e-progresso)
12. [Trial → Conversão](#12-trial--conversão)
13. [Estados do Onboarding](#13-estados-do-onboarding)
14. [Modelo de Dados](#14-modelo-de-dados)
15. [Métricas de Sucesso](#15-métricas-de-sucesso)

---

## 1. Filosofia de Onboarding

### 1.1 Princípios

| Princípio | Implicação |
|-----------|------------|
| **Valor em minutos, não em horas** | O lojista deve conseguir receber o primeiro pedido simulado em **menos de 10 minutos** do início do cadastro. |
| **Onboarding adaptativo** | Cada segmento (comida, farmácia, mercado) tem seu próprio fluxo. Um pizzaiolo não vê campos de "princípio ativo". |
| **Self-service primeiro, suporte depois** | O cadastro é 100% auto-guiado. Suporte humano só quando o lojista pedir ou travar por mais de 5 min em uma etapa. |
| **Progresso visível** | O lojista vê exatamente quanto falta para começar. "3 de 5 etapas concluídas" — nunca "continue preenchendo". |
| **Trial ativo, não passivo** | O período trial não é "30 dias de graça" — é "complete essas etapas para desbloquear o valor". Trial sem ação vira churn. |
| **Primeiro pedido é o marco zero** | O onboarding só termina quando o primeiro pedido real é processado. Até lá, é tudo preparação. |

### 1.2 Definição de Sucesso

```
Onboarding bem-sucedido = lojista que, em 7 dias:
  ✅ Completou o cadastro
  ✅ Adicionou 10+ produtos ao catálogo
  ✅ Conectou o WhatsApp (ou configurou notificações)
  ✅ Cadastrou ao menos 1 entregador
  ✅ Recebeu e processou o primeiro pedido REAL

Meta de taxa de conclusão:
  Cadastro iniciado → completado:      > 80%
  Cadastro completo → 10+ produtos:    > 60%
  → Primeiro pedido em 7 dias:         > 40%
  → Trial → pagante (30 dias):         > 25%
```

### 1.3 Abordagem Omnichannel

O lojista pode começar o onboarding em qualquer canal e continuar em outro:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  WHATSAPP    │     │   WEB        │     │  PRESENCIAL  │
│              │     │              │     │              │
│ "Quero       │     │ rapidrop.    │     │ Consultor    │
│  começar"    │──►  │ com.br/      │──►  │ visita a     │──► Dashboard
│ → link de    │     │ cadastro     │     │ loja         │
│   cadastro   │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 2. Jornada do Lojista (Mapa)

```
                                    ┌─────────────────────────────────────────────┐
                                    │             FUNIL DE ONBOARDING              │
                                    └─────────────────────────────────────────────┘

  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │              │   │              │   │              │   │              │   │              │
  │ 1. DESCOBERTA│   │ 2. CADASTRO  │   │ 3. SETUP     │   │ 4. PRIMEIRO  │   │ 5. CONVERSÃO │
  │              │   │              │   │              │   │   PEDIDO     │   │              │
  │  ┌─────────┐ │   │  ┌─────────┐ │   │  ┌─────────┐ │   │  ┌─────────┐ │   │  ┌─────────┐ │
  │  │ Landing │ │   │  │ Email   │ │   │  │ Catálogo│ │   │  │ Pedido  │ │   │  │ Plano   │ │
  │  │ page    │ │   │  │ + senha │ │   │  │ (10+    │ │   │  │ sandbox │ │   │  │ pago    │ │
  │  └─────────┘ │   │  └─────────┘ │   │  │ itens)  │ │   │  └─────────┘ │   │  │ ativo   │ │
  │              │   │              │   │  └─────────┘ │   │              │   │  └─────────┘ │
  │  ┌─────────┐ │   │  ┌─────────┐ │   │  ┌─────────┐ │   │  ┌─────────┐ │   │              │
  │  │ Indicação│ │   │  │ Dados   │ │   │  │ Entrega │ │   │  │ Pedido  │ │   │              │
  │  │ (boca a │ │   │  │ da loja │ │   │  │ dorfres │ │   │  │ real    │ │   │              │
  │  │  boca)  │ │   │  └─────────┘ │   │  └─────────┘ │   │  └─────────┘ │   │              │
  │  └─────────┘ │   │              │   │              │   │              │   │              │
  │              │   │  ┌─────────┐ │   │  ┌─────────┐ │   │              │   │              │
  │  ┌─────────┐ │   │  │ Segmento│ │   │  │ WhatsApp│ │   │              │   │              │
  │  │ Rede    │ │   │  │ ───►    │ │   │  │ conexão │ │   │              │   │              │
  │  │ social  │ │   │  │ fluxo   │ │   │  └─────────┘ │   │              │   │              │
  │  └─────────┘ │   │  │ adaptado│ │   │              │   │              │   │              │
  │              │   │  └─────────┘ │   │  ┌─────────┐ │   │              │   │              │
  │              │   │              │   │  │ Finan-  │ │   │              │   │              │
  │              │   │              │   │  │ ceiro   │ │   │              │   │              │
  │              │   │              │   │  └─────────┘ │   │              │   │              │
  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
         │                  │                  │                  │                  │
         ▼                  ▼                  ▼                  ▼                  ▼
   Meta: entrar        Meta: criar        Meta: pronto       Meta: validar       Meta: ativo
   no funil            conta +            para operar        o valor real        e pagante
                       escolher                              do produto
                       segmento
```

---

## 3. Fluxo de Cadastro

### 3.1 Tela a Tela

```
TELA 1: Landing → "Começar teste grátis"
  ┌──────────────────────────────────────────────┐
  │  🚀 RapiDrop — Gestão de pedidos e entregas  │
  │                                              │
  │  [ 📧 Email                   ]              │
  │  [ 🔒 Senha                   ]              │
  │  [ 🔒 Confirmar senha         ]              │
  │                                              │
  │  [ 📱 WhatsApp (opcional)     ]              │
  │                                              │
  │  [ 🔵 Começar teste grátis — 2 meses ]       │
  │                                              │
  │  Já tem conta? [Entrar]                      │
  └──────────────────────────────────────────────┘

TELA 2: Escolha do segmento
  ┌──────────────────────────────────────────────┐
  │  Qual é o seu tipo de negócio?               │
  │                                              │
  │  ┌────────────────────────────────────────┐  │
  │  │ 🍕  Alimentação                        │  │
  │  │     Restaurante, pizzaria, hamburgueria│  │
  │  └────────────────────────────────────────┘  │
  │                                              │
  │  ┌────────────────────────────────────────┐  │
  │  │ 💊  Farmácia / Drogaria                │  │
  │  │     Farmácia independente, manipulação │  │
  │  └────────────────────────────────────────┘  │
  │                                              │
  │  ┌────────────────────────────────────────┐  │
  │  │ 🛒  Mercado / Supermercado             │  │
  │  │     Mercado de bairro, açougue, sacolão│  │
  │  └────────────────────────────────────────┘  │
  │                                              │
  │  [ 🔵 Continuar ]                            │
  └──────────────────────────────────────────────┘

TELA 3: Dados do estabelecimento
  ┌──────────────────────────────────────────────┐
  │  Dados do seu negócio                        │
  │                                              │
  │  [ Nome fantasia                    ]        │
  │  [ Razão social (se aplicável)      ]        │
  │  [ CPF/CNPJ                         ]        │
  │  [ Telefone                         ]        │
  │                                              │
  │  Endereço:                                   │
  │  [ CEP → auto-completa             ]        │
  │  [ Logradouro                      ]        │
  │  [ Número          ] [ Complemento  ]        │
  │  [ Bairro                          ]        │
  │  [ Cidade           ] [ UF          ]        │
  │                                              │
  │  Horário de funcionamento:                   │
  │  [ ⏰ Seg-Sex: 08:00 às 22:00       ]        │
  │  [ ⏰ Sáb:     09:00 às 23:00       ]        │
  │  [ ⏰ Dom:     10:00 às 22:00       ]        │
  │                                              │
  │  [ 🔵 Salvar e continuar ]                   │
  └──────────────────────────────────────────────┘

TELA 4: Dashboard — Checklist de onboarding
  ┌──────────────────────────────────────────────┐
  │  🎉 Seu cadastro foi criado!                 │
  │                                              │
  │  Para começar a receber pedidos, complete:   │
  │                                              │
  │  ☐ 1. Adicionar produtos ao catálogo  (0/10) │
  │  ☐ 2. Cadastrar entregadores          (0/1)  │
  │  ☐ 3. Conectar WhatsApp                    │
  │  ☐ 4. Configurar formas de pagamento        │
  │  ☐ 5. Definir área de entrega               │
  │  ☐ 6. Fazer um pedido de teste 🎯          │
  │                                              │
  │  🔵 Começar pelo catálogo                    │
  │  [⏰ Lembrete: você tem 2 meses grátis!]     │
  └──────────────────────────────────────────────┘
```

### 3.2 Validações e Guards

| Campo | Validação | UX |
|-------|-----------|----|
| Email | Formato válido + único (sem cadastro duplicado) | "Este email já está cadastrado. [Fazer login]?" |
| Senha | Mínimo 8 caracteres, 1 número, 1 letra | Mostrador de força da senha |
| CPF/CNPJ | Válido (algoritmo dígitos verificadores) | Formatação automática: `XX.XXX.XXX/XXXX-XX` |
| Telefone | Formato válido brasileiro | Máscara: `(XX) XXXXX-XXXX` |
| CEP | CEP real (via API ViaCEP) | Auto-completa endereço completo |

---

## 4. Setup do Estabelecimento

### 4.1 Configurações Iniciais

Após o cadastro básico, o lojista precisa configurar:

```
1. LOGO E IDENTIDADE VISUAL
   ─ Upload do logo (PNG, até 2MB)
   ─ Cor principal (para o white-label)
   ─ Slug do link: rapidrop.com.br/p/{slug}
   ─ (Opcional) Domínio próprio: www.minhaloja.com.br

2. ÁREA DE ENTREGA
   ─ Raio de entrega (km) para cada tipo de veículo
   ─ Bairros atendidos (seleção manual ou por raio)
   �─ Mapa visual com raio desenhado (MapLibre)

3. TAXA DE ENTREGA
   ─ Fixa: R$ X por pedido
   ─ Por km: R$ X por km (até Y km)
   ─ Grátis acima de R$ Z
   �─ Combinada: fixa + por km

4. HORÁRIOS E DIAS
   ─ Horário de funcionamento por dia da semana
   ─ Feriados (fechado ou horário especial)
   ─ Tempo de preparo médio (minutos)

5. MÍNIMO POR PEDIDO
   ─ Valor mínimo para delivery (ex: R$ 20,00)
```

### 4.2 Configurações por Segmento

```yaml
Alimentação:
  ─ Tipos de variação: tamanho (P/M/G), sabor, borda
  ─ Adicionais: até 10 por produto
  ─ Categorias típicas sugeridas: "Pizzas", "Bebidas", "Sobremesas"
  ─ Tempo de preparo por produto (min)

Farmácia:
  ─ Campos de medicamento: princípio ativo, tarja, laboratório, ANVISA
  ─ Categorias sugeridas: "Analgésicos", "Antialérgicos", "Cosméticos"
  ─ Flag: exige receita? Requer refrigeração?
  ─ Busca por EAN (código de barras)

Mercado:
  ─ Departamentos sugeridos: "Hortifrúti", "Açougue", "Limpeza", "Bebidas"
  ─ Unidades: kg, g, un, l, ml, dúzia, pacote
  ─ Flag: item fracionável? (ex: "300g de queijo")
  ─ Flag: essencial? (se faltar, pedido todo cancela?)
```

---

## 5. Setup do Catálogo

### 5.1 Fluxo de Adição de Produtos

O lojista precisa adicionar produtos ao catálogo. Esta é a etapa que mais
abandona (muitos produtos para cadastrar). Por isso, o fluxo prioriza:

```
1. COMEÇAR COM POUCOS PRODUTOS (FASE INICIAL)
   ─ Pedir apenas 5-10 produtos para começar
   ─ "Depois você adiciona o restante"
   ─ Sugerir os mais vendidos primeiro

2. IMPORTAÇÃO EM MASSA (FASE SEGUINTE)
   ─ Upload de CSV/planilha
   ─ (Farmácia) Importar por código de barras (EAN)
   ─ Integração com sistema de PDV existente (futuro)

3. CATEGORIAS PRÉ-CRIADAS
   ─ Baseado no segmento, criar categorias padrão
   ─ Lojista só renomeia/adiciona, não começa do zero

4. FOTOS DOS PRODUTOS
   ─ Upload de foto (ou placeholder)
   ─ (Farmácia) Foto da embalagem + bula
   ─ Compressão automática para WebP
```

### 5.2 Experiência de Adição Rápida

```
┌────────────────────────────────────────────────────┐
│  ADICIONAR PRODUTO — Pizzaria do Norte              │
├────────────────────────────────────────────────────┤
│                                                      │
│  [ Nome: ________________________________ ]          │
│  [ Preço: R$ _________                     ]          │
│  [ Categoria: [Pizzas ▼]                   ]          │
│  [ Foto: 📸 (opcional)                    ]          │
│                                                      │
│  Tem variações? (tamanho, sabor)                    │
│  [ ❌ Não ]  [ ✅ Sim — adicionar tamanhos ]          │
│                                                      │
│  ──────────────────────────────────────────          │
│                                                      │
│  [ 🔵 Adicionar e continuar ]                        │
│  [ 🔵 Adicionar e criar outro ]                      │
│                                                      │
│  Produtos adicionados: 3 de 10 (mínimo)              │
│  ████████░░░░░░░░░░░░░░░░░                           │
└────────────────────────────────────────────────────┘
```

### 5.3 Sugestões Inteligentes

Para acelerar o cadastro, o sistema sugere produtos baseado no segmento:

```python
SEGMENT_SUGGESTIONS = {
    "food": [
        "Categorias: Pizzas, Bebidas, Sobremesas, Entradas",
        "Produtos: Pizza Muçarela, Pizza Calabresa, Coca-Cola 2L",
    ],
    "pharmacy": [
        "Categorias: Analgésicos, Antialérgicos, Vitaminas, Higiene",
        "Busca por EAN: digite o código de barras e os dados preenchem automaticamente",
    ],
    "grocery": [
        "Departamentos: Hortifrúti, Açougue, Bebidas, Limpeza, Padaria",
        "Produtos: Arroz 5kg, Feijão 1kg, Leite 1L, Café 500g",
    ],
}
```

---

## 6. Setup de Entregadores

### 6.1 Fluxo de Cadastro do Entregador

```
1. LOJISTA cadastra entregador no dashboard:
   ─ Nome, telefone, veículo (moto/bike/carro), documento

2. SISTEMA envia convite via WhatsApp:
   ─ "Olá [nome]! Você foi convidado a ser entregador da
       [Pizzaria do Norte]. Baixe o app: [link]"

3. ENTREGADOR baixa o app:
   ─ Faz login com o telefone
   ─ Confirma dados
   ─ Marca disponibilidade

4. LOJISTA vê entregador como "disponível" no dashboard:
   ─ Pronto para receber atribuições!

⏱️ Tempo total: ~2 minutos para o lojista + ~3 minutos para o entregador
```

### 6.2 Convite em Massa

Para lojistas que já têm entregadores:

```
1. Lojista insere números de WhatsApp
2. Sistema envia convite em lote
3. Cada entregador recebe link para baixar o app
4. Lojista vê status: "3 convites enviados, 2 aceitos, 1 pendente"
```

### 6.3 Atribuição de Veículo e Área

Por entregador, o lojista configura:

```
Entregador: João (Moto)
├── Raio máximo: 5 km (moto vai mais longe)
├── Cargas especiais: ✅ frágil ✅ refrigeração
└── Status: 🟢 Online

Entregador: Maria (Bike)
├── Raio máximo: 3 km
├── Cargas especiais: ❌ frágil ❌ refrigeração ❌ muito peso
└── Status: 🔴 Offline
```

---

## 7. Conexão WhatsApp

### 7.1 Conexão Simplificada (Fase 1)

Na Fase 1, o lojista não precisa conectar o número dele. O RapiDrop
usa o próprio número para enviar notificações. O lojista só precisa:

```
1. Informar o telefone do estabelecimento (para o sistema identificar)
2. Escolher: "Quer que notifiquemos seus clientes por WhatsApp?"
   ─ Sim: clientes recebem notificações do número do RapiDrop
   ─ Não: notificações apenas por SMS (custo adicional)
```

### 7.2 Conexão Avançada (Fase 2)

Quando o lojista quiser conectar o próprio número (ver documento
[`docs/integracao-whatsapp.md`](integracao-whatsapp.md#7-conexão-do-lojista-onboarding-whatsapp)):

```
1. Acessa "Configurações → WhatsApp" no dashboard
2. Clica em "Conectar meu WhatsApp Business"
3. Escaneia QR Code (ou faz embedded signup)
4. Pronto! Mensagens dos clientes aparecem no dashboard
```

---

## 8. Setup Financeiro

### 8.1 Configuração de Formas de Pagamento

O lojista escolhe quais formas de pagamento aceitar:

```
┌────────────────────────────────────────────────────┐
│  FORMAS DE PAGAMENTO — Pizzaria do Norte            │
├────────────────────────────────────────────────────┤
│                                                      │
│  Quais formas de pagamento seus clientes podem      │
│  usar nos pedidos?                                   │
│                                                      │
│  ☑ PIX                          ↗ 80% dos pedidos  │
│  ☑ Cartão crédito (online)      ↗ 15% dos pedidos  │
│  ☐ Cartão débito (online)                          │
│  ☑ Dinheiro                     ↘  5% dos pedidos  │
│  ☐ Cartão na entrega                               │
│  ☑ Boleto (apenas mercado)                         │
│                                                      │
│  ─────────────────────────────────────               │
│                                                      │
│  💳 Cartão de crédito — Parcelamento:               │
│  [☑ 1x] [☑ 2x] [☑ 3x] [☐ 4x] [☐ 5x] [☐ 6x]       │
│  [☐ 7x] [☐ 8x] [☐ 9x] [☐ 10x] [☐ 11x] [☐ 12x]    │
│                                                      │
│  Quem absorve o custo do parcelamento?              │
│  ○ Eu (lojista)  ● Cliente  ○ Dividimos            │
│                                                      │
│  [ 🔵 Salvar configurações ]                        │
└────────────────────────────────────────────────────┘
```

### 8.2 Conexão Asaas (Fase 2)

Para receber por split automático:

```
1. Lojista clica "Conectar conta para recebimento"
2. É redirecionado ao Asaas (embedded)
3. Preenche dados bancários em ~2 minutos
4. Conta criada! Passa a receber splits automaticamente

Na Fase 1 (fatura), não precisa de conta Asaas.
O lojista paga a fatura no fim do mês via PIX/boleto.
```

---

## 9. Primeiro Pedido (Sandbox → Real)

### 9.1 Pedido de Teste (Sandbox)

Antes de abrir para clientes reais, o lojista faz um pedido de teste:

```
1. Botão "🔬 Fazer pedido de teste" no dashboard
2. Sistema cria um pedido simulado do próprio lojista
3. Pedido aparece na central de pedidos
4. Lojista pratica: confirmar, preparar, marcar como pronto
5. Sistema pergunta: "Entendeu como funciona? ✅ Sim"
6. Pronto! Link público liberado.
```

### 9.2 Checklist de Go-Live

O sistema só libera o link público quando tudo está configurado:

```
☑ Mínimo 5 produtos no catálogo
☑ Pelo menos 1 entregador cadastrado
☑ Formas de pagamento configuradas
☑ Taxa de entrega definida
☑ Área de cobertura configurada
☑ Pedido de teste concluído
```

### 9.3 Primeiro Pedido Real

Quando o primeiro pedido real chega:

```
1. NOTIFICAÇÃO ESPECIAL
   ─ Som diferente (mais festivo)
   ─ "🎉 PRIMEIRO PEDIDO REAL! 🎉"
   ─ Confete na tela (opcional)

2. SISTEMA MONITORA DE PERTO
   �─ Tempo de confirmação (quanto tempo o lojista demorou?)
   ─ Cada passo é registrado para análise de onboarding

3. APÓS A ENTREGA
   ─ "Parabéns! Seu primeiro pedido foi entregue! 🎉"
   ─ "Nota: ⭐⭐⭐⭐⭐ (automática — primeiro pedido é sempre 5)"
   ─ Botão: "Compartilhar link nas redes sociais"
```

---

## 10. Onboarding Adaptativo por Segmento

### 10.1 Matriz de Diferenças

| Etapa | Alimentação | Farmácia | Mercado |
|-------|:-----------:|:--------:|:-------:|
| **Categorias sugeridas** | Pizza, Bebidas, Sobremesa | Analgésicos, Vitaminas, Higiene | Hortifrúti, Açougue, Limpeza |
| **Importação de produtos** | Manual (poucos itens) | Por EAN + base ANVISA | Por EAN + CSV |
| **Variações** | Tamanho, sabor, borda | Apresentação (cx/cp/gts) | Unidade, peso fracionado |
| **Campos extras** | Tempo de preparo | Princípio ativo, tarja, laboratório | Departamento, código de barras, substituto |
| **Verificação especial** | — | Alvará ANVISA + CRF | — |
| **Primeiro pedido** | Pizza ou prato principal | Dipirona ou paracetamol | Arroz + feijão + leite |
| **Complexidade onboarding** | ⭐ Baixa | ⭐⭐⭐ Alta | ⭐⭐ Média |

### 10.2 Farmácia — Verificações Especiais

Farmácias exigem verificações adicionais antes de liberar o cadastro:

```
1. Alvará sanitário (upload do documento)
2. Número do CRF (Conselho Regional de Farmácia)
3. Responsável técnico (nome + CRF)
4. Termo de responsabilidade aceito
   ─ "O RapiDrop auxilia na gestão, mas a responsabilidade
      pela dispensação é do farmacêutico responsável"

⏱️ Farmácia demora mais para completar onboarding.
   Meta: 48h para verificação manual dos documentos.
```

### 10.3 Conteúdo Adaptativo

Cada etapa do onboarding mostra exemplos relevantes ao segmento:

```
Tela "Adicionar Produtos":
  ─ Alimentação: "Que tal começar com sua pizza mais pedida?"
  ─ Farmácia: "Busque por código de barras para preencher automaticamente"
  ─ Mercado: "Comece pelos departamentos essenciais: arroz, feijão, café"

Tela "Área de Entrega":
  ─ Alimentação: "Seus clientes moram perto? 3 km é o ideal para pizza"
  ─ Farmácia: "Farmácia atende bairros próximos. 2 km é suficiente."
  ─ Mercado: "Mercado pode ir mais longe. 5 km é comum."
```

---

## 11. Gamificação e Progresso

### 11.1 Barra de Progresso

Sempre visível no topo do dashboard durante o onboarding:

```
┌────────────────────────────────────────────────────────────┐
│  🚀 Preparando sua loja para receber pedidos               │
│                                                             │
│  ████████████████████░░░░░░░░░░░░░░  65%                    │
│                                                             │
│  ☑ Conta criada                ☑ Catálogo (15 itens)       │
│  ☑ WhatsApp conectado          ☑ Entregadores (2)          │
│  ☑ Área de entrega             ☐ Formas de pagamento       │
│  ☑ Taxa de entrega             ☐ Pedido de teste 🎯       │
│                                                             │
│  Próximo passo: [Configurar pagamentos]                     │
└────────────────────────────────────────────────────────────┘
```

### 11.2 Conquistas (Milestones)

```
🎉 "CATÁLOGO COMPLETO!" — 10+ produtos adicionados
🎉 "EQUIPE FORMADA!" — 2+ entregadores cadastrados
🎉 "CONECTADO!" — WhatsApp integrado
🎉 "PRIMEIRO PEDIDO!" — Primeiro pedido real recebido
🎉 "SEMANA DE OURO!" — 7 dias sem cancelamentos
```

### 11.3 Rankings entre Lojistas (Opcional)

```
  "Você está entre os 20% mais rápidos no cadastro!"
  "Sua loja tem mais produtos que 60% dos novos lojistas"
```

---

## 12. Trial → Conversão

### 12.1 Timeline do Trial

```
DIA 0:  Cadastro → 2 meses grátis
        🎉 Boas-vindas + checklist de onboarding

DIA 3:  Se não completou o cadastro:
        "Está com dificuldade? Precisa de ajuda? Responda essa mensagem."

DIA 7:  Se completou mas não teve pedidos:
        "Compartilhe seu link com os clientes e ganhe R$ 20 em créditos!"

DIA 15: Se está ativo (pedidos):
        "Você já processou X pedidos! Sabia que pode... [feature]"

DIA 30: Metade do trial:
        "Metade do período grátis! Continue usando 🚀"

DIA 45: 15 dias para o fim:
        "Seu período grátis termina em 15 dias.
         Assim que acabar, a taxa é de apenas 2% por pedido.
         Sem mensalidade. Sem surpresas."

DIA 55: 5 dias para o fim:
        "Últimos 5 dias! Após o trial, você paga apenas
         2% sobre cada pedido. Sem custo fixo."

DIA 60: Fim do trial:
        "Seu período grátis terminou! 🎉
         A partir de agora, a taxa de 2% por pedido está ativa.
         Você já processou R$ X em pedidos — a taxa seria de apenas R$ Y."
```

### 12.2 Conversão Automática

A transição trial → pagante é **automática e sem atrito**:

```
Fim do trial:
  ─ Lojista NÃO precisa fazer nada
  ─ A taxa de 2% começa a valer automaticamente
  ─ Dashboard continua igual (sem bloqueio)
  ─ Primeira fatura gerada no fim do mês

Se lojista não quer continuar:
  ─ Pode cancelar a qualquer momento
  ─ Dados mantidos por 90 dias (pode reativar)
  ─ Após 90 dias: dados anonimizados
```

### 12.3 Oferta de Upgrade (para planos futuros)

Quando houver planos (Básico vs Profissional), a conversão pode incluir:

```
┌────────────────────────────────────────────────────┐
│  🎉 Seu trial terminou! Escolha seu plano:          │
├────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │   BÁSICO     │  │ PROFISSIONAL │                 │
│  │              │  │              │                 │
│  │ 2% por pedido│  │ 1,5% por     │                 │
│  │ 1 entregador │  │ pedido       │                 │
│  │ Catálogo     │  │ Entregadores │                 │
│  │   simples    │  │   ilimitados │                 │
│  │              │  │ Relatórios   │                 │
│  │              │  │ IA de        │                 │
│  │              │  │   substituição│                 │
│  │              │  │              │                 │
│  │ [🔵 Continuar]│  │ [⭐ Escolher]│                 │
│  │  grátis       │  │  R$ 0/trial  │                 │
│  └──────────────┘  └──────────────┘                 │
└────────────────────────────────────────────────────┘
```

---

## 13. Estados do Onboarding

### 13.1 Máquina de Estados do Lojista

Assim como o pedido tem uma máquina de estados, o cadastro do lojista também:

```
                        ┌──────────┐
                        │ LEAD     │ (visitou a landing, não cadastrou)
                        └──────────┘
                             │
                             ▼
                        ┌──────────┐
                        │REGISTRADO│ (criou conta, escolheu segmento)
                        └──────────┘
                             │
                             ▼
                     ┌──────────────┐
                     │EM SETUP      │ (preenchendo dados da loja)
                     └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ CONFIG   │  │ CATÁLOGO│  │ ENTREGA │
       │ INICIAL  │  │ (5+     │  │ DORES   │
       │ (loja)   │  │  itens) │  │ (1+     │
       └──────────┘  └──────────┘  └──────────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
                            ▼
                      ┌──────────┐
                      │PRONTO    │ (checklist completo)
                      │P/ TESTE  │
                      └────┬─────┘
                           │
                           ▼
                      ┌──────────┐
                      │ TESTE    │ (pedido sandbox feito)
                      │ REALIZADO│
                      └────┬─────┘
                           │
                           ▼
                      ┌──────────┐
                      │ ATIVO   │ (link público, recebendo pedidos)
                      └────┬─────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ PAGANTE  │ │ TRIAL   │ │ CANCELADO│
       │ (pós-    │ │ (ainda   │ │          │
       │  trial)  │ │ grátis)  │ │          │
       └──────────┘ └──────────┘ └──────────┘
```

### 13.2 Tabela de Transições do Onboarding

| De | Para | Gatilho |
|----|------|---------|
| `lead` | `registrado` | Completou cadastro (email + senha + segmento) |
| `registrado` | `em_setup` | Iniciou preenchimento dos dados da loja |
| `em_setup` | `config_inicial` | Completou dados da loja (endereço, horário, área) |
| `em_setup` | `catalogo` | Adicionou 5+ produtos |
| `em_setup` | `entregadores` | Cadastrou 1+ entregador |
| `config_inicial` | `pronto_p_teste` | WhatsApp configurado + formas de pagamento + área |
| `catalogo` | `pronto_p_teste` | + entregadores configurados + pagamento |
| `entregadores` | `pronto_p_teste` | + catálogo + pagamento |
| `pronto_p_teste` | `teste_realizado` | Pedido sandbox concluído |
| `teste_realizado` | `ativo` | Link público liberado |
| `ativo` | `pagante` | Trial expirou (automático) |
| `ativo` / `pagante` | `cancelado` | Lojista solicita cancelamento |

### 13.3 Abandono de Onboarding

Se o lojista abandona em qualquer etapa:

| Abandonou em | Ação automática |
|-------------|-----------------|
| `lead` | Nenhum (não temos contato ainda) |
| `registrado` (não voltou em 24h) | Email + WhatsApp: "Termine seu cadastro em 2 minutos" |
| `em_setup` (parou por 48h) | "Precisa de ajuda? Responda que a gente te liga" |
| `pronto_p_teste` (não testou em 7 dias) | "Seu link ainda não está no ar. Complete o teste para liberar!" |

---

## 14. Modelo de Dados

```sql
-- Progresso do onboarding do lojista
CREATE TABLE merchant_onboarding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER NOT NULL UNIQUE REFERENCES merchants(id),

    -- Estado atual
    current_status VARCHAR(30) NOT NULL DEFAULT 'registrado',
    -- 'lead' | 'registrado' | 'em_setup' | 'config_inicial'
    -- 'catalogo' | 'entregadores' | 'pronto_p_teste'
    -- 'teste_realizado' | 'ativo' | 'pagante' | 'cancelado'

    -- Progresso (checklist)
    has_catalog_min BOOLEAN NOT NULL DEFAULT FALSE,     -- 5+ produtos
    has_rider BOOLEAN NOT NULL DEFAULT FALSE,            -- 1+ entregador
    has_whatsapp_connected BOOLEAN NOT NULL DEFAULT FALSE,
    has_payment_configured BOOLEAN NOT NULL DEFAULT FALSE,
    has_delivery_area BOOLEAN NOT NULL DEFAULT FALSE,
    has_test_order BOOLEAN NOT NULL DEFAULT FALSE,       -- sandbox feito
    is_public BOOLEAN NOT NULL DEFAULT FALSE,            -- link liberado

    -- Segmento escolhido
    segment VARCHAR(20) NOT NULL,

    -- Timestamps de cada etapa
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    setup_started_at TIMESTAMPTZ,
    first_product_added_at TIMESTAMPTZ,
    first_rider_added_at TIMESTAMPTZ,
    test_order_completed_at TIMESTAMPTZ,
    went_public_at TIMESTAMPTZ,
    trial_ends_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,

    -- Métricas
    time_to_first_product_minutes INTEGER,   -- tempo até adicionar primeiro produto
    time_to_go_live_hours INTEGER,            -- tempo total até ficar público
    products_added_in_onboarding INTEGER DEFAULT 0,
    riders_added_in_onboarding INTEGER DEFAULT 0,
    onboarding_abandoned_at TIMESTAMPTZ,
    onboarding_completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Eventos de onboarding (audit trail)
CREATE TABLE onboarding_event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    event_type VARCHAR(50) NOT NULL,
    -- 'account_created' | 'segment_chosen' | 'product_added'
    -- 'rider_added' | 'whatsapp_connected' | 'test_order_done'
    -- 'went_public' | 'first_real_order' | 'trial_ended' | 'converted'
    -- 'abandoned' | 'cancelled'
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conteúdo do onboarding (templates por segmento)
CREATE TABLE onboarding_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment VARCHAR(20) NOT NULL,           -- 'food' | 'pharmacy' | 'grocery' | 'all'
    step VARCHAR(50) NOT NULL,              -- 'welcome' | 'catalog' | 'riders' | etc
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    cta_text VARCHAR(100),
    cta_link VARCHAR(500),
    sort_order INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_onboarding_status ON merchant_onboarding(current_status)
    WHERE current_status NOT IN ('pagante', 'cancelado');
CREATE INDEX idx_onboarding_abandoned ON merchant_onboarding(onboarding_abandoned_at)
    WHERE onboarding_abandoned_at IS NOT NULL;
CREATE INDEX idx_onboarding_events ON onboarding_event(merchant_id, created_at DESC);
```

---

## 15. Métricas de Sucesso

### 15.1 Indicadores de Onboarding

| Métrica | Definição | Meta | Fórmula |
|---------|-----------|:----:|---------|
| **Taxa de conversão cadastro** | Visitantes que completam cadastro | > 30% | `registrados / visitantes` |
| **Taxa de setup completo** | Cadastrados que completam checklist | > 60% | `pronto_p_teste / registrados` |
| **Time to first product** | Tempo até adicionar primeiro produto | < 5 min | Média em minutos |
| **Time to go live** | Tempo até link público | < 48h | Média em horas |
| **Taxa de teste** | Quem faz o pedido sandbox | > 80% | `teste_realizado / pronto_p_teste` |
| **Taxa de primeiro pedido real** | Quem recebe primeiro pedido em 7 dias | > 40% | `pedido_real_7d / ativo` |
| **Trial → pagante** | Conversão ao fim do trial | > 25% | `pagantes / ativos_no_trial` |
| **Abandono por etapa** | Onde os lojistas desistem | — | `count abandonados / etapa` |

### 15.2 Dashboard de Onboarding (Admin)

```
┌────────────────────────────────────────────────────────┐
│  📊 ONBOARDING — Este mês                               │
├────────────────────────────────────────────────────────┤
│                                                          │
│  🧑‍🍳 Novos cadastros: 34                                 │
│  ✅ Setup completo:    22 (65%)                          │
│  🚀 Primeiro pedido:   14 (41%)                          │
│  💰 Conversão trial:   12 dos 18 que venceram (67%)    │
│                                                          │
│  Gargalos (onde mais abandonam):                        │
│  ████████░░ 1. Catálogo (30% abandonam aqui)           │
│  ████░░░░░░ 2. Entregadores (15% abandonam)            │
│  ██░░░░░░░░ 3. Pagamento (8% abandonam)                 │
│                                                          │
│  Tempo médio para primeiro pedido: 5h 23min ↓ 12%      │
└────────────────────────────────────────────────────────┘
```

### 15.3 Gatilhos de Alerta

| Situação | Alerta | Ação |
|----------|--------|------|
| Abandono no catálogo > 40% | 🔴 Time de produto | Revisar UX da tela de produtos |
| Tempo de setup > 72h médio | 🟡 Time de suporte | Oferecer ajuda personalizada |
| Trial não converteu > 50% | 🔴 Time de marketing | Revisar comunicação do trial |
| Nenhum pedido em 7 dias após go-live | 🟠 CS | Ativa onboarding de "reativação" |

---

> **Documento criado em:** Junho 2026
> **Versão:** 1.0
> **Baseado nos documentos:** `docs/ideacao-rapidrop.md`, `docs/integracao-whatsapp.md`,
> `docs/fluxo-financeiro.md`, `docs/experiencia-cliente.md`
