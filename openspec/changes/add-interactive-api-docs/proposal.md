## Why

FastAPI already auto-generates interactive docs, but CacauFito's endpoints have no descriptions, response schemas, or examples attached — the generated docs today just list bare paths and generic types, which isn't useful for someone trying to understand or try the API without reading the source code.

## What Changes

- Every public endpoint (`/predict`, `/history`, `/history/export.csv`, `/stats`, `/stats/timeseries`, auth endpoints, etc.) SHALL have a human-readable description and a documented response schema in the interactive API docs.
- The interactive docs SHALL be reachable at a known path and let a person try each endpoint directly from the browser (FastAPI's built-in capability, made complete rather than left at defaults).
- Response examples SHALL reflect realistic values (e.g., a real class name and confidence range), not just bare type names.

## Capabilities

### New Capabilities
- `interactive-api-docs`: complete, example-driven interactive documentation for every CacauFito endpoint, reachable and usable directly from a browser.

### Modified Capabilities
(none — this only adds documentation/metadata to existing endpoints, not new behavior)

## Impact

- `src/inference_service/main.py` — add FastAPI `response_model`, `summary`, `description`, and example values to every route.
- No change to any endpoint's actual request/response behavior — this is documentation-only.
