"""Minimal HTTP API exposing the cacao leaf classifier (see specs/leaf-inference-service),
plus the static upload frontend (see specs/leaf-upload-frontend) served from the same origin."""
import logging
import os

import csv
import io

from fastapi import Body, Cookie, Depends, FastAPI, File, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import auth, history
from .model import SUPPORTED_CONTENT_TYPES, InvalidImageError, LeafClassifier, compute_uncertainty
from .schemas import FeedbackResponse, HealthResponse, HistoryResponse, PredictResponse, StatsResponse

SESSION_COOKIE = "session_token"


def require_user(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> int:
    """FastAPI dependency: resolves the authenticated user for protected endpoints,
    or raises 401 if there's no valid session (see specs/user-authentication)."""
    user_id = auth.get_user_id_for_session(session_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user_id

logger = logging.getLogger(__name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "samples")

app = FastAPI(title="CacauFito Leaf Inference Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = LeafClassifier()


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Check service health",
    description="Confirms the service is up and reports the class labels the loaded model was trained on.",
)
def health():
    return {"status": "ok", "classes": classifier.classes}


@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Classify a cacao leaf photo",
    description=(
        "Accepts a single leaf image (JPEG/PNG/WEBP) and returns the predicted condition "
        "(healthy, cssvd, or anthracnose), a confidence score, the full per-class probability "
        "breakdown, and an uncertainty flag for low-confidence or close-call predictions."
    ),
)
async def predict(file: UploadFile = File(...), user_id: int = Depends(require_user)):
    if file.content_type and file.content_type not in SUPPORTED_CONTENT_TYPES and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Supported: JPEG, PNG, WEBP.",
        )

    image_bytes = await file.read()
    try:
        result = classifier.predict(image_bytes)
    except InvalidImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    is_uncertain, uncertainty_reason = compute_uncertainty(result["probabilities"])
    result["is_uncertain"] = is_uncertain
    result["uncertainty_reason"] = uncertainty_reason

    try:
        history.record_prediction(
            result["label"], result["confidence"], result["probabilities"], image_bytes, user_id=user_id
        )
    except Exception:
        logger.exception("Failed to record prediction history; continuing without it.")

    return result


@app.get(
    "/history",
    response_model=HistoryResponse,
    summary="List recorded predictions",
    description="Returns recorded predictions newest-first, paginated with `limit`/`offset`.",
)
def get_history(
    limit: int = Query(default=20, ge=1, le=100, description="Max entries per page (1-100)."),
    offset: int = Query(default=0, ge=0, description="How many entries to skip from the newest."),
    user_id: int = Depends(require_user),
):
    items, total = history.list_predictions(user_id, limit=limit, offset=offset)
    next_offset = offset + len(items) if offset + len(items) < total else None
    return {"items": items, "total": total, "next_offset": next_offset}


@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Aggregate prediction counts by class",
    description="Returns the total number of predictions recorded and a count per known class (always all 3 classes, zero-filled if never predicted).",
)
def get_stats(user_id: int = Depends(require_user)):
    try:
        total, by_class = history.get_stats(user_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Prediction stats are temporarily unavailable.") from exc

    return {
        "total": total,
        "by_class": {cls: by_class.get(cls, 0) for cls in classifier.classes},
    }


@app.get(
    "/stats/timeseries",
    summary="Prediction counts per day, per class",
    description="Returns a day-bucketed breakdown of predictions per class, covering the full recorded history. Days with no predictions are simply absent (the caller fills gaps for charting).",
)
def get_stats_timeseries(user_id: int = Depends(require_user)):
    return {"days": history.get_stats_timeseries(user_id)}


@app.post(
    "/predict/{prediction_id}/feedback",
    response_model=FeedbackResponse,
    summary="Confirm or correct a past prediction",
    description=(
        "Records ground-truth feedback for a prediction already in history: send the correct "
        "class (same as predicted to confirm, or a different one to correct it). Accepts at "
        "most one feedback per prediction."
    ),
)
def submit_feedback(
    prediction_id: int,
    body: dict = Body(..., examples=[{"label": "cssvd"}]),
):
    label = body.get("label")
    if label not in classifier.classes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid label '{label}'. Supported: {classifier.classes}.",
        )

    try:
        history.record_feedback(prediction_id, label)
    except history.PredictionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except history.FeedbackAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {"prediction_id": prediction_id, "label": label}


@app.get(
    "/history/export.csv",
    summary="Export full prediction history as CSV",
    description="Downloads every recorded prediction (no pagination) as a CSV file, one row per prediction, with per-class probability columns.",
)
def export_history_csv(user_id: int = Depends(require_user)):
    rows = history.list_all_predictions(user_id)
    fieldnames = ["id", "created_at", "label"] + [f"prob_{cls}" for cls in classifier.classes]

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "id": row["id"],
            "created_at": row["created_at"],
            "label": row["label"],
            **{f"prob_{cls}": row["probabilities"].get(cls, "") for cls in classifier.classes},
        })
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prediction_history.csv"},
    )


@app.post(
    "/auth/register",
    summary="Register a new account",
    description="Creates a new account with a unique identifier (e.g. email) and a password.",
)
def auth_register(body: dict = Body(..., examples=[{"identifier": "person@example.com", "password": "s3cret"}])):
    identifier = body.get("identifier")
    password = body.get("password")
    if not identifier or not password:
        raise HTTPException(status_code=400, detail="identifier and password are required.")

    try:
        auth.register_user(identifier, password)
    except auth.IdentifierAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {"identifier": identifier}


@app.post(
    "/auth/login",
    summary="Log in",
    description="Verifies credentials and establishes a session (returned as a cookie).",
)
def auth_login(
    response: Response,
    body: dict = Body(..., examples=[{"identifier": "person@example.com", "password": "s3cret"}]),
):
    identifier = body.get("identifier")
    password = body.get("password")
    if not identifier or not password:
        raise HTTPException(status_code=400, detail="identifier and password are required.")

    try:
        token = auth.login(identifier, password)
    except auth.InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax")
    return {"identifier": identifier}


@app.post(
    "/auth/logout",
    summary="Log out",
    description="Invalidates the current session.",
)
def auth_logout(response: Response, session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    if session_token:
        auth.logout(session_token)
    response.delete_cookie(SESSION_COOKIE)
    return {"status": "ok"}


@app.get(
    "/auth/me",
    summary="Check current session",
    description="Returns whether the caller currently has a valid session.",
)
def auth_me(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    user_id = auth.get_user_id_for_session(session_token)
    return {"authenticated": user_id is not None}


@app.get("/")
def frontend_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/login.html")
def frontend_login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/history.html")
def frontend_history_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))


@app.get("/dashboard.html")
def frontend_dashboard_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

if os.path.isdir(SAMPLES_DIR):
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

