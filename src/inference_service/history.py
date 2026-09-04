"""Prediction history storage (see specs/prediction-history/spec.md).

SQLite-backed, one row per successfully returned prediction. Bounded to
RETENTION_LIMIT rows; the oldest row (and its image file, if any) is evicted
whenever a new insert would exceed the cap.
"""
import json
import os
import sqlite3
import time
import uuid

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "history")
IMAGES_DIR = os.path.join(HISTORY_DIR, "images")
DB_PATH = os.path.join(HISTORY_DIR, "history.db")

RETENTION_LIMIT = 200


def _connect():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at REAL NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities_json TEXT NOT NULL,
            image_path TEXT
        )
        """
    )
    return conn


def _save_image(image_bytes: bytes) -> str | None:
    """Best-effort image write. Returns the stored file path, or None on failure."""
    if not image_bytes:
        return None
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.jpg"
        path = os.path.join(IMAGES_DIR, filename)
        with open(path, "wb") as f:
            f.write(image_bytes)
        return path
    except OSError:
        return None


def _enforce_retention(conn):
    (count,) = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()
    overflow = count - RETENTION_LIMIT
    if overflow <= 0:
        return
    rows = conn.execute(
        "SELECT id, image_path FROM predictions ORDER BY created_at ASC, id ASC LIMIT ?",
        (overflow,),
    ).fetchall()
    for row_id, image_path in rows:
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass
        conn.execute("DELETE FROM predictions WHERE id = ?", (row_id,))


def record_prediction(label: str, confidence: float, probabilities: dict, image_bytes: bytes = b"") -> None:
    """Persists one history entry. Raises on failure — callers decide how to handle it
    (see main.py, which wraps this call so a failure never breaks the /predict response)."""
    image_path = _save_image(image_bytes)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO predictions (created_at, label, confidence, probabilities_json, image_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (time.time(), label, confidence, json.dumps(probabilities), image_path),
        )
        _enforce_retention(conn)
        conn.commit()
    finally:
        conn.close()


def list_predictions(limit: int = 20, offset: int = 0):
    """Returns (items, total) newest-first. items is a list of dicts."""
    conn = _connect()
    try:
        (total,) = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()
        rows = conn.execute(
            "SELECT id, created_at, label, confidence, probabilities_json, image_path "
            "FROM predictions ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    finally:
        conn.close()

    items = [
        {
            "id": row[0],
            "created_at": row[1],
            "label": row[2],
            "confidence": row[3],
            "probabilities": json.loads(row[4]),
        }
        for row in rows
    ]
    return items, total


def get_stats():
    """Returns (total, by_class) — total prediction count and a label -> count mapping
    for classes that have at least one recorded prediction. Classes with zero
    predictions are not included here; filling in the full known class list with
    zeros is the caller's responsibility (see main.py's /stats route), since this
    module has no knowledge of which classes the classifier supports."""
    conn = _connect()
    try:
        rows = conn.execute("SELECT label, COUNT(*) FROM predictions GROUP BY label").fetchall()
    finally:
        conn.close()

    by_class = {label: count for label, count in rows}
    total = sum(by_class.values())
    return total, by_class
