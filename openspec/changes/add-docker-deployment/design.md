## Context

See proposal.md for motivation. `src/inference_service/main.py` already loads the model artifact eagerly at import time (`classifier = LeafClassifier()`), which already fails fast if `models/*.pt`/`label_mapping.json` are missing — this capability mostly needs to preserve that behavior inside a container rather than invent it. `history.py`'s SQLite database and image files already live under a `history/` directory relative to the repo root, which maps naturally onto a Docker volume.

## Goals / Non-Goals

**Goals:**
- Make "clone and run" reliable on any machine with Docker installed.
- Keep `models/` and `history/` as externally-mountable directories, not baked into the image.

**Non-Goals:**
- Multi-container orchestration (e.g., a separate database container) — this PoC's SQLite file doesn't need one.
- Production concerns like horizontal scaling, HTTPS termination, or a reverse proxy — out of scope for a course PoC.
- GPU support inside the container — inference runs on CPU (as it already does outside Docker); training remains a separate, Kaggle-GPU-based process (`notebooks/`), not something this container runs.

## Decisions

**Base image: an official `python:3.12-slim` image, with CPU-only PyTorch/torchvision installed via pip.**
Matches the project's already-CPU-only inference path (see `models/verify_reload.py`, which already runs on CPU) — no CUDA base image needed, keeping the image smaller and avoiding GPU driver complexity that a demo machine likely doesn't have anyway.

**Volumes: `models/` and `history/` mounted from the host via `docker-compose.yml`, not copied into the image.**
Keeps the image itself small and stateless — rebuilding the image (e.g., after a code change) never touches the trained model or accumulated history, and history genuinely persists across container recreation, per the spec's requirement.

**Fail-fast: preserved as-is from the existing eager model load in `main.py`; no new code needed, just verified inside the container.**
The existing `LeafClassifier.__init__` already raises on a missing `models/label_mapping.json` or `.pt` file — Docker just needs to not swallow that startup failure silently (verified via `docker compose up` showing a clear error and a non-running container, not a silently-crash-looping one).

## Risks / Trade-offs

- [Image size from PyTorch/torchvision, even CPU-only, is non-trivial (several hundred MB)] → Acceptable for a course PoC; not optimized further (e.g., no multi-stage build slimming) given the scope.
- [`data/amini/dataset/` (9.6GB, gitignored) must not be baked into the image] → Explicitly excluded via a `.dockerignore`, mirroring the existing `.gitignore` exclusions.
