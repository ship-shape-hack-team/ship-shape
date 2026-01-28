"""Recommendation model."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Recommendation:
    """Actionable recommendation from an assessor."""

    assessor_result_id: str
    category: str  # testing, documentation, security, code_quality, ecosystem, maintainability
    severity: str  # critical, high, medium, low
    description: str
    metadata: Optional[Dict[str, Any]] = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Validate recommendation data."""
        valid_categories = ["testing", "documentation", "security", "code_quality", "ecosystem", "maintainability"]
        if self.category not in valid_categories:
            raise ValueError(f"Invalid category: {self.category}. Must be one of {valid_categories}")

        valid_severities = ["critical", "high", "medium", "low"]
        if self.severity not in valid_severities:
            raise ValueError(f"Invalid severity: {self.severity}. Must be one of {valid_severities}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "assessor_result_id": self.assessor_result_id,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recommendation":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            assessor_result_id=data["assessor_result_id"],
            category=data["category"],
            severity=data["severity"],
            description=data["description"],
            metadata=data.get("metadata"),
        )
