## Context

`notebooks/train_kaggle.ipynb` is a linear, cell-by-cell Kaggle notebook (see proposal.md - Why) meant to be run top-to-bottom via "Save & Run All". It currently trains EfficientNet-B0 once with fixed hyperparameters (`lr=1e-3`, `BATCH_SIZE=32`, `StepLR(step_size=5, gamma=0.5)`, 15 epochs) after building `train_loader`/`val_loader`/`test_loader`. Kaggle sessions have a wall-clock budget (~55 min full run today), so any search step must stay cheap.

## Goals / Non-Goals

**Goals:**
- Add an Optuna study that searches learning rate (and optionally batch size / weight decay) using short training runs scored on validation accuracy.
- Feed the best trial's hyperparameters into the existing full training loop.
- Keep the added search bounded in time so the notebook still fits Kaggle's session limits.

**Non-Goals:**
- Tuning architecture choices (backbone, unfrozen layers, image size) — out of scope.
- Distributed/parallel Optuna execution, pruning across multiple GPUs, or persistent Optuna storage — a single in-memory study is sufficient for this PoC.
- Changing the evaluation/report section (Requirement: Evaluation reporting, Feasibility disclosure) — untouched.

## Decisions

- **Library**: Optuna (`pip install optuna`), matching the course's expectation of a standard, well-known HPO tool; TPE sampler (Optuna's default) is used as-is rather than configuring a custom sampler, since the search space is small (2-3 hyperparameters).
- **Objective function**: retrains a fresh EfficientNet-B0 classifier head for a small, fixed number of epochs (fewer than the full `NUM_EPOCHS`, e.g. 3-5) per trial and returns best validation accuracy reached in that short run. This reuses the existing `train_loader`/`val_loader` and the same frozen-backbone setup, so the objective is a smaller version of the existing training loop rather than new modeling code.
- **Search space**: `lr` (log-uniform, e.g. 1e-4 to 1e-2) as the primary parameter; `weight_decay` and `batch size` are optional secondary parameters if time budget allows — kept small (e.g. 8-15 trials) to bound wall-clock cost on Kaggle.
- **Placement**: new section inserted after "4. Dataset e DataLoaders" and before "5. Modelo" / "6. Loop de treino", so the chosen hyperparameters are available as variables (e.g. `best_lr`) that section 6's optimizer construction reads instead of the current hard-coded `lr=1e-3`.
- **Reporting**: print/markdown cell summarizing `study.best_params` and `study.best_value` immediately after the search, giving the presentation something concrete to demo per the course's "cubram os requisitos" requirement.

## Risks / Trade-offs

- [Optuna search adds wall-clock time on top of an already ~55min Kaggle run] → Mitigate with a small trial count (8-15) and few epochs per trial (3-5), keeping the added cost to a few minutes.
- [Short-epoch trial objective may not perfectly predict full-training performance] → Acceptable for a PoC/course deliverable; documented as a simplification in the notebook markdown, not hidden.
- [New dependency `optuna` not yet installed in the Kaggle image] → Added to the existing `pip -q install` cell in section 1, same pattern as `kaggle`/`scikit-learn` today.
