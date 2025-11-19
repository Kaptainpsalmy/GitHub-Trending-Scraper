"""FastAPI application for GitHub Trending API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="GitHub Trending API",
        description="REST API for GitHub Trending repositories data",
        version="1.0.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to your frontend domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "GitHub Trending API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "latest_trending": "/api/v1/trending/latest",
            "filtered_trending": "/api/v1/trending",
            "repo_history": "/api/v1/trending/history",
        },
    }