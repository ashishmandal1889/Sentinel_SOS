"""
Sentinel SOS - Main Application Entrypoint.

Initializes FastAPI application, registers middleware, mounts API routers,
configures centralized error handlers, and manages startup/shutdown lifecycle.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.db.mongodb import mongo_manager
from app.db.sql import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events cleanly."""
    logger.info(f"Starting {settings.SENTINEL_APP_NAME} in [{settings.SENTINEL_ENV}] mode.")

    # Automatically create tables for dev/testing environment
    if settings.is_development or settings.is_testing:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("SQL database schema verified/created successfully.")
        except Exception as e:
            logger.error(f"SQL database initialization warning: {e}")

        # Initialize MongoDB indexes if connected
        try:
            mongo_manager.init_indexes()
        except Exception as e:
            logger.warning(f"MongoDB index initialization deferred: {e}")

    yield

    logger.info("Shutting down Sentinel SOS application.")
    mongo_manager.close()


app = FastAPI(
    title=settings.SENTINEL_APP_NAME,
    description="Intelligent Emergency-Response Management System API Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.SENTINEL_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized exception handlers
register_exception_handlers(app)

# Include API v1 router under configured prefix
app.include_router(api_router, prefix=settings.SENTINEL_API_PREFIX)

# Also expose basic health probe at root and /health for standard load balancers
@app.get("/", tags=["Health"])
def root():
    return {
        "name": settings.SENTINEL_APP_NAME,
        "environment": settings.SENTINEL_ENV,
        "docs": "/docs",
        "api_v1": f"{settings.SENTINEL_API_PREFIX}/health",
    }


@app.get("/health", tags=["Health"])
def root_health():
    return {"status": "ok", "app": settings.SENTINEL_APP_NAME}


@app.get("/api/health", tags=["Health"])
def api_health():
    """Backward-compatible health endpoint."""
    return {"status": "ok", "version": "1.0.0"}
