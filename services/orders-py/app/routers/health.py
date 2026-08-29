"""Liveness and readiness endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    time: datetime


@router.get("/health", response_model=HealthResponse, summary="Service health check")
def health() -> HealthResponse:
    return HealthResponse(status="ok", time=datetime.now(UTC))
