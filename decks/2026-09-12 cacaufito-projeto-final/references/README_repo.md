# CacauFito

Prova de conceito de visão computacional que classifica a condição fitossanitária de uma folha de cacau — **sadia**, **CSSVD** (vírus do inchaço do broto) ou **antracnose** — a partir de uma foto, com uma API de inferência e um frontend de upload por trás.

Repositório de entrega das disciplinas **Tópicos Avançados em Engenharia de Software 2** e **Desenvolvimento de Software com IA** (PPGTI/UFRN), com foco em **Spec-Driven Development (SDD)**: cada funcionalidade nova foi especificada antes de implementada, com aprovação humana em checkpoints definidos.

> O treino do modelo (notebook, canvas de ML, vídeo de pitch) é a entrega da disciplina **Aprendizagem Profunda**, mantida no repositório irmão [cacau_fito_DL](https://github.com/daniballester-ai/cacau_fito_DL) — este repositório compartilha o mesmo código, mas com foco em engenharia de software.

## O que tem aqui

- **Modelo**: EfficientNet-B0 (transfer learning), treinado sobre o [Amini Cocoa Contamination Dataset](https://www.kaggle.com/datasets/ohagwucollinspatrick/amini-cocoa-contamination-dataset) (CC BY 4.0), 78,1% de acurácia no teste, com hiperparâmetros (`lr`, `weight_decay`) escolhidos por busca com Optuna. Notebook e detalhes de treino no repositório [cacau_fito_DL](https://github.com/daniballester-ai/cacau_fito_DL).
- **API de inferência**: FastAPI (`src/inference_service/`) — `POST /predict`, `GET /history`, `GET /stats`, `GET /health`.
- **Frontend**: upload de imagem + histórico de predições, servido pela própria API (`frontend/`).
- **Specs**: todo o projeto foi especificado com SDD — [OpenSpec](openspec/) para o modelo, histórico de predições e sinalização de resultado incerto; [GitHub Spec Kit](specs/) para a feature de estatísticas (comparação em [`docs/comparacao_sdd_tools.md`](docs/comparacao_sdd_tools.md)).
- **Docs**: [ML Canvas](docs/ml_canvas.md), [escopo e justificativa SDD](docs/escopo.md), [limitações e próximos passos](docs/limitations_and_next_steps.md), [checkpoint humano](docs/checkpoint_humano.md), [relatório final](docs/relatorio_final.md).
- **Arquitetura e processo assistido por IA**: [diagrama de arquitetura](docs/architecture-diagram.md), [ADRs](docs/adr/), [evidência de guardrail real](docs/guardrail_evidence.md), [log de sessão do agente](docs/agent_session_log.md), [modelos/ferramentas/estratégias de IA](docs/ferramentas_ia.md).

## Checkpoint humano (SDD)

Nenhum endpoint novo entra em produção só porque os testes automatizados passaram. Antes de expor um novo endpoint HTTP publicamente (merge para `main`), um humano do grupo revisa o diff gerado pelo agente e decide explicitamente: aprovar como está / editar / rejeitar e voltar à especificação. Detalhes em [`docs/checkpoint_humano.md`](docs/checkpoint_humano.md).

## Requisitos funcionais cobertos por spec + testes

| Funcionalidade | Spec | Testes |
|---|---|---|
| Classificação da folha (modelo + endpoint `/predict`) | [`openspec/specs/leaf-disease-classifier`](openspec/specs/leaf-disease-classifier/), [`leaf-inference-service`](openspec/specs/leaf-inference-service/) | — |
| Upload no frontend | [`openspec/specs/leaf-upload-frontend`](openspec/specs/leaf-upload-frontend/) | — |
| Sinalização de resultado incerto (`is_uncertain`) | mudança arquivada em `openspec/changes/archive/` | `tests/test_uncertainty.py` |
| Histórico de predições (paginado, com retenção) | [`openspec/specs/prediction-history`](openspec/specs/prediction-history/) | `tests/test_history*.py` |
| Estatísticas agregadas (`GET /stats`) | [`specs/001-prediction-stats`](specs/001-prediction-stats/) (Spec Kit) | `tests/test_stats*.py` |
| Otimização de hiperparâmetros do treino (Optuna) | mudança arquivada em [`openspec/changes/archive/2026-09-11-add-optuna-tuning-notebook/`](openspec/changes/archive/2026-09-11-add-optuna-tuning-notebook/) | verificação manual no notebook (ver repo DL) |

**Especificados, implementação em andamento** (completam os 10 requisitos funcionais do projeto final):

| Funcionalidade | Spec |
|---|---|
| Feedback do usuário sobre o diagnóstico | [`openspec/changes/add-diagnosis-feedback`](openspec/changes/add-diagnosis-feedback/) |
| Exportação do histórico em CSV | [`openspec/changes/add-history-csv-export`](openspec/changes/add-history-csv-export/) |
| Autenticação de usuário (multi-usuário) | [`openspec/changes/add-user-authentication`](openspec/changes/add-user-authentication/) |
| Dashboard de estatísticas (série temporal) | [`openspec/changes/add-stats-dashboard`](openspec/changes/add-stats-dashboard/) |
| Deploy containerizado (Docker) | [`openspec/changes/add-docker-deployment`](openspec/changes/add-docker-deployment/) |
| Documentação interativa de API | [`openspec/changes/add-interactive-api-docs`](openspec/changes/add-interactive-api-docs/) |

## Como rodar

```bash
python -m pip install fastapi "uvicorn[standard]" python-multipart torch torchvision pillow
python -m uvicorn src.inference_service.main:app --reload
```

Abra `http://127.0.0.1:8000` no navegador. Imagens de exemplo em [`samples/`](samples/).

## Testes

```bash
python -m pip install pytest
python -m pytest tests/ -v
```

## Estrutura

```text
src/inference_service/   API (predict, history, stats)
frontend/                 upload + histórico
models/                   modelo treinado + mapeamento de classes
notebooks/                notebooks de treino (detalhados no repo cacau_fito_DL)
data/amini/                manifesto do dataset (imagens não versionadas, 9.6GB)
openspec/, specs/         especificações (OpenSpec e Spec Kit)
docs/                      canvas, escopo, limitações, comparação de ferramentas, relatório final
tests/                    suíte pytest
```

## Autoria

Danielle Magalhães Ballester ([danielleballester@gmail.com](mailto:danielleballester@gmail.com)) e Jales Anderson de Assis Monteiro ([jalesmonteiro@hotmail.com](mailto:jalesmonteiro@hotmail.com)), trabalho de PPGTI/UFRN.
