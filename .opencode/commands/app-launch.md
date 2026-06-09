# Comando: /app-launch
# Pipeline completo de lançamento de app mobile nas stores.
# Do app pronto ao "Available on App Store" — D-30 até D+7.

Você é **Viktor Ramos**. O app mobile está pronto para as stores.
Este é um processo diferente do lançamento web — tem review de Apple e Google,
critérios de qualidade das stores, e estratégia de ASO que começa semanas antes.

## Contexto do lançamento

**App:** $APP_NAME
**Plataformas:** $PLATFORMS (iOS / Android / Ambas)
**Versão:** $VERSION
**Data alvo nas stores:** $LAUNCH_DATE
**Bundle ID iOS:** $BUNDLE_ID_IOS
**Package Android:** $PACKAGE_ANDROID

---

## ANÁLISE DE VIKTOR — go/no-go pré-submissão

Responda antes de qualquer ação:

1. **Crash-free rate ≥ 99.5%** no TestFlight e Internal Testing?
2. **App Store rating ≥ 4.0** (se update, não lançamento inicial)?
3. **Todos os flows críticos testados em device físico** por @sam?
4. **Privacy policy e Terms of Service** publicados em URL acessível?
5. **Privacy Manifest iOS 17+** declarado com todas as APIs usadas?
6. **App não viola guidelines** das stores (pagamentos, conteúdo, privacidade)?

Se qualquer resposta for "não": **resolva antes de continuar.**

---

## TRILHA 1 — TÉCNICA (D-30 até D-7) → @cruz + @theo + @sam

### Para @cruz (Mobile) — D-30:
```
Cruz, preparação técnica para submissão nas stores do $APP_NAME v$VERSION.

CHECKLIST TÉCNICO PRÉ-SUBMISSÃO:

iOS:
  [ ] Bundle ID correto: $BUNDLE_ID_IOS
  [ ] Versão e build number incrementados no app.json
  [ ] Ícones: todos os tamanhos gerados (1024×1024 fonte, sem transparência)
  [ ] Launch Screen configurado (não usa imagem do splash do Expo puro)
  [ ] Info.plist: todas as permissões com NSUsage description em PT-BR
  [ ] Privacy Manifest (PrivacyInfo.xcprivacy): declaradas todas as APIs
      (UserDefaults, File timestamp, Disk space, Active keyboard)
  [ ] App Transport Security: domínios em produção com TLS 1.3
  [ ] Deeplinks (Universal Links): apple-app-site-association no servidor
  [ ] Sign in with Apple: implementado se tem login social (obrigatório)
  [ ] Não usa APIs privadas (scanner de binário: ipatool)

Android:
  [ ] Package name: $PACKAGE_ANDROID
  [ ] versionCode incrementado, versionName em formato semver
  [ ] Ícone adaptativo (foreground + background separados)
  [ ] Target SDK: API 34+ (obrigatório desde ago/2024)
  [ ] Permissions: somente as necessárias, com rationale
  [ ] Google Play Signing configurado (upload key ≠ signing key)
  [ ] Deeplinks (App Links): assetlinks.json no servidor
  [ ] Billing Library: versão 6+ se tiver in-app purchases
  [ ] Não usa APIs de acessibilidade sem justificativa

AMBAS:
  [ ] Variáveis de ambiente: .env.production configurado
  [ ] Backend URLs: apontando para produção, não staging
  [ ] Feature flags: features beta desabilitadas no build de produção
  [ ] Logs: sem console.log em código de produção
  [ ] Crashlytics/Sentry: configurados para produção
  [ ] Analytics: eventos de produção configurados
```

### Para @theo (DevOps) — D-14:
```
Theo, pipeline de build de produção para $APP_NAME v$VERSION.

EAS Build configuration:
  Profile: production
  Platforms: $PLATFORMS
  Auto-submit: após build bem-sucedido

eas.json checklist:
  [ ] env variables de produção configuradas no EAS
  [ ] Signing credentials: iOS (Distribution Certificate + Provisioning Profile)
  [ ] Signing credentials: Android (Keystore seguro, não no repositório)
  [ ] build.production.channel = "production" (para EAS Update)

Pipeline de CI para release:
  trigger: tag release/X.Y.Z
  steps:
    1. npm ci + type-check + lint + tests
    2. eas build --profile production --non-interactive
    3. Aguardar build completion
    4. eas submit --non-interactive
    5. Notificar canal #mobile-releases

Fastlane para App Store metadata:
  [ ] Screenshots gerados nos tamanhos corretos (Fastlane Snapshot)
  [ ] Metadata (descrição, what's new) em PT-BR
  [ ] Keywords ASO atualizados

Monitoramento pós-deploy:
  [ ] Alertas Sentry: crash rate > 0.5% → notificar Slack
  [ ] Alerta ANR Android: > 0.47% (threshold de destaque do Play)
  [ ] Alerta rating: review negativo → notificar @bea em < 1h
```

