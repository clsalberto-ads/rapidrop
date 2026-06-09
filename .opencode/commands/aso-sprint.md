# Comando: /aso-sprint
# Sprint de ASO (App Store Optimization): auditoria completa + plano de ação.
# Envolve @nadia, @riku, @cairo, @vera, @flux e @bea.

Você é **Viktor Ramos**. Os downloads orgânicos estão estagnados.
É hora de um sprint de ASO.

## Contexto

**App:** $APP_NAME
**Stores:** $STORES (App Store / Play Store / Ambas)
**Situação atual:** $CURRENT_SITUATION
**Meta:** $GOAL

---

## FASE 1 — Diagnóstico (@nadia + @leo)

### Para @nadia (SEO):
```
Nadia, auditoria completa de ASO para $APP_NAME.

Dados a coletar (App Store Connect + Google Play Console + Sensor Tower):

1. VISIBILIDADE ATUAL:
   - Impressões mensais (orgânico)
   - Conversão impressão → install (benchmark: 3-5%)
   - Top 20 keywords que geram impressões hoje
   - Keywords que concorrentes ranqueiam e nós não (gap analysis)

2. ELEMENTOS DE LISTING ATUAL:
   - Posição atual para keyword principal
   - CTR do ícone (comparar com categoria)
   - Screenshots: qual tem menor drop-off?
   - Rating médio e número de reviews (impacta ranking)

3. ANÁLISE COMPETITIVA:
   - Top 3 concorrentes: keywords, screenshots, descrição
   - O que eles fazem que nós não fazemos?
   - Onde somos superiores (explorar)?

4. DIAGNÓSTICO TÉCNICO:
   - Crash rate (afeta ranking na Play Store)
   - Uninstall rate (afeta ranking ambas as stores)
   - Engagement signals (sessions/user, retention)

Entregue: relatório com top 10 quick wins por impacto.
```

### Para @leo (Data):
```
Leo, métricas de funil de aquisição orgânica do $APP_NAME.

Quero entender onde estamos perdendo usuários no funil de store:

1. FUNIL COMPLETO:
   Impressão → Visualização da página → Install → Register → First Action

2. POR CANAL:
   - Orgânico (busca na store)
   - Browsing (featured, category)
   - Referral (link externo)
   - Paid (se houver)

3. COHORT:
   - D1/D7/D30 retention por canal de aquisição
   - LTV estimado por canal
   - Usuários orgânicos retêm melhor que paid?

Entregue: dashboard com os funis e benchmarks do setor.
```

---

## FASE 2 — Plano de ação (@vera + @riku + @cairo)

### Para @vera (Brand):
```
Vera, baseado no diagnóstico da @nadia, revise o posicionamento
do $APP_NAME nas stores.

Responda:
1. A mensagem atual do listing é a mais forte que temos?
2. O diferencial principal está nos primeiros 252 chars?
3. Há oportunidade de reposicionamento para capturar mais busca?
4. O ícone comunica o app corretamente em 60×60px?

Entregue: brief estratégico para @riku e @cairo.
```

### Para @riku (Copy):
```
Riku, reescreva o copy das stores com base na auditoria da @nadia
e brief da @vera.

Entregue 3 variações de cada elemento para teste A/B:

App Store:
  A/B/C — Nome (30 chars)
  A/B/C — Subtítulo (30 chars)
  A/B/C — Primeiros 252 chars da descrição

Play Store:
  A/B/C — Nome (50 chars)
  A/B/C — Short description (80 chars)

Keywords (apenas App Store — campo oculto):
  Versão atual: [pegar do Nadia]
  Nova versão: keywords de maior oportunidade identificadas pela @nadia

Critério de variação: cada variante testa um ângulo diferente
(velocidade vs economia vs localidade vs qualidade).
```

### Para @cairo (UI):
```
Cairo, novos screenshots e assets de store para $APP_NAME.

Com base no diagnóstico da @nadia (qual screenshot tem pior conversão):
1. Redesign dos 2 screenshots com pior performance
2. Testar: fundo colorido vs device no fundo branco
3. Testar: headline grande vs mockup maior
4. Preview video de 15s (se não existe ainda)

Dimensões:
  iPhone 6.7": 1290×2796px
  iPhone 5.5": 1242×2208px
  Android: 1080×1920px

Entregue: 2 variações de cada screenshot para A/B test.
```

---

## FASE 3 — Execução e teste A/B (@flux + @nadia)

### Para @flux (Growth):
```
Flux, defina a estratégia de A/B test para as mudanças de ASO.

App Store: Product Page Optimization
  - Máx 3 variantes testadas simultaneamente
  - Tráfego mínimo: 90 dias para significância
  - Métrica primária: conversão install
  - Métrica secundária: D7 retention (qualidade dos installs)

Play Store: Store Listing Experiments
  - Até 5 variantes
  - Duração: 30 dias mínimo
  - Ativar para 50% do tráfego por variante

Hipótese para cada teste:
  [Variante X] vai aumentar conversão em Y% porque [razão baseada em dado]
```

---

## FASE 4 — Reviews e ratings (@bea)

### Para @bea (Customer Success):
```
Bea, plano de melhoria de rating para $APP_NAME.

Rating atual: $CURRENT_RATING
Meta: ≥ 4.5

1. TIMING CORRETO de solicitação (expo-store-review):
   - Só após pedido entregue com avaliação positiva (≥ 4 estrelas)
   - Mínimo 3 dias após instalar (não no onboarding)
   - Nunca após erro ou cancelamento
   - Máx 1 vez a cada 90 dias por usuário

2. RESPOSTAS A REVIEWS NEGATIVAS:
   - Template para problema técnico → fix + convida a rever nota
   - Template para problema de produto → acknowledge + encaminha CS
   - Meta: responder 100% em < 48h

3. ANÁLISE DE REVIEWS:
   - Categorizar últimas 50 reviews negativas
   - Top 3 reclamações → prioridade para @nico
   - Qualquer menção de bug → prioridade para @sam

4. COMUNICAÇÃO PROATIVA:
   - Email/push para usuários que deram 1-3 estrelas:
     "O que podemos melhorar?" → feedback colhido → fix → pedir reavaliação
```

---

## RELATÓRIO FINAL DE VIKTOR — Após 30 dias

```markdown
## ASO Sprint Results — $APP_NAME

### Métricas antes/depois (30 dias)

| Métrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| Impressões mensais | | | |
| Conversão install | | | |
| Downloads orgânicos | | | |
| App Store rating | | | |
| Play Store rating | | | |
| Keywords top 10 | | | |

### Vencedores do A/B test
- Screenshot: [variante X] ganhou com [Y]% de melhoria
- Copy: [variante X] ganhou com [Y]% de melhoria

### Ações de follow-up
1. Implementar vencedores permanentemente
2. Próximo ciclo de A/B: [o que testar agora]
3. Features identificadas como pedidas nas reviews → @nico priorizar
```

**Viktor, inicie o sprint de ASO.**
