# Implementation Plan: Prediction Stats

**Branch**: `001-prediction-stats` | **Date**: 2026-09-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-prediction-stats/spec.md`

## Summary

Add a way to retrieve an aggregate summary (total count + per-class breakdown) of all predictions recorded so far, computed on demand from the existing prediction history storage, with a well-defined zero-filled response when no predictions exist yet and a clear failure signal if the underlying storage is unavailable.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI (existing `src/inference_service/main.py`); Python's built-in `sqlite3` via the existing `src/inference_service/history.py` module — no new dependency

**Storage**: Existing SQLite database at `history/history.db` (see `prediction-history` capability); this feature only reads from the existing `predictions` table, no schema change

**Testing**: pytest (existing `tests/` suite, `fastapi.testclient.TestClient` pattern already used in `tests/test_history_api.py`)

**Target Platform**: Same local/PoC deployment as the rest of CacauFito's inference service (single-process FastAPI app)

**Project Type**: Web service (single small backend service with a static frontend) — this feature is backend-only

**Performance Goals**: No specific target beyond the existing service's PoC scale (single-digit to low-hundreds of requests); a `COUNT(*) ... GROUP BY` query over a table capped at 200 rows (per the existing retention policy) is effectively instant

**Constraints**: Must not require a schema migration or any change to how predictions are recorded; must reuse the existing `history` module rather than opening a second connection path to the same database

**Scale/Scope**: PoC scope — one small read-only endpoint, no new persistent state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project constitution has been ratified yet (`.specify/memory/constitution.md` is still the unfilled template) — no gates to check against. Proceeding without constitutional constraints; this is noted here rather than silently skipped.

## Project Structure

### Documentation (this feature)

```text
specs/001-prediction-stats/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
└── inference_service/
    ├── main.py          # add GET /stats route here
    ├── history.py        # add a get_stats() function here (reuses existing DB connection helper)
    └── model.py           # unchanged

tests/
├── test_stats.py                 # new: unit tests for history.get_stats()
└── test_stats_api.py             # new: API-level tests for GET /stats
```

**Structure Decision**: Single-project structure (this is the existing `src/inference_service/` backend, no separate frontend/backend split needed for a backend-only feature). Follows the same file organization already established by the `prediction-history` feature (a function in `history.py`, a route in `main.py`, tests in `tests/`).

## Complexity Tracking

*No violations — no constitution gates are defined yet, and the design below adds a single read-only function and route reusing existing infrastructure.*
