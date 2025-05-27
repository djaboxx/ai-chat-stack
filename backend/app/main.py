"""
Main FastAPI application
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .api import router
from .core.mongodb import mongodb

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Chat Stack Backend",
    description="Backend for React WebSocket Chat Application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"status": "ok", "message": "AI Chat Stack Backend is running"}


@app.on_event("startup")
async def startup():
    """Execute code on application startup"""
    logger.info("Connecting to MongoDB...")
    await mongodb.connect()
    logger.info("MongoDB connection established")


@app.on_event("shutdown")
async def shutdown():
    """Execute code on application shutdown"""
    logger.info("Closing MongoDB connection...")
    await mongodb.close()
    logger.info("MongoDB connection closed")
