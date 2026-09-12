## Why

Every prediction, history entry, and stat today belongs to nobody in particular — the system has exactly one shared, anonymous history. To support multiple people using CacauFito independently (each seeing only their own diagnoses), the system needs a notion of user identity. This also changes the frontend's and prediction-history's existing "no authentication required" posture, so those requirements need updating, not just a new capability bolted on.

## What Changes

- The system SHALL let a person register an account and log in with it.
- Submitting a prediction and viewing prediction history/stats SHALL require being logged in.
- Each prediction history entry SHALL be scoped to the user who made it — a user SHALL only see their own history and stats, not other users'.
- **BREAKING**: anonymous, no-login use of the frontend and `/predict` (previously guaranteed by `leaf-upload-frontend`'s "No authentication required" requirement) is replaced by login-gated use.

## Capabilities

### New Capabilities
- `user-authentication`: registration, login/logout, and session management for CacauFito users.

### Modified Capabilities
- `leaf-upload-frontend`: replaces the "No authentication required" requirement with a login-gated requirement — the frontend now requires a logged-in session to upload and predict.
- `prediction-history`: history recording and listing are now scoped per authenticated user; the "History browsing page" requirement's login-free scenario is replaced accordingly.

## Impact

- New `users` table/module for account storage (credentials, session state).
- `src/inference_service/main.py` — new registration/login/logout endpoints; existing `/predict`, `/history`, `/history/export.csv`, `/stats` endpoints require an authenticated session and filter by user.
- `src/inference_service/history.py` — prediction rows gain a `user_id` column; all read/write functions become user-scoped.
- `frontend/` — new login/registration page; existing pages require an active session.
- **BREAKING** for any existing anonymous client/script relying on the previous no-login behavior (e.g., `src/inference_service/verify_api.py`, `samples/`-based manual testing) — these need updating to authenticate first.
