"""API-level tests for GET /stats/timeseries (see openspec/changes/add-stats-dashboard)."""
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


@pytest.fixture
def client():
    client = TestClient(main.app)
    authenticate(client)
    return client


def test_timeseries_after_predictions_returns_expected_shape(client):
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 200

    ts = client.get("/stats/timeseries")
    assert ts.status_code == 200
    body = ts.json()
    assert "days" in body
    assert len(body["days"]) == 1
    assert "date" in body["days"][0]
    assert "by_class" in body["days"][0]


def test_stats_lifetime_totals_unchanged_by_timeseries_addition(client):
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 200

    stats = client.get("/stats")
    assert stats.status_code == 200
    body = stats.json()
    assert set(body.keys()) == {"total", "by_class"}
    assert body["total"] == 1
