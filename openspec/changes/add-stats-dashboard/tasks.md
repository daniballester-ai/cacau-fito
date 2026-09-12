## 1. Time-Series Aggregation

- [x] 1.1 Implement `get_stats_timeseries()` in `src/inference_service/history.py` grouping by day and label, and verify a unit test with predictions across multiple days returns correct per-day, per-class counts
- [x] 1.2 Verify empty history returns an empty series (not an error)

## 2. API Integration

- [x] 2.1 Implement `GET /stats/timeseries` in `src/inference_service/main.py`, and verify a manual request after predictions across a couple of days returns the expected shape
- [x] 2.2 Verify `GET /stats`'s existing response is unchanged by this addition

## 3. Dashboard Page

- [x] 3.1 Build `frontend/dashboard.html` (+ static JS/CSS) loading Chart.js from CDN and rendering the time-series as a chart plus the existing lifetime totals, and verify manually after making predictions across sample data that the chart renders correctly
- [x] 3.2 Add an empty-state message for no data, and verify manually on a fresh/empty history

## 4. Verification

- [x] 4.1 Run the full test suite (`python -m pytest tests/ -v`) and confirm all prior tests still pass alongside the new ones
