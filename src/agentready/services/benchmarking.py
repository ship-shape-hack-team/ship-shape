"""Benchmarking service for repository ranking and comparison."""

from datetime import datetime
from typing import Dict, List

from ..models.assessment import Assessment
from ..models.assessor_result import AssessorResult
from ..models.benchmark import (
    BenchmarkRanking,
    BenchmarkSnapshot,
    DimensionScore,
    StatisticalSummary,
)
from .statistics import StatisticsCalculator


class BenchmarkingService:
    """Service for benchmarking and ranking repositories."""

    def __init__(self):
        """Initialize benchmarking service."""
        self.stats_calculator = StatisticsCalculator()

    def create_benchmark(
        self,
        assessments: List[Assessment],
        assessor_results_by_assessment: Dict[str, List[AssessorResult]],
    ) -> BenchmarkSnapshot:
        """Create a benchmark snapshot from assessments.

        Args:
            assessments: List of completed assessments
            assessor_results_by_assessment: Map of assessment_id -> list of assessor results

        Returns:
            BenchmarkSnapshot with rankings and statistical summary
        """
        if not assessments:
            raise ValueError("Cannot create benchmark with no assessments")

        # Extract scores
        overall_scores = [a.overall_score for a in assessments]
        
        # Calculate overall statistics
        overall_stats = self.stats_calculator.calculate_statistics(overall_scores)

        # Calculate per-assessor statistics
        assessor_stats = self._calculate_assessor_statistics(assessor_results_by_assessment)

        # Create statistical summary
        summary = StatisticalSummary(
            overall_score=overall_stats,
            test_coverage=assessor_stats.get("quality_test_coverage"),
            integration_tests=assessor_stats.get("quality_integration_tests"),
            documentation_standards=assessor_stats.get("quality_documentation_standards"),
            ecosystem_tools=assessor_stats.get("quality_ecosystem_tools"),
        )

        # Create benchmark snapshot
        benchmark = BenchmarkSnapshot(
            repository_count=len(assessments),
            created_at=datetime.utcnow(),
            statistical_summary=summary,
        )

        return benchmark

    def calculate_rankings(
        self,
        benchmark: BenchmarkSnapshot,
        assessments: List[Assessment],
        assessor_results_by_assessment: Dict[str, List[AssessorResult]],
    ) -> List[BenchmarkRanking]:
        """Calculate rankings for all repositories in a benchmark.

        Args:
            benchmark: Benchmark snapshot
            assessments: List of assessments
            assessor_results_by_assessment: Map of assessment_id -> assessor results

        Returns:
            List of BenchmarkRanking objects
        """
        if not assessments:
            return []

        # Extract overall scores for ranking
        overall_scores = [a.overall_score for a in assessments]

        rankings = []

        for assessment in assessments:
            # Calculate overall rank and percentile
            rank = self.stats_calculator.calculate_rank(
                assessment.overall_score,
                overall_scores,
                higher_is_better=True,
            )
            percentile = self.stats_calculator.calculate_percentile_rank(
                assessment.overall_score,
                overall_scores,
            )

            # Calculate dimension scores
            dimension_scores = self._calculate_dimension_scores(
                assessment.id,
                assessor_results_by_assessment,
                overall_scores,
            )

            ranking = BenchmarkRanking(
                benchmark_snapshot_id=benchmark.id,
                repo_url=assessment.repo_url,
                rank=rank,
                percentile=percentile,
                dimension_scores=dimension_scores,
            )

            rankings.append(ranking)

        # Sort by rank
        rankings.sort(key=lambda r: r.rank)

        return rankings

    def _calculate_assessor_statistics(
        self, assessor_results_by_assessment: Dict[str, List[AssessorResult]]
    ) -> Dict[str, "Statistics"]:
        """Calculate statistics for each assessor across all assessments."""
        # Group scores by assessor name
        scores_by_assessor: Dict[str, List[float]] = {}

        for assessment_id, results in assessor_results_by_assessment.items():
            for result in results:
                if result.status == "success":
                    if result.assessor_name not in scores_by_assessor:
                        scores_by_assessor[result.assessor_name] = []
                    scores_by_assessor[result.assessor_name].append(result.score)

        # Calculate statistics for each assessor
        assessor_stats = {}
        for assessor_name, scores in scores_by_assessor.items():
            if scores:
                assessor_stats[assessor_name] = self.stats_calculator.calculate_statistics(scores)

        return assessor_stats

    def _calculate_dimension_scores(
        self,
        assessment_id: str,
        assessor_results_by_assessment: Dict[str, List[AssessorResult]],
        all_overall_scores: List[float],
    ) -> Dict[str, DimensionScore]:
        """Calculate dimension scores for a single assessment."""
        results = assessor_results_by_assessment.get(assessment_id, [])
        dimension_scores = {}

        # Group all scores by assessor for ranking
        all_scores_by_assessor: Dict[str, List[float]] = {}
        for aid, ares in assessor_results_by_assessment.items():
            for result in ares:
                if result.status == "success":
                    if result.assessor_name not in all_scores_by_assessor:
                        all_scores_by_assessor[result.assessor_name] = []
                    all_scores_by_assessor[result.assessor_name].append(result.score)

        # Calculate rank and percentile for each assessor
        for result in results:
            if result.status == "success":
                assessor_scores = all_scores_by_assessor.get(result.assessor_name, [])
                
                rank = self.stats_calculator.calculate_rank(
                    result.score,
                    assessor_scores,
                    higher_is_better=True,
                )
                
                percentile = self.stats_calculator.calculate_percentile_rank(
                    result.score,
                    assessor_scores,
                )

                dimension_scores[result.assessor_name] = DimensionScore(
                    score=result.score,
                    rank=rank,
                    percentile=percentile,
                )

        return dimension_scores

    def get_top_repositories(
        self, rankings: List[BenchmarkRanking], limit: int = 10
    ) -> List[BenchmarkRanking]:
        """Get top N repositories by rank.

        Args:
            rankings: List of benchmark rankings
            limit: Number of top repositories to return

        Returns:
            Top N rankings
        """
        sorted_rankings = sorted(rankings, key=lambda r: r.rank)
        return sorted_rankings[:limit]

    def get_bottom_repositories(
        self, rankings: List[BenchmarkRanking], limit: int = 10
    ) -> List[BenchmarkRanking]:
        """Get bottom N repositories by rank.

        Args:
            rankings: List of benchmark rankings
            limit: Number of bottom repositories to return

        Returns:
            Bottom N rankings
        """
        sorted_rankings = sorted(rankings, key=lambda r: r.rank, reverse=True)
        return sorted_rankings[:limit]
