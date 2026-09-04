## Context

See proposal.md for motivation. `/predict` already returns per-class probabilities (`{label, confidence, probabilities}`) computed by `src/inference_service/model.py`'s `LeafClassifier.predict()`. No new model inference or training is needed — the uncertainty rule is a pure function of numbers already computed. The frontend (`frontend/static/app.js`) already renders `label` and `confidence` in a result card.

## Goals / Non-Goals

**Goals:**
- Add a deterministic, testable rule that flags a prediction as uncertain from its existing probabilities.
- Surface that flag clearly in both the API response and the UI, without touching the model itself.

**Non-Goals:**
- Retraining or calibrating the model's confidence scores (e.g., temperature scaling) — out of scope; this only interprets the scores the model already produces.
- Letting the threshold be configured per-request or per-user — it is a single documented constant for this PoC.
- Blocking or refusing to return an uncertain prediction — the label is still returned, just flagged.

## Decisions

**Threshold rule: `is_uncertain = confidence < LOW_CONFIDENCE_THRESHOLD OR (top_prob - second_prob) < CLOSE_CALL_MARGIN`.**
Two independent conditions cover the two real failure modes: a genuinely low top score (model isn't sure about anything), and a close race between two classes (model is confident *something* is right, but not which). Using both — rather than only a confidence floor — is what the proposal calls out as the real edge case: a 40%/38%/22% split has a top confidence that might clear a simple threshold, yet is clearly not a confident single-class call. Alternatives considered: entropy-based uncertainty (more principled but harder to explain in a PoC report and to tune from just 3 classes); a single flat confidence threshold alone (simpler, but misses the close-call case named in the proposal).

**Threshold values: `LOW_CONFIDENCE_THRESHOLD = 0.6`, `CLOSE_CALL_MARGIN = 0.1`, both documented constants in code.**
Chosen as reasonable starting points for a 3-class classifier (a random guess would average ~33% confidence, so 60% is a meaningful "above chance and then some" bar) and validated against the change's test fixtures during implementation (tasks.md). Not derived from a formal calibration study — documented as a PoC choice, adjustable later if real usage shows it's miscalibrated.

**Response shape: add `is_uncertain: boolean` always, and `uncertainty_reason: string | null`.**
Always including `is_uncertain` (rather than omitting the field when false) keeps the response shape predictable for clients — no need to check for key presence. `uncertainty_reason` is `null` when not uncertain, `"low_confidence"` or `"close_call"` when it is (the two conditions above, checked in that order so a genuinely low-confidence result reports as "low_confidence" even if it also happens to be a close call).

**Frontend: badge/label in the existing result card, not a separate warning banner or blocking modal.**
Keeps the existing "Resultado: <label> — Confiança: X%" layout, adding a small "Resultado incerto" badge next to it when flagged — matches the PoC's minimal-UI posture (see `leaf-upload-frontend`'s existing design) without a bigger UI overhaul.

## Risks / Trade-offs

- [Fixed threshold values are a guess, not calibrated against real-world misdiagnosis cost] → Documented as a PoC constant; flag this explicitly in the course report and `docs/limitations_and_next_steps.md` as a follow-up for real deployment.
- [Two independent conditions could both fire and it's not obvious to a reader which one "wins"] → Resolved by checking low-confidence first in the implementation, and specifying that order explicitly in the spec scenario.
- [Existing API consumers that only read `label`/`confidence`/`probabilities` are unaffected since the change is additive] → No action needed; documented in the proposal's Impact section.
