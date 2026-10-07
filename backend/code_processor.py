from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".go", ".rs", ".php", ".rb",
    ".swift", ".kt", ".kts",
    ".html", ".css", ".scss",
    ".sql", ".sh", ".bash",
    ".json", ".yaml", ".yml",
    ".xml", ".md", ".txt",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    "target",
    "bin",
    "obj",
    ".next",
    "coverage",
    ".pytest_cache",

    # Testing files are not useful for understanding
    # the main application.
    "tests",
    "test",
}

IGNORED_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}


MAX_FILES = 20
MAX_CHARS_PER_FILE = 6000
MAX_TOTAL_CHARS = 25000


def is_relevant_file(path: Path) -> bool:

    # Ignore test directories
    if any(
        part.lower() in IGNORED_DIRECTORIES
        for part in path.parts
    ):
        return False

    # Ignore lock files
    if path.name in IGNORED_FILE_NAMES:
        return False

    # Only process supported source/documentation files
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    return True


def read_file_safely(path: Path) -> str:

    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )[:MAX_CHARS_PER_FILE]

    except Exception:
        return ""


def build_repository_context(repo_path: str):

    root = Path(repo_path)

    all_files = [
        p
        for p in root.rglob("*")
        if p.is_file() and is_relevant_file(p)
    ]

    # Files that are especially useful for understanding
    # what a repository does.
    priority = {
        "README.md": 0,
        "README": 0,

        "main.py": 1,
        "app.py": 1,
        "server.py": 1,
        "run.py": 1,
        "index.py": 1,

        "main.js": 1,
        "app.js": 1,
        "server.js": 1,
        "index.js": 1,

        "main.ts": 1,
        "app.ts": 1,
        "server.ts": 1,
        "index.ts": 1,

        "package.json": 2,
        "requirements.txt": 2,
        "pyproject.toml": 2,
        "pom.xml": 2,

        ".": 5,
    }

    def file_priority(path: Path):

        name_priority = priority.get(path.name, 4)

        extension_priority = {
            ".py": 1,
            ".js": 1,
            ".jsx": 1,
            ".ts": 1,
            ".tsx": 1,
            ".java": 1,
            ".cpp": 1,
            ".c": 1,
            ".go": 1,
            ".rs": 1,

            ".sql": 2,
            ".html": 2,
            ".css": 2,

            ".json": 3,
            ".yaml": 3,
            ".yml": 3,

            ".md": 0,
        }

        return (
            name_priority,
            extension_priority.get(
                path.suffix.lower(),
                5
            ),
            len(path.parts)
        )

    all_files.sort(key=file_priority)

    selected_files = []
    chunks = []

    total_chars = 0

    for path in all_files:

        if len(selected_files) >= MAX_FILES:
            break

        content = read_file_safely(path)

        if not content.strip():
            continue

        relative_path = path.relative_to(root)

        block = (
            f"\n===== FILE: {relative_path} =====\n"
            f"{content}\n"
        )

        remaining = MAX_TOTAL_CHARS - total_chars

        if remaining <= 300:
            break

        if len(block) > remaining:
            block = block[:remaining]

        chunks.append(block)

        selected_files.append(
            str(relative_path)
        )

        total_chars += len(block)

    return "".join(chunks), selected_files