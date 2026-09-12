## Purpose

Lets a user confirm or correct the label of a past prediction, linking that judgment to the corresponding prediction history entry, so real usage can eventually become a labeled dataset for retraining.

## ADDED Requirements

### Requirement: Feedback submission
The system SHALL let a user submit feedback for a specific past prediction, identified by its prediction history ID, stating either that the predicted label was correct or which of the other known classes it should have been.

#### Scenario: User confirms a correct prediction
- **WHEN** a user submits feedback confirming the predicted label for a given prediction ID
- **THEN** the system records that the prediction was confirmed correct

#### Scenario: User corrects a prediction
- **WHEN** a user submits feedback specifying a different (valid) class than the one predicted for a given prediction ID
- **THEN** the system records the corrected label alongside a reference to the original prediction

#### Scenario: Feedback for a nonexistent prediction is rejected
- **WHEN** a user submits feedback referencing a prediction ID that does not exist in history
- **THEN** the system rejects the submission with a clear error, without creating a feedback record

### Requirement: One feedback per prediction
The system SHALL accept at most one feedback submission per prediction.

#### Scenario: Second feedback submission is rejected
- **WHEN** a user submits feedback for a prediction that already has feedback recorded
- **THEN** the system rejects the second submission with a clear error, and the original feedback remains unchanged
