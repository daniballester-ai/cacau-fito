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
            image_path TEXT,
            user_id INTEGER
        )
        """
    )
    _ensure_user_id_column(conn)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            prediction_id INTEGER UNIQUE NOT NULL,
            corrected_label TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    return conn


def _ensure_user_id_column(conn):
    """Adds the user_id column to a pre-existing predictions table that predates
    it (see add-user-authentication design.md — old rows get user_id = NULL and
    are excluded from all per-user views going forward)."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(predictions)").fetchall()}
    if "user_id" not in columns:
        conn.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER")


class PredictionNotFoundError(Exception):
    """Raised when feedback references a prediction ID that doesn't exist in history."""


class FeedbackAlreadyExistsError(Exception):
    """Raised when a second feedback submission is attempted for the same prediction."""


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


def record_prediction(label: str, confidence: float, probabilities: dict, image_bytes: bytes = b"", user_id: int = None) -> None:
    """Persists one history entry, attributed to user_id. Raises on failure — callers
    decide how to handle it (see main.py, which wraps this call so a failure never
    breaks the /predict response)."""
    image_path = _save_image(image_bytes)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO predictions (created_at, label, confidence, probabilities_json, image_path, user_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (time.time(), label, confidence, json.dumps(probabilities), image_path, user_id),
        )
        _enforce_retention(conn)
        conn.commit()
    finally:
        conn.close()


def list_predictions(user_id: int, limit: int = 20, offset: int = 0):
    """Returns (items, total) newest-first, scoped to user_id. items is a list of dicts."""
    conn = _connect()
    try:
        (total,) = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,)
        ).fetchone()
        rows = conn.execute(
            "SELECT id, created_at, label, confidence, probabilities_json, image_path "
            "FROM predictions WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset),
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


def record_feedback(prediction_id: int, label: str) -> None:
    """Records ground-truth feedback for a specific prediction. Raises
    PredictionNotFoundError if prediction_id doesn't exist in history, or
    FeedbackAlreadyExistsError if feedback was already recorded for it."""
    conn = _connect()
    try:
        row = conn.execute("SELECT id FROM predictions WHERE id = ?", (prediction_id,)).fetchone()
        if row is None:
            raise PredictionNotFoundError(f"No prediction found with id {prediction_id}")

        existing = conn.execute(
            "SELECT prediction_id FROM feedback WHERE prediction_id = ?", (prediction_id,)
        ).fetchone()
        if existing is not None:
            raise FeedbackAlreadyExistsError(f"Feedback already recorded for prediction {prediction_id}")

        conn.execute(
            "INSERT INTO feedback (prediction_id, corrected_label, created_at) VALUES (?, ?, ?)",
            (prediction_id, label, time.time()),
        )
        conn.commit()
    finally:
        conn.close()


def get_feedback(prediction_id: int):
    """Returns the recorded corrected_label for a prediction, or None if no feedback exists."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT corrected_label FROM feedback WHERE prediction_id = ?", (prediction_id,)
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def list_all_predictions(user_id: int):
    """Returns every recorded prediction for user_id, newest-first, no pagination.
    Used for the full CSV export (see prediction-history-export capability)."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, created_at, label, confidence, probabilities_json "
            "FROM predictions WHERE user_id = ? ORDER BY created_at DESC, id DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "created_at": row[1],
            "label": row[2],
            "confidence": row[3],
            "probabilities": json.loads(row[4]),
        }
        for row in rows
    ]


def get_stats(user_id: int):
    """Returns (total, by_class) — total prediction count and a label -> count mapping,
    scoped to user_id, for classes that have at least one recorded prediction. Classes
    with zero predictions are not included here; filling in the full known class list
    with zeros is the caller's responsibility (see main.py's /stats route), since this
    module has no knowledge of which classes the classifier supports."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT label, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY label", (user_id,)
        ).fetchall()
    finally:
        conn.close()

    by_class = {label: count for label, count in rows}
    total = sum(by_class.values())
    return total, by_class


def get_stats_timeseries(user_id: int):
    """Returns a list of {"date": "YYYY-MM-DD", "by_class": {label: count}} entries,
    scoped to user_id, one per calendar day that had at least one prediction, ordered
    ascending by date. A day's by_class only contains labels that actually occurred
    that day (see prediction-stats-timeseries spec's "not misreported" scenario) —
    the caller (e.g. the dashboard) is responsible for filling gaps for a continuous chart."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT date(created_at, 'unixepoch') AS day, label, COUNT(*) "
            "FROM predictions WHERE user_id = ? GROUP BY day, label ORDER BY day ASC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    days = {}
    for day, label, count in rows:
        days.setdefault(day, {})[label] = count

    return [{"date": day, "by_class": by_class} for day, by_class in sorted(days.items())]
