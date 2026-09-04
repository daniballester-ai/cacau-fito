## Why

Every prediction the CacauFito inference service makes today is thrown away the moment the response is sent — there is no record of what was diagnosed, when, or with what confidence. For a course exercise on Spec-Driven Development this is a good candidate: it has real business rules (what to store, how much to retain), genuine edge cases (empty history, storage failures, unbounded growth), and touches multiple files across the backend and frontend rather than being a single-function change.

## What Changes

- Every call to the inference service's prediction endpoint SHALL be recorded as a history entry (timestamp, predicted label, confidence, per-class probabilities, and a reference to the submitted image).
- A new endpoint SHALL let a client list past predictions, most recent first, with pagination.
- A new minimal page SHALL let a person browse prediction history without needing to call the API directly.
- History storage SHALL be bounded (a retention policy) so it cannot grow without limit on a small PoC deployment.
- A failure to record history SHALL NOT cause the prediction request itself to fail — history recording is best-effort logging, not part of the prediction contract.

## Capabilities

### New Capabilities
- `prediction-history`: persists a record of each prediction made by the inference service and exposes it for later browsing (API + minimal page), with a bounded retention policy.

### Modified Capabilities
(none — the existing `/predict` request/response contract is unchanged; history recording is additive and best-effort)

## Impact

- `src/inference_service/main.py` and `src/inference_service/model.py` (or a new module) — record a history entry after each successful prediction.
- New persistence for history entries (e.g., a local SQLite database or JSON store — decided in design.md).
- New history endpoint(s) in the inference service.
- `frontend/` — a new minimal history page/view.
- No change to the existing `/predict` request or response shape.
