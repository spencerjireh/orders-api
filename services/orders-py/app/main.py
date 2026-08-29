"""FastAPI application entrypoint for the orders service."""

from fastapi import FastAPI

from app import __version__
from app.routers import health, orders

app = FastAPI(
    title="Orders API",
    description="Demo orders service used as a protected target application.",
    version=__version__,
)

app.include_router(health.router)
app.include_router(orders.router)
