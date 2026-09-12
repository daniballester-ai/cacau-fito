"""Pydantic response models for the interactive API docs (see
specs/interactive-api-docs/spec.md). These only document existing response
shapes — no endpoint behavior changes."""
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    classes: list[str] = Field(..., json_schema_extra={"example": ["healthy", "cssvd", "anthracnose"]})


class PredictResponse(BaseModel):
    label: str = Field(..., json_schema_extra={"example": "healthy"})
    confidence: float = Field(..., ge=0, le=1, json_schema_extra={"example": 0.94})
    probabilities: dict[str, float] = Field(
        ...,
        json_schema_extra={"example": {"healthy": 0.94, "cssvd": 0.04, "anthracnose": 0.02}},
    )
    is_uncertain: bool = Field(..., json_schema_extra={"example": False})
    uncertainty_reason: str | None = Field(None, json_schema_extra={"example": None})


class HistoryItem(BaseModel):
    id: int = Field(..., json_schema_extra={"example": 42})
    created_at: float = Field(..., json_schema_extra={"example": 1757600000.0})
    label: str = Field(..., json_schema_extra={"example": "cssvd"})
    confidence: float = Field(..., ge=0, le=1, json_schema_extra={"example": 0.81})
    probabilities: dict[str, float] = Field(
        ...,
        json_schema_extra={"example": {"healthy": 0.1, "cssvd": 0.81, "anthracnose": 0.09}},
    )


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int = Field(..., json_schema_extra={"example": 3})
    next_offset: int | None = Field(None, json_schema_extra={"example": None})


class StatsResponse(BaseModel):
    total: int = Field(..., json_schema_extra={"example": 12})
    by_class: dict[str, int] = Field(
        ...,
        json_schema_extra={"example": {"healthy": 5, "cssvd": 4, "anthracnose": 3}},
    )


class FeedbackResponse(BaseModel):
    prediction_id: int = Field(..., json_schema_extra={"example": 42})
    label: str = Field(..., json_schema_extra={"example": "cssvd"})
