## 1. Response Models

- [ ] 1.1 Define Pydantic response models for `/predict`, `/history`, `/stats`, and any other JSON-returning endpoint in `src/inference_service/main.py` (or a new `schemas.py`), and verify `/docs` shows named fields instead of bare dicts

## 2. Descriptions and Examples

- [ ] 2.1 Add `summary`, `description`, and realistic response examples to every route decorator, and verify each endpoint listed in `/docs` shows a non-empty description
- [ ] 2.2 Verify response examples show realistic values (e.g., an actual class name, confidence between 0 and 1) rather than placeholder/generic values

## 3. Verification

- [ ] 3.1 Manually open `/docs` on a running instance and execute `GET /health` directly from the page, and verify the real response is shown
- [ ] 3.2 Run the full test suite (`python -m pytest tests/ -v`) and confirm all existing tests still pass (this change must not alter any endpoint's actual behavior)
