"""API-level tests for /auth/register, /auth/login, /auth/logout, and the
session requirement on protected endpoints (see openspec/changes/add-user-authentication)."""
import os

import pytest
from fastapi.testclient import TestClient

from src.inference_service import history, main

SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), "..", "samples", "healthy_1.jpg")


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


@pytest.fixture
def client():
    return TestClient(main.app)


def test_register_then_login_succeeds(client):
    response = client.post("/auth/register", json={"identifier": "person@example.com", "password": "s3cret"})
    assert response.status_code == 200

    response = client.get("/auth/me")
    assert response.json() == {"authenticated": False}

    response = client.post("/auth/login", json={"identifier": "person@example.com", "password": "s3cret"})
    assert response.status_code == 200

    response = client.get("/auth/me")
    assert response.json() == {"authenticated": True}


def test_duplicate_registration_returns_409(client):
    client.post("/auth/register", json={"identifier": "person@example.com", "password": "s3cret"})
    response = client.post("/auth/register", json={"identifier": "person@example.com", "password": "other"})
    assert response.status_code == 409


def test_login_with_wrong_credentials_returns_401(client):
    client.post("/auth/register", json={"identifier": "person@example.com", "password": "s3cret"})
    response = client.post("/auth/login", json={"identifier": "person@example.com", "password": "wrong"})
    assert response.status_code == 401


def test_logout_invalidates_session_for_protected_endpoints(client):
    client.post("/auth/register", json={"identifier": "person@example.com", "password": "s3cret"})
    client.post("/auth/login", json={"identifier": "person@example.com", "password": "s3cret"})
    assert client.get("/history").status_code == 200

    client.post("/auth/logout")
    assert client.get("/history").status_code == 401


def test_unauthenticated_requests_to_protected_endpoints_are_rejected(client):
    assert client.get("/history").status_code == 401
    assert client.get("/stats").status_code == 401
    assert client.get("/history/export.csv").status_code == 401
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 401


def test_two_users_only_see_their_own_history_and_stats():
    client_a = TestClient(main.app)
    client_a.post("/auth/register", json={"identifier": "a@example.com", "password": "pw"})
    client_a.post("/auth/login", json={"identifier": "a@example.com", "password": "pw"})

    client_b = TestClient(main.app)
    client_b.post("/auth/register", json={"identifier": "b@example.com", "password": "pw"})
    client_b.post("/auth/login", json={"identifier": "b@example.com", "password": "pw"})

    with open(SAMPLE_IMAGE, "rb") as f:
        response = client_a.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 200

    history_a = client_a.get("/history").json()
    history_b = client_b.get("/history").json()
    assert history_a["total"] == 1
    assert history_b["total"] == 0

    stats_a = client_a.get("/stats").json()
    stats_b = client_b.get("/stats").json()
    assert stats_a["total"] == 1
    assert stats_b["total"] == 0
