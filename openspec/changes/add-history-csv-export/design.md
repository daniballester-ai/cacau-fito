## Context

See proposal.md for motivation. `prediction-history` already stores all fields this export needs; this is a read-only, additive projection of the same `predictions` table used by `GET /history`.

## Goals / Non-Goals

**Goals:**
- Provide a single, complete CSV snapshot of history on demand.

**Non-Goals:**
- Filtering or date-range parameters for the export — out of scope for this PoC; the export is always the full history (bounded by the existing 200-entry retention policy, so it can never be unbounded).
- Scheduled/automatic exports — this is a synchronous, on-demand download only.
- Including the actual image files in the export — only metadata; images stay on disk as already handled by `prediction-history`.

## Decisions

**Format: CSV via Python's built-in `csv` module, one row per prediction, probabilities flattened into one column per class.**
No new dependency; matches the "no more infrastructure than needed" pattern already used by `prediction-history` (built-in `sqlite3`) and `prediction-stats` (built-in aggregation). Flattening probabilities into named columns (`prob_healthy`, `prob_cssvd`, `prob_anthracnose`) rather than a single JSON-blob column keeps the file directly usable in a spreadsheet without post-processing.

**Endpoint: `GET /history/export.csv`, returning `Content-Type: text/csv` with a `Content-Disposition` filename.**
A distinct path under `/history` (rather than a query parameter like `?format=csv` on `GET /history`) keeps the paginated JSON endpoint's contract completely untouched, matching the proposal's explicit "no change to `GET /history`" scope.

## Risks / Trade-offs

- [Exporting all history at once could be slow on a much larger dataset] → Acceptable given the existing 200-entry retention cap already bounds this; revisit if the cap is ever raised.
