"""FastAPI application setup for quality profiling API.

This module initializes the FastAPI application with:
- CORS middleware for frontend integration
- Error handling middleware
- API routes for repositories, assessments, and benchmarks
- Database initialization
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..storage.connection import initialize_database
from .middleware.errors import ErrorHandlerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup: Initialize database
    try:
        initialize_database(create_schema=True)
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise

    yield

    # Shutdown: Cleanup
    print("Shutting down API server...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title="Ship-Shape Quality Profiling API",
        description="REST API for repository quality assessment, benchmarking, and visualization",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS for frontend integration (allow all origins in dev)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=False,  # Must be False when using wildcard origins
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    # Add error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)

    # Register API routes
    from .routes import assessments, benchmarks, export, health, repositories

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(repositories.router, prefix="/api/v1", tags=["repositories"])
    app.include_router(assessments.router, prefix="/api/v1", tags=["assessments"])
    app.include_router(benchmarks.router, prefix="/api/v1", tags=["benchmarks"])
    app.include_router(export.router, prefix="/api/v1", tags=["export"])

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Ship-Shape Quality Profiling API",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
        }

    return app


# Create application instance
app = create_app()
