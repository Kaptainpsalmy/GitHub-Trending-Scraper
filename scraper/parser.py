"""HTML parser for GitHub Trending pages."""
import logging
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Parser:
    """Parses GitHub Trending HTML into structured data."""

    @staticmethod
    def parse_trending(html: str, scraped_at: str) -> List[Dict[str, Any]]:
        """
        Parse trending page HTML into repository data.

        Args:
            html: HTML content of trending page
            scraped_at: ISO timestamp of when scraping occurred

        Returns:
            List of repository dictionaries
        """
        # Try different parsers in order of preference
        parsers = ["lxml", "html.parser", "html5lib"]
        soup = None

        for parser in parsers:
            try:
                soup = BeautifulSoup(html, parser)
                logger.info(f"Using parser: {parser}")
                break
            except Exception as e:
                logger.warning(f"Parser {parser} failed: {e}")
                continue

        if soup is None:
            raise ValueError("No suitable HTML parser available. Please install lxml or html5lib.")

        repos = []

        repo_articles = soup.find_all("article", class_="Box-row")
        if not repo_articles:
            logger.error("No repository articles found - page structure may have changed")
            raise ValueError("Could not find repository elements on page")

        for rank, article in enumerate(repo_articles, 1):
            try:
                repo_data = Parser._parse_repo_article(article, rank, scraped_at)
                if repo_data:
                    repos.append(repo_data)
            except Exception as e:
                logger.warning(f"Failed to parse repo at rank {rank}: {e}")
                continue

        logger.info(f"Successfully parsed {len(repos)} repositories")
        return repos

    @staticmethod
    def _parse_repo_article(
        article: BeautifulSoup, rank: int, scraped_at: str
    ) -> Optional[Dict[str, Any]]:
        """Parse individual repository article."""
        try:
            # Extract repo name and URL
            title_element = article.find("h2", class_="h3") or article.find("h2")
            if not title_element:
                return None

            repo_link = title_element.find("a")
            if not repo_link:
                return None

            repo_href = repo_link.get("href", "").strip()
            repo_full_name = repo_href.lstrip("/")

            # Handle repo name parsing more carefully
            if "/" in repo_full_name:
                author, repo_name = repo_full_name.split("/", 1)
            else:
                author, repo_name = None, repo_full_name

            if not author or not repo_name:
                return None

            # Extract description - try multiple possible selectors
            description_elem = (article.find("p", class_="col-9") or
                              article.find("p", class_=re.compile("col")) or
                              article.find("p"))
            description = description_elem.text.strip() if description_elem else ""

            # Extract language
            language_elem = (article.find("span", itemprop="programmingLanguage") or
                           article.find("span", class_=re.compile("language")))
            language = language_elem.text.strip() if language_elem else None

            # Extract stars
            stars_data = Parser._parse_stars(article)

            return {
                "rank": rank,
                "repo_name": repo_full_name,
                "author": author,
                "repository": repo_name,
                "description": description,
                "language": language,
                "total_stars": stars_data["total"],
                "stars_today": stars_data["today"],
                "repo_url": urljoin("https://github.com/", repo_href),
                "scraped_at": scraped_at,
            }

        except Exception as e:
            logger.warning(f"Error parsing repository article: {e}")
            return None

    @staticmethod
    def _parse_stars(article: BeautifulSoup) -> Dict[str, Optional[int]]:
        """Parse stars information from repository article."""
        stars_data = {"total": 0, "today": 0}

        # Find all links in the stats section
        links = article.find_all("a", class_=re.compile("muted|Link"))
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Look for stars count
            if "stargazers" in href:
                stars_text = link.get_text(strip=True)
                total_stars = Parser._parse_number(stars_text)
                if total_stars is not None:
                    stars_data["total"] = total_stars

            # Look for stars today
            if "stars today" in text.lower():
                stars_today = Parser._parse_number(text)
                if stars_today is not None:
                    stars_data["today"] = stars_today
                break  # Found stars today, no need to continue

        # Alternative approach: look for specific patterns
        if stars_data["today"] == 0:
            # Look for spans with star counts
            spans = article.find_all("span")
            for span in spans:
                text = span.get_text(strip=True)
                if "stars today" in text.lower():
                    stars_today = Parser._parse_number(text)
                    if stars_today is not None:
                        stars_data["today"] = stars_today
                    break

        return stars_data

    @staticmethod
    def _parse_number(text: str) -> Optional[int]:
        """Parse numbers like '1,234' or '2.5k' into integers."""
        if not text:
            return None

        # Remove non-numeric characters except decimal points and 'k'
        clean_text = re.sub(r"[^\d.k]", "", text.lower())

        try:
            if "k" in clean_text:
                number = float(clean_text.replace("k", "")) * 1000
                return int(number)
            else:
                return int(clean_text.replace(",", ""))
        except (ValueError, TypeError):
            return None