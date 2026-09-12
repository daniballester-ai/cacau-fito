## Context

See proposal.md for motivation. `prediction-history` (`src/inference_service/history.py`) already persists one SQLite row per prediction with an autoincrement `id`. This feature adds a second small table referencing that `id`, with no change to the existing schema or its requirements.

## Goals / Non-Goals

**Goals:**
- Let a user record ground truth (confirm/correct) against a specific past prediction.
- Guarantee at most one feedback record per prediction, enforced by the system, not just by client discipline.

**Non-Goals:**
- Actually retraining the model on this feedback — out of scope; this only captures the data.
- Editing or deleting existing feedback once submitted.
- Attributing feedback to a specific user identity — this PoC has no authentication yet (see the separate `add-user-authentication` capability); feedback is anonymous, matching the rest of the system's current no-login posture.

## Decisions

**Storage: a second SQLite table `feedback(prediction_id UNIQUE, corrected_label, created_at)` in the same `history/history.db`.**
Reuses the existing database file and connection helper pattern established by `history.py`, rather than introducing a new storage technology for a small, related dataset. A `UNIQUE` constraint on `prediction_id` is what enforces "one feedback per prediction" at the storage layer — not just an application-level check that could race under concurrent requests.

**Confirmation vs. correction: a single `corrected_label` field, set to the original prediction's label when confirming.**
Rather than a separate boolean "was_correct" flag plus an optional corrected label, storing the resulting label directly (equal to the original when confirmed, different when corrected) keeps the schema and the "what does this feedback assert" question simple: it always asserts one specific ground-truth label for that prediction, however it was captured.

**Endpoint: `POST /predict/{prediction_id}/feedback` with a `{"label": "..."}` body.**
Keeps the relationship between a prediction and its feedback explicit in the URL, and reuses the same three known class names already used by `/predict`'s response — no new vocabulary for a client to learn.

## Risks / Trade-offs

- [Anonymous feedback — anyone with a prediction ID can submit feedback for it] → Acceptable for a PoC without authentication yet; revisit once `add-user-authentication` exists.
- [No mechanism yet to retrain on this data] → Out of scope per Non-Goals; this feature only makes the data available for a future, separate effort.
