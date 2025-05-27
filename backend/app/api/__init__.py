"""
API router initialization
"""
from fastapi import APIRouter
from .ws_endpoint import router as ws_router

# Create a root router
router = APIRouter()

# Include the WebSocket endpoints
router.include_router(ws_router)
