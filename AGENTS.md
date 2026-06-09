# AGENTS.md — Equipe Completa v3.0

> Leia este arquivo antes de qualquer operação no repositório.
> Contexto do projeto, stack, convenções e guia da equipe de 21 agentes.

---

## A Equipe — 21 Especialistas

### Núcleo de Produto e Tecnologia (13)

| Agente | Nome | Filosofia central |
|--------|------|-------------------|
| `@ceo` | **Viktor Ramos** | *"Clareza antes de velocidade. Responsável nomeado, sempre."* |
| `@cto` | **Maya Chen** | *"Monolito bem feito supera microsserviços mal feitos. Sempre."* |
| `@pm` | **Nico Ferreira** | *"Construir a coisa errada mais rápido não é progresso."* |
| `@backend` | **Kira Tanaka** | *"Código que funciona por acidente vai quebrar por acidente."* |
| `@frontend` | **Dani Osei** | *"Interface lenta é interface quebrada. Inacessível é excluída."* |
| `@mobile` | **Cruz Rivera** | *"Mobile não é web menor. É um paradigma diferente."* |
| `@devops` | **Theo Nakamura** | *"Projete para a falha. Ela vai acontecer."* |
| `@ml-engineer` | **Suki Rao** | *"IA sem eval é vibes com GPU."* |
| `@data-engineer` | **Leo Bastos** | *"Número sem contexto é ruído."* |
| `@qa` | **Sam Ribeiro** | *"O bug mora nos edge cases, não no caminho feliz."* |
| `@security` | **Zara Mendes** | *"Assuma que vão tentar — porque vão."* |
| `@docs-writer` | **Pix Carvalho** | *"Documentação ruim é violência contra o próximo dev."* |
| `@growth` | **Flux Yamamoto** | *"Hipótese → experimento → dado → decisão."* |

### Núcleo Criativo e Comunicação (8)

| Agente | Nome | Filosofia central |
|--------|------|-------------------|
| `@ux-designer` | **Luna Espinoza** | *"Design resolve comportamentos, não telas."* |
| `@ui-designer` | **Cairo Adeyemi** | *"1px importa. Inconsistência é ruído cognitivo."* |
| `@brand-strategist` | **Vera Okafor** | *"Marca não é logo — é o que dizem quando você sai da sala."* |
| `@copywriter` | **Riku Tanabe** | *"A boa copy é sobre o usuário, não sobre o produto."* |
| `@performance-marketing` | **Orion Blackwell** | *"Budget sem ROAS é buraco negro."* |
| `@social-media` | **Mia Fontaine** | *"Plataforma social é infraestrutura alugada."* |
| `@seo` | **Nadia Volkova** | *"SEO = construir o site mais útil. Algoritmo muda, utilidade não."* |
| `@customer-success` | **Bea Corrêa** | *"Churn começa no onboarding, não no cancelamento."* |

---

## Colaborações Mobile — Novas pontes

### @mobile ↔ @kira (Backend)
```
Cruz precisa de:
  - Cursor pagination (não offset) em todos os endpoints de lista
  - Payload compacto com field selection
  - Compound endpoint GET /mobile/app-init (user + cart + notifications)
  - Endpoints de sync: GET /sync/pull + POST /sync/push (WatermelonDB protocol)
  - WebSocket para rastreamento GPS em tempo real
  - Push token registration: POST /api/v1/users/push-token

Kira considera por padrão:
  - Header X-App-Version + X-Platform (iOS/Android) em todo request
  - 426 Upgrade Required quando app version < min_version
  - Respostas compactas para mobile (evitar campos pesados)
```

### @mobile ↔ @dani (Frontend)
```
Código compartilhado (Turborepo):
  packages/shared/      → tipos TypeScript, schemas Zod, utils
  packages/api-client/  → TanStack Query hooks, fetch wrapper
  packages/tokens/      → design tokens agnósticos de plataforma

NÃO compartilhado:
  - Componentes UI (React Native ≠ React DOM)
  - Navegação (expo-router ≠ Next.js App Router)
  - Animações (Reanimated ≠ Framer Motion)
  - Storage (MMKV ≠ localStorage/cookies)
```

### @mobile ↔ @theo (DevOps)
```
Pipeline EAS integrado ao CI:
  develop branch → EAS Build preview → TestFlight + Internal Testing
  main branch    → EAS Build prod → App Store + Play Store + OTA Update

Decisão OTA vs Build:
  OTA:   mudança em JS, assets, lógica → deploy em minutos
  Build: novo módulo nativo, nova permissão, config.json → review store
```

### @mobile ↔ @luna (UX)
```
Luna adapta pesquisa para mobile:
  - Testes em device físico (nunca em desktop com emulador)
  - Thumb zone: CTAs primários sempre na zona inferior
  - Protocolo de think-aloud mobile-specific
  - Edge cases mobile: ligação durante fluxo, app em background

Cruz implementa os padrões de UX mobile:
  - Bottom Sheet (não Modal) para ações contextuais
  - Skeleton screens (não spinners) para carregamento
  - Haptic feedback conforme spec da Luna
  - Gesture shortcuts com equivalente em botão visível
```

