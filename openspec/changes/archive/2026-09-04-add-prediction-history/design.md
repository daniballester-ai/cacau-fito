## Context

See proposal.md for motivation. The inference service (`src/inference_service/`) is a small FastAPI app with a single `/predict` endpoint and a same-origin static frontend (`frontend/`). It has no database or persistence today — everything is stateless per-request. This change adds the first piece of server-side state to the PoC.

## Goals / Non-Goals

**Goals:**
- Record every successful prediction with enough detail to review later (label, confidence, per-class probabilities, timestamp, image reference).
- Expose that history through a paginated API and a minimal browsing page, consistent with the existing no-login PoC posture.
- Keep storage bounded so a long-running demo instance doesn't grow unbounded on disk.

**Non-Goals:**
- User accounts, per-user history, or authentication of any kind.
- Editing or manually deleting individual history entries.
- Search, filtering, or analytics over history (beyond simple newest-first pagination).
- Long-term/production-grade storage (e.g., cloud object storage, a managed database) — this is still a PoC.

## Decisions

**Storage: SQLite via Python's built-in `sqlite3`, one row per prediction.**
Alternatives considered: a flat JSON file (simplest to start, but pagination and ordering require loading and re-sorting the whole file on every request, and concurrent writes from multiple requests are not safely atomic) and a full ORM/Postgres setup (unnecessary weight for a PoC with a single small table). SQLite ships with Python (no new dependency), gives real `ORDER BY`/`LIMIT`/`OFFSET` pagination, and handles concurrent writes safely enough for this scale. Schema: `id, created_at, label, confidence, probabilities_json, image_path`.

**Image storage: save the uploaded image bytes to a local `history/images/` directory, referenced by a generated file name in the DB row.**
Keeping the image alongside the metadata (rather than only the prediction result) is what makes history actually reviewable — a label and confidence number alone don't let a person sanity-check what the model saw. Images are written best-effort; a write failure degrades to recording metadata without the image reference rather than failing the request (see Requirement: Prediction recording).

**Retention: bounded to the 200 most recent entries, enforced on write.**
A PoC demo instance has no operator actively pruning storage, so an explicit cap is needed. 200 is a round number well beyond what a course demo will generate, chosen for demo purposes and documented as a constant (not user-configurable in this PoC). When a new entry would exceed the cap, the oldest entry's DB row and image file are deleted together in the same write path — see Requirement: Bounded retention.

**History endpoint: `GET /history?limit=&offset=`, `limit` default 20 / max 100.**
Simple offset-based pagination matches the "browse newest-first" use case in the spec; cursor-based pagination would add complexity this PoC doesn't need. Response shape: `{items: [...], total, next_offset}`, where `items` are ordered newest-first.

**History page: a second static page (`frontend/history.html`) served the same way `index.html` is today, fetching `/history` client-side.**
Reuses the existing same-origin static-serving pattern in `src/inference_service/main.py` instead of introducing a frontend framework or a templating engine.

**Recording is invoked from the existing `/predict` handler, after a successful classification, wrapped in a try/except that only logs on failure.**
This keeps the existing `/predict` contract (request/response shape, status codes) completely unchanged — history is additive instrumentation, not a new failure mode for predictions, matching the proposal's explicit non-goal of modifying `leaf-inference-service`.

## Risks / Trade-offs

- [SQLite file living on local disk means history is lost if the service's storage is ephemeral (e.g., a container without a persistent volume)] → Acceptable for a PoC; document this as a known limitation rather than solving it now.
- [Storing raw uploaded images grows disk usage] → Bounded by the 200-entry retention cap; images are deleted together with their DB row when evicted.
- [Concurrent requests writing to SQLite simultaneously] → SQLite's default journaling mode handles this at PoC request volume; not designed for high concurrency, which is out of scope.
- [Someone re-uploading many images quickly could evict genuinely interesting history entries sooner than expected] → Acceptable for a PoC demo; not a concern worth adding configurability for now.

## Migration Plan

Additive only — no existing data or endpoints change. On first run after this change, the SQLite database file and `history/images/` directory are created automatically if they don't exist (no manual migration step). Rollback is simply removing the history endpoints/recording code and deleting the SQLite file and image directory; nothing else in the system depends on them.
