"""Shared test helpers (see openspec/changes/add-user-authentication)."""
import uuid


def authenticate(client, identifier: str = None, password: str = "test-password"):
    """Registers a fresh user and logs in on the given TestClient, which then
    carries the session cookie for subsequent requests. Returns the identifier used."""
    identifier = identifier or f"user_{uuid.uuid4().hex}@example.com"
    response = client.post("/auth/register", json={"identifier": identifier, "password": password})
    assert response.status_code == 200, response.text
    response = client.post("/auth/login", json={"identifier": identifier, "password": password})
    assert response.status_code == 200, response.text
    return identifier
