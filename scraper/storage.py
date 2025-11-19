"""Data storage for GitHub Trending repositories."""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from sqlmodel import SQLModel, Field, Session, create_engine, select

logger = logging.getLogger(__name__)


class TrendingRepo(SQLModel, table=True):
    """SQLModel for trending repositories."""

    __tablename__ = "trending"

    id: Optional[int] = Field(default=None, primary_key=True)
    rank: int
    repo_name: str = Field(index=True)
    author: str
    repository: str
    description: str
    language: Optional[str] = Field(default=None, index=True)
    total_stars: int
    stars_today: int
    repo_url: str
    scraped_at: str = Field(index=True)


class Storage:
    """Handles data storage to CSV, JSON, and SQLite."""

    def __init__(self, data_dir: str = "data", db_path: str = "data/github.db"):
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self._setup_directories()
        self._setup_database()

    def _setup_directories(self) -> None:
        """Create necessary directories."""
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "backups").mkdir(exist_ok=True)

    def _setup_database(self) -> None:
        """Initialize SQLite database with tables."""
        engine = create_engine(f"sqlite:///{self.db_path}")
        SQLModel.metadata.create_all(engine)

    def save_to_files(self, repos: List[Dict[str, Any]]) -> None:
        """Save repositories to CSV and JSON files."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Save to CSV
        csv_path = self.data_dir / "trending.csv"
        df = pd.DataFrame(repos)

        if csv_path.exists():
            # Append with timestamp for history
            backup_path = self.data_dir / "backups" / f"trending_{timestamp}.csv"
            df.to_csv(backup_path, index=False)
            logger.info(f"Created backup: {backup_path}")

        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(repos)} repos to {csv_path}")

        # Save to JSON
        json_path = self.data_dir / "trending.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(repos, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(repos)} repos to {json_path}")

    def save_to_database(self, repos: List[Dict[str, Any]]) -> None:
        """Save repositories to SQLite database."""
        engine = create_engine(f"sqlite:///{self.db_path}")

        with Session(engine) as session:
            for repo_data in repos:
                # Check if this repo already exists for this scrape time
                existing = session.exec(
                    select(TrendingRepo).where(
                        TrendingRepo.repo_name == repo_data["repo_name"],
                        TrendingRepo.scraped_at == repo_data["scraped_at"],
                    )
                ).first()

                if not existing:
                    repo = TrendingRepo(**repo_data)
                    session.add(repo)

            session.commit()

        logger.info(f"Saved {len(repos)} repos to database")

    def get_latest_repos(
        self, language: Optional[str] = None, since: Optional[str] = None
    ) -> List[TrendingRepo]:
        """Get latest repositories from database with optional filtering."""
        engine = create_engine(f"sqlite:///{self.db_path}")

        with Session(engine) as session:
            # Get the most recent scrape time
            latest_scrape = session.exec(
                select(TrendingRepo.scraped_at).order_by(TrendingRepo.scraped_at.desc()).limit(1)
            ).first()

            if not latest_scrape:
                return []

            # Build query
            query = select(TrendingRepo).where(TrendingRepo.scraped_at == latest_scrape)

            if language:
                query = query.where(TrendingRepo.language == language)

            if since:
                # This would require additional logic for time-based filtering
                # For now, we rely on the scraped_at timestamp
                pass

            repos = session.exec(query.order_by(TrendingRepo.rank)).all()
            return list(repos)

    def get_repo_history(self, repo_name: str) -> List[TrendingRepo]:
        """Get historical data for a specific repository."""
        engine = create_engine(f"sqlite:///{self.db_path}")

        with Session(engine) as session:
            repos = session.exec(
                select(TrendingRepo)
                .where(TrendingRepo.repo_name == repo_name)
                .order_by(TrendingRepo.scraped_at.desc())
            ).all()
            return list(repos)