# Modelos, Ferramentas e Estratégias de IA — CacauFito

## Modelos de IA

| Modelo | Uso |
|---|---|
| **Claude Sonnet 5** (`claude-sonnet-5`) | Agente principal de desenvolvimento assistido por IA — especificação (SDD), implementação, testes, revisão de código, documentação, ao longo de todo o projeto |
| **EfficientNet-B0** (pré-treinada em ImageNet) | Modelo de visão computacional do próprio produto — classifica a folha de cacau (não é uma "ferramenta de desenvolvimento", é o modelo entregue) |

## Ferramentas (IDE, CLI agent, harness, spec, testes)

| Categoria | Ferramenta | Uso |
|---|---|---|
| Harness / CLI agent | **Claude Code** | Ambiente de execução do agente — edição de arquivos, execução de comandos, navegador headless, controle de permissões |
| Especificação (SDD) | **OpenSpec** | Especificação delta-driven da maioria das capabilities (modelo, histórico, incerteza, feedback, auth, dashboard, docker, docs de API) |
| Especificação (SDD) | **GitHub Spec Kit** | Especificação user-story-driven da feature de estatísticas (`GET /stats`), usada para comparar abordagens (ver `docs/comparacao_sdd_tools.md`) |
| Testes | **pytest** + `fastapi.testclient.TestClient` | Suíte automatizada cobrindo histórico, incerteza, estatísticas |
| Testes de frontend | **Playwright** (Chrome headless) | Verificação real em navegador — encontrou um bug real de especificidade CSS (`[hidden]` sobrescrito por `.btn`) que passaria despercebido numa revisão só de código |
| Treino do modelo | **Kaggle Notebooks** (GPU gratuita) + **Optuna** | Treino do EfficientNet-B0 e busca de hiperparâmetros (`learning_rate`, `weight_decay`) |
| Controle de versão | **Git** + **GitHub** (`gh` CLI) | Histórico de commits real, Pull Requests |

## Estratégias de prompt e de condução do agente

- **Especificar antes de implementar**: toda funcionalidade nova passou por `proposal.md` → `specs/<capability>/spec.md` (requisitos + cenários Given/When/Then, com pelo menos 1 caso de borda) → `design.md` (decisões técnicas, alternativas rejeitadas) → `tasks.md` (plano de tarefas revisável), antes de qualquer código ser escrito.
- **Perguntas de esclarecimento em vez de suposição silenciosa**: sempre que uma decisão de escopo era ambígua (ex.: qual funcionalidade especificar a seguir, qual granularidade de rótulo usar), o agente parou e perguntou em vez de assumir — documentado nos próprios artefatos de design (seção "Assumptions"/"Decisions").
- **Verificação real, não só leitura de código**: para mudanças de frontend, o agente rodou a aplicação de verdade num navegador headless antes de considerar a tarefa concluída — foi assim que o bug do `[hidden]`/CSS foi encontrado (ver `docs/relatorio_final.md`).
- **Checkpoint humano antes de expor endpoint**: definido e simulado explicitamente em `docs/checkpoint_humano.md` — a aprovação final de que uma mudança pode ir para `main` continua sendo humana, mesmo com testes automatizados passando.
- **Guardrails de permissão**: regras de bloqueio configuradas no harness (não apenas descritas) para impedir leitura/edição de segredos (`.env`) e comandos destrutivos (`rm -rf`, `git push --force`, `git reset --hard`) — evidência de bloqueio real em `docs/guardrail_evidence.md`.
