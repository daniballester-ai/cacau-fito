## Why

Today a prediction is recorded in history but nothing captures whether it was actually correct. Without user feedback, there is no path toward a labeled dataset of real field usage that could improve the model later — every prediction's ground truth is lost the moment it's made. Letting a user confirm or correct a diagnosis closes that loop with minimal effort.

## What Changes

- A user SHALL be able to submit feedback on a specific past prediction: either confirm the predicted label was correct, or correct it to one of the other known classes.
- Feedback SHALL be linked to the corresponding prediction history entry (by its existing history ID).
- A prediction SHALL accept feedback only once — a second feedback submission for the same prediction SHALL be rejected, not silently overwritten or duplicated.
- Feedback is additive instrumentation: it does not change what `/predict` or `/history` already return.

## Capabilities

### New Capabilities
- `diagnosis-feedback`: lets a user confirm or correct a recorded prediction's label, linked to its history entry, with at most one feedback per prediction.

### Modified Capabilities
(none — `prediction-history` is only read from, not restructured; its existing requirements are unchanged)

## Impact

- `src/inference_service/history.py` (or a new module) — new storage for feedback entries, referencing existing prediction history rows.
- `src/inference_service/main.py` — new endpoint to submit feedback for a given prediction ID.
- No change to the existing `/predict` or `/history` response shapes.
