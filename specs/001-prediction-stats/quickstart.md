# Quickstart: Prediction Stats

Validates the feature end-to-end once implemented. See [contracts/stats-api.md](./contracts/stats-api.md) for the exact response shape and [data-model.md](./data-model.md) for field semantics.

## Prerequisites

- Project dependencies installed (`fastapi`, `uvicorn`, `torch`/`torchvision`, `pytest` — already required by the rest of CacauFito).
- A trained model artifact present under `models/` (already required for `/predict` to work at all).

## Scenario 1 — Stats reflect recorded predictions

1. Start the service: `python -m uvicorn src.inference_service.main:app --host 127.0.0.1 --port 8000`
2. Make a few predictions of different classes, e.g.:
   ```bash
   curl -s -X POST -F "file=@samples/healthy_1.jpg;type=image/jpeg" http://127.0.0.1:8000/predict
   curl -s -X POST -F "file=@samples/cssvd_1.jpg;type=image/jpeg" http://127.0.0.1:8000/predict
   curl -s -X POST -F "file=@samples/anthracnose_1.jpg;type=image/jpeg" http://127.0.0.1:8000/predict
   ```
3. Request the stats: `curl -s http://127.0.0.1:8000/stats`
4. **Expected**: `total` equals the number of predictions made, and `by_class` counts sum to `total`, matching what a manual read of `GET /history` would show for the same period.

## Scenario 2 — Stats before any prediction

1. Start the service against a fresh/empty `history/` directory (or delete `history/history.db` before starting).
2. Request the stats: `curl -s http://127.0.0.1:8000/stats`
3. **Expected**: `200 OK` with `{"total": 0, "by_class": {"healthy": 0, "cssvd": 0, "anthracnose": 0}}` — not an error.

## Automated verification

Run the feature's test suite: `python -m pytest tests/test_stats.py tests/test_stats_api.py -v`
