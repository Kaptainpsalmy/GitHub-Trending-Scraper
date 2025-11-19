"""Tests for HTML parser."""
import pytest
from bs4 import BeautifulSoup

from scraper.parser import Parser


class TestParser:
    def test_parse_trending_basic(self, sample_html):
        """Test basic parsing functionality."""
        scraped_at = "2025-11-19T00:00:00Z"
        repos = Parser.parse_trending(sample_html, scraped_at)

        assert len(repos) == 1
        repo = repos[0]

        assert repo["rank"] == 1
        assert repo["repo_name"] == "octocat/Hello-World"
        assert repo["author"] == "octocat"
        assert repo["repository"] == "Hello-World"
        assert repo["description"] == "My first repository on GitHub!"
        assert repo["language"] == "Python"
        assert repo["total_stars"] == 1234
        assert repo["stars_today"] == 250
        assert repo["repo_url"] == "https://github.com/octocat/Hello-World"
        assert repo["scraped_at"] == scraped_at

    def test_parse_trending_empty_html(self):
        """Test parsing empty HTML."""
        with pytest.raises(ValueError, match="Could not find repository elements"):
            Parser.parse_trending("<html></html>", "2025-11-19T00:00:00Z")

    def test_parse_number_with_k_suffix(self):
        """Test parsing numbers with 'k' suffix."""
        assert Parser._parse_number("1.5k") == 1500
        assert Parser._parse_number("2k") == 2000
        assert Parser._parse_number("1,234") == 1234
        assert Parser._parse_number("invalid") is None
        assert Parser._parse_number("") is None

    def test_parse_stars_variations(self):
        """Test parsing different star count formats."""
        html_variations = [
            # Test without stars today
            """
            <article class="Box-row">
                <h2><a href="/test/repo">test/repo</a></h2>
                <p>Test repo</p>
                <div>
                    <span>Python</span>
                    <a href="/test/repo/stargazers">1,234</a>
                </div>
            </article>
            """,
        ]

        for html in html_variations:
            soup = BeautifulSoup(html, "lxml")
            article = soup.find("article")
            stars_data = Parser._parse_stars(article)

            assert "total" in stars_data
            assert "today" in stars_data

    def test_parse_repo_with_missing_elements(self):
        """Test parsing repository with missing elements."""
        incomplete_html = """
        <article class="Box-row">
            <h2><a href="/test/repo">test/repo</a></h2>
            <!-- Missing description and other elements -->
        </article>
        """

        soup = BeautifulSoup(incomplete_html, "lxml")
        article = soup.find("article")
        scraped_at = "2025-11-19T00:00:00Z"

        repo_data = Parser._parse_repo_article(article, 1, scraped_at)
        assert repo_data is not None
        assert repo_data["description"] == ""
        assert repo_data["language"] is None
        assert repo_data["total_stars"] == 0
        assert repo_data["stars_today"] == 0