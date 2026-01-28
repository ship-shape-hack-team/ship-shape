"""Quality profile aggregate model."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .assessment import Assessment
from .assessor_result import AssessorResult
from .repository import Repository


@dataclass
class QualityProfile:
    """Comprehensive quality profile for a repository."""

    repository: Repository
    assessment: Assessment
    assessor_results: List[AssessorResult]
    metadata: Optional[Dict] = None

    def get_score_by_assessor(self, assessor_name: str) -> Optional[float]:
        """Get score for a specific assessor."""
        for result in self.assessor_results:
            if result.assessor_name == assessor_name:
                return result.score
        return None

    def get_all_recommendations(self) -> List:
        """Get all recommendations across all assessors."""
        recommendations = []
        for result in self.assessor_results:
            if result.recommendations:
                recommendations.extend(result.recommendations)
        return recommendations

    def get_recommendations_by_severity(self, severity: str) -> List:
        """Get recommendations filtered by severity."""
        all_recs = self.get_all_recommendations()
        return [r for r in all_recs if r.severity == severity]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "repository": self.repository.to_dict(),
            "assessment": self.assessment.to_dict(),
            "assessor_results": [r.to_dict() for r in self.assessor_results],
            "metadata": self.metadata,
        }