### @mobile ↔ @cairo (UI)
```
Cairo entrega tokens agnósticos:
  - Spacing em pt/dp (não px) — funciona em iOS e Android
  - Shadows: objeto iOS (shadowColor/offset) + Android (elevation)
  - Motion: arrays Bezier para Reanimated + spring config
  - NativeWind config gerado a partir dos tokens Figma

Cruz aplica no mobile:
  - NativeWind 4 para estilos (mesmo Tailwind da web)
  - expo-symbols para ícones iOS nativos (SF Symbols)
  - expo-image para carregamento otimizado com blurhash
```

### @mobile ↔ @seo (SEO)
```
Nadia configura:
  - apple-app-site-association (Universal Links iOS)
  - assetlinks.json (App Links Android)
  - Firebase App Indexing (conteúdo do app no Google)

Cruz implementa no app:
  - Linking handlers para cada deep link
  - Validação de deep links antes de processar
  - Fallback web quando app não instalado
```

### @mobile ↔ @orion (Performance Marketing)
```
Orion configura:
  - AppsFlyer SDK (MMP) no app via Cruz
  - SKAdNetwork para iOS (conversion values)
  - Deep links de campanha via Branch

Cruz implementa:
  - SDK initialization no app startup
  - Eventos de conversão (install, first_order, purchase)
  - Deferred deep links (clicou no anúncio → instalou → abre tela certa)
```

### @mobile ↔ @security (Security)
```
Zara exige no mobile:
  - expo-secure-store para tokens (nunca AsyncStorage)
  - Certificate pinning em endpoints de pagamento
  - Jailbreak/root detection antes de operações financeiras
  - Deep link validation (previne URL injection)
  - Privacy Manifest iOS 17+ (declaração de coleta de dados)

Cruz implementa:
  - TokenStorage service com SecureStore
  - DeviceSecurity.checkDeviceSecurity() no startup
  - validateDeepLink() antes de processar qualquer URL
```

---

## Stack Completa

```yaml
Backend:
  Python 3.12+ | FastAPI | SQLAlchemy 2.x async
  PostgreSQL 16 + pgvector + PostGIS
  Redis 7 | Celery 5 | Ruff + mypy --strict
  Prometheus | Grafana

Frontend Web:
  Next.js 15 (App Router) | TypeScript 5.x strict
  TailwindCSS 4.x + shadcn/ui | TanStack Query v5
  React Hook Form + Zod | Framer Motion

Mobile:
  React Native 0.76+ (New Architecture)
  Expo SDK 52+ | expo-router 4.x
  TypeScript 5.x strict | NativeWind 4
  Reanimated 3 + Gesture Handler
  MMKV | WatermelonDB | TanStack Query v5
  expo-location + expo-task-manager (GPS background)
  expo-notifications (push + local)
  expo-secure-store (tokens seguros)

Monorepo:
  Turborepo | pnpm workspaces
  packages/shared | packages/api-client | packages/tokens

Mobile CI/CD:
  EAS Build + EAS Submit + EAS Update (OTA)
  Fastlane (screenshots, metadata)
  GitHub Actions (integração completa)

Design System:
  Figma + Tokens Studio → Style Dictionary
  CSS variables (web) + NativeWind config (mobile)
  Zeroheight (documentação)
  Chromatic (visual regression)

Infraestrutura:
  Docker Compose (local) | GitHub Actions (CI/CD)
  Railway → AWS ECS (escala)
  Sentry + Prometheus + Grafana + OpenTelemetry

IA/ML:
  Anthropic Claude (Haiku/Sonnet) | pgvector
  TF.js React Native + ONNX Runtime (on-device)
  MLflow + RAGAS (MLOps + eval)

Analytics Mobile:
  Firebase Analytics | PostHog | AppsFlyer (MMP)
  Sentry React Native | Flashlight (perf)

Marketing:
  Meta Ads + Google UAC + TikTok Ads + Apple Search Ads
  AppsFlyer (SKAdNetwork) | Branch (deep links)
  Metricool | RevenueCat
```

---

## Comandos disponíveis

| Comando | Para que |
|---------|----------|
| `/kickoff` | Novo projeto do zero |
| `/feature` | Feature completa do PRD ao código |
| `/design-sprint` | Discovery → Wireframe → UI → Handoff mobile+web |
| `/campaign` | Campanha Brand → Copy → Visual → Paid → Social |
| `/product-launch` | Lançamento coordenado de produto (web + mobile) |
| `/review` | Revisão multi-perspectiva de código |
| `/incident` | Protocolo P0 de resposta a incidente |
| `/growth-review` | Análise de métricas + plano de crescimento |
