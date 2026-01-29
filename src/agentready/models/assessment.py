"""Assessment model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class AssessmentMetadata:
    """Metadata for an assessment."""

    assessment_id: str
    head_commit_sha: str
    file_count: int
    line_count: int
    languages: Dict[str, int]
    commit_count: Optional[int] = None
    contributor_count: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "commit_count": self.commit_count,
            "head_commit_sha": self.head_commit_sha,
            "file_count": self.file_count,
            "line_count": self.line_count,
            "languages": self.languages,
            "contributor_count": self.contributor_count,
        }


@dataclass
class Assessment:
    """Represents a quality assessment of a repository."""

    repo_url: str
    overall_score: float
    status: str  # pending, running, completed, failed, cancelled
    started_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Validate assessment data."""
        if not 0 <= self.overall_score <= 100:
            raise ValueError(f"Score must be 0-100, got {self.overall_score}")

        valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "repo_url": self.repo_url,
            "overall_score": self.overall_score,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Assessment":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            repo_url=data["repo_url"],
            overall_score=data["overall_score"],
            status=data["status"],
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            metadata=data.get("metadata"),
        )
