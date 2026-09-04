# Phase 0 Research: Prediction Stats

No open "NEEDS CLARIFICATION" items remained from the Technical Context — the feature reuses infrastructure already established by the `prediction-history` capability. This document records the resulting decisions and why alternatives were rejected.

## Decision: Compute stats on demand with a single SQL aggregate query

**Rationale**: The existing `predictions` table is capped at 200 rows by the retention policy already in place (`history.RETENTION_LIMIT`). A `SELECT label, COUNT(*) ... GROUP BY label` (plus a separate `COUNT(*)` for the total, or a single pass in Python) is effectively free at this scale, and requires no new storage, caching layer, or background job.

**Alternatives considered**:
- *Maintain a running counter updated on every `record_prediction()` call* — rejected: adds a second source of truth that could drift from the actual table contents (e.g., if a row is evicted by retention, the counter would need separate decrement logic), for no measurable performance benefit at this scale.
- *Cache the stats response for N seconds* — rejected: unnecessary complexity for a PoC with no real traffic volume; on-demand computation is simpler and always accurate.

## Decision: Always include all three known classes in the response, defaulting missing ones to zero

**Rationale**: `spec.md`'s FR-003 and the "class never appeared" edge case require a consistent shape regardless of what has been recorded. The known class list is already defined once, in `label_mapping.json`'s `classes` array (loaded by `LeafClassifier`) — reusing that instead of hardcoding the three class names in the stats code avoids a second place that could go stale if the model's class list ever changes.

**Alternatives considered**:
- *Only include classes that have at least one recorded prediction* — rejected: this is exactly what FR-003 rules out; a class with zero predictions must still appear with `0`, not be silently absent, since a missing key is easy to misread as "no data available" rather than "zero occurrences."

## Decision: Reuse `history.py`'s existing `_connect()` helper for a new `get_stats()` function

**Rationale**: Matches the pattern already established by `record_prediction()` and `list_predictions()` in the same module — one helper, one place that knows the DB path and schema. Keeps `main.py`'s new route a thin wrapper, consistent with how `GET /history` already delegates to `history.list_predictions()`.

**Alternatives considered**:
- *Compute stats directly in `main.py` with inline SQL* — rejected: duplicates connection/schema knowledge that already lives in `history.py`, and breaks the existing separation between the HTTP layer (`main.py`) and the storage layer (`history.py`).

## Decision: Signal storage failure with an HTTP 503, not a 200 with zeroed/partial data

**Rationale**: `spec.md`'s FR-006 and the corresponding edge case explicitly require that a storage problem must not be confused with "zero predictions recorded" — those are semantically different (no data yet vs. couldn't read the data). An HTTP 5xx status is the standard, technology-appropriate way to signal "the server could not fulfill this request due to an internal problem," consistent with how the existing `/predict` endpoint already uses HTTP status codes to distinguish client errors (400) from successful responses (200).

**Alternatives considered**:
- *Return 200 with a `zeroed` result and an `error` field* — rejected: silently returning a 200 for a failure case invites callers to skip checking for the error field and misread the zeros as real data, which is precisely the ambiguity FR-006 rules out.
