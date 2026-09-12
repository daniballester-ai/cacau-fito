## Why

The course deliverable for PPGTI3003 (Aprendizagem Profunda) requires the training notebook to demonstrate the ML/deep-learning pipeline end to end, and hyperparameter optimization is one of the explicitly expected steps of a deep learning training pipeline covered in the course. The current `notebooks/train_kaggle.ipynb` trains EfficientNet-B0 with a single, hand-picked set of hyperparameters (learning rate, batch size, scheduler step/gamma) and has no systematic search step. Adding an Optuna-based hyperparameter search closes this gap before the notebook, canvas, and pitch video are submitted.

## What Changes

- Add a new notebook section that uses Optuna to search over the classifier's key hyperparameters (at minimum: learning rate, and one or two of batch size / weight decay / LR scheduler step size) using a short-epoch objective evaluated on the validation split.
- Report the best trial's hyperparameters and validation score, and use them (or let the user apply them) as the configuration for the full training run in the existing training section.
- No changes to the model architecture, dataset preparation, or evaluation/report sections — this only adds a tuning step ahead of the existing training loop.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `leaf-disease-classifier`: training pipeline requirement is extended so that model hyperparameters used for the final training run come from a documented Optuna search rather than being hard-coded, and the search process/results are reported for traceability.

## Impact

- Affected file: `notebooks/train_kaggle.ipynb` (new cells/section between the DataLoader setup and the final training loop).
- New dependency: `optuna` (installed via pip in the notebook's setup cell, alongside the existing `kaggle`/`scikit-learn` install).
- No impact on `models/`, the inference service, or the frontend — this only changes how the training notebook arrives at its hyperparameters.
