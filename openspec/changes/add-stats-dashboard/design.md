## Context

See proposal.md for motivation. `history.py` already exposes `get_stats()` (lifetime totals) built on the same `predictions` table this feature reads from. `created_at` is already stored as a Unix timestamp per row (see `record_prediction()`), so day-bucketing is a `SELECT date(created_at, 'unixepoch')` style grouping in SQLite — no schema change needed.

## Goals / Non-Goals

**Goals:**
- Answer "how has this trended over time," which a lifetime total cannot.
- Reuse the existing `predictions` table with no schema change.

**Non-Goals:**
- Configurable time granularity (week/month) or custom date ranges — this PoC always shows the full history bucketed by day.
- Real-time/streaming updates to the dashboard — it's a snapshot, refreshed on page load.

## Decisions

**Bucketing: SQL `GROUP BY date(created_at, 'unixepoch'), label` in `history.py`.**
SQLite's built-in date functions handle Unix-timestamp-to-date bucketing without needing to load rows into Python and group there — consistent with how `get_stats()` already does its aggregation in SQL rather than in application code.

**Chart library: Chart.js (loaded from a CDN, `<script>` tag), a small line/bar chart.**
Chosen for being a single well-known dependency with no build step, matching the frontend's existing no-build-step, plain HTML/CSS/JS approach (`frontend/static/*.js`) rather than introducing a bundler or framework for one chart.

**Endpoint: `GET /stats/timeseries`, returning `{"days": [{"date": "...", "by_class": {...}}, ...]}`.**
A separate endpoint (rather than adding query parameters to `GET /stats`) keeps the existing lifetime-totals contract completely untouched, matching this proposal's explicit non-goal.

## Risks / Trade-offs

- [A day with zero predictions for a class is simply absent from that day's data, per the spec's explicit scenario] → The frontend must fill gaps with zero for a continuous chart axis; documented as the dashboard's responsibility, not the data endpoint's, keeping the API honest about what actually happened vs. what's convenient to plot.
