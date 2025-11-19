"""API routes for GitHub Trending data."""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from scraper.storage import Storage
from scraper.parser import Parser

router = APIRouter()
storage = Storage()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/trending/latest")
async def get_latest_trending(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[dict]:
    """Get the latest trending repositories."""
    repos = storage.get_latest_repos()
    return [
        {
            "rank": repo.rank,
            "repo_name": repo.repo_name,
            "author": repo.author,
            "repository": repo.repository,
            "description": repo.description,
            "language": repo.language,
            "total_stars": repo.total_stars,
            "stars_today": repo.stars_today,
            "repo_url": repo.repo_url,
            "scraped_at": repo.scraped_at,
        }
        for repo in repos[offset : offset + limit]
    ]


@router.get("/trending")
async def get_filtered_trending(
    language: Optional[str] = Query(None, description="Filter by programming language"),
    since: Optional[str] = Query(None, description="Time range (daily, weekly, monthly)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[dict]:
    """Get filtered trending repositories."""
    repos = storage.get_latest_repos(language=language, since=since)
    return [
        {
            "rank": repo.rank,
            "repo_name": repo.repo_name,
            "author": repo.author,
            "repository": repo.repository,
            "description": repo.description,
            "language": repo.language,
            "total_stars": repo.total_stars,
            "stars_today": repo.stars_today,
            "repo_url": repo.repo_url,
            "scraped_at": repo.scraped_at,
        }
        for repo in repos[offset : offset + limit]
    ]


@router.get("/trending/history")
async def get_repo_history(
    repo: str = Query(..., description="Repository name in format 'author/repo'"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> List[dict]:
    """Get historical data for a specific repository."""
    repos = storage.get_repo_history(repo)
    return [
        {
            "rank": repo.rank,
            "repo_name": repo.repo_name,
            "author": repo.author,
            "repository": repo.repository,
            "description": repo.description,
            "language": repo.language,
            "total_stars": repo.total_stars,
            "stars_today": repo.stars_today,
            "repo_url": repo.repo_url,
            "scraped_at": repo.scraped_at,
        }
        for repo in repos[offset : offset + limit]
    ]