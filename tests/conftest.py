"""Pytest configuration and fixtures."""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_html():
    """Sample HTML for testing parser."""
    return """
    <html>
        <body>
            <article class="Box-row">
                <h2 class="h3">
                    <a href="/octocat/Hello-World">octocat / Hello-World</a>
                </h2>
                <p class="col-9">My first repository on GitHub!</p>
                <div class="f6 color-fg-muted mt-2">
                    <span class="d-inline-block ml-0 mr-3">
                        <span class="repo-language-color" style="background-color: #3572A5"></span>
                        <span itemprop="programmingLanguage">Python</span>
                    </span>
                    <a class="Link--muted" href="/octocat/Hello-World/stargazers">
                        <svg aria-label="star" role="img" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
                            <path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"></path>
                        </svg>
                        1,234
                    </a>
                    <a class="Link--muted" href="/octocat/Hello-World/stargazers">
                        <svg aria-label="star" role="img" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
                            <path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"></path>
                        </svg>
                        250 stars today
                    </a>
                </div>
            </article>
        </body>
    </html>
    """


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        yield tmp.name
    os.unlink(tmp.name)


@pytest.fixture
def sample_repo_data():
    """Sample repository data for testing."""
    return {
        "rank": 1,
        "repo_name": "octocat/Hello-World",
        "author": "octocat",
        "repository": "Hello-World",
        "description": "My first repository on GitHub!",
        "language": "Python",
        "total_stars": 1234,
        "stars_today": 250,
        "repo_url": "https://github.com/octocat/Hello-World",
        "scraped_at": "2025-11-19T00:00:00Z"
    }