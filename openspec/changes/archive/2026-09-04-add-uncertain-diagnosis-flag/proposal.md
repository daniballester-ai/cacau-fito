## Why

The inference service always presents a single confident-looking class name, even when the model's top prediction barely edges out the runner-up (e.g., 34% vs. 33% vs. 33%) or the top confidence is low overall. Presenting that as a flat diagnosis overstates what the model actually knows, which is misleading for a phytosanitary decision. Flagging low-confidence results as "uncertain" is a small, well-scoped rule with a real edge case (near-tie between classes) — a good fit for this SDD exercise.

## What Changes

- The prediction endpoint's response SHALL include an `is_uncertain` flag, computed from a documented confidence threshold.
- The prediction endpoint's response SHALL include an `uncertainty_reason` when `is_uncertain` is true (e.g., "low_confidence" or "close_call" between the top two classes).
- The upload frontend SHALL visually distinguish an uncertain result from a confident one, instead of presenting every result the same way.
- No change to the existing fields (`label`, `confidence`, `probabilities`) — this only adds new fields/behavior alongside them.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `leaf-inference-service`: the prediction response gains an uncertainty flag and reason, computed from a confidence/close-call rule, without changing the existing response fields or error behavior.
- `leaf-upload-frontend`: the result display distinguishes an uncertain prediction from a confident one.

## Impact

- `src/inference_service/model.py` and/or `main.py` — compute the uncertainty flag from the existing per-class probabilities already returned by the model; no new model training or artifact needed.
- `frontend/static/app.js` and `frontend/static/style.css` — render the uncertain state distinctly.
- No breaking change to `/predict`'s existing fields — purely additive to the response shape.
