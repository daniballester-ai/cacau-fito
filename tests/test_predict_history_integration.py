"""Integration tests: /predict must keep working even if history recording fails
(see openspec/changes/add-prediction-history, task 2.2)."""
import os

import pytest
from fastapi.testclient import TestClient

from src.inference_service import history, main
from tests.conftest import authenticate

SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), "..", "samples", "healthy_1.jpg")


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def test_predict_succeeds_even_if_history_recording_fails(monkeypatch):
    def broken_record_prediction(*args, **kwargs):
        raise RuntimeError("simulated storage failure")

    monkeypatch.setattr(main.history, "record_prediction", broken_record_prediction)

    client = TestClient(main.app)
    authenticate(client)
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert body["label"] in {"healthy", "cssvd", "anthracnose"}
    assert 0.0 <= body["confidence"] <= 1.0
