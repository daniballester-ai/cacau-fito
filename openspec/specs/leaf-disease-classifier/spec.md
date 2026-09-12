# leaf-disease-classifier Specification

## Purpose

Trains and evaluates an image classification model that predicts a cacau leaf's phytosanitary condition from a photo, and produces a reusable model artifact for the inference service.

## Requirements

### Requirement: Model training on the curated dataset
The training pipeline SHALL fit an image classification model using the `cacao-leaf-dataset` training subset and select the checkpoint with the best validation performance. The hyperparameters used for this training run (at minimum the learning rate) SHALL be derived from a documented hyperparameter search over the validation subset rather than hard-coded without justification.

#### Scenario: Training run produces a model artifact
- **WHEN** the training pipeline is run against the prepared dataset
- **THEN** a trained model artifact is saved along with the class label mapping used during training

#### Scenario: Hyperparameter search precedes the final training run
- **WHEN** the training notebook is run end to end
- **THEN** a hyperparameter search is executed first, evaluating multiple trials against the validation subset, and the resulting best hyperparameters and their validation score are reported before the final training run

### Requirement: Evaluation reporting
The training pipeline SHALL report standard classification metrics (at minimum accuracy and per-class precision/recall) on the held-out test subset.

#### Scenario: Metrics produced after training
- **WHEN** training completes
- **THEN** an evaluation report is generated showing accuracy and per-class precision/recall on the test subset

### Requirement: Feasibility disclosure
Given the dataset is small and informally collected, the evaluation report SHALL flag when test performance is not reliable enough to support real-world use (e.g., due to class imbalance or too few test examples), rather than presenting a single accuracy number without caveats.

#### Scenario: Low-confidence result flagged
- **WHEN** a test class has fewer than the documented minimum number of examples or shows high variance across evaluation runs
- **THEN** the evaluation report explicitly notes this limitation next to the corresponding metric
