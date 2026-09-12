## Purpose

Provides complete, example-driven interactive documentation for every CacauFito endpoint, so a person can understand and try the API directly from a browser without reading the source code.

## ADDED Requirements

### Requirement: Documented endpoints
Every public endpoint SHALL have a human-readable summary/description and a documented response schema visible in the interactive API docs.

#### Scenario: Every endpoint has a description
- **WHEN** a person opens the interactive API docs
- **THEN** every listed endpoint shows a non-empty, human-readable description of what it does, not just its path and method

#### Scenario: Response schema is documented, not just typed
- **WHEN** a person inspects an endpoint's response in the interactive docs
- **THEN** the documented response includes field names and realistic example values (e.g., an actual class name and a confidence between 0 and 1), not only bare type annotations

### Requirement: Docs are reachable and interactive
The interactive API docs SHALL be reachable at a known path and allow a person to execute a request against a running instance directly from the docs page.

#### Scenario: Docs page loads and endpoints can be tried
- **WHEN** a person opens the documented docs path on a running instance
- **THEN** the page loads successfully and lets them execute at least one endpoint (e.g., `GET /health`) directly from the page, viewing the real response
