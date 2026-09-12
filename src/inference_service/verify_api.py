"""Ad-hoc verification of the inference service using FastAPI's TestClient
(no real server process needed) — exercises the spec scenarios directly:
valid image -> label+confidence, unsupported input -> clear error, not a crash.

Authenticates first: /predict is a protected endpoint since add-user-authentication
(BREAKING change — see openspec/changes/add-user-authentication/proposal.md).
"""
import os
import uuid

from fastapi.testclient import TestClient

from src.inference_service.main import app

client = TestClient(app)

DATA_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "amini")
SAMPLE_IMAGE = os.path.join(DATA_ROOT, "dataset", "images", "train", "ID_cxnsIb.JPG")
EXPECTED_LABEL = "cssvd"

print("== authenticate ==")
identifier = f"verify_api_{uuid.uuid4().hex}@example.com"
password = "verify-api-password"
r = client.post("/auth/register", json={"identifier": identifier, "password": password})
assert r.status_code == 200, r.text
r = client.post("/auth/login", json={"identifier": identifier, "password": password})
assert r.status_code == 200, r.text
print(f"Logged in as {identifier}")

print("== /health ==")
r = client.get("/health")
print(r.status_code, r.json())
assert r.status_code == 200
assert r.json()["classes"] == ["healthy", "cssvd", "anthracnose"]

print("\n== /predict with a known cssvd test image ==")
with open(SAMPLE_IMAGE, "rb") as f:
    r = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
print(r.status_code, r.json())
assert r.status_code == 200
body = r.json()
assert body["label"] in {"healthy", "cssvd", "anthracnose"}
assert 0.0 <= body["confidence"] <= 1.0
print(f"Predicted: {body['label']} (expected ground truth: {EXPECTED_LABEL}) confidence={body['confidence']:.3f}")

print("\n== /predict with an unsupported file type ==")
r = client.post("/predict", files={"file": ("notes.txt", b"not an image", "text/plain")})
print(r.status_code, r.json())
assert r.status_code == 400

print("\n== /predict with a corrupted 'image' (wrong content but jpeg mimetype) ==")
r = client.post("/predict", files={"file": ("fake.jpg", b"\x00\x01garbage", "image/jpeg")})
print(r.status_code, r.json())
assert r.status_code == 400

print("\nAll checks passed.")
