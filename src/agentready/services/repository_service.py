"""Repository service for managing repository metadata."""

import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ..models.repository_record import RepositoryRecord


class RepositoryService:
    """Service for repository metadata extraction and management."""

    def extract_repo_info(self, repo_url_or_path: str) -> RepositoryRecord:
        """Extract repository information from URL or local path.

        Args:
            repo_url_or_path: Git URL or local file path

        Returns:
            Repository model with extracted metadata
        """
        # Check if it's a local path
        if os.path.exists(repo_url_or_path):
            return self._from_local_path(repo_url_or_path)
        else:
            return self._from_url(repo_url_or_path)

    def _from_url(self, repo_url: str) -> RepositoryRecord:
        """Create Repository from Git URL.

        Args:
            repo_url: Git repository URL

        Returns:
            Repository model
        """
        # Parse URL to extract name
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) >= 2:
            owner = path_parts[-2]
            repo_name = path_parts[-1].replace(".git", "")
            name = f"{owner}/{repo_name}"
        else:
            name = repo_url.split("/")[-1].replace(".git", "")

        return RepositoryRecord(
            repo_url=repo_url,
            name=name,
            description=None,
            primary_language=None,
        )

    def _from_local_path(self, path: str) -> RepositoryRecord:
        """Create Repository from local path.

        Args:
            path: Local file system path

        Returns:
            Repository model
        """
        repo_path = Path(path).resolve()
        name = repo_path.name

        # Try to detect primary language
        primary_language = self._detect_primary_language(repo_path)

        return RepositoryRecord(
            repo_url=f"file://{repo_path}",
            name=name,
            description=f"Local repository at {path}",
            primary_language=primary_language,
        )

    def _detect_primary_language(self, repo_path: Path) -> Optional[str]:
        """Detect primary programming language from file extensions.

        Args:
            repo_path: Path to repository

        Returns:
            Primary language name or None
        """
        language_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".cpp": "C++",
            ".c": "C",
        }

        # Count files by extension
        extension_counts = {}

        for ext, lang in language_extensions.items():
            count = len(list(repo_path.rglob(f"*{ext}")))
            if count > 0:
                extension_counts[lang] = extension_counts.get(lang, 0) + count

        if not extension_counts:
            return None

        # Return language with most files
        return max(extension_counts, key=extension_counts.get)

    def get_repo_size_info(self, repo_path: Path) -> dict:
        """Get repository size information.

        Args:
            repo_path: Path to repository

        Returns:
            Dictionary with file count and line count estimates
        """
        file_count = 0
        line_count = 0

        try:
            for file_path in repo_path.rglob("*"):
                if file_path.is_file():
                    # Skip binary and large files
                    if file_path.suffix in [".py", ".js", ".ts", ".java", ".go", ".rs"]:
                        file_count += 1
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                line_count += sum(1 for _ in f)
                        except Exception:
                            pass

        except Exception:
            pass

        return {
            "file_count": file_count,
            "line_count": line_count,
        }
