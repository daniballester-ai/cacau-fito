# CacauFito

Prova de conceito de visão computacional para classificar a condição fitossanitária de folhas de cacau — **sadia**, **CSSVD** (vírus do inchaço do broto) ou **antracnose** — a partir de uma foto.

Projeto duplo: entrega prática das disciplinas **Aprendizado Profundo** (treino do modelo) e **Tópicos Avançados em Engenharia de Software 2** (Spec-Driven Development), no PPGTI/UFRN, e exploração técnica inicial para o projeto CacauClima.

## O que tem aqui

- **Modelo**: EfficientNet-B0 (transfer learning), treinado no Kaggle sobre o [Amini Cocoa Contamination Dataset](https://www.kaggle.com/datasets/ohagwucollinspatrick/amini-cocoa-contamination-dataset) (CC BY 4.0) — 77,8% de acurácia no teste. Ver [`notebooks/train_kaggle.ipynb`](notebooks/train_kaggle.ipynb).
- **API de inferência**: FastAPI (`src/inference_service/`) — `POST /predict`, `GET /history`, `GET /stats`, `GET /health`.
- **Frontend**: upload de imagem + histórico de predições, servido pela própria API (`frontend/`).
- **Specs**: todo o projeto foi especificado com SDD — [OpenSpec](openspec/) para o modelo, histórico de predições e sinalização de resultado incerto; [GitHub Spec Kit](specs/) para a feature de estatísticas (comparação em [`docs/comparacao_sdd_tools.md`](docs/comparacao_sdd_tools.md)).
- **Docs**: [ML Canvas](docs/ml_canvas.md), [escopo e justificativa SDD](docs/escopo.md), [limitações e próximos passos](docs/limitations_and_next_steps.md).

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
notebooks/                notebook de treino (Kaggle)
data/amini/                manifesto do dataset (imagens não versionadas, 9.6GB)
openspec/, specs/         especificações (OpenSpec e Spec Kit)
docs/                      canvas, escopo, limitações, comparação de ferramentas
tests/                    suíte pytest
```
