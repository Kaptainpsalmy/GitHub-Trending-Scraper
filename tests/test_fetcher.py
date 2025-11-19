"""Tests for HTTP fetcher."""
import pytest
import requests_mock
from scraper.fetcher import Fetcher


class TestFetcher:
    def test_build_url_default(self):
        """Test URL building with default parameters."""
        fetcher = Fetcher()
        url = fetcher._build_url(None, "daily")
        assert url == "https://github.com/trending"

    def test_build_url_with_language(self):
        """Test URL building with language filter."""
        fetcher = Fetcher()
        url = fetcher._build_url("python", "daily")
        assert url == "https://github.com/trending/python"

    def test_build_url_with_since(self):
        """Test URL building with time range."""
        fetcher = Fetcher()
        url = fetcher._build_url(None, "weekly")
        assert url == "https://github.com/trending?since=weekly"

    def test_build_url_with_language_and_since(self):
        """Test URL building with both language and time range."""
        fetcher = Fetcher()
        url = fetcher._build_url("python", "monthly")
        assert url == "https://github.com/trending/python?since=monthly"

    def test_fetch_trending_success(self):
        """Test successful trending page fetch."""
        fetcher = Fetcher(delay=0)

        with requests_mock.Mocker() as m:
            m.get("https://github.com/trending", text="<html>trending page</html>")

            html = fetcher.fetch_trending()
            assert html == "<html>trending page</html>"

    def test_fetch_trending_with_language(self):
        """Test fetching trending page with language filter."""
        fetcher = Fetcher(delay=0)

        with requests_mock.Mocker() as m:
            m.get("https://github.com/trending/python", text="<html>python trending</html>")

            html = fetcher.fetch_trending(language="python")
            assert html == "<html>python trending</html>"

    @pytest.mark.skip("Rate limiting test requires specific setup")
    def test_fetch_trending_rate_limit(self):
        """Test handling of rate limiting."""
        # This would test the 429 response handling
        pass