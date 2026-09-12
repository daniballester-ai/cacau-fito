## 1. User Storage and Password Hashing

- [ ] 1.1 Create the `users` table (`id, identifier UNIQUE, password_hash, created_at`) and `register_user(identifier, password)` using a standard password-hashing library (e.g., `passlib`/bcrypt), and verify a unit test registers a user and confirms the password is not stored in plaintext
- [ ] 1.2 Verify registering with an already-used identifier is rejected without creating a second account

## 2. Sessions and Login

- [ ] 2.1 Create the `sessions` table and `login(identifier, password)` verifying credentials and issuing a session, and verify a unit test logs in with correct credentials and receives a valid session
- [ ] 2.2 Verify login with incorrect credentials is rejected and no session is created
- [ ] 2.3 Implement `logout(session)` invalidating the session, and verify a logged-out session is no longer accepted by protected endpoints

## 3. API Integration

- [ ] 3.1 Add `POST /auth/register`, `POST /auth/login`, `POST /auth/logout` endpoints in `src/inference_service/main.py`, and verify manual requests for each succeed/fail as expected
- [ ] 3.2 Add a session-required dependency and apply it to `/predict`, `/history`, `/history/export.csv`, and `/stats`, and verify an unauthenticated request to each now returns an authentication error instead of succeeding
- [ ] 3.3 Add `user_id` to the `predictions` table and scope `record_prediction()`, `list_predictions()`, and `get_stats()` by the authenticated user, and verify two different logged-in users only ever see their own predictions in history and stats

## 4. Frontend Integration

- [ ] 4.1 Build a minimal login/registration page, and verify manually that a logged-out visitor is directed to it instead of reaching the upload page
- [ ] 4.2 Verify manually that a logged-in user can upload and predict as before, and that logging out then revisiting the upload page redirects to login again

## 5. Update Existing Scripts for the Breaking Change

- [ ] 5.1 Update `src/inference_service/verify_api.py` (and any other anonymous manual-test script) to authenticate first, per the BREAKING change noted in proposal.md
- [ ] 5.2 Run the full test suite (`python -m pytest tests/ -v`), updating existing tests that assumed anonymous access, and confirm everything passes under the new authenticated flow
