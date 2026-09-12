# Diagrama de Arquitetura — CacauFito

## Diagrama de contêineres (nível C4 — Container)

```mermaid
C4Container
    title CacauFito — Diagrama de Contêineres

    Person(user, "Usuário", "Produtor ou pesquisador que quer diagnosticar uma folha de cacau")

    System_Boundary(cacaufito, "CacauFito") {
        Container(frontend, "Frontend", "HTML/CSS/JavaScript", "Upload de imagem, histórico, dashboard — servido pela própria API")
        Container(api, "Serviço de Inferência", "Python, FastAPI", "Expõe /predict, /history, /stats, /auth; carrega o modelo treinado")
        ContainerDb(db, "Histórico", "SQLite", "Predições, feedback e sessões de usuário")
        Container(model, "Artefato do Modelo", "PyTorch (.pt)", "Pesos treinados do EfficientNet-B0 + mapeamento de classes")
    }

    System_Ext(kaggle, "Kaggle Notebook", "Treino do modelo (GPU), fora do runtime da aplicação")

    Rel(user, frontend, "Usa", "HTTPS")
    Rel(frontend, api, "Chama", "JSON/multipart sobre HTTP")
    Rel(api, db, "Lê/grava")
    Rel(api, model, "Carrega no startup")
    Rel(kaggle, model, "Produz", "Download manual do artefato treinado")
```

## Pipeline de dados e treino

```mermaid
flowchart LR
    A[Dataset Amini<br/>Kaggle, CC BY 4.0] --> B[Split treino/val/teste<br/>build_manifest.py]
    B --> C[Treino + Optuna<br/>notebook Kaggle, GPU]
    C --> D[Artefato do modelo<br/>models/*.pt + label_mapping.json]
    D --> E[Serviço de Inferência<br/>FastAPI]
    E --> F[Frontend<br/>upload + histórico + dashboard]
```

## Fluxo de uma predição (sequência)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant A as API (FastAPI)
    participant M as Modelo (PyTorch)
    participant H as Histórico (SQLite)

    U->>F: Envia foto da folha
    F->>A: POST /predict (multipart)
    A->>M: classifier.predict(imagem)
    M-->>A: rótulo, confiança, probabilidades
    A->>A: compute_uncertainty(probabilidades)
    A->>H: record_prediction() (best-effort)
    A-->>F: rótulo + confiança + is_uncertain
    F-->>U: Exibe resultado (com badge de incerteza, se aplicável)
```

## Notas de arquitetura

- **Contratos claros entre módulos**: `model.py` (inferência pura) não conhece `history.py` (storage); `main.py` (camada HTTP) integra os dois, mas cada um pode ser testado isoladamente (ver `tests/test_uncertainty.py`, `tests/test_history.py`).
- **Baixo acoplamento com o treino**: o treino roda inteiramente fora do runtime da aplicação (notebook Kaggle); o serviço de inferência só depende do artefato final (`models/*.pt`), nunca do pipeline de treino em si.
- **Registro best-effort**: uma falha ao gravar histórico nunca derruba `/predict` (ver `tests/test_predict_history_integration.py`) — decisão registrada em `openspec/changes/archive/2026-09-04-add-prediction-history/design.md`.
