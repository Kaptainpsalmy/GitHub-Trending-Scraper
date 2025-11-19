"""Tests for data storage."""
import pytest
import json
import pandas as pd
from pathlib import Path

from scraper.storage import Storage, TrendingRepo
from sqlmodel import Session, select


class TestStorage:
    def test_save_to_files(self, temp_db, sample_repo_data, tmp_path):
        """Test saving repositories to CSV and JSON files."""
        storage = Storage(data_dir=str(tmp_path), db_path=temp_db)
        repos = [sample_repo_data]

        storage.save_to_files(repos)

        # Check CSV file
        csv_path = tmp_path / "trending.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 1
        assert df.iloc[0]["repo_name"] == "octocat/Hello-World"

        # Check JSON file
        json_path = tmp_path / "trending.json"
        assert json_path.exists()
        with open(json_path, "r") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["repo_name"] == "octocat/Hello-World"

    def test_save_to_database(self, temp_db, sample_repo_data):
        """Test saving repositories to database."""
        storage = Storage(data_dir="data", db_path=temp_db)
        repos = [sample_repo_data]

        storage.save_to_database(repos)

        # Verify data in database
        engine = storage._setup_database()
        with Session(engine) as session:
            results = session.exec(select(TrendingRepo)).all()
            assert len(results) == 1
            repo = results[0]
            assert repo.repo_name == "octocat/Hello-World"
            assert repo.author == "octocat"
            assert repo.total_stars == 1234

    def test_get_latest_repos(self, temp_db, sample_repo_data):
        """Test retrieving latest repositories from database."""
        storage = Storage(data_dir="data", db_path=temp_db)

        # Add test data
        storage.save_to_database([sample_repo_data])

        # Retrieve latest
        latest_repos = storage.get_latest_repos()
        assert len(latest_repos) == 1
        assert latest_repos[0].repo_name == "octocat/Hello-World"

    def test_get_repo_history(self, temp_db, sample_repo_data):
        """Test retrieving repository history."""
        storage = Storage(data_dir="data", db_path=temp_db)

        # Add multiple entries for same repo
        repo1 = sample_repo_data.copy()
        repo2 = sample_repo_data.copy()
        repo2["scraped_at"] = "2025-11-20T00:00:00Z"
        repo2["stars_today"] = 300

        storage.save_to_database([repo1, repo2])

        # Get history
        history = storage.get_repo_history("octocat/Hello-World")
        assert len(history) == 2
        assert history[0].stars_today == 300  # Most recent first
        assert history[1].stars_today == 250

    def test_filter_repos_by_language(self, temp_db, sample_repo_data):
        """Test filtering repositories by language."""
        storage = Storage(data_dir="data", db_path=temp_db)

        # Add repos with different languages
        python_repo = sample_repo_data.copy()
        js_repo = sample_repo_data.copy()
        js_repo["repo_name"] = "test/javascript-repo"
        js_repo["language"] = "JavaScript"

        storage.save_to_database([python_repo, js_repo])

        # Filter by Python
        python_repos = storage.get_latest_repos(language="Python")
        assert len(python_repos) == 1
        assert python_repos[0].language == "Python"

        # Filter by JavaScript
        js_repos = storage.get_latest_repos(language="JavaScript")
        assert len(js_repos) == 1
        assert js_repos[0].language == "JavaScript"