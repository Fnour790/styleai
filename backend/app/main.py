"""
StyleAI Backend — FastAPI application.

Startup sequence:
1. Load FashionCLIP model into memory
2. Ensure Qdrant collection exists
3. Mount routes
4. Serve static uploads
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import get_settings
from app.ai.clip_tagger import fashion_tagger
from app.services.qdrant_service import qdrant_service
from app.api.routes import wardrobe, recommendations, chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once at startup and once at shutdown."""
    logger.info("═══ StyleAI starting up ═══")

    # Load ML model (takes ~10–20s first time, instant after)
    try:
        fashion_tagger.load()
    except Exception as e:
        logger.warning(f"FashionCLIP load failed (AI tagging disabled): {e}")

    # Ensure Qdrant collection
    try:
        qdrant_service.ensure_collection()
    except Exception as e:
        logger.warning(f"Qdrant not available: {e}")

    # Ensure uploads dir exists
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    logger.info("StyleAI ready ✓")
    yield
    logger.info("StyleAI shutting down")


app = FastAPI(
    title="StyleAI API",
    description="AI-powered personal stylist backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(wardrobe.router)
app.include_router(recommendations.router)
app.include_router(chat.router)

# Serve uploaded clothing images as static files
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": fashion_tagger._loaded,
        "env": settings.app_env,
    }


@app.get("/")
def root():
    return {"message": "StyleAI API", "docs": "/docs"}
