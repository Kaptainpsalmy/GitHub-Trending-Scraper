"""HTTP fetcher for GitHub Trending with retries and polite delays."""
import time
import logging
from typing import Optional
from urllib.parse import urljoin

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://github.com/trending"


class Fetcher:
    """Handles HTTP requests with retries, rate limiting, and error handling."""

    def __init__(
        self,
        delay: float = 1.0,
        user_agent: str = "github-trending-scraper/1.0 (+https://github.com/user/github-trending-scraper)",
    ):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
            }
        )
        self.last_request_time = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def fetch_trending(
        self, language: Optional[str] = None, since: str = "daily"
    ) -> str:
        """
        Fetch trending page HTML with polite delays and retries.

        Args:
            language: Programming language to filter by (optional)
            since: Time range ('daily', 'weekly', 'monthly')

        Returns:
            HTML content as string

        Raises:
            requests.RequestException: If request fails after retries
        """
        # Respect rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)

        url = self._build_url(language, since)
        logger.info(f"Fetching trending page: {url}")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            if "trending" not in response.url:
                logger.warning(f"Redirected to non-trending page: {response.url}")

            self.last_request_time = time.time()
            return response.text

        except requests.HTTPError as e:
            if response.status_code == 429:
                logger.warning("Rate limited by GitHub, backing off...")
                time.sleep(60)  # Wait 1 minute for rate limit
            logger.error(f"HTTP error {response.status_code} for {url}: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise

    def _build_url(self, language: Optional[str], since: str) -> str:
        """Build the trending URL with query parameters."""
        if language:
            path = f"{language}?since={since}" if since != "daily" else language
        else:
            path = f"?since={since}" if since != "daily" else ""

        return urljoin(BASE_URL, path) if path else BASE_URL