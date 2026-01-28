"""Assessor result model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4


@dataclass
class AssessorResult:
    """Result from a single assessor execution."""

    assessment_id: str
    assessor_name: str
    score: float
    metrics: Dict[str, Any]
    status: str  # success, failed, skipped
    executed_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    recommendations: Optional[List["Recommendation"]] = None

    def __post_init__(self):
        """Validate assessor result data."""
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be 0-100, got {self.score}")

        valid_statuses = ["success", "failed", "skipped"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "assessor_name": self.assessor_name,
            "score": self.score,
            "metrics": self.metrics,
            "status": self.status,
            "executed_at": self.executed_at.isoformat(),
            "recommendations": [r.to_dict() for r in self.recommendations] if self.recommendations else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AssessorResult":
        """Create from dictionary."""
        from .recommendation import Recommendation

        return cls(
            id=data["id"],
            assessment_id=data["assessment_id"],
            assessor_name=data["assessor_name"],
            score=data["score"],
            metrics=data["metrics"],
            status=data["status"],
            executed_at=datetime.fromisoformat(data["executed_at"]),
            recommendations=[Recommendation.from_dict(r) for r in data.get("recommendations", [])],
        )