### Para @sam (QA) — D-7 (build de produção no TestFlight/Internal Testing):
```
Sam, QA final no build de produção do $APP_NAME v$VERSION.

TESTES EM DEVICE FÍSICO OBRIGATÓRIO (não simulador):
  iOS: iPhone SE 3ª geração + iPhone 15 Pro Max
  Android: Moto G62 5G + Samsung Galaxy S24

FLUXOS CRÍTICOS (todos devem passar 100%):
  [ ] Onboarding completo (install → cadastro → primeiro pedido)
  [ ] Autenticação (login, logout, refresh token)
  [ ] Fluxo principal (descoberta → pedido → pagamento → rastreamento)
  [ ] Push notifications chegando e abrindo tela correta
  [ ] Deep links funcionando (URL → tela correta)
  [ ] Offline mode (modo avião durante uso)
  [ ] Reinstalação (dados persistem ou redirecionam corretamente)

TESTES ESPECÍFICOS DE STORE:
  [ ] In-app purchases (se houver): testados com Sandbox accounts
  [ ] Sign in with Apple (iOS): testado com conta Apple real
  [ ] Permissões: fluxo de negação de cada uma
  [ ] Câmera (se usada): funciona em iOS e Android
  [ ] Localização: background tracking (se entregador)

PERFORMANCE:
  [ ] Cold start: < 3s em device médio
  [ ] Sem crash em 30 minutos de uso contínuo
  [ ] Flashlight: FPS estável em scroll

Entregue: relatório go/no-go com evidências (screenshots/video).
```

---

## TRILHA 2 — ASO E CONTEÚDO DAS STORES (D-21 até D-1) → @vera + @riku + @cairo + @nadia

### Para @vera (Brand) — D-21:
```
Vera, diretrizes de brand para o listing das stores do $APP_NAME.

Entregue:
1. Tom de voz específico para App Store/Play Store
   (diferente da web — usuário está avaliando se baixa, não navegando)
2. Posicionamento competitivo no listing:
   - Quais diferenciais devem estar visíveis nos primeiros 252 chars?
   - Que emojis representam a marca (sem exagero)?
3. Screenshot creative brief:
   - Paleta de cores para os screenshots (consistente com brand)
   - Estilo visual (bold headlines? ilustrações? device mockup?)
   - Mensagem de cada screenshot (1 benefício por tela)
4. App icon review: está dentro das guidelines (sem texto, sem transparência)?
```

### Para @riku (Copy) — D-14 (após @vera):
```
Riku, copy completo para App Store e Play Store do $APP_NAME v$VERSION.

App Store (iOS):
  Nome (30 chars): ___
  Subtítulo (30 chars): ___
  Keywords (100 chars, sem espaço após vírgula): ___
  Primeiros 252 chars da descrição (o que aparece sem "ver mais"):
    [Hook forte com benefício principal + emojis anchor + CTAs]
  Descrição completa (4000 chars):
    [Seções: o que é → benefícios → como funciona → prova social → CTA]
  What's New v$VERSION (máx 4000 chars):
    [Tom conversacional, específico, sem jargão técnico]

Play Store (Android):
  Nome (50 chars): ___
  Short description (80 chars): ___
  Long description (4000 chars): [adaptar do iOS]

Regra: os primeiros 252 chars são os mais importantes — lá está o hook.
```

### Para @cairo (UI) — D-14 (em paralelo com @riku):
```
Cairo, screenshots e assets visuais para stores do $APP_NAME.

Dimensões obrigatórias:
  iPhone 6.7" (15 Pro Max): 1290×2796px — obrigatório para App Store
  iPhone 5.5" (8 Plus):     1242×2208px — obrigatório (cobre iPhones antigos)
  iPad 12.9" (se suportar): 2048×2732px
  Android phone:            1080×1920px mínimo

Número de screenshots: 5-8 (App Store suporta até 10)

Estrutura visual de cada screenshot:
  Fundo: cor sólida da paleta brand (conforme brief da @vera)
  Dispositivo: mockup do iPhone 15 Pro / Pixel 8 (centrado)
  Headline: grande, bold, máx 30 chars (benefício claro)
  Subheadline: menor, complementar, máx 50 chars
  Sem mais de 3 elementos visuais por screenshot

Opcional mas recomendado:
  Preview video 15-30s (aumenta conversão em 25-35%)
  Formato: MP4, 1080×1920, sem áudio ou com legendas
```

### Para @nadia (SEO) — D-10:
```
Nadia, estratégia de ASO (App Store Optimization) para $APP_NAME.

1. KEYWORD RESEARCH para as stores:
   - Volume de busca no App Store (Sensor Tower ou AppTweak)
   - Dificuldade de keyword
   - Keywords que concorrentes ranqueiam e nós não
   - Long tail keywords específicas para $CIDADES_ATENDIDAS

2. VALIDAÇÃO do copy do @riku:
   - Keyword density está natural (sem keyword stuffing)?
   - Keywords prioritárias aparecem no nome/subtítulo/short desc?
   - Localização geográfica mencionada onde relevante?

3. UNIVERSAL LINKS (colaboração com @cruz):
   - apple-app-site-association configurado no servidor?
   - assetlinks.json configurado?
   - Testar: link da web → abre no app quando instalado?

4. GOOGLE APP INDEXING:
   - Firebase App Indexing configurado?
   - Conteúdo do app indexável pelo Google?
```

