import re
import shutil
import tempfile
from pathlib import Path

from git import Repo
from git.exc import GitCommandError


GITHUB_PATTERN = re.compile(
    r"^https?://github\.com/[^/\s]+/[^/\s]+/?(?:\.git)?$",
    re.IGNORECASE,
)


def validate_github_url(url: str) -> str:
    url = url.strip()

    if not GITHUB_PATTERN.match(url):
        raise ValueError(
            "Please enter a valid public GitHub repository URL, "
            "for example: https://github.com/username/repository"
        )

    if not url.endswith(".git"):
        url = url.rstrip("/") + ".git"

    return url


def clone_repository(url: str) -> str:
    """Clone a public GitHub repository into a temporary directory."""
    validated_url = validate_github_url(url)

    temp_dir = tempfile.mkdtemp(prefix="github_code_explainer_")
    destination = Path(temp_dir) / "repository"

    try:
        Repo.clone_from(
            validated_url,
            destination,
            depth=1,
            no_single_branch=True,
        )
        return str(destination)
    except GitCommandError as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(
            "Could not clone the repository. Make sure the URL is correct "
            "and the repository is public."
        ) from exc


def cleanup_repository(repo_path: str) -> None:
    """Delete the temporary cloned repository."""
    path = Path(repo_path)

    # repo_path points to .../temp_folder/repository
    if path.exists():
        shutil.rmtree(path.parent, ignore_errors=True)
