## 1. Storage Layer

- [x] 1.1 Implement `list_all_predictions()` in `src/inference_service/history.py` returning every row (no pagination), and verify a unit test confirms it returns all recorded entries in a known order

## 2. API Integration

- [x] 2.1 Implement `GET /history/export.csv` in `src/inference_service/main.py` building a CSV response (header + one row per prediction, probabilities flattened into per-class columns), and verify a manual request after a few predictions returns a well-formed CSV
- [x] 2.2 Verify the export on an empty history returns a valid CSV with only the header row

## 3. Verification

- [x] 3.1 Run the full test suite (`python -m pytest tests/ -v`) and confirm all prior tests still pass alongside the new ones
