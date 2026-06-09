# RapiDrop — Documento de Ideação

> **SaaS** — Gestor de pedidos e entregas para qualquer lojista com entrega própria
> Backend: Python (FastAPI) | Frontend: Next.js | App: React Native/Expo

---

## Índice

1. [Visão Geral do Negócio](#1-visão-geral-do-negócio)
2. [Personas e Dores](#2-personas-e-dores)
3. [Módulos e Funcionalidades](#3-módulos-e-funcionalidades)
4. [Fluxos de Usuário](#4-fluxos-de-usuário)
5. [Arquitetura Técnica](#5-arquitetura-técnica)
6. [Modelagem de Dados (Alto Nível)](#6-modelagem-de-dados-alto-nível)
7. [Roadmap Sugerido](#7-roadmap-sugerido)
8. [Modelo de Negócio](#8-modelo-de-negócio)
9. [Diferenciais Competitivos](#9-diferenciais-competitivos)

---

## 1. Visão Geral do Negócio

### 1.1 O Problema

Pequenos e médios comércios no Brasil — restaurantes, farmácias, mercados — enfrentam um dilema:

- **Marketplaces (iFood, Rappi, Daki, etc.)** cobram comissões de 12% a 27% por pedido + taxas fixas. A margem do lojista desaparece.
- **Gestão própria de entregas** é caótica: pedidos chegando por WhatsApp, telefone e Instagram ao mesmo tempo, sem centralização. O dono vira atendente.
- **Para farmácias**: grandes redes (Drogasil, Pague Menos) dominam o delivery. Farmácias independentes perdem clientes por não conseguir oferecer entrega organizada.
- **Para mercados**: o cliente quer comprar poucos itens e receber rápido, mas o mercado não tem estrutura para processar pedidos pequenos de forma rentável.
- **Soluções existentes** ou são muito caras (Oracle Hospitality, sistemas de PDV corporativos), muito específicas (só cardápio digital) ou muito limitadas (planilhas, grupos de WhatsApp).

O lojista precisa de uma ferramenta **simples, acessível e que centralize os pedidos** de todos os canais, gerencie a equipe de entregadores e reduza a dependência dos grandes marketplaces — **independente do segmento**.

### 1.2 A Solução — RapiDrop

RapiDrop é um **SaaS multisegmento de gestão de pedidos e entregas** que permite a qualquer lojista:

1. **Centralizar pedidos** de múltiplos canais (WhatsApp, Instagram, telefone, site próprio, presencial) em um único dashboard
2. **Gerenciar entregadores próprios** — cadastro, escala, acompanhamento em tempo real, rateio de entregas
3. **Controlar o catálogo de produtos** — itens, categorias, preços, disponibilidade, variações
4. **Acompanhar entregas ao vivo** — status do pedido, GPS do entregador, notificações para o cliente
5. **Analisar dados** — pedidos por período, produtos mais vendidos, performance de entregadores
6. **Se adaptar ao segmento** — configurável para comida, fármacos, mantimentos, conveniência

### 1.3 Público-Alvo

#### Alimentação
| Segmento | Descrição | Tamanho estimado (Brasil) |
|----------|-----------|---------------------------|
| **Padarias e cafeterias** | Delivery próprio, alta frequência de pedidos | 35.000+ |
| **Pizzarias** | Pico noturno, gestão de múltiplos entregadores | 40.000+ |
| **Restaurantes de bairro** | Clientes fiéis, delivery fora dos marketplaces | 200.000+ |
| **Hamburguerias** | Operação intensa fim de semana | 25.000+ |
| **Marmitarias / Comida saudável** | Assinaturas e pedidos recorrentes | 15.000+ |
| **Lojas de conveniência** | Delivery de proximidade | 50.000+ |
| **Subtotal alimentação** | | **~365.000 estabelecimentos** |

#### Farmácias e Drogarias
| Segmento | Descrição | Tamanho estimado (Brasil) |
|----------|-----------|---------------------------|
| **Farmácias independentes** | 1-3 lojas, gestão familiar, sem delivery organizado | 60.000+ |
| **Drogarias de bairro** | Delivery por WhatsApp, perdem para grandes redes | 25.000+ |
| **Manipulação** | Farmácias de manipulação com entrega | 8.000+ |
| **Subtotal farmácias** | | **~93.000 estabelecimentos** |

#### Supermercados e Mercados
| Segmento | Descrição | Tamanho estimado (Brasil) |
|----------|-----------|---------------------------|
| **Mercados de bairro** | Delivery próprio, clientes fiéis, assinatura de mantimentos | 80.000+ |
| **Supermercados pequenos** | 1-5 checkouts, entrega própria limitada | 35.000+ |
| **Açougues / Peixarias** | Entrega de cortes especiais, pedidos por WhatsApp | 20.000+ |
| **Sacolões / Hortifrúti** | Cestas semanais, delivery por assinatura | 15.000+ |
| **Adega / Bebidas** | Delivery rápido de bebidas, pico noite e fds | 25.000+ |
| **Subtotal supermercados** | | **~175.000 estabelecimentos** |

**TAM (Total Addressable Market):** **~633.000 estabelecimentos no Brasil** que fazem delivery próprio ou misto.

### 1.4 Proposta de Valor

> "RapiDrop é a central de operações de delivery do lojista independente. Um sistema que unifica pedidos, entregadores e clientes, adaptado ao seu segmento — sem comissões abusivas e sem complexidade."

**Para cada segmento:**
| Segmento | Mensagem principal |
|----------|-------------------|
| **Restaurantes** | "Seus pedidos centralizados, seus entregadores no controle, sem iFood comer sua margem." |
| **Farmácias** | "Delivery organizado para farmácia independente. Receita digital, controle de tarja, e o cliente fiel sem precisar ir até a grande rede." |
| **Supermercados** | "Seu mercado com delivery próprio. O cliente compra pelo WhatsApp ou site, você separa, seu entregador leva. Simples." |

---

## 2. Personas e Dores

### 2.1 Persona 1 — O Lojista / Dono de Restaurante

**Nome:** Ricardo (42 anos)
**Negócio:** Pizzaria de bairro com 8 anos, 8 funcionários, 3 entregadores
**Dores:**
- Perde pedidos porque o WhatsApp toca sem parar e não consegue atender todo mundo
- Não sabe se o entregador está atrasado ou se perdeu o caminho
- iFood come 22% do valor de cada pizza — dói no bolso
- Tenta controlar pedidos em planilha mas erra na contagem do troco e nos endereços
- Os clientes ligam perguntando "cadê meu pedido?" e ele não tem resposta

**O que quer:**
- Um sistema que centralize tudo, que seja simples de usar (não é de tecnologia)
- Saber onde cada entregador está sem precisar ligar
- Poder ativar/desativar itens do cardápio em tempo real
- Relatório simples de quanto vendeu no dia e quantas entregas cada motoboy fez

### 2.2 Persona 2 — O Farmacêutico / Dono de Farmácia

**Nome:** Dra. Marina (38 anos)
**Negócio:** Farmácia independente há 10 anos, 4 funcionários, 2 entregadores de moto
**Dores:**
- Perde clientes para Drogasil e Pague Menos que entregam em 30 minutos
- Cliente liga pedindo remédio controlado e ela precisa explicar que precisa de receita — o cliente desiste
- Não consegue organizar entregas de medicamentos que precisam de refrigeração (insulina, vacinas)
- O balconista anota pedido errado: troca a dosagem, o laboratório, a apresentação
- Cliente pede "dor de cabeça" e ela precisa de 3 perguntas pra saber qual remédio sugerir

**O que quer:**
- Um catálogo digital onde o cliente veja o remédio com foto, bula, preço e dosagem certa
- Sistema que peça a receita na hora do pedido (upload de foto) para medicamentos de tarja
- Poder marcar quais itens precisam de refrigeração pra entregador saber
- Sugestão inteligente: "O cliente perguntou por dor de cabeça — mostra dipirona, paracetamol, ibuprofeno"
- Rápido: cliente pede e em 20 min a entrega sai

### 2.3 Persona 3 — O Dono de Mercado de Bairro

**Nome:** Seu Edgar (52 anos)
**Negócio:** Mercado de bairro há 20 anos, 6 funcionários, kombi própria para entregas
**Dores:**
- Cliente manda lista no WhatsApp e a atendente passa 20 minutos anotando item por item
- Cliente reclama que veio arroz marca A mas ele mandou marca B (não tinha A)
- Não sabe como cobrar frete justo — perde dinheiro em entrega longa ou perde cliente com frete caro
- Entrega marcada pra 18h mas entregador demora porque volta pro mercado entre cada entrega
- Cliente quer pagar no cartão na entrega mas o maquininha às vezes não passa

**O que quer:**
- Cliente montar a própria lista pelo site ou WhatsApp — sem atendente no meio
- Poder sugerir substituto: "não temos arroz A, podemos enviar B ou C?" e cliente aprova
- Taxa de entrega automática por km ou valor mínimo de pedido
- Roteirização: entregas da tarde agrupadas pra kombi fazer tudo de uma vez
- Maquininha na entrega com valor já calculado

### 2.4 Persona 4 — O Entregador

**Nome:** Jefferson (24 anos)
**Função:** Motoboy / Entregador (pode trabalhar pra restaurante, farmácia ou mercado)
**Dores:**
- O dono passa o endereço no WhatsApp e ele precisa olhar no Google Maps manualmente
- Às vezes recebe 3 entregas ao mesmo tempo sem saber qual fazer primeiro
- Cliente liga pra ele (não pro estabelecimento) perguntando onde está o pedido
- Perde tempo voltando pra base pra pegar o próximo pedido
- Quando é remédio: não sabe se precisa de cuidados especiais (refrigeração, frágil)

**O que quer:**
- Um app que mostre o próximo pedido, endereço e melhor rota
- Poder marcar "saiu para entrega" e "entregue" com um toque
- Não precisar dar satisfação pro cliente — o sistema notifica automático
- Ver quanto ganhou no dia
- Saber se a carga tem itens especiais (frágil, refrigeração, documentos)

### 2.5 Persona 5 — O Atendente / Operador

**Nome:** Carla (29 anos)
**Função:** Atendente (pode ser de restaurante, farmácia ou mercado)
**Dores:**
- Anota pedido no papel, grita pra cozinha/estoque, perde o papel, briga com todo mundo
- Cliente pede algo que está em falta mas o sistema antigo ainda mostra disponível
- Precisa digitar o mesmo pedido em 3 lugares diferentes (caixa, produção, entregador)
- Na farmácia: cliente pergunta "tem esse remédio?" e ela precisa ir no estoque olhar
- No mercado: cliente envia lista de 30 itens e ela precisa digitar um por um

**O que quer:**
- Um sistema onde ela digita o pedido uma vez e ele aparece pra produção e pro entregador
- Poder ver se um item está disponível antes de confirmar
- Impressão automática do pedido na cozinha/estoque
- Na farmácia: busca rápida por princípio ativo ou laboratório
- No mercado: cliente montar a própria lista online — ela só revisa e aprova
- Menos gritaria, mais organização

### 2.6 Persona 6 — O Administrador do SaaS (Dono do RapiDrop)

**Nome:** Você (o founder)
**Dores:**
- Precisa de uma plataforma que escale sem precisar de suporte manual para cada lojista
- Quer cobrar recorrentemente sem ter que ficar atrás de pagamento
- Precisa de métricas claras de saúde do negócio (MRR, churn, LTV)
- Quase desistiu porque viu sistema de delivery como "commodity" — mas percebeu que o mercado de lojistas independentes é imenso e mal servido
- Agora com 3 segmentos, precisa garantir que a plataforma seja flexível o suficiente sem se tornar complexa demais

**O que quer:**
- Onboarding 100% self-service para o lojista, adaptado ao segmento
- Planos claros (teste grátis → plano pago) com features por segmento
- Dashboard de métricas do SaaS em tempo real, segmentado por categoria
- Poder criar restrições por plano (ex: Plano Básico = 1 entregador, Premium = ilimitado)
- Gestão de cobrança e ciclos de faturamento
- Visibilidade de quais segmentos estão performando melhor (MRR por categoria)

### 2.7 Persona 7 — O Cliente Final (Comprador)

**Nome:** Ana (34 anos)
**Contexto:** Mora perto do comércio, pede 2x por semana (comida, remédio, mercado)
**Dores:**
- Não quer baixar mais um app — quer pedir pelo WhatsApp ou Instagram
- Quando pede, não sabe se o estabelecimento recebeu
- Fica ansiosa esperando sem saber onde está o entregador
- Na farmácia: precisa enviar foto da receita e não sabe se está visível/legível
- No mercado: lista compras no bloco de notas do celular e manda pro mercado — erra itens

**O que quer:**
- Confirmar que o pedido foi recebido
- Saber quanto tempo vai demorar
- Ver onde está o entregador ao vivo (como no iFood, mas sem app)
- Poder pagar por PIX ou cartão na entrega
- Na farmácia: enviar receita por foto dentro do próprio pedido
- No mercado: buscar por nome do produto e ver fotos, marcas, preços

---

## 3. Módulos e Funcionalidades

### Sistema de Pagamento de Entregadores

> O RapiDrop possui um sistema completo e configurável de pagamento de entregadores.
> Consulte o documento dedicado para especificação detalhada:
> ➡️ [`docs/pagamento-entregadores.md`](pagamento-entregadores.md)

### 3.1 Módulo SaaS Admin (Super Admin)

**Propósito:** O dono do RapiDrop gerencia toda a plataforma daqui.

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Dashboard do SaaS** | MRR, churn, lojistas ativos, pedidos processados, revenue | P0 |
| **Gestão de Lojistas** | CRUD completo, aprovar/desativar/bloquear lojistas | P0 |
| **Segmento do Lojista** | Classificar lojista por segmento (comida/farmácia/mercado) para estatísticas e onboarding | P0 |
| **Planos e Precificação** | Criar planos por segmento ou plano genérico, definir limites | P0 |
| **Cobrança / Faturamento** | Integração com gateway (Stripe/Asaas), ciclos de cobrança, invoices | P0 |
| **Gestão de Cupons** | Cupons de desconto para lojistas (ex: 30 dias grátis) | P1 |
| **Suporte / Tickets** | Sistema simples de tickets para lojistas abrirem chamados | P1 |
| **Audit Log** | Registro de todas as ações administrativas | P1 |
| **Configurações Globais** | Taxas padrão, limites de upload, e-mails transacionais | P1 |
| **Métricas por Segmento** | MRR, churn e crescimento separados por categoria (comida vs farmácia vs mercado) | P2 |
| **API Pública** | Documentação e chaves de API para integrações externas | P2 |

### 3.2 Módulo Lojista — Dashboard e Pedidos

**Propósito:** O coração do sistema — o lojista gerencia os pedidos em tempo real.

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Central de Pedidos (kanban)** | Pedidos em tempo real: Novo → Confirmado → Em preparo → Saiu p/ entrega → Entregue | P0 |
| **Detalhe do Pedido** | Itens, valor, endereço, cliente, observações, tempo decorrido | P0 |
| **Notificação Sonora** | Som ao receber novo pedido | P0 |
| **Impressão Automática** | Pedido impresso na cozinha/estoque ao ser confirmado (WebSocket + thermal) | P1 |
| **Histórico de Pedidos** | Busca por data, cliente, status, valor | P0 |
| **Pedidos por Canal** | Filtro por canal de origem (WhatsApp, Instagram, Site, Presencial) | P1 |
| **Visão de Preparo** | Tela separada para a produção (cozinha/estoque) ver apenas pedidos a preparar | P1 |
| **Re-pedido com 1 clique** | Cliente que já pediu antes — repetir pedido inteiro | P1 |
| **Substituição de Item** | (Mercado/Farmácia) Sugerir substituto quando item está em falta | P1 |
| **Upload de Receita** | (Farmácia) Visualizar foto da receita enviada pelo cliente no pedido | P1 |
| **Itens Fracionados** | (Mercado) Suporte a peso/quantidade fracionada (300g de queijo, 1/2 dúzia) | P1 |

### 3.3 Módulo Lojista — Catálogo de Produtos

**Propósito:** Gerenciamento do catálogo de produtos adaptado a cada segmento.

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Gestão de Categorias** | Organização hierárquica do catálogo. Ex: Comida → "Pizzas", Farmácia → "Analgésicos", Mercado → "Hortifrúti" | P0 |
| **Gestão de Produtos** | Nome, descrição, preço, foto, SKU/EAN, marca, fabricante | P0 |
| **Variações e Adicionais** | Comida: tamanho/sabor. Farmácia: apresentação (comprimido/xarope/gota). Mercado: embalagem (1kg/5kg/unidade) | P0 |
| **Unidade de Medida** | Configurável por produto: unidade, kg, grama, litro, ml, pacote, dúzia | P0 |
| **Disponibilidade** | Ativar/desativar item. Agendar disponibilidade (ex: "Café da manhã só até 11h") | P0 |
| **Gestão de Estoque** | Quantidade em estoque, alerta de estoque baixo, esgotado automático | P1 |
| **Preço por Unidade Fracionada** | (Mercado) Preço por kg/ml com cálculo automático para quantidades fracionadas | P1 |
| **Campos por Segmento** | Farmácia: princípio ativo, tarja (vermelha/preta/sem tarja), exige receita, refrigeração. Mercado: departamento, código de barras | P1 |
| **Bula Digital** | (Farmácia) Link para bula online do medicamento | P2 |
| **Importação em Massa** | Importar catálogo via CSV/planilha ou API | P2 |
| **Catalogo por Turno** | Exibir apenas certos itens em cada período do dia | P2 |
| **Sugestão Inteligente** | (Farmácia) Ao digitar "dor" mostrar opções relacionadas (analgésicos, anti-inflamatórios) | P2 |

### 3.4 Módulo Lojista — Entregadores

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Cadastro de Entregadores** | Nome, telefone, veículo (moto/bike/carro), documento, foto | P0 |
| **Status Online/Offline** | Entregador marca disponibilidade. Só recebe pedido se estiver online | P0 |
| **Atribuição de Pedido** | Automática (menor fila, melhor rota) ou manual (dono escolhe) | P0 |
| **Fila de Entregas** | Cada entregador vê sua fila: entregas pendentes ordenadas por rota | P1 |
| **Tracking ao Vivo** | Mapa com posição de cada entregador (GPS do app) | P1 |
| **Itens Especiais na Entrega** | Sinalizar para o entregador: "contém líquido", "frágil", "refrigeração", "documento" | P1 |
| **Histórico por Entregador** | Quantidade de entregas, tempo médio, valor médio, avaliações | P1 |
| **Ranking de Entregadores** | Classificação por performance com score ponderado (entregas, pontualidade, avaliação, aceitação) | P1 |
| **Dashboard do Ranking** | Visualização ao vivo da posição de cada entregador com bônus estimado | P1 |
| **Configuração de Pagamento** | Método (diária/por entrega/híbrido), estratégia, valores, faixas, bônus | P0 |
| **Configuração de Ranking** | Métricas, pesos, período, modelo de bônus (fixo/pool/metas) | P1 |
| **Extrato por Período** | Cálculo automático do valor a pagar por entregador com detalhamento | P1 |
| **Rateio Automático** | Sugerir qual entregador pegar baseado em proximidade geográfica | P2 |
| **Rota Otimizada** | Agrupar múltiplas entregas na melhor sequência | P2 |
| **Área de Cobertura** | Definir raio de entrega por tipo de veículo (moto vai mais longe que bike) | P2 |

### 3.5 Módulo Lojista — Financeiro

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Resumo do Dia** | Total de pedidos, faturamento bruto, média por pedido, forma de pagamento | P0 |
| **Pedidos por Período** | Faturamento diário/semanal/mensal com gráficos comparativos | P1 |
| **Pagamento de Entregadores** | Sistema completo configurável — veja especificação em [`docs/pagamento-entregadores.md`](pagamento-entregadores.md) | P0 |
| **Taxa de Entrega Inteligente** | Cálculo por km, faixa de CEP, valor mínimo de pedido | P1 |
| **Custo com Entregadores** | Relatório de quanto foi pago aos entregadores por período, método, entregador | P1 |
| **Relatório Fiscal** | Exportação de relatório mensal para contabilidade | P2 |
| **Conciliação** | Comparar pedidos do sistema com extrato bancário/gateway | P2 |

### 3.6 Módulo Lojista — Clientes

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Base de Clientes** | Nome, telefone, endereço(s), histórico de pedidos, total gasto | P0 |
| **Endereços Salvos** | Cliente pode ter múltiplos endereços (casa, trabalho) | P0 |
| **Histórico do Cliente** | Último pedido, frequência, ticket médio, itens favoritos | P1 |
| **Observações por Cliente** | "Cliente prefere pizza bem passada", "tocar interfone 2x", "cliente diabético" | P1 |
| **Segmentação** | Clientes ativos, inativos, VIPs, novos | P2 |
| **Campanhas** | Disparar WhatsApp em massa (ex: "Cliente fiel, ganhe 10% hoje") | P2 |
| **Receitas Recorrentes** | (Farmácia) Clientes com medicamentos de uso contínuo — lembrete mensal | P2 |
| **Cestas / Assinaturas** | (Mercado) Cesta semanal de hortifrúti, assinatura de mantimentos | P2 |

### 3.7 App do Entregador (Mobile)

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Login com PIN/QR Code** | Entregador acessa via app com código do estabelecimento | P0 |
| **Pedidos Atribuídos** | Lista de entregas pendentes com endereço, valor, itens | P0 |
| **Sinalização de Carga** | Ícones indicando: 🧊 refrigeração, ⚠️ frágil, 💊 medicamento, 🍕 alimento | P0 |
| **Navegação Integrada** | Botão "Abrir no Maps/Waze" com endereço pré-preenchido | P0 |
| **Status da Entrega** | Botões: "Sai p/ entrega" → "Entregue" com timestamp | P0 |
| **Confirmação de Entrega** | Foto do comprovante (opcional), assinatura digital (farmácia: confirmação de recebimento) | P1 |
| **GPS em Background** | Envia posição periódica para o estabelecimento ver no mapa | P1 |
| **Feed de Pedidos** | Notificação push de novo pedido atribuído | P1 |
| **Extrato do Dia** | Total de entregas, km rodados, valor a receber | P1 |
| **Chat Rápido** | Botão "Ligar para o cliente", "Ligar para o estabelecimento", "Ligar para a farmácia" | P1 |

### 3.8 Página Pública do Lojista (Site Próprio)

**Propósito:** Cada lojista tem seu site público com catálogo e checkout — sem precisar de app.

| Funcionalidade | Descrição | Prioridade |
|----------------|-----------|------------|
| **Catálogo Online** | Página pública com produtos, fotos, preços, busca | P0 |
| **Segmento Adaptável** | Layout e campos que se adaptam ao segmento (farmácia vs comida vs mercado) | P0 |
| **Carrinho e Checkout** | Cliente monta pedido e finaliza direto no site | P0 |
| **Múltiplas Formas de Pagamento** | PIX, Cartão, Dinheiro (troco para quanto) | P0 |
| **Cálculo de Taxa de Entrega** | Por faixa de CEP ou por km (geolocalização) | P0 |
| **Upload de Receita** | (Farmácia) Campo para enviar foto da receita antes de finalizar pedido | P1 |
| **Previsão de Entrega** | Tempo estimado baseado em histórico + fila de entregas | P1 |
| **Indicador de Disponibilidade** | Mostrar se item está em estoque. (Farmácia: "sujeito a receita") | P1 |
| **Busca Inteligente** | (Farmácia) Buscar por princípio ativo, laboratório, sintoma | P1 |
| **Lista de Compras** | (Mercado) Cliente cria lista e adiciona itens em lote | P1 |
| **Tracking do Pedido** | Página de rastreamento com status e posição do entregador | P1 |
| **Login com WhatsApp** | Cliente identifica pelo número de WhatsApp (sem senha) | P1 |
| **Favoritos** | Cliente salva itens e pedidos favoritos | P2 |
| **Substituto Sugerido** | (Mercado) Se item está em falta, sugerir marca similar para aprovação | P2 |

### 3.9 Integrações

| Integração | Descrição | Prioridade | Segmento |
|------------|-----------|------------|----------|
| **WhatsApp (API Oficial)** | Receber pedidos, confirmar, notificar status | P0 | Todos |
| **Instagram / Facebook** | Pedidos via Direct/Comentários | P1 | Todos |
| **iFood (API de Pedidos)** | Receber pedidos do iFood no mesmo dashboard | P1 | Comida |
| **Rappi / Zé Delivery** | Receber pedidos no dashboard | P2 | Comida/Bebidas |
| **Impressora Térmica** | Suporte Elgin, Bematech, Daruma | P1 | Todos |
| **Gateway de Pagamento** | PIX via Stripe/Asaas/Efí | P1 | Todos |
| **Google Maps / Waze** | Navegação integrada | P1 | Todos |
| **Google Analytics / Meta Pixel** | Tracking de conversão no site próprio | P2 | Todos |
| **ERP / PDV (ContaAzul, Nibo, Tiny)** | Sincronizar produtos e pedidos | P2 | Todos |
| **Sistemas de Farmácia** | Integração com RD Station, Farmarcas, ConsulData | P2 | Farmácia |
| **ANVISA / Bula Online** | Link para bula aprovada pela ANVISA nos medicamentos | P1 | Farmácia |
| **Mercado Pago / PagSeguro** | Maquininha na entrega com valor pré-programado | P2 | Todos |
| **API de CEP** | Buscar endereço automaticamente por CEP | P0 | Todos |

### 3.10 Notificações (Cross-Módulo)

| Tipo | Canal | Disparo |
|------|-------|---------|
| Novo pedido recebido | Som + Push + WhatsApp | Lojista / Equipe |
| Pedido confirmado | WhatsApp | Cliente |
| Pedido saiu para entrega | WhatsApp | Cliente |
| Entregador a caminho | WhatsApp + Push | Cliente |
| Pedido entregue | WhatsApp | Cliente |
| Receita necessária | WhatsApp | Cliente (farmácia) |
| Item indisponível | WhatsApp | Cliente (sugerir substituto) |
| Novo pedido atribuído | Push | Entregador |
| Carga especial (refrigeração/frágil) | Push | Entregador |
| Alerta de atraso | Push + WhatsApp | Lojista |
| Cliente não encontrado | Push + Ligação | Entregador → Lojista |
| Lembrete de reposição | WhatsApp | Cliente (farmácia: remédio contínuo) |
| Estoque baixo | Push/Email | Lojista |

> 📱 **Experiência completa do cliente final:** Cadastro único, catálogo, favoritos (lojas e pratos), checkout, promoções, distância e estratégia de aquisição estão detalhados em [`docs/experiencia-cliente.md`](experiencia-cliente.md).

---

## 4. Fluxos de Usuário

### 4.1 Fluxo do Cliente Final — Restaurante

```
[Cliente acessa link do restaurante]
    │
    ▼
[Vê cardápio online — fotos, descrições, preços]
    │
    ▼
[Adiciona itens ao carrinho — escolhe tamanho, borda, adicionais]
    │
    ▼
[Seleciona forma de pagamento]
    ├── PIX → QR Code gerado automaticamente
    ├── Cartão → Link de pagamento enviado por WhatsApp
    └── Dinheiro → Informa valor do troco
    │
    ▼
[Informa endereço (CEP ou geolocalização)]
    │
    ▼
[Confirma pedido]
    │
    ▼
[Recebe confirmação no WhatsApp: "Seu pedido #42 foi recebido!"]
    │
    ▼
[Acompanha status: Preparando → Saiu para entrega → Entregue]
```

### 4.2 Fluxo do Cliente Final — Farmácia

```
[Cliente acessa link da farmácia — ou manda "olá" no WhatsApp]
    │
    ▼
[Busca medicamento por nome, princípio ativo ou sintoma]
    │
    ▼
[Seleciona: apresentação, dosagem, quantidade]
    │
    ▼
[Se medicamento de tarja → upload da receita (foto)]
    │
    ▼
[Adiciona ao carrinho]
    │
    ▼
[Se item requer refrigeração → aviso: "entregaremos em caixa térmica"]
    │
    ▼
[Pagamento: PIX / Cartão / Dinheiro]
    │
    ▼
[Confirma pedido → farmácia valida receita]
    │
    ▼
[Recebe confirmação + prazo]
    │
    ▼
[Acompanha status: Separando → Saiu para entrega → Entregue]
```

### 4.3 Fluxo do Cliente Final — Mercado

```
[Cliente acessa link do mercado]
    │
    ▼
[Navega por departamentos: Hortifrúti, Açougue, Limpeza, Bebidas...]
    │
    ▼
[Adiciona itens — alguns por unidade, outros por peso (kg, gramas)]
    │
    ▼
[Se item em falta → sistema sugere substituto → cliente aprova ou troca]
    │
    ▼
[Escolhe janela de entrega: "Hoje 14h-16h" ou "Amanhã 8h-10h"]
    │
    ▼
[Valor mínimo de pedido é verificado]
    │
    ▼
[Pagamento + confirmação]
    │
    ▼
[Recebe aviso: "Separando pedido" → "Saiu para entrega"]
```

### 4.4 Fluxo do Pedido (Visão do Lojista — Genérico)

```
[Pedido chega — notificação sonora + pop-up no dashboard]
    │
    ▼
[Lojista vê detalhes: itens, endereço, valor, observações + tipo de carga]
    │
    ▼
[Lojista confirma pedido → status "Confirmado" + WhatsApp pro cliente]
    │
    ▼
[Produção/Estoque vê pedido na tela dedicada ou imprime automaticamente]
    │
    ▼
[Separação dos itens — se farmácia: valida receita; se mercado: verifica substitutos]
    │
    ▼
[Lojista atribui entregador (automático ou manual)]
    │
    ▼
[Entregador recebe notificação no app + sinalização de carga especial]
    │
    ▼
[Preparo finalizado → status "Saiu para entrega" + WhatsApp pro cliente]
    │
    ▼
[Entregador navega até o endereço]
    │
    ▼
[Entregador marca "Entregue" → status finalizado]
    │
    ▼
[Cliente recebe confirmação]
```

### 4.5 Fluxo de Cadastro do Lojista (Self-Service)

```
[Lojista acessa rapidrop.com.br]
    │
    ▼
[Clica em "Começar teste grátis"]
    │
    ▼
[Cadastra: nome, email, telefone, senha]
    │
    ▼
[Informa dados do estabelecimento: nome, endereço, categoria, horário]
    │
    ▼
[ESCOLHA O SEGMENTO:
    ├── 🍕 Alimentação (restaurantes, pizzarias, padarias)
    ├── 💊 Farmácia e Drogarias
    └── 🛒 Mercado e Supermercado
]
    │
    ▼
[Onboarding adaptado ao segmento:
    ├── Comida: cadastra cardápio, categorias, variações
    ├── Farmácia: cadastra medicamentos, tarjas, laboratórios
    └── Mercado: cadastra departamentos, produtos por peso/unidade
]
    │
    ▼
[Escolhe plano: Básico (grátis 14 dias) ou Profissional (grátis 7 dias)]
    │
    ▼
[Faz integração via WhatsApp (lê QR Code)]
    │
    ▼
[Cadastra primeiro entregador]
    │
    ▼
[Configura taxa de entrega e área de cobertura]
    │
    ▼
[Compartilha link do site: "Compre pelo site ou WhatsApp!"]
    │
    ▼
[Primeiro pedido real chega! 🎉]
```

### 4.6 Fluxo de Entrega (Visão do Entregador)

```
[App do entregador — login com PIN do estabelecimento]
    │
    ▼
[Tela inicial: status Online/Offline + entregas pendentes]
    │
    ▼
[Online → disponível para atribuição]
    │
    ▼
[Pedido atribuído → notificação + entra na fila]
    │
    ▼
[Entregador vê: endereço, itens, valor, observações + ícones de carga especial]
    │
    ▼
[Se carga especial: "🧊 manter refrigerado", "⚠️ frágil", "💊 medicamento"]
    │
    ▼
[Separação finalizada? → Botão "Sair para entrega"]
    │
    ▼
[Abre navegação no Maps/Waze]
    │
    ▼
[Chegou no local? → Botão "Entregue"]
    │
    ▼
[Opcional: foto do comprovante / confirmação de recebimento (farmácia)]
    │
    ▼
[Pedido finalizado → próximo da fila]
```

### 4.7 Fluxo do SaaS Admin (Dono do RapiDrop)

```
[Login como admin]
    │
    ▼
[Dashboard: Lojistas ativos (87) | Novos hoje (5) | MRR: R$ 8.430]
    │
    ▼
[Métricas por Segmento:
    ├── Alimentação: 45 lojistas | MRR: R$ 4.200
    ├── Farmácia: 22 lojistas | MRR: R$ 2.100
    └── Mercado: 20 lojistas | MRR: R$ 2.130
]
    │
    ▼
[Lista de lojistas → busca/filtro por: segmento, plano, status, data]
    │
    ▼
[Detalhe do lojista:
    - Segmento: Farmácia
    - Pedidos no mês: 342
    - Faturamento estimado: R$ 18.900
    - Plano: Profissional
    - Próximo vencimento: 15/07
    - Status: Ativo
]
    │
    ▼
[Ações: Desativar / Mudar plano / Ver fatura / Abrir ticket]
```

---

## 5. Arquitetura Técnica

### 5.1 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTES                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐ │
│  │ Site     │  │ Admin    │  │ Portal   │  │ App             │ │
│  │ Público  │  │ SaaS     │  │ Lojista  │  │ Entregador     │ │
│  │ (Next.js)│  │ (Next.js)│  │ (Next.js)│  │ (React Native)  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬────────┘ │
└───────┼──────────────┼──────────────┼──────────────────┼─────────┘
        │              │              │                  │
        └──────────────┴──────────────┴──────────────────┘
                        │        HTTPS + WSS
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REVERSE PROXY (Nginx / Traefik)             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                  FASTAPI BACKEND (Python 3.12+)                  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │ Auth     │  │ Orders   │  │ Catalog  │  │ Riders           ││
│  │ Module   │  │ Module   │  │ Module   │  │ Module           ││
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────────────┤│
│  │ Customers│  │ Payments │  │ Reports  │  │ Notifications    ││
│  │ Module   │  │ Module   │  │ Module   │  │ Module           ││
│  ├──────────┤  └──────────┘  └──────────┘  └──────────────────┘│
│  │ Segment  │                                                    │
│  │ Module   │  ┌──────────────────────────────────────────────┐│
│  └──────────┘  │  Shared: SQLAlchemy Async, Redis Cache        ││
│                │  Auth: JWT + Refresh Tokens, OAuth (WhatsApp) ││
│                │  WebSocket Manager (order tracking, GPS)      ││
│                │  Segment Engine (configs por segmento)        ││
│                └──────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  PostgreSQL  │    │      Redis       │    │  RabbitMQ /      │
│  + PostGIS   │    │  Cache + PubSub  │    │  Celery          │
│  (DD principal)│   │  + Sessions     │    │  (Fila de tasks) │
└──────────────┘    └──────────────────┘    └──────────────────┘
        │                                              │
        ▼                                              ▼
┌──────────────────┐                        ┌──────────────────┐
│  Object Storage  │                        │  Workers:        │
│  (S3/MinIO)      │                        │  - Webhook       │
│  Fotos produtos  │                        │  - Email         │
│  Comprovantes    │                        │  - Relatórios    │
│  Receitas (cripto)│                       │  - Importação    │
└──────────────────┘                        └──────────────────┘
```

### 5.2 Segment Engine — O Diferencial Arquitetural

O **Segment Engine** é o coração da flexibilidade do RapiDrop. Ele permite que um mesmo código sirva múltiplos segmentos sem virar uma "salada de ifs".

```
Segment Engine (config-driven)
├── merchant.segment = "food" | "pharmacy" | "grocery"
│
├── [Catalog Config]
│   ├── food:     categories, variations (size/flavor), add-ons
│   ├── pharmacy: active_ingredient, prescription_flag, tarja, lab, refrigeration
│   └── grocery:  department, barcode, unit_type (kg/un/l), weight_support
│
├── [Order Config]
│   ├── food:     preparation_time, kitchen_view, printing
│   ├── pharmacy: prescription_validation, refrigeration_check
│   └── grocery:  substitution_flow, weight_items, delivery_window
│
├── [Checkout Config]
│   ├── food:     tip_option, special_instructions
│   ├── pharmacy: prescription_upload, age_verification
│   └── grocery:  delivery_schedule, substitution_approval, min_order
│
├── [Notification Templates]
│   ├── food:     "Seu pedido está sendo preparado 🍕"
│   ├── pharmacy: "Sua receita foi validada ✅"
│   └── grocery:  "Seu pedido está sendo separado 🛒"
│
└── [UI Config (Frontend)]
    ├── food:     hero image = pizza, icons = food, colors = warm
    ├── pharmacy: hero image = farmácia, icons = medicine, colors = green/white
    └── grocery:  hero image = mercado, icons = grocery, colors = fresh
```

### 5.3 Estrutura de Módulos (Backend)

```
rapidrop/
├── apps/
│   ├── api/                    # FastAPI application
│   │   ├── src/
│   │   │   ├── core/           # Config, security, database
│   │   │   ├── modules/
│   │   │   │   ├── auth/       # Login, register, JWT, OAuth
│   │   │   │   ├── saas_admin/ # Super admin features
│   │   │   │   ├── merchants/  # Merchant CRUD, segment config
│   │   │   │   ├── segment/    # Segment Engine (configs, validation)
│   │   │   │   ├── orders/     # Order lifecycle
│   │   │   │   ├── catalog/    # Products, categories, variations
│   │   │   │   ├── riders/     # Riders, assignments, tracking
│   │   │   │   ├── customers/  # Customer base, history
│   │   │   │   ├── payments/   # Payment processing
│   │   │   │   ├── notifications/ # Push, WhatsApp, Email
│   │   │   │   ├── reports/    # Analytics, exports
│   │   │   │   └── webhooks/   # iFood, external integrations
│   │   │   ├── shared/         # Common utilities, DTOs, exceptions
│   │   │   └── main.py         # App entry point
│   │   ├── alembic/            # Database migrations
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── web/                    # Next.js (Next.js 15 App Router)
│       ├── src/
│       │   ├── app/
│       │   │   ├── (public)/   # Landing page, blog
│       │   │   ├── (store)/    # Storefront (adaptável por segmento)
│       │   │   ├── (merchant)/ # Merchant dashboard
│       │   │   │   ├── pedidos/
│       │   │   │   ├── catalogo/
│       │   │   │   ├── entregadores/
│       │   │   │   ├── clientes/
│       │   │   │   └── relatorios/
│       │   │   └── admin/      # SaaS admin panel
│       │   ├── components/
│       │   ├── lib/
│       │   │   ├── segment-engine/  # Renderização adaptativa por segmento
│       │   │   └── api-client/
│       │   └── styles/
│       └── package.json
├── packages/
│   ├── shared/                 # Types, Zod schemas, utilities
│   ├── api-client/             # TanStack Query hooks
│   └── tokens/                 # Design tokens
├── docker-compose.yml
├── turbo.json
└── package.json (root)
```

### 5.4 Tecnologias e Justificativas

| Tecnologia | Por quê? |
|------------|----------|
| **FastAPI** | Performance, async nativo, validação com Pydantic v2, docs automáticas (Swagger), tipagem forte. Ideal para APIs que precisam de WebSocket (tracking em tempo real). |
| **SQLAlchemy 2.x async** | ORM mais maduro do ecossistema Python. Async para não travar nas operações de I/O. Suporte a PostGIS. |
| **PostgreSQL + PostGIS** | Consultas geográficas (calcular distância, buscar entregadores próximos, faixas de CEP). pgvector pronto para futuro ML. |
| **Redis** | Cache de catálogo (evita bater no DB a cada visita), PubSub para WebSocket, sessões, fila de jobs. |
| **Celery / RabbitMQ** | Tasks assíncronas: enviar WhatsApp, gerar relatórios, processar webhooks, importar catálogo. |
| **Next.js 15 App Router** | SSR para site público (SEO), RSC para performance, layout aninhado para as áreas do SaaS, Server Actions para formulários. |
| **TanStack Query** | Cache e sincronização de dados no frontend. Refetch automático, optimistic updates para pedidos. |
| **shadcn/ui** | Componentes acessíveis e estilizados com Tailwind. Customizáveis, sem lock-in. |
| **React Native / Expo** | App do entregador cross-platform. Expo SDK cuida de GPS, push, câmera. |
| **WebSocket** | Pedidos em tempo real, tracking de GPS do entregador, atualização de status sem polling. |
| **Segment Engine** | Arquitetura config-driven para suportar múltiplos segmentos sem duplicar código. |

### 5.5 WebSocket — Eventos em Tempo Real

```
Eventos do servidor → cliente (lojista):
  order.new              → Novo pedido recebido
  order.status_changed   → Pedido mudou de status
  rider.location_update  → Posição GPS do entregador
  rider.status_changed   → Entregador ficou online/offline
  prescription.validated → (Farmácia) Receita validada

Eventos do servidor → cliente (entregador):
  order.assigned         → Novo pedido atribuído
  order.cancelled        → Pedido cancelado
  order.priority_update  → Reordenamento da fila
  cargo.special_alert    → ⚠️ Carga especial (refrigeração/frágil)

Eventos do servidor → cliente (cliente final):
  order.confirmed        → Pedido confirmado
  order.preparing        → Em preparo / separação
  order.out_for_delivery → Saiu para entrega
  rider.location_update  → Posição do entregador (anonimizada)
  order.substitution     → (Mercado) Item substituído — precisa aprovar

Eventos do cliente → servidor:
  rider.location_update  → Envio periódico de GPS
  merchant.order_status  → Mudança manual de status
  order.substitution_approve → (Mercado) Cliente aprovou substituto
```

### 5.6 Segurança (Diretrizes Iniciais)

- **Autenticação**: JWT + Refresh Token. Tokens curtos (15min access, 7d refresh).
- **Multi-tenancy**: Isolamento por `merchant_id` em todas as queries. Nunca um lojista vê dado de outro.
- **RBAC**: 3 roles básicas — `saas_admin`, `merchant_owner`, `rider`. Expansível.
- **API rate limiting**: Por IP, por merchant, por endpoint.
- **LGPD**: Consentimento do cliente final, política de retenção de dados, exportação.
- **HTTPS-only**: SSL/TLS em toda comunicação.
- **Audit logging**: Toda ação administrativa e financeira é logada imutavelmente.
- **Dados sensíveis de saúde**: Receitas médicas criptografadas em repouso (AES-256). Acesso restrito e logado (farmácia).
- **Classificação de medicamentos**: Validação de tarja (vermelha/preta) antes de permitir venda sem receita.

---

## 6. Modelagem de Dados (Alto Nível)

### 6.1 Entidades Principais

```
saas_admin
├── id, email, name, password_hash, role

merchant (lojista)
├── id, name, business_name, document (CNPJ/CPF), email, phone
├── merchant_type: enum (food | pharmacy | grocery)
├── address (street, number, city, state, zip, lat, lng)
├── plan_id (FK), plan_status (active/trial/cancelled/blocked)
├── settings: jsonb (delivery_fee_config, working_hours, timezone, segment_configs)
├── is_active, created_at, trial_ends_at

plan
├── id, name, slug (basic/pro/enterprise)
├── price_cents, max_riders, max_orders_monthly
├── allowed_segments: jsonb (["food", "pharmacy", "grocery"])
├── features: jsonb (can_integrate_ifood, can_export_reports, prescription_validation, etc.)

product_category
├── id, merchant_id (FK), name, sort_order, is_active
├── segment_fields: jsonb (nullable — campos extras por segmento)
│   └── pharmacy: "departamento" (medicamentos, cosmeticos, higiene)
│   └── grocery: "setor" (hortifruti, acougue, limpeza)

product
├── id, merchant_id (FK), category_id (FK)
├── name, description, price_cents, image_url, barcode (EAN)
├── unit_type: enum (unit | kg | g | l | ml | pack | dozen)
├── is_available, has_variations, stock_quantity, stock_alert_at
├── segment_specific: jsonb (campos que variam por segmento)
│   └── food: prep_time_minutes, recipe_url
│   └── pharmacy: active_ingredient, tarja (red/black/none),
│       requires_prescription, requires_refrigeration, lab_name, anvisa_code
│   └── grocery: department, weight_supported, substitute_product_id

product_variation
├── id, product_id (FK), name (e.g. "Grande", "Comprimido 500mg", "1kg")
├── price_cents_adjustment, is_default

order
├── id (sequential per merchant: #42), merchant_id (FK)
├── customer_id (FK), rider_id (FK, nullable)
├── channel (whatsapp/instagram/site/presencial)
├── status (pending/confirmed/preparing/out_for_delivery/delivered/cancelled)
├── items: jsonb (product_id, name, qty, unit_price, variations, weight, substitution_ok)
├── subtotal_cents, delivery_fee_cents, total_cents
├── payment_method (pix/card/cash), payment_status
├── customer_address, customer_notes
├── segment_data: jsonb
│   └── pharmacy: prescription_image_url, prescription_validated_at
│   └── grocery: delivery_window, substitutions (jsonb)
├── assigned_at, confirmed_at, preparing_at, out_for_delivery_at, delivered_at

rider (entregador)
├── id, merchant_id (FK)
├── name, phone, vehicle_type (motorcycle/bike/car), document
├── is_online, current_location (lat, lng, updated_at)
├── is_active, created_at

order_rider
├── id, order_id (FK), rider_id (FK)
├── assigned_at, accepted_at, picked_up_at, delivered_at
├── status (assigned/accepted/picked_up/delivered)

customer
├── id, phone (unique per merchant), name
├── merchant_id (FK)
├── total_orders, total_spent_cents, last_order_at
├── notes: jsonb (merchant-specific notes)
├── health_notes: jsonb (pharmacy: allergies, continuous_use_meds — criptografado)

payment_transaction
├── id, order_id (FK), merchant_id (FK)
├── gateway (stripe/asaas/pagseguro), gateway_transaction_id
├── amount_cents, fee_cents, status, method
├── paid_at, refunded_at

prescription (farmácia)
├── id, order_id (FK), customer_id (FK)
├── image_url (criptografado), validated_at, validated_by
├── doctor_name, doctor_crm, issue_date, expiry_date
├── status (pending/validated/rejected), rejection_reason

subscription_invoice
├── id, merchant_id (FK), plan_id (FK)
├── period_start, period_end, amount_cents
├── status (pending/paid/overdue/cancelled), paid_at
├── gateway_invoice_id

rider_payment_config
├── id, merchant_id (FK)
├── method (daily_rate / per_delivery / hybrid)
├── strategy (fixed_with_minimum / tiered_by_volume / etc)
├── config: jsonb (valores, faixas, bônus, adicionais)
├── ranking_enabled, ranking_period, ranking_metrics_config: jsonb
├── ranking_bonus_model (fixed_position / pool / individual_goals)
├── ranking_bonus_config: jsonb
├── is_active, created_at, updated_at

rider_payment_period
├── id, merchant_id (FK), rider_id (FK)
├── period_start, period_end, method
├── base_amount_cents, additional_cents, ranking_bonus_cents
├── ranking_position, total_cents
├── metrics_snapshot: jsonb (métricas congeladas no cálculo)
├── delivery_breakdown: jsonb (detalhamento por entrega)
├── status (calculating / pending_approval / approved / paid / cancelled)
├── paid_at, payment_method, payment_proof
├── approved_by, approved_at
```

### 6.2 Considerações de Modelagem

- **Segment Engine via jsonb**: Em vez de criar tabelas separadas para cada segmento, usamos campos `jsonb` (`segment_specific`, `segment_data`, `segment_fields`) para armazenar dados específicos. Isso mantém o schema enxuto e flexível.
- **Criptografia de receitas**: Imagens de receitas médicas são criptografadas em repouso (AES-256) e só descriptografadas para o farmacêutico responsável.
- **PostGIS para geolocalização**: `ST_DWithin` para buscar entregadores próximos, `ST_Distance` para calcular taxa de entrega.
- **Índices críticos**: `(merchant_id, status, created_at)` para listagem de pedidos, `(merchant_id, phone)` para busca de cliente, `(merchant_id, is_online)` para entregadores disponíveis, `(merchant_type, created_at)` para métricas do admin.
- **Índices para farmácia**: `(merchant_id, segment_specific->>'active_ingredient')` para busca por princípio ativo.
- **Índices para mercado**: `(merchant_id, barcode)` para busca por código de barras.

---

## 7. Roadmap Sugerido

### Fase 1 — Fundação (Meses 1-2) 🏗️

**Foco**: MVP funcional para validar com os primeiros lojistas de **um segmento** (comida).

- [ ] Setup do monorepo (Turborepo + pnpm)
- [ ] FastAPI base com auth (JWT)
- [ ] PostgreSQL + Redis + Docker Compose
- [ ] CRUD de lojistas (cadastro, login, plano, segmento)
- [ ] Segment Engine básico (config-driven para 1 segmento)
- [ ] Catálogo de produtos (categorias + produtos + variações)
- [ ] Recebimento de pedidos (manual via dashboard)
- [ ] Gestão de entregadores (cadastro + atribuição manual)
- [ ] App do entregador (React Native): ver pedidos, marcar status
- [ ] Página pública do lojista (catálogo + checkout simples)
- [ ] Dashboard do lojista (pedidos em tempo real)
- [ ] Deploy inicial (Railway ou AWS)

**Métrica de sucesso**: 5 lojistas pagantes com 50+ pedidos processados

### Fase 2 — Multi-Segmento (Mês 3) 🧩

- [ ] Segment Engine completo (configs para food, pharmacy, grocery)
- [ ] Onboarding adaptado por segmento (cadastro differenciado)
- [ ] Farmácia: upload de receita, tarja, refrigeração, busca por princípio ativo
- [ ] Mercado: peso fracionado, departamentos, substitutos, código de barras
- [ ] Catálogo público adaptável por segmento
- [ ] Ajustes de checkout por segmento (janela de entrega para mercado, receita para farmácia)
- [ ] Conquistar 2 lojistas de farmácia e 2 de mercado para validar

**Métrica de sucesso**: 15 lojistas pagantes (mín. 3 de cada segmento), NPS por segmento > 40

### Fase 3 — Integrações e Tempo Real (Mês 4) 🔌

- [ ] WebSocket para pedidos em tempo real
- [ ] Notificações push (app entregador + site)
- [ ] Integração WhatsApp (receber pedidos + notificar clientes)
- [ ] PIX via gateway de pagamento
- [ ] Tracking GPS do entregador (app → mapa no dashboard)
- [ ] Sinalização de carga especial no app do entregador
- [ ] Impressão automática (thermal printer)
- [ ] Canal de entrada: Instagram

**Métrica de sucesso**: 30 lojistas pagantes, < 1s delay nas notificações

### Fase 4 — SaaS Admin e Planos (Mês 5) 💰

- [ ] Painel super admin completo com métricas por segmento
- [ ] Gestão de planos e precificação (por segmento ou genérico)
- [ ] Cobrança automática (Stripe/Asaas)
- [ ] Trial de 14 dias com conversão
- [ ] Métricas do SaaS (MRR, churn, LTV, cohorts) segmentadas
- [ ] Cupons de desconto
- [ ] Restrições por plano (max entregadores, max pedidos, features por segmento)

**Métrica de sucesso**: MRR > R$ 5.000, churn < 8%

### Fase 5 — Analytics e Retenção (Mês 6) 📊

- [ ] Relatórios para o lojista adaptados por segmento
- [ ] Base de clientes com histórico e segmentação
- [ ] Campanhas de marketing via WhatsApp
- [ ] Integração iFood (receber pedidos no mesmo dashboard)
- [ ] SEO do site público (páginas dos lojistas indexadas)
- [ ] Landing page institucional do RapiDrop

**Métrica de sucesso**: 60 lojistas pagantes, NPS > 50

### Fase 6 — Escala e Otimização (Mês 7+) 🚀

- [ ] Alocação automática de entregadores (menor fila)
- [ ] Rota otimizada para múltiplas entregas
- [ ] App Cliente Final (React Native / Expo)
- [ ] ML para previsão de tempo de entrega
- [ ] Assinaturas e cestas recorrentes (mercado + farmácia)
- [ ] Integração com sistemas de farmácia (RD, Farmarcas)
- [ ] API pública para parceiros
- [ ] Performance: caching, query optimization, CDN
- [ ] i18n (expansão para outros países)

**Métrica de sucesso**: 150+ lojistas pagantes, MRR > R$ 20.000

---

## 8. Modelo de Negócio

> ⚠️ **Este modelo de precificação substitui a versão anterior de planos fixos.**
> A especificação completa está em [`docs/assinatura-saas.md`](assinatura-saas.md).

### 8.1 Visão Geral do Modelo

O RapiDrop adota um modelo de cobrança em **duas fases**, desenhado para equilibrar baixa barreira de entrada com receita previsível:

```
FASE 1 (mêses 1-12):      FASE 2 (após 12 meses):
Percentual por pedido      Escolha do lojista:
                           ├─ Opção A: continuar no percentual
                           └─ Opção B: mensalidade fixa calculada
                              pelo histórico de vendas
```

### 8.2 Fase 1 — Percentual por Pedido (Primeiro Ano)

O lojista paga **um percentual sobre o valor total de cada pedido** processado pelo RapiDrop. Sem mensalidade fixa. Sem fidelidade.

| Segmento | Taxa | Cortesia inicial |
|----------|:----:|:----------------:|
| **Alimentação** | 2,0% por pedido | 2 primeiros meses grátis |
| **Farmácia** | 1,5% por pedido | 2 primeiros meses grátis |
| **Mercado** | 1,5% por pedido | 2 primeiros meses grátis |

```
Exemplo: Pedido de R$ 100,00 em um restaurante
         Taxa: 2% → R$ 2,00 cobrados do lojista
```

A cobrança é mensal, consolidando todos os pedidos do mês anterior. Pedidos cancelados ou reembolsados não geram cobrança.

### 8.3 Fase 2 — Escolha do Lojista (Após 12 Meses)

Ao completar 12 meses de uso, o lojista pode escolher entre:

**Opção A — Continuar no percentual**
- Mesma taxa do segmento (2% ou 1,5%)
- Sem mensalidade fixa
- Ideal para lojistas que preferem custo variável

**Opção B — Migrar para mensalidade fixa**
- Valor calculado pelo histórico dos últimos 12 meses
- Fórmula: `max(média_12_meses, média_6_meses_recentes)` — sem buffer
- **Revisão anual obrigatória**: recalculada usando pedidos reais dos últimos 12 meses, simulando o percentual — garante que o SaaS nunca ganhe menos que no modelo percentual
- Reajuste anual por IPCA (limitado a 15%)
- 🔄 **Pode voltar ao percentual a qualquer momento** — sem multa, sem período mínimo
- Ideal para lojistas que querem previsibilidade de custos

### 8.4 Receitas Adicionais

| Fonte | Como |
|-------|------|
| **Comissão de pagamento** | 2-3% sobre transações processadas via gateway (parceria) |
| **White label** | Site próprio com domínio personalizado (R$ 29/mês extra) |
| **SMS** | Taxa por notificação SMS (quando WhatsApp não disponível) |
| **Marketplace** | Futuro: taxa sobre pedidos vindos de descoberta no marketplace RapiDrop |
| **Add-on Farmácia** | Módulo de validação de receitas + integração ANVISA (R$ 29/mês extra) |
| **Add-on Mercado** | Módulo de substitutos inteligentes + lista de compras (R$ 19/mês extra) |

### 8.5 Economia Unitária (Estimativa)

```
CAC estimado (misto orgânico + referral):     R$ 80-120
Ticket médio mensal por lojista (ano 1):      ~R$ 100-150
Margem bruta (sem infra):                     ~80%
Churn estimado:                               5-8% / mês
LTV (12 meses):                               ~R$ 900-1.500
Payback:                                      ~1-2 meses
```

> **Nota sobre o LTV:** O modelo de percentual alinha incentivos — a receita do RapiDrop cresce junto com o faturamento do lojista. Lojistas que crescem geram mais receita sem aumento de custo de aquisição.

---

## 9. Diferenciais Competitivos

### 9.1 Concorrência por Segmento

#### Alimentação
| Concorrente | Modelo | Fraqueza | Oportunidade RapiDrop |
|-------------|--------|----------|---------------------------|
| **iFood** | Marketplace | Comissão 12-27%, restaurante é só fornecedor | Damos o controle ao lojista, sem comissão |
| **WhatsApp + Planilha** | Artesanal | Caótico, erra pedido, sem gestão | Centralizamos, organizamos, automatizamos |
| **Cardápio Web (Goomer, Menu)** | Cardápio digital | Só cardápio, sem gestão de entregas | Fluxo completo (pedido → entrega) |
| **Sistemas de PDV** | Gestão completa | Caros (R$ 500+/mês), complexos | Simples, acessível, focado em delivery |

#### Farmácias
| Concorrente | Modelo | Fraqueza | Oportunidade RapiDrop |
|-------------|--------|----------|---------------------------|
| **Grandes redes (Drogasil, Pague Menos)** | Delivery próprio | Cliente só compra deles, farmácia independente perde | Farmácia independente com delivery profissional |
| **WhatsApp + Balcão** | Manual | Atendente vira digitador, erro de medicação | Catálogo digital com busca por princípio ativo e dosagem |
| **Sistemas de farmácia (RD, Farmarcas)** | Gestão interna | Sem delivery, sem site público, sem tracking | Camada de delivery sobre o sistema existente |
| **Consultórios farmacêuticos** | Presencial | Cliente precisa ir até a farmácia | Delivery de medicamentos contínuos com receita digital |

#### Supermercados
| Concorrente | Modelo | Fraqueza | Oportunidade RapiDrop |
|-------------|--------|----------|---------------------------|
| **Zé Delivery / Cornershop** | Marketplace | Só bebidas/mercado seletivo, comissão alta | Mercado de bairro com catálogo completo |
| **WhatsApp + Lista** | Manual | Atendente perde 20min digitando lista | Cliente monta própria lista online |
| **Sites de grande rede (Pão de Açúcar, Carrefour)** | E-commerce próprio | Só para grandes, mínimo alto, entrega agendada dias | Mercado pequeno com entrega no mesmo dia |
| **Aplicativos de assinatura** | Cestas | Limitado a cestas pré-definidas | Catálogo completo + cestas personalizadas |

### 9.2 Diferenciais Estratégicos

1. **Multisegmento nativo** — Um sistema que serve restaurantes, farmácias e mercados com a mesma base de código. Config-driven, não "if-else hell".
2. **Independência de marketplace** — O lojista não precisa do iFood/Rappi. Ele tem o próprio canal direto com o cliente.
3. **WhatsApp como canal primário** — O cliente não baixa app. Já está no WhatsApp. Pedido flui naturalmente em qualquer segmento.
4. **Mobile-first para entregador** — App nativo com GPS, rota, notificações e sinalização de carga especial (refrigeração, frágil, medicamento).
5. **Simplicidade radical** — Interface pensada para o dono de comércio que não é tech-savvy. 3 cliques e um pedido é criado.
6. **Segment Engine** — A arquitetura que permite suportar 3 segmentos sem código duplicado. Cada segmento tem seu fluxo, seus campos, suas regras — mas tudo no mesmo monolito bem estruturado.
7. **Crescimento via rede** — O entregador indica outros estabelecimentos. O cliente descobre novos lugares. Crescimento orgânico entre segmentos.
8. **Data-Driven para o lojista** — Relatórios simples que mostram quais produtos vendem mais, em quais dias, para quais clientes.

### 9.3 Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Lojista não adotar tecnologia | Alto | Onboarding guiado por WhatsApp, interface super simples, suporte humano no início |
| Churn alto pós trial | Alto | Engajamento na trial: meta de 10 pedidos na primeira semana. Suporte ativo |
| Complexidade de suportar 3 segmentos | Alto | Segment Engine bem definido desde o início. Não deixar acumular dívida técnica. Testes por segmento. |
| Concorrência de marketplaces | Médio | Foco em lojistas que já querem sair do iFood. Proposta de valor clara. |
| Regulação farmacêutica (ANVISA) | Médio | Consultoria jurídica especializada. Validação de receitas apenas como suporte, não como substituto do farmacêutico. |
| Farmácia: responsabilidade civil | Alto | Termo de uso claro: sistema auxilia, mas responsabilidade pela dispensação é do farmacêutico responsável. Seguro de responsabilidade civil. |
| Problemas com tracking GPS | Médio | Fallback: envio de localização por link do WhatsApp |
| Cliente final não encontrar o site público | Médio | SEO, Google Business Profile, QR Code no balcão/embalagem |

---

## 10. Próximos Passos

### Imediatos
1. **Validar o documento com 3-5 potenciais clientes** (um de cada segmento)
2. **Refinar escopo do MVP** — começar com 1 segmento (comida) e preparar arquitetura para expandir
3. **Consultoria jurídica para farmácia** — entender requisitos ANVISA, LGPD para dados de saúde
4. **Wireframes da UX** — @luna desenha os fluxos principais de cada segmento

### Curto Prazo
5. **PRD detalhado da Fase 1** — @nico transforma em requisitos técnicos
6. **Setup do projeto** — @maya define arquitetura final, @theo prepara infra, @kira e @dani iniciam o código
7. **Segment Engine spec** — definição detalhada das configurações por segmento

### Médio Prazo
8. **Onboarding adaptativo** — experiência de cadastro differenciada por segmento
9. **Aquisição de clientes** — campanhas segmentadas para cada persona
10. **Métricas por segmento** — dashboards que mostrem saúde de cada vertical do negócio

---

> **Documento criado em:** Junho 2026
> **Versão:** 2.0
> **Principais mudanças v2.0:** Adicionados segmentos de Farmácia e Supermercado ao público-alvo.
> Arquitetura Segment Engine, novas personas (farmacêutico, dono de mercado),
> modelos de dados extendidos (prescription, segment_data), roadmaps por segmento.
