## Why

Prediction history today can only be browsed a page at a time through `GET /history` or the history page. Anyone who wants to analyze the full history outside the app — in a spreadsheet, or as an input to future retraining work alongside `diagnosis-feedback` — has no way to get the data out in bulk.

## What Changes

- The system SHALL let a client download the full prediction history as a CSV file.
- The export SHALL include, per row, the same fields already exposed by `GET /history` (timestamp, predicted label, confidence) plus per-class probabilities.
- Exporting an empty history SHALL produce a valid CSV with just a header row, not an error.
- This is a read-only export — it does not change how history is recorded or paginated.

## Capabilities

### New Capabilities
- `prediction-history-export`: exposes the full prediction history as a downloadable CSV file.

### Modified Capabilities
(none — `prediction-history`'s existing requirements for recording and paginated listing are unchanged)

## Impact

- `src/inference_service/history.py` — a function to stream/build all history rows for export (distinct from the paginated `list_predictions`).
- `src/inference_service/main.py` — a new endpoint returning a CSV response.
- No change to `GET /history`'s existing paginated behavior.
