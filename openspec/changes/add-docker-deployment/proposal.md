## Why

Running CacauFito today requires manually installing Python dependencies (including PyTorch) into the right environment on the target machine — a real barrier to reproducing or demoing the app anywhere else. A container image makes "clone and run" reliable across machines, which matters for a course deliverable that needs to be demoed live.

## What Changes

- The system SHALL be packaged as a container image that runs the inference service (and serves the frontend) with a single command, without manual dependency installation on the host.
- Model artifacts and persistent data (prediction history database, uploaded-image files) SHALL be mountable from outside the container, so they survive a container restart/rebuild.
- The container SHALL fail fast and clearly if required model artifacts are missing at startup, rather than starting in a broken state that only fails on first request.

## Capabilities

### New Capabilities
- `containerized-deployment`: packages the CacauFito inference service and frontend as a runnable container image with a documented, single-command startup.

### Modified Capabilities
(none — this only changes how the existing system is packaged and run, not its behavior)

## Impact

- New `Dockerfile` and `docker-compose.yml` at the repo root.
- `models/` and `history/` directories mounted as volumes rather than baked into the image (so history persists and the model doesn't need to be re-embedded on every rebuild).
- No change to any existing endpoint or frontend behavior.