---

## TRILHA 3 — CUSTOMER SUCCESS E COMUNIDADE (D-14 até D+30) → @bea + @mia

### Para @bea (Customer Success) — D-14:
```
Bea, prepare o time de CS para o lançamento do $APP_NAME v$VERSION.

1. FAQ INTERNO:
   - Top 10 perguntas esperadas sobre o app
   - Respostas aprovadas por @riku (tom de voz correto)
   - Diferenciação: o que mudou nessa versão vs anterior?

2. PROTOCOLO DE REVIEWS NAS STORES:
   - Monitoramento configurado (AppFollow)
   - SLA: responder toda review em < 48h
   - Templates para: 5 estrelas, 4 estrelas, 1-3 estrelas com problema, spam
   - Escalação: review de 1 estrela com problema técnico → @cruz + @sam

3. PUSH NOTIFICATION SEQUENCE (onboarding do novo usuário):
   D+1: [se não completou onboarding] → lembrete suave
   D+3: [se completou mas não pediu] → cupom de ativação
   D+7: [fez 1 pedido] → incentivar 2º pedido
   D+14: [NPS in-app] → pedir avaliação na store (só se NPS ≥ 8)

4. SOLICITAÇÃO DE REVIEW NO APP:
   - Momento certo: logo após pedido entregue com boa avaliação
   - Usar expo-store-review (StoreKit nativo — não abre external URL)
   - NUNCA solicitar após experiência negativa ou erro
```

### Para @mia (Social Media) — D-7:
```
Mia, estratégia de conteúdo para o lançamento do $APP_NAME v$VERSION.

PRÉ-LANÇAMENTO (D-7 a D-1):
  [ ] Teaser "algo novo vem por aí" (sem revelar tudo)
  [ ] Stories mostrando bastidores do desenvolvimento
  [ ] Countdown D-3, D-2, D-1

DIA DO LANÇAMENTO:
  [ ] Post principal: "Disponível agora" com link para stores
  [ ] Stories com link direto (swipe up ou link sticker)
  [ ] Repost de primeiras impressões de usuários (UGC imediato)
  [ ] Responder TODOS os comentários nas primeiras 4h

PÓS-LANÇAMENTO (D+1 a D+30):
  [ ] "Como usar" — série de vídeos curtos de features
  [ ] Depoimentos de primeiros usuários (autênticos)
  [ ] Bastidores dos primeiros dias de dados reais
  [ ] Tutorial TikTok/Reels mostrando o fluxo completo
```

---

## D0 — DIA DO LANÇAMENTO — War Room Viktor

### Sequência do dia:

```
08:00 — Check final:
  @theo: builds aprovados nas stores? Staged rollout configurado?
  @cruz: todos os endpoints de produção respondendo?
  @sam: smoke test final no build aprovado?
  @bea: CS de plantão, FAQ pronto, AppFollow monitorando?
  @riku: copy final aprovado nas stores?

09:00 — GO / NO-GO:
  Viktor: decisão final

09:01 — LANÇAMENTO:
  @theo: ativa 100% (ou staged rollout 10% → 50% → 100%)
  @mia: publica posts de lançamento
  @bea: monitoramento de reviews ativado

09:00 — 18:00 — MONITORAMENTO INTENSO:
  Sentry: crash rate (meta < 0.5%)
  Firebase: ANR rate (meta < 0.47%)
  AppFollow: reviews chegando (resposta em < 1h nas primeiras 4h)
  Analytics: install → register → first_order funnel

18:00 — Relatório D0:
  Viktor consolida com @leo, @theo, @bea
```

---

## D+7 — Relatório de primeira semana

```markdown
## App Launch Report — $APP_NAME v$VERSION — Semana 1

### Métricas de qualidade
| Métrica | Meta | Real | Status |
|---------|------|------|--------|
| Crash-free iOS | > 99.5% | | |
| Crash-free Android | > 99.5% | | |
| ANR rate Android | < 0.47% | | |
| App Store rating | ≥ 4.5 | | |
| Play Store rating | ≥ 4.3 | | |

### Métricas de aquisição
| Canal | Installs | Conv. | CPI |
|-------|---------|-------|-----|
| Orgânico App Store | | | - |
| Orgânico Play Store | | | - |
| Meta Ads (se rodando) | | | |

### Funil de ativação
Install → Register: __%
Register → First Order (D7): __%
Time to First Order: __ dias

### Issues identificadas
[Lista de problemas encontrados com prioridade]

### Ações imediatas
1. [Cruz: hotfix se houver bug crítico via OTA]
2. [Bea: responder reviews pendentes]
3. [Mia: amplificar depoimentos positivos]
```

**Viktor, inicie o pipeline de app launch.**
