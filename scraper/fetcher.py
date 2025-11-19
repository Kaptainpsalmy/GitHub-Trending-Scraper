"""HTTP fetcher for GitHub Trending with retries and polite delays."""
# Import the time module for handling delays and timing between requests
import time
# Import logging module to track events and errors during HTTP requests
import logging
# Import Optional for type hints to indicate parameters that can be None
from typing import Optional
# Import urljoin to safely combine base URL with paths and query parameters
from urllib.parse import urljoin

# Import requests library for making HTTP requests to GitHub
import requests
# Import retry decorator and related utilities from tenacity for automatic retries
from tenacity import (
    retry,  # Main decorator to add retry behavior to functions
    stop_after_attempt,  # Stop retrying after specified number of attempts
    wait_exponential,  # Wait with exponential backoff between retries
    retry_if_exception_type,  # Only retry on specific exception types
    before_sleep_log,  # Log a message before sleeping between retries
)

# Create a logger instance specifically for this module to track fetcher activities
logger = logging.getLogger(__name__)

# Define the base URL for GitHub's trending page that we'll be scraping
BASE_URL = "https://github.com/trending"


class Fetcher:
    """Handles HTTP requests with retries, rate limiting, and error handling."""

    def __init__(
        self,
        # Set default delay between requests to 1.0 seconds to be polite to GitHub's servers
        delay: float = 1.0,
        # Define a user agent string to identify our scraper to GitHub
        user_agent: str = "github-trending-scraper/1.0 (+https://github.com/user/github-trending-scraper)",
    ):
        # Store the delay value as an instance variable for use in request timing
        self.delay = delay
        # Create a requests Session object to maintain connection pooling and headers
        self.session = requests.Session()
        # Update the session headers with proper HTTP headers to mimic a real browser
        self.session.headers.update(
            {
                # User-Agent identifies our scraper to the server
                "User-Agent": user_agent,
                # Accept header tells server what content types we can handle
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                # Accept-Language specifies our preferred language for responses
                "Accept-Language": "en-US,en;q=0.5",
                # Accept-Encoding specifies what compression algorithms we support
                "Accept-Encoding": "gzip, deflate, br",
            }
        )
        # Initialize last_request_time to 0 so first request isn't delayed
        self.last_request_time = 0

    # Apply retry decorator with specific configuration for handling failed requests
    @retry(
        # Stop retrying after 3 total attempts (initial + 2 retries)
        stop=stop_after_attempt(3),
        # Use exponential backoff: wait 4s, then 8s, then 10s max between retries
        wait=wait_exponential(multiplier=1, min=4, max=10),
        # Only retry if the exception is a requests.RequestException (network errors)
        retry=retry_if_exception_type((requests.RequestException,)),
        # Log a warning message before each retry attempt
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def fetch_trending(
        self, 
        # Optional parameter to filter by programming language (Python, JavaScript, etc.)
        language: Optional[str] = None, 
        # Time range for trending: 'daily', 'weekly', or 'monthly'
        since: str = "daily"
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
        # Calculate how much time has passed since our last request
        time_since_last = time.time() - self.last_request_time
        # If we made a request too recently, sleep for the remaining delay time
        if time_since_last < self.delay:
            # Sleep for the difference to maintain polite request rate
            time.sleep(self.delay - time_since_last)

        # Build the complete URL with language filter and time range parameters
        url = self._build_url(language, since)
        # Log that we're about to fetch this URL for debugging and monitoring
        logger.info(f"Fetching trending page: {url}")

        # Wrap the actual HTTP request in try-except to handle potential errors
        try:
            # Make GET request to the URL with 10 second timeout to avoid hanging
            response = self.session.get(url, timeout=10)
            # Check if response status code indicates success (200-299), raise exception if not
            response.raise_for_status()

            # Safety check: verify we're still on a trending page and weren't redirected elsewhere
            if "trending" not in response.url:
                # Log warning if we were redirected away from trending page
                logger.warning(f"Redirected to non-trending page: {response.url}")

            # Update the last request time to current time for rate limiting calculations
            self.last_request_time = time.time()
            # Return the HTML content of the page as a string for parsing
            return response.text

        # Handle HTTP errors (4xx and 5xx status codes)
        except requests.HTTPError as e:
            # Special handling for rate limiting (HTTP 429 Too Many Requests)
            if response.status_code == 429:
                # Log that we've been rate limited
                logger.warning("Rate limited by GitHub, backing off...")
                # Wait a full minute before retrying when rate limited
                time.sleep(60)
            # Log the specific HTTP error for debugging
            logger.error(f"HTTP error {response.status_code} for {url}: {e}")
            # Re-raise the exception to trigger retry mechanism or fail completely
            raise
        # Handle other request-related exceptions (network errors, timeouts, etc.)
        except requests.RequestException as e:
            # Log the request failure for debugging
            logger.error(f"Request failed for {url}: {e}")
            # Re-raise the exception to trigger retry mechanism
            raise

    def _build_url(self, language: Optional[str], since: str) -> str:
        """Build the trending URL with query parameters."""
        # Check if a specific programming language filter was provided
        if language:
            # If language is specified, build path with language and optional time parameter
            # For non-daily ranges, add 'since' query parameter, otherwise just language
            path = f"{language}?since={since}" if since != "daily" else language
        else:
            # If no language filter, build path with just time parameter if not daily
            path = f"?since={since}" if since != "daily" else ""

        # Safely join base URL with constructed path, or return base URL if path is empty
        return urljoin(BASE_URL, path) if path else BASE_URL