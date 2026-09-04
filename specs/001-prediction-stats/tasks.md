---

description: "Task list for feature implementation"
---

# Tasks: Prediction Stats

**Input**: Design documents from `/specs/001-prediction-stats/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/stats-api.md, quickstart.md

**Tests**: Included — the existing codebase already has a pytest suite covering every prior feature (`tests/test_history.py`, `tests/test_history_api.py`, `tests/test_uncertainty.py`), so this feature follows the same convention.

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent implementation and testing of each story.

## Path Conventions

Single project — `src/inference_service/`, `tests/` at repository root (see plan.md's Project Structure).

## Phase 1: Setup

**Purpose**: Confirm the existing project is ready for this feature — no new infrastructure needed, this is an additive read-only feature on top of the existing `prediction-history` capability.

- [X] T001 Confirm the dev environment still runs the existing suite (`python -m pytest tests/ -v` passes before starting, so any later failure is attributable to this feature)

---

## Phase 2: Foundational

**Purpose**: No blocking prerequisites — this feature reuses the existing `src/inference_service/history.py` connection helper and `src/inference_service/main.py` FastAPI app as-is, with no schema change. Skipping to user stories directly.

---

## Phase 3: User Story 1 - View overall diagnosis distribution (Priority: P1) 🎯 MVP

**Goal**: A client can retrieve a total count and a per-class breakdown of all predictions recorded so far in one request.

**Independent Test**: Make several predictions across different classes via `/predict`, then call the stats endpoint and confirm the counts and total are accurate.

### Tests for User Story 1

- [X] T002 [P] [US1] Unit test `history.get_stats()` returns correct `total` and `by_class` counts after inserting predictions across multiple classes, in `tests/test_stats.py`
- [X] T003 [P] [US1] Unit test `history.get_stats()` reflects a skewed distribution accurately (not an even split) in `tests/test_stats.py`
- [X] T004 [P] [US1] API test: `GET /stats` after several `/predict` calls returns a body matching `contracts/stats-api.md`'s success shape, with `total` equal to the sum of `by_class` values, in `tests/test_stats_api.py`

### Implementation for User Story 1

- [X] T005 [US1] Implement `get_stats()` in `src/inference_service/history.py`: one query (or two) against the existing `predictions` table returning `{label: count}` and the total row count
- [X] T006 [US1] Add `GET /stats` route in `src/inference_service/main.py` that calls `history.get_stats()`, fills in every known class from `classifier.classes` (defaulting absent classes to `0`), and returns the shape from `contracts/stats-api.md`
- [X] T007 [US1] Manually verify per quickstart.md Scenario 1: start the service, make a few `/predict` calls with different `samples/*.jpg` files, call `GET /stats`, and confirm the numbers match

**Checkpoint**: User Story 1 is independently functional — stats can be retrieved and are accurate.

---

## Phase 4: User Story 2 - View stats with no predictions yet (Priority: P2)

**Goal**: Requesting stats before any prediction exists returns a valid zero-filled response instead of an error.

**Independent Test**: Request stats against a fresh/empty prediction history and confirm a `200` with all-zero counts, not an error.

### Tests for User Story 2

- [X] T008 [P] [US2] Unit test `history.get_stats()` returns `total: 0` and every class at `0` when the `predictions` table is empty, in `tests/test_stats.py`
- [X] T009 [P] [US2] API test: `GET /stats` on a fresh instance (no predictions recorded) returns `200` with the all-zero shape from `contracts/stats-api.md`, in `tests/test_stats_api.py`

### Implementation for User Story 2

- [X] T010 [US2] Confirm `get_stats()` and the `/stats` route already satisfy this case naturally (an empty table's `GROUP BY` returns no rows, so every known class must still be filled in as `0` by the route, per T006) — adjust `main.py`'s class-filling logic if the empty case is not already covered
- [X] T011 [US2] Manually verify per quickstart.md Scenario 2: against an empty/fresh `history/` directory, confirm `GET /stats` returns the all-zero response, not an error

**Checkpoint**: User Story 2 is independently functional — the empty-history edge case is handled correctly.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Cover the remaining requirement not tied to a specific user story (storage-failure signaling) and finalize.

- [X] T012 [P] Unit or API test simulating a storage failure (e.g., monkeypatching `history.get_stats()` to raise) and confirming `GET /stats` returns `503` with the error shape from `contracts/stats-api.md`, per FR-006, in `tests/test_stats_api.py`
- [X] T013 Add a `try/except` around the storage call in the `/stats` route in `src/inference_service/main.py` to return the `503` response on failure, per `contracts/stats-api.md`
- [X] T014 Run the full suite (`python -m pytest tests/ -v`) and confirm all prior tests still pass alongside the new ones

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies — start here.
- **Foundational (Phase 2)**: None required for this feature.
- **User Story 1 (Phase 3)**: Depends on Setup only. This is the MVP — it can ship alone.
- **User Story 2 (Phase 4)**: Depends on User Story 1's implementation (T005, T006) already existing, since it verifies the same code path's edge case rather than adding new code paths.
- **Polish (Phase 5)**: Depends on User Story 1's route (T006) existing, since it wraps that same route's storage call.

## Parallel Execution Examples

Within Phase 3, tests can run in parallel (different assertions, same new files, but written as independent test functions):

```text
T002 [P] [US1] ...
T003 [P] [US1] ...
T004 [P] [US1] ...
```

Within Phase 4, likewise:

```text
T008 [P] [US2] ...
T009 [P] [US2] ...
```

## Implementation Strategy

**MVP first**: Complete Phase 1 → Phase 3 (User Story 1) → stop and demo. This alone delivers the feature's core value (SC-001, SC-002).

**Incremental delivery**: Add Phase 4 (empty-history edge case, SC-003) next, then Phase 5 (storage-failure signaling, FR-006) — each phase is a small, independently testable increment on top of the same single route.
