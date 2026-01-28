"""Recommendation engine for generating actionable guidance."""

from typing import List

from ..models.assessor_result import AssessorResult
from ..models.recommendation import Recommendation


class RecommendationEngine:
    """Generate actionable recommendations from assessor results."""

    def generate_recommendations(self, assessor_results: List[AssessorResult]) -> List[Recommendation]:
        """Generate recommendations across all assessor results.

        Args:
            assessor_results: List of assessor results

        Returns:
            Consolidated list of recommendations
        """
        all_recommendations = []

        for result in assessor_results:
            if result.recommendations:
                all_recommendations.extend(result.recommendations)

        return all_recommendations

    def prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Sort recommendations by severity.

        Args:
            recommendations: List of recommendations

        Returns:
            Sorted list (critical → high → medium → low)
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        return sorted(
            recommendations,
            key=lambda r: severity_order.get(r.severity, 999)
        )

    def filter_by_category(self, recommendations: List[Recommendation], category: str) -> List[Recommendation]:
        """Filter recommendations by category.

        Args:
            recommendations: List of recommendations
            category: Category to filter by

        Returns:
            Filtered recommendations
        """
        return [r for r in recommendations if r.category == category]

    def filter_by_severity(self, recommendations: List[Recommendation], min_severity: str = "medium") -> List[Recommendation]:
        """Filter recommendations by minimum severity.

        Args:
            recommendations: List of recommendations
            min_severity: Minimum severity (critical, high, medium, low)

        Returns:
            Filtered recommendations
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        min_level = severity_order.get(min_severity, 2)

        return [
            r for r in recommendations
            if severity_order.get(r.severity, 999) <= min_level
        ]

    def summarize_by_severity(self, recommendations: List[Recommendation]) -> dict:
        """Summarize recommendation counts by severity.

        Args:
            recommendations: List of recommendations

        Returns:
            Dictionary with severity counts
        """
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for rec in recommendations:
            if rec.severity in summary:
                summary[rec.severity] += 1

        return summary
