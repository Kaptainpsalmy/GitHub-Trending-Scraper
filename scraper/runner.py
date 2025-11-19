"""Command-line runner for GitHub Trending scraper."""
import argparse
import logging
import sys
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path

from scraper.fetcher import Fetcher
from scraper.parser import Parser
from scraper.storage import Storage


def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("github_trending_scraper")
    logger.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "scraper.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="GitHub Trending Scraper")
    parser.add_argument(
        "--range",
        "-r",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Time range for trending (default: daily)",
    )
    parser.add_argument(
        "--language",
        "-l",
        help="Programming language to filter by (e.g., python, javascript)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store data files (default: data)",
    )
    parser.add_argument(
        "--db-path",
        default="data/github.db",
        help="Path to SQLite database (default: data/github.db)",
    )

    args = parser.parse_args()

    logger = setup_logging()

    try:
        logger.info(
            f"Starting GitHub Trending scrape (range: {args.range}, language: {args.language or 'all'})"
        )

        # Initialize components
        fetcher = Fetcher(delay=args.delay)
        storage = Storage(data_dir=args.data_dir, db_path=args.db_path)

        # Fetch data
        html = fetcher.fetch_trending(language=args.language, since=args.range)

        # Parse data
        scraped_at = datetime.now(timezone.utc).isoformat()
        repos = Parser.parse_trending(html, scraped_at)

        if not repos:
            logger.error("No repositories parsed from HTML")
            return 1

        # Store data
        storage.save_to_files(repos)
        storage.save_to_database(repos)

        logger.info(f"Successfully scraped and stored {len(repos)} repositories")
        return 0

    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())