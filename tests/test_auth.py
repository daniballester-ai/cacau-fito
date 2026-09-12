"""Unit tests for src/inference_service/auth.py (see openspec/changes/add-user-authentication)."""
import pytest

from src.inference_service import auth, history


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def test_register_creates_account_with_hashed_password():
    auth.register_user("person@example.com", "s3cret")

    conn = auth._connect()
    try:
        row = conn.execute(
            "SELECT identifier, password_hash FROM users WHERE identifier = ?", ("person@example.com",)
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row[1] != "s3cret"  # not stored in plaintext


def test_duplicate_registration_is_rejected():
    auth.register_user("person@example.com", "s3cret")
    with pytest.raises(auth.IdentifierAlreadyExistsError):
        auth.register_user("person@example.com", "different-password")


def test_login_with_correct_credentials_returns_valid_session():
    auth.register_user("person@example.com", "s3cret")
    token = auth.login("person@example.com", "s3cret")

    assert token
    assert auth.get_user_id_for_session(token) is not None


def test_login_with_wrong_password_is_rejected():
    auth.register_user("person@example.com", "s3cret")
    with pytest.raises(auth.InvalidCredentialsError):
        auth.login("person@example.com", "wrong-password")


def test_login_with_unregistered_identifier_is_rejected():
    with pytest.raises(auth.InvalidCredentialsError):
        auth.login("nobody@example.com", "whatever")


def test_logout_invalidates_the_session():
    auth.register_user("person@example.com", "s3cret")
    token = auth.login("person@example.com", "s3cret")
    assert auth.get_user_id_for_session(token) is not None

    auth.logout(token)
    assert auth.get_user_id_for_session(token) is None
