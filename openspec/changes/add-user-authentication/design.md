## Context

See proposal.md for motivation. Today `predictions` (in `history.py`) has no notion of who made a prediction — everything is one shared, anonymous table. This is the first capability that introduces persistent user identity into CacauFito, and it changes two previously-anonymous capabilities (`leaf-upload-frontend`, `prediction-history`) rather than only adding something new.

## Goals / Non-Goals

**Goals:**
- Let multiple people use CacauFito independently, each seeing only their own predictions/history/stats.
- Keep the authentication mechanism simple and appropriate for a PoC — not a production-grade identity system.

**Non-Goals:**
- Password reset flows, email verification, or third-party login (OAuth/SSO) — out of scope for this PoC.
- Roles/permissions beyond "logged in vs. not" — no admin role, no per-user quotas.
- Migrating existing anonymous history rows to a specific user — pre-existing rows (recorded before this change) are out of scope for backfill; they remain unattributed and are not shown to any user going forward (see Migration Plan).

## Decisions

**Session mechanism: server-side session cookie backed by a `sessions` table (or signed cookie), not JWT.**
For a PoC with a single small FastAPI service (no separate services needing to verify a token independently), a simple server-side session is less moving parts than JWT issuance/verification/rotation, and lets logout immediately invalidate a session (a JWT would remain valid until expiry). Alternative considered: JWT — rejected as unnecessary complexity for a single-service PoC.

**Password storage: hashed with a standard password-hashing algorithm (e.g., bcrypt via `passlib`), never stored or logged in plaintext.**
Non-negotiable baseline security practice regardless of PoC scope — storing plaintext passwords would be an unacceptable risk even in a course project, per the org's "security by design" expectations.

**User scoping: add a `user_id` foreign key to the existing `predictions` table (and the `feedback` table from `add-diagnosis-feedback`, if merged first) rather than a separate per-user database.**
Keeps a single shared schema with a scoping column, consistent with how most multi-tenant systems this size are built, and every existing query in `history.py` just gains a `WHERE user_id = ?` clause — no wholesale rewrite of the storage layer.

**Pre-existing anonymous rows: left as unattributed and excluded from all per-user views going forward.**
Rather than inventing a fictitious "legacy" user to own old rows (which would misrepresent whose predictions they were), old rows are simply not shown to anyone once this change ships — documented explicitly as a known, deliberate data-migration trade-off, not a silent data loss surprise.

## Risks / Trade-offs

- [Existing anonymous history/samples-based manual testing scripts break] → Documented as a **BREAKING** change in proposal.md; `src/inference_service/verify_api.py` and similar manual scripts need to authenticate first, tracked as an explicit task.
- [Session storage adds new state to reason about (expiry, invalidation)] → Kept minimal: a session is valid until logout or a fixed expiry, no refresh-token complexity.
- [Pre-existing anonymous history becomes invisible to all users] → Acceptable and documented; this is a PoC losing PoC-only demo data, not production data.

## Migration Plan

Additive schema change (new `users`, `sessions` tables; new `user_id` column on `predictions`). Existing rows in `predictions` get `user_id = NULL` and are excluded from all authenticated queries going forward — no attempt to backfill ownership. Rollback: drop the new tables/column and revert the endpoints to their pre-authentication behavior; no data is destroyed by rolling back (the `user_id` column can simply be ignored again).
