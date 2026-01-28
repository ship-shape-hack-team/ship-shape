"""Benchmark models for repository ranking and comparison."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class Statistics:
    """Statistical summary for a metric."""

    mean: float
    median: float
    std_dev: float
    min: float
    max: float
    percentiles: Dict[str, float]  # p25, p50, p75, p90, p95

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "mean": self.mean,
            "median": self.median,
            "std_dev": self.std_dev,
            "min": self.min,
            "max": self.max,
            "percentiles": self.percentiles,
        }


@dataclass
class StatisticalSummary:
    """Statistical summary across all assessed repositories."""

    overall_score: Statistics
    test_coverage: Optional[Statistics] = None
    integration_tests: Optional[Statistics] = None
    documentation_standards: Optional[Statistics] = None
    ecosystem_tools: Optional[Statistics] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "overall_score": self.overall_score.to_dict(),
        }
        
        if self.test_coverage:
            result["test_coverage"] = self.test_coverage.to_dict()
        if self.integration_tests:
            result["integration_tests"] = self.integration_tests.to_dict()
        if self.documentation_standards:
            result["documentation_standards"] = self.documentation_standards.to_dict()
        if self.ecosystem_tools:
            result["ecosystem_tools"] = self.ecosystem_tools.to_dict()
            
        return result


@dataclass
class BenchmarkSnapshot:
    """Point-in-time benchmark across all repositories."""

    repository_count: int
    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    statistical_summary: Optional[StatisticalSummary] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "repository_count": self.repository_count,
            "statistical_summary": self.statistical_summary.to_dict() if self.statistical_summary else None,
        }


@dataclass
class DimensionScore:
    """Score and ranking for a single quality dimension."""

    score: float
    rank: int
    percentile: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "rank": self.rank,
            "percentile": self.percentile,
        }


@dataclass
class BenchmarkRanking:
    """Repository ranking within a benchmark snapshot."""

    benchmark_snapshot_id: str
    repo_url: str
    rank: int
    percentile: float
    dimension_scores: Dict[str, DimensionScore]
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "benchmark_snapshot_id": self.benchmark_snapshot_id,
            "repo_url": self.repo_url,
            "rank": self.rank,
            "percentile": self.percentile,
            "dimension_scores": {
                name: score.to_dict() for name, score in self.dimension_scores.items()
            },
        }
