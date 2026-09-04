## 1. Uncertainty Rule

- [x] 1.1 Implement `compute_uncertainty(probabilities)` returning `(is_uncertain, uncertainty_reason)` using the documented thresholds (`LOW_CONFIDENCE_THRESHOLD = 0.6`, `CLOSE_CALL_MARGIN = 0.1`, low-confidence checked before close-call), and verify unit tests cover: high-confidence single winner (not uncertain), low top confidence (uncertain/low_confidence), close race between top two (uncertain/close_call), and a case that is both low-confidence and a close call (reports low_confidence, per the documented order) — DONE: `src/inference_service/model.py`'s `compute_uncertainty()`; `tests/test_uncertainty.py` (4 tests) passes

## 2. API Integration

- [x] 2.1 Call `compute_uncertainty()` from the prediction path and add `is_uncertain` and `uncertainty_reason` to the `/predict` response, and verify a manual request against a known confident sample image returns `is_uncertain: false, uncertainty_reason: null` — DONE: `main.py`'s `/predict` handler; manual request against `samples/healthy_1.jpg` confirmed
- [x] 2.2 Verify existing response fields (`label`, `confidence`, `probabilities`) and existing error responses (unsupported file, invalid image) are unchanged by re-running `src/inference_service/verify_api.py` — DONE: all checks passed, existing fields/errors unchanged

## 3. Frontend Display

- [x] 3.1 Render an "Resultado incerto" badge/indicator in the result card when `is_uncertain` is true, and verify manually (or via a browser automation check) that an uncertain response shows the indicator — DONE: `#uncertain-badge` in `frontend/index.html` + `app.js`; verified in real headless Chrome (Playwright) with a genuinely uncertain sample (see 4.1) — badge visible with correct message
- [x] 3.2 Verify a confident response renders exactly as it did before this change (no indicator, no layout change) — DONE: verified in the same browser session with `healthy_1.jpg` — badge not visible, no layout change

## 4. Verification with Real Samples

- [x] 4.1 Run the samples in `samples/` (and/or the local test split) through `/predict` and confirm at least one real low-confidence or close-call case exists and is correctly flagged, documenting the example used — DONE: scanned the local test split; `data/amini/dataset/images/train/ID_eh1vIH.jpeg` (true label cssvd) predicts cssvd 42.1% vs anthracnose 41.2% vs healthy 16.8% — genuine close call (margin 0.9pp < 10pp), correctly flagged `is_uncertain: true, uncertainty_reason: "low_confidence"` (top confidence 42.1% is also below the 60% threshold). Copied to `samples/uncertain_cssvd_1.jpg` for future manual testing
