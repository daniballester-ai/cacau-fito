## 1. Storage Layer

- [x] 1.1 Create the SQLite schema (`id, created_at, label, confidence, probabilities_json, image_path`) and a small storage module with `record_prediction()` and `list_predictions(limit, offset)` functions, and verify a unit test can insert a row and read it back — DONE: `src/inference_service/history.py`; `tests/test_history.py::test_record_and_read_back` passes
- [x] 1.2 Implement bounded retention (evict oldest row + its image file when the 200-entry cap would be exceeded on insert), and verify a test inserting 201 entries ends with exactly 200 rows and the oldest image file removed from disk — DONE: `_enforce_retention()`; `test_retention_evicts_oldest_and_its_image_file` passes
- [x] 1.3 Implement image file writing to `history/images/` with a generated unique filename per entry, and verify a written file is readable back and its path matches the stored `image_path` — DONE: `_save_image()`; `test_image_file_written_and_path_matches_stored_reference` passes

## 2. Recording Integration

- [x] 2.1 Call `record_prediction()` from the `/predict` handler after a successful classification, and verify a manual `/predict` call results in exactly one new row in storage — DONE: manual `/predict` + `/history` check confirmed exactly 1 row
- [x] 2.2 Wrap the recording call so any failure (storage or image write) is caught and logged without affecting the `/predict` response, and verify a test that forces a storage failure still returns a normal 200 prediction response — DONE: try/except around `history.record_prediction()` in `main.py`; `tests/test_predict_history_integration.py` passes
- [x] 2.3 Verify a rejected upload (invalid/unsupported file, per existing `/predict` validation) does not create a history entry — DONE: manual test with a `.md` file returned 400 and `/history` total stayed at 1

## 3. History API

- [x] 3.1 Implement `GET /history?limit=&offset=` (default limit 20, max 100) returning `{items, total, next_offset}` ordered newest-first, and verify a test with several recorded predictions returns them in the correct order — DONE: `main.py`'s `get_history()`; `tests/test_history_api.py::test_history_lists_predictions_newest_first` passes
- [x] 3.2 Verify pagination: requesting a page smaller than the total returns only that page's entries and a usable `next_offset` — DONE: `test_history_pagination_returns_only_requested_page_and_next_offset` passes
- [x] 3.3 Verify the empty-history case: calling `/history` with nothing recorded returns an empty `items` list, not an error — DONE: `test_history_empty_returns_empty_list_not_error` passes

## 4. History Page

- [x] 4.1 Build `frontend/history.html` (+ any needed static JS/CSS) that fetches `/history` and displays label, confidence, and timestamp per entry, served the same way as `index.html`, and verify manually loading the page after making a few predictions shows them newest-first — DONE: `frontend/history.html` + `frontend/static/history.js`, served via `/history.html`; verified in real headless Chrome (Playwright) — 3 predictions rendered newest-first with correct labels/confidence/timestamps. Found and fixed a real bug along the way: the `[hidden]` attribute was being overridden by `.btn`'s `display: inline-flex` (CSS specificity), so hidden buttons stayed visible — added a `[hidden] { display: none !important; }` rule, fixing it for this page and the existing "Limpar" button on the main page too
- [x] 4.2 Add an empty-state message shown when `/history` returns no items, and verify manually that a fresh/empty history shows this message instead of a blank page — DONE: verified in the same browser session with an empty history store
- [x] 4.3 Verify no login or authentication is required to view the history page or call `/history` — DONE: no auth exists on `/history.html` or `/history`; both browser test cases completed with no login step

## 5. Documentation

- [x] 5.1 Document the retention limit, storage location, and known limitation (history lost if storage is ephemeral) in a short note (e.g., `docs/prediction-history.md` or an addition to `docs/limitations_and_next_steps.md`), and verify the note is present and accurate — DONE: `docs/prediction-history.md`
