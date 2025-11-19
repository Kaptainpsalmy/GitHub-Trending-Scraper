#!/usr/bin/env python3
"""Manual runner script for the GitHub Trending scraper."""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from scraper.runner import main

if __name__ == "__main__":
    sys.exit(main())