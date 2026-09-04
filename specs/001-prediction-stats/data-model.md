# Data Model: Prediction Stats

## Prediction Stats Summary

A derived, read-only aggregate over the existing `predictions` table (owned by the `prediction-history` capability, see `src/inference_service/history.py`). It is not a new stored entity — it is computed fresh on every request from the existing rows.

| Field | Type | Description |
|---|---|---|
| `total` | integer | Total number of predictions currently recorded (equal to the sum of all `by_class` values). |
| `by_class` | object (class name → integer) | One entry per known class (`healthy`, `cssvd`, `anthracnose`, sourced from the classifier's `label_mapping.json`), each with the count of recorded predictions for that class. A class with no recorded predictions is present with value `0`, never omitted. |

**Validation rules** (from `spec.md`'s functional requirements):
- `total` MUST equal the sum of all values in `by_class` (FR-001, FR-002).
- `by_class` MUST contain a key for every known class, regardless of count (FR-003).
- When no predictions have been recorded, `total` is `0` and every `by_class` value is `0` (FR-004) — this is a valid, successful response, not an error.
- Only successfully recorded predictions are counted — consistent with what `prediction-history` already persists (FR-005); this feature does not re-derive or duplicate that recording logic.

**State transitions**: None — this is a stateless read computed at request time; it has no lifecycle of its own beyond the underlying `predictions` rows it summarizes.

**Failure case**: If the underlying storage cannot be read, no Prediction Stats Summary is returned at all (see `contracts/stats-api.md` for the corresponding error response) — a partial or zeroed summary is never returned as if it were valid, per FR-006.
