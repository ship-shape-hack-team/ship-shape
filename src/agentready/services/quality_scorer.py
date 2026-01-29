"""Quality scoring service for calculating weighted quality scores."""

from typing import Dict, List

from ..models.assessor_result import AssessorResult


class QualityScorerService:
    """Calculate weighted quality scores from assessor results."""

    # Default weights based on research (DORA, ISO 25010, CISQ)
    DEFAULT_WEIGHTS = {
        "quality_test_coverage": 0.25,
        "quality_integration_tests": 0.20,
        "quality_documentation_standards": 0.20,
        "quality_ecosystem_tools": 0.20,
        "quality_code_quality": 0.05,
        "quality_security": 0.05,
        "quality_dora_metrics": 0.03,
        "quality_maintainability": 0.02,
    }

    def __init__(self, weights: Dict[str, float] = None):
        """Initialize scorer with custom or default weights.

        Args:
            weights: Optional custom weights for assessors
        """
        self.weights = weights or self.DEFAULT_WEIGHTS

    def calculate_overall_score(self, assessor_results: List[AssessorResult]) -> float:
        """Calculate weighted overall quality score.

        Args:
            assessor_results: List of assessor results

        Returns:
            Weighted score 0-100
        """
        if not assessor_results:
            return 0.0

        # Create mapping of assessor names to scores
        scores = {result.assessor_name: result.score for result in assessor_results if result.status == "success"}

        if not scores:
            return 0.0

        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0

        for assessor_name, score in scores.items():
            weight = self.weights.get(assessor_name, 0.0)
            if weight > 0:
                weighted_sum += score * weight
                total_weight += weight

        if total_weight == 0:
            # Fallback: simple average if no weights match
            return sum(scores.values()) / len(scores)

        # Normalize by total weight used
        return weighted_sum / total_weight

    def get_performance_tier(self, overall_score: float) -> str:
        """Get performance tier based on score.

        Args:
            overall_score: Overall quality score 0-100

        Returns:
            Performance tier: Elite, High, Medium, or Low
        """
        if overall_score >= 90:
            return "Elite"
        elif overall_score >= 75:
            return "High"
        elif overall_score >= 60:
            return "Medium"
        else:
            return "Low"

    def get_dimension_scores(self, assessor_results: List[AssessorResult]) -> Dict[str, float]:
        """Get scores by dimension/assessor.

        Args:
            assessor_results: List of assessor results

        Returns:
            Dictionary mapping assessor names to scores
        """
        return {
            result.assessor_name: result.score
            for result in assessor_results
            if result.status == "success"
        }

    def identify_weakest_areas(self, assessor_results: List[AssessorResult], threshold: float = 60.0) -> List[str]:
        """Identify assessors with scores below threshold.

        Args:
            assessor_results: List of assessor results
            threshold: Score threshold (default: 60)

        Returns:
            List of assessor names needing improvement
        """
        weak_areas = []

        for result in assessor_results:
            if result.status == "success" and result.score < threshold:
                weak_areas.append(result.assessor_name)

        return sorted(weak_areas, key=lambda name: next(
            r.score for r in assessor_results if r.assessor_name == name
        ))
