"""User accounts and sessions (see specs/user-authentication/spec.md).

SQLite-backed, sharing the same database file as prediction history. Passwords
are hashed with bcrypt; sessions are opaque tokens stored server-side so logout
invalidates them immediately (no JWT expiry window to wait out).
"""
import os
import sqlite3
import time
import uuid

import bcrypt

from . import history

SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days


class IdentifierAlreadyExistsError(Exception):
    """Raised when registration is attempted with an identifier already in use."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials don't match a registered account."""


def _connect():
    os.makedirs(history.HISTORY_DIR, exist_ok=True)
    conn = sqlite3.connect(history.DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    return conn


def register_user(identifier: str, password: str) -> int:
    """Creates a new account. Returns the new user's id. Raises
    IdentifierAlreadyExistsError if the identifier is already registered."""
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = _connect()
    try:
        try:
            cursor = conn.execute(
                "INSERT INTO users (identifier, password_hash, created_at) VALUES (?, ?, ?)",
                (identifier, password_hash, time.time()),
            )
        except sqlite3.IntegrityError as exc:
            raise IdentifierAlreadyExistsError(f"Identifier '{identifier}' is already registered") from exc
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def login(identifier: str, password: str) -> str:
    """Verifies credentials and issues a new session token. Raises
    InvalidCredentialsError if the identifier is unknown or the password is wrong."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE identifier = ?", (identifier,)
        ).fetchone()
        if row is None:
            raise InvalidCredentialsError("Invalid identifier or password")

        user_id, password_hash = row
        if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            raise InvalidCredentialsError("Invalid identifier or password")

        token = uuid.uuid4().hex
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user_id, time.time()),
        )
        conn.commit()
        return token
    finally:
        conn.close()


def logout(token: str) -> None:
    """Invalidates a session token. No-op if the token doesn't exist."""
    conn = _connect()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()


def get_user_id_for_session(token: str):
    """Returns the user_id for a valid, non-expired session token, or None."""
    if not token:
        return None
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT user_id, created_at FROM sessions WHERE token = ?", (token,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    user_id, created_at = row
    if time.time() - created_at > SESSION_TTL_SECONDS:
        return None
    return user_id
