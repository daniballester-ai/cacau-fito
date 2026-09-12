## MODIFIED Requirements

### Requirement: Model training on the curated dataset
The training pipeline SHALL fit an image classification model using the `cacao-leaf-dataset` training subset and select the checkpoint with the best validation performance. The hyperparameters used for this training run (at minimum the learning rate) SHALL be derived from a documented hyperparameter search over the validation subset rather than hard-coded without justification.

#### Scenario: Training run produces a model artifact
- **WHEN** the training pipeline is run against the prepared dataset
- **THEN** a trained model artifact is saved along with the class label mapping used during training

#### Scenario: Hyperparameter search precedes the final training run
- **WHEN** the training notebook is run end to end
- **THEN** a hyperparameter search is executed first, evaluating multiple trials against the validation subset, and the resulting best hyperparameters and their validation score are reported before the final training run
