## Why

`GET /stats` today only reports lifetime totals per class — it can't show how diagnoses have trended over time (e.g., "did anthracnose cases spike this week?"). A visual dashboard needs a time-series breakdown to be useful, not just a snapshot total. Note: the original stats feature (`GET /stats`, lifetime totals) was specified with GitHub Spec Kit at `specs/001-prediction-stats/`, a different artifact format than OpenSpec's delta specs — this change adds a new, independent OpenSpec capability alongside it rather than expressing a cross-tool "modification" of that Spec Kit artifact.

## What Changes

- The system SHALL provide a time-bucketed breakdown of predictions per class (e.g., per day), as a new endpoint alongside the existing `GET /stats` lifetime totals.
- A new dashboard page SHALL visualize this time-series as a chart, alongside the existing per-class totals.
- The dashboard SHALL handle the no-data case (no predictions yet) with a clear empty state, consistent with the rest of the app's existing empty-state handling.

## Capabilities

### New Capabilities
- `prediction-stats-timeseries`: a time-bucketed (per-day, per-class) breakdown of recorded predictions, independent of and additive to the existing lifetime-totals `GET /stats`.
- `stats-dashboard`: a frontend page visualizing that time-series as a chart.

### Modified Capabilities
(none — this is purely additive; `GET /stats`'s existing lifetime-totals behavior is untouched)

## Impact

- `src/inference_service/history.py` — a new function grouping predictions by day and class.
- `src/inference_service/main.py` — a new endpoint returning the time-series data.
- `frontend/` — a new dashboard page with a chart (library choice in design.md).
- No change to the existing `GET /stats` response shape.
