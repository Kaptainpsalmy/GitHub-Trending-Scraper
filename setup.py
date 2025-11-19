from setuptools import setup, find_packages

setup(
    name="github-trending-scraper",
    version="1.0.0",
    description="A production-ready GitHub Trending repositories scraper with API and dashboard",
    packages=find_packages(include=["scraper", "api", "scraper.*", "api.*"]),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pandas>=2.0.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlmodel>=0.0.14",
        "tenacity>=8.2.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-mock>=3.11.0",
            "requests-mock>=1.11.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pre-commit>=3.4.0",
        ]
    },
    python_requires=">=3.10",
)