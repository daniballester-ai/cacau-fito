## 1. Storage Layer

- [x] 1.1 Create the `feedback` table (`prediction_id UNIQUE, corrected_label, created_at`) and a `record_feedback(prediction_id, label)` function in `src/inference_service/history.py`, and verify a unit test can insert feedback and read it back
- [x] 1.2 Implement the uniqueness guarantee (reject a second insert for the same `prediction_id`) at the storage layer, and verify a test asserts the second call raises/returns a clear error rather than overwriting

## 2. API Integration

- [x] 2.1 Implement `POST /predict/{prediction_id}/feedback` in `src/inference_service/main.py` validating the label against the known classes, and verify a manual request against a real prediction ID succeeds
- [x] 2.2 Verify submitting feedback for a nonexistent prediction ID returns a clear error (not a crash)
- [x] 2.3 Verify submitting a second feedback for the same prediction ID is rejected with a clear error, and the first feedback is unchanged

## 3. Verification

- [x] 3.1 Run the full test suite (`python -m pytest tests/ -v`) and confirm all prior tests still pass alongside the new ones
