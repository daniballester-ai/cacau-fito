## Context

See proposal.md for motivation. FastAPI already generates OpenAPI/Swagger UI docs at `/docs` (and ReDoc at `/redoc`) for free from route signatures — this capability is about filling in the metadata FastAPI uses to make those docs meaningful (descriptions, response models, examples), not building a docs system from scratch.

## Goals / Non-Goals

**Goals:**
- Make the existing, already-reachable `/docs` page actually useful by attaching descriptions/examples to every route.

**Non-Goals:**
- A custom-built documentation site or static docs generator — FastAPI's built-in Swagger UI is sufficient and is what the requirement asks for.
- API versioning documentation — out of scope; this project has one API version.

## Decisions

**Mechanism: FastAPI's native `response_model`, `summary`, `description`, and `responses=` example parameters on each route decorator, plus Pydantic models replacing ad-hoc dicts where useful.**
This is the idiomatic, zero-new-dependency way to enrich FastAPI's auto-generated OpenAPI schema — no separate documentation tool or generator needed, keeping this purely additive metadata on existing routes.

**Scope: cover every endpoint that exists at the time this change is implemented** (health, predict, history, history export, stats, stats timeseries, and the auth endpoints from `add-user-authentication` if merged first).
Since the proposal's requirement is "every public endpoint," this is a sweep across the whole `main.py` router rather than a partial pass — documented explicitly so it's clear at implementation time which endpoints must be covered.

## Risks / Trade-offs

- [New endpoints added after this change ships won't automatically have descriptions] → Acceptable; this is a one-time completeness pass, not an enforced ongoing check (no CI gate is in scope here).
