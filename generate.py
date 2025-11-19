import os

project_structure = {
    "github-trending-scraper": {
        "scraper": [
            "__init__.py",
            "fetcher.py",
            "parser.py",
            "storage.py",
            "runner.py"
        ],
        "api": [
            "__init__.py",
            "main.py",
            "routes.py"
        ],
        "web": [
            "index.html",
            "style.css",
            "app.js"
        ],
        "tests": [
            "test_parser.py",
            "test_storage.py",
            "test_fetcher.py",
            "conftest.py"
        ],
        ".github/workflows": [
            "ci.yml",
            "schedule.yml"
        ],
        "data": [],
        "logs": [],
        "": [  # root-level files
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "pyproject.toml",
            "README.md",
            ".gitignore",
            "pre-commit-config.yaml"
        ]
    }
}

def create_structure(base_path, structure):
    for folder, contents in structure.items():
        base_dir = os.path.join(base_path, folder)
        os.makedirs(base_dir, exist_ok=True)

        for item in contents:
            if isinstance(contents, dict):
                create_structure(base_dir, contents)
                break
            file_path = os.path.join(base_dir, item)
            with open(file_path, "w") as f:
                f.write("")  # create empty file

# Run generator
root_name = "github-trending-scraper"
create_structure(".", project_structure[root_name])
print(f"Project '{root_name}' created successfully!")
