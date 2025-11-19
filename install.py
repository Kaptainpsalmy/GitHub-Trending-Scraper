#!/usr/bin/env python3
"""Simple installation script for the GitHub Trending Scraper."""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main installation function."""
    print("🚀 Setting up GitHub Trending Scraper...")

    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # Install dependencies using pip
    if not run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "Installing dependencies"
    ):
        print("❌ Failed to install dependencies")
        return 1

    # Try to install in development mode
    if not run_command(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            "Installing package in development mode"
    ):
        print("⚠️  Development mode installation failed, but continuing...")

    # Install pre-commit hooks if pre-commit is available
    if run_command([sys.executable, "-m", "pip", "show", "pre-commit"], "Checking for pre-commit"):
        if run_command("pre-commit install", "Installing pre-commit hooks"):
            print("✅ Pre-commit hooks installed")

    print("\n🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Run the scraper: python -m scraper.runner")
    print("2. Start the API: uvicorn api.main:app --reload")
    print("3. Serve the frontend: cd web && python -m http.server 3000")
    print("4. Run tests: pytest")

    return 0


if __name__ == "__main__":
    sys.exit(main())