## 1. Container Image

- [x] 1.1 Write a `Dockerfile` (base `python:3.12-slim`, CPU-only torch/torchvision, copies `src/`, `frontend/`, `samples/`) and a `.dockerignore` excluding `data/amini/dataset/`, `.git/`, `history/`, and verify `docker build` succeeds
- [x] 1.2 Verify the built image, run standalone with `models/` mounted, serves `GET /health` successfully

## 2. Compose and Volumes

- [x] 2.1 Write `docker-compose.yml` mounting `models/` and `history/` as volumes and exposing port 8000, and verify `docker compose up` starts the service reachable at `http://localhost:8000`
- [x] 2.2 Verify prediction history recorded in one `docker compose up` session is still present after `docker compose down` + `docker compose up` again (same volumes)

## 3. Fail-Fast Verification

- [x] 3.1 Verify starting the container with an empty/missing `models/` volume fails at startup with a clear error, and the container does not stay up serving broken requests

## 4. Documentation

- [x] 4.1 Document the single-command startup (`docker compose up`) in `README.md`, replacing/augmenting the existing manual `pip install` + `uvicorn` instructions
