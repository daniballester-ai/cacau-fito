"""Minimal HTTP API exposing the cacao leaf classifier (see specs/leaf-inference-service),
plus the static upload frontend (see specs/leaf-upload-frontend) served from the same origin."""
import logging
import os

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import history
from .model import SUPPORTED_CONTENT_TYPES, InvalidImageError, LeafClassifier, compute_uncertainty

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


@app.get("/health")
def health():
    return {"status": "ok", "classes": classifier.classes}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
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
        history.record_prediction(result["label"], result["confidence"], result["probabilities"], image_bytes)
    except Exception:
        logger.exception("Failed to record prediction history; continuing without it.")

    return result


@app.get("/history")
def get_history(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    items, total = history.list_predictions(limit=limit, offset=offset)
    next_offset = offset + len(items) if offset + len(items) < total else None
    return {"items": items, "total": total, "next_offset": next_offset}


@app.get("/stats")
def get_stats():
    try:
        total, by_class = history.get_stats()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Prediction stats are temporarily unavailable.") from exc

    return {
        "total": total,
        "by_class": {cls: by_class.get(cls, 0) for cls in classifier.classes},
    }


@app.get("/")
def frontend_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/history.html")
def frontend_history_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))


app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

if os.path.isdir(SAMPLES_DIR):
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

