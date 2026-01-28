"""Repository database record model (separate from assessor Repository model)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RepositoryRecord:
    """Database record for a repository (used by storage layer and API)."""

    repo_url: str
    name: str
    description: Optional[str] = None
    primary_language: Optional[str] = None
    last_assessed: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "repo_url": self.repo_url,
            "name": self.name,
            "description": self.description,
            "primary_language": self.primary_language,
            "last_assessed": self.last_assessed.isoformat() if self.last_assessed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RepositoryRecord":
        """Create from dictionary."""
        return cls(
            repo_url=data["repo_url"],
            name=data["name"],
            description=data.get("description"),
            primary_language=data.get("primary_language"),
            last_assessed=datetime.fromisoformat(data["last_assessed"]) if data.get("last_assessed") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
