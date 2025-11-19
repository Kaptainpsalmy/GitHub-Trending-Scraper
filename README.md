# GitHub Trending Scraper

A production-ready GitHub Trending repositories scraper with REST API and dashboard. This project automatically scrapes trending repositories from GitHub, stores the data in multiple formats, and provides a web interface for exploration.

## 🚀 Features

- **Automated Scraping**: Scrapes GitHub trending pages daily, weekly, and monthly
- **Multiple Storage Formats**: Saves data to CSV, JSON, and SQLite
- **REST API**: FastAPI-based API with filtering and pagination
- **Web Dashboard**: Responsive dashboard with search and filtering
- **Scheduled Execution**: Automated daily scraping via GitHub Actions
- **Docker Support**: Containerized deployment
- **Production Ready**: Error handling, retries, logging, and tests

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLModel
- **Scraping**: requests, BeautifulSoup4, tenacity
- **Data Processing**: pandas
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Infrastructure**: Docker, GitHub Actions
- **Testing**: pytest, requests-mock

## 📦 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/github-trending-scraper.git
   cd github-trending-scraper# GitHub-Trending-Scraper
