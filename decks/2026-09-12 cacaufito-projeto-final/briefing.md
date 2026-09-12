# Briefing: CacauFito — Projeto Final (Desenvolvimento de Software com IA)

**Fonte:** decks/2026-09-12 cacaufito-projeto-final/references/ (docs do repositório CacauFito) — texto
**Data da extração:** 2026-09-12

## Essência em uma frase

CacauFito é um classificador de folhas de cacau por visão computacional (sadia / CSSVD / antracnose), construído inteiramente com Spec-Driven Development e um agente de IA (Claude Code) sob harness e guardrails reais — o produto final da disciplina, mas o que se avalia é o processo.

## Conceitos-chave (candidatos a slide)

1. **O problema** — cacauicultores sem forma acessível de identificar pragas/doenças foliares em campo; duas doenças graves (CSSVD, antracnose) se espalham se não identificadas cedo — sugestão visual: metáfora animada (folha doente vs. sadia, lupa/diagnóstico)
2. **A tarefa de ML** — classificação de imagem supervisionada, 3 classes mutuamente exclusivas, a partir de foto de celular em campo — sugestão visual: d3-fluxo (foto → modelo → diagnóstico)
3. **Pipeline de dados e treino** — dataset Amini (Kaggle, CC BY 4.0, 5.529 imagens), split 70/15/15, EfficientNet-B0 pré-treinada com backbone congelado, hiperparâmetros ajustados via Optuna — sugestão visual: d3-fluxo (dataset → treino+Optuna → avaliação → artefato → API → app)
4. **Resultados do modelo** — acurácia de teste 77,8% sem Optuna → 78,1% com Optuna; ganhos por classe (recall cssvd +1,8pp, precisão healthy +1,7pp) — sugestão visual: card_metricas / gráfico de barras antes-depois
5. **SDD com duas ferramentas** — OpenSpec (delta-driven: proposal → specs → design → tasks) usado no modelo, histórico, incerteza, feedback, auth, dashboard, docker, docs de API; GitHub Spec Kit (user-story-driven: spec → plan → research → data-model → contracts → tasks) usado na feature de estatísticas — sugestão visual: comparacao (tabela + dois fluxos lado a lado)
6. **Harness e autonomia** — autonomia supervisionada com checkpoints humanos obrigatórios antes de expor endpoint; guardrail real configurado (`.claude/settings.json`, `permissions.deny`) bloqueando leitura/edição de `.env` e comandos destrutivos (`rm -rf`, `git push --force`) — testado ao vivo nesta sessão, bloqueio real capturado — sugestão visual: d3-fluxo (ação proposta → guardrail → bloqueado/permitido) ou timeline dos episódios reais
7. **Arquitetura** — API FastAPI (predict/history/stats) + frontend estático + storage SQLite; contratos claros entre `model.py` (inferência pura), `history.py` (storage), `main.py` (HTTP); 2 ADRs documentados (EfficientNet-B0 transfer learning; SQLite para histórico) — sugestão visual: diagrama C4 de contêineres + sequência de uma predição
8. **Demonstração funcional** — upload de folha → diagnóstico com confiança → sinalização de "resultado incerto" (baixa confiança OU disputa acirrada entre classes) → histórico paginado → estatísticas agregadas — sugestão visual: sequência de telas/fluxo de uso
9. **Aprendizado real** — bug de especificidade CSS (`[hidden]` sobrescrito por `.btn { display: inline-flex }`) só encontrado testando de verdade em navegador headless (Playwright), não pela leitura do código — sugestão visual: metáfora animada (bug escondido revelado só ao testar)
10. **10 requisitos funcionais** — 6 já implementados (classificação, upload, incerteza, histórico, stats, Optuna) + 6 especificados aguardando implementação (feedback do usuário, exportação CSV, autenticação multi-usuário, dashboard com série temporal, deploy Docker, docs de API interativa) — sugestão visual: checklist/progresso (6/10 → 10/10)
11. **Próximos passos** — implementar as 6 specs restantes, retreinar com feedback real de usuários, expandir dataset para região do Sul da Bahia — sugestão visual: timeline

## Dados e números

- Dataset: 5.529 imagens rotuladas (Amini Cocoa Contamination Dataset, CC BY 4.0), split 70/15/15
- Acurácia de teste: 77,8% → 78,1% (com Optuna, +0,3pp), melhor acurácia de validação 79,9% → 80,2%
- F1 por classe (com Optuna): healthy 0,768, cssvd 0,779, anthracnose 0,799
- Ganhos específicos do Optuna: recall cssvd +1,8pp, precisão healthy +1,7pp
- Optuna: 10 trials (5 completos + 5 podados), `lr=0.00142`, `weight_decay=0.000126`, ~1h40 de GPU adicional
- 10 requisitos funcionais planejados; 6 implementados, 6 especificados
- 2 ferramentas de SDD comparadas (OpenSpec vs. Spec Kit)
- Guardrail: 2 regras testadas ao vivo com bloqueio real confirmado (Read(.env), Bash rm -rf)

## Trechos de código/config emblemáticos

- Regra de incerteza (`is_uncertain = confidence < 0.6 OR (top - segundo) < 0.1`)
- `.claude/settings.json` — `permissions.deny` com as 5 regras de guardrail
- Erro real capturado: `Permission to use Bash with command rm -rf "..." has been denied.`

## Narrativa sugerida

Problema (cacauicultores sem diagnóstico acessível) → tarefa de ML e dataset → como o processo foi conduzido (SDD com 2 ferramentas, harness com autonomia supervisionada e guardrail real, checkpoint humano) → arquitetura (ADRs + diagrama) → resultados do modelo (com Optuna) → demo funcional → aprendizados reais (o bug do CSS) → onde está o projeto hoje (6/10 requisitos) e próximos passos.

## Lacunas

- Nenhuma captura de tela real da aplicação rodando foi extraída das referências (apenas descrições em texto) — o slide de demo pode usar uma reconstrução visual/mockup da interface em vez de screenshot real, a menos que o usuário forneça prints.
- Vídeo de pitch da disciplina de Aprendizagem Profunda existe no repositório irmão (`cacau_fito_DL`), mas não foi copiado para as referências — mencionar apenas como contexto, não incorporar.
