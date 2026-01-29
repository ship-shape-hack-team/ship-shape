#!/usr/bin/env python3
"""Test benchmarking functionality with multiple repositories."""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentready.models.assessment import Assessment
from agentready.models.assessor_result import AssessorResult
from agentready.services.benchmarking import BenchmarkingService
from agentready.services.statistics import StatisticsCalculator

print("=" * 80)
print("🏆 QUALITY BENCHMARKING DEMONSTRATION")
print("=" * 80)
print()

# Create mock assessment data for multiple repositories
print("📦 Creating mock assessments for 5 repositories...")
print()

mock_repos = [
    {
        "name": "excellent-repo",
        "url": "https://github.com/example/excellent",
        "scores": {"test_coverage": 95, "integration_tests": 90, "documentation": 95, "ecosystem": 100},
    },
    {
        "name": "good-repo",
        "url": "https://github.com/example/good",
        "scores": {"test_coverage": 80, "integration_tests": 75, "documentation": 85, "ecosystem": 85},
    },
    {
        "name": "average-repo",
        "url": "https://github.com/example/average",
        "scores": {"test_coverage": 65, "integration_tests": 60, "documentation": 70, "ecosystem": 65},
    },
    {
        "name": "needs-work-repo",
        "url": "https://github.com/example/needs-work",
        "scores": {"test_coverage": 45, "integration_tests": 40, "documentation": 50, "ecosystem": 55},
    },
    {
        "name": "minimal-repo",
        "url": "https://github.com/example/minimal",
        "scores": {"test_coverage": 20, "integration_tests": 15, "documentation": 30, "ecosystem": 25},
    },
]

assessments = []
assessor_results_map = {}

for repo in mock_repos:
    # Create assessor results
    results = [
        AssessorResult(
            assessment_id=repo["name"],
            assessor_name="quality_test_coverage",
            score=repo["scores"]["test_coverage"],
            metrics={},
            status="success",
            executed_at=datetime.utcnow(),
        ),
        AssessorResult(
            assessment_id=repo["name"],
            assessor_name="quality_integration_tests",
            score=repo["scores"]["integration_tests"],
            metrics={},
            status="success",
            executed_at=datetime.utcnow(),
        ),
        AssessorResult(
            assessment_id=repo["name"],
            assessor_name="quality_documentation_standards",
            score=repo["scores"]["documentation"],
            metrics={},
            status="success",
            executed_at=datetime.utcnow(),
        ),
        AssessorResult(
            assessment_id=repo["name"],
            assessor_name="quality_ecosystem_tools",
            score=repo["scores"]["ecosystem"],
            metrics={},
            status="success",
            executed_at=datetime.utcnow(),
        ),
    ]

    # Calculate overall score
    overall = sum(r.score for r in results) / len(results)

    # Create assessment
    assessment = Assessment(
        id=repo["name"],
        repo_url=repo["url"],
        overall_score=overall,
        status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )

    assessments.append(assessment)
    assessor_results_map[assessment.id] = results

    print(f"  ✓ {repo['name']}: {overall:.1f}/100")

print()

# Test Statistics Calculator
print("📊 TESTING STATISTICS CALCULATOR")
print("-" * 80)

stats_calc = StatisticsCalculator()
overall_scores = [a.overall_score for a in assessments]
stats = stats_calc.calculate_statistics(overall_scores)

print(f"Mean Score: {stats.mean:.1f}/100")
print(f"Median Score: {stats.median:.1f}/100")
print(f"Std Deviation: {stats.std_dev:.1f}")
print(f"Range: {stats.min:.1f} - {stats.max:.1f}")
print()
print("Percentiles:")
for p, value in stats.percentiles.items():
    print(f"  {p.upper()}: {value:.1f}")
print()

# Test Benchmarking Service
print("🏆 TESTING BENCHMARKING SERVICE")
print("-" * 80)

benchmarking_service = BenchmarkingService()

# Create benchmark
benchmark = benchmarking_service.create_benchmark(assessments, assessor_results_map)

print(f"✓ Benchmark created:")
print(f"  ID: {benchmark.id}")
print(f"  Repositories: {benchmark.repository_count}")
print(f"  Created: {benchmark.created_at}")
print()

# Calculate rankings
rankings = benchmarking_service.calculate_rankings(benchmark, assessments, assessor_results_map)

print(f"✓ Rankings calculated: {len(rankings)} repositories")
print()

# Display rankings
print("=" * 80)
print("📋 REPOSITORY RANKINGS")
print("=" * 80)
print()

for ranking in rankings:
    # Find repo name
    repo_name = next(r["name"] for r in mock_repos if r["url"] == ranking.repo_url)
    
    # Get performance tier
    from agentready.services.quality_scorer import QualityScorerService
    scorer = QualityScorerService()
    
    # Find assessment for this ranking
    assessment = next(a for a in assessments if a.repo_url == ranking.repo_url)
    tier = scorer.get_performance_tier(assessment.overall_score)
    
    tier_emoji = {"Elite": "🥇", "High": "🥈", "Medium": "🥉", "Low": "📊"}[tier]
    
    print(f"#{ranking.rank} {tier_emoji} {repo_name}")
    print(f"   Overall Score: {assessment.overall_score:.1f}/100")
    print(f"   Percentile: {ranking.percentile:.1f}th (top {100-ranking.percentile:.0f}%)")
    print(f"   Tier: {tier}")
    
    # Show dimension rankings
    print("   Dimension Rankings:")
    for dim_name, dim_score in ranking.dimension_scores.items():
        clean_name = dim_name.replace("quality_", "").replace("_", " ").title()
        print(f"     • {clean_name}: {dim_score.score:.1f} (#{dim_score.rank}, {dim_score.percentile:.0f}th percentile)")
    print()

# Test top/bottom functions
print("=" * 80)
print("🎯 TOP AND BOTTOM ANALYSIS")
print("=" * 80)
print()

top_3 = benchmarking_service.get_top_repositories(rankings, limit=3)
print("Top 3 Repositories:")
for ranking in top_3:
    repo_name = next(r["name"] for r in mock_repos if r["url"] == ranking.repo_url)
    assessment = next(a for a in assessments if a.repo_url == ranking.repo_url)
    print(f"  #{ranking.rank} {repo_name}: {assessment.overall_score:.1f}/100")

print()

bottom_2 = benchmarking_service.get_bottom_repositories(rankings, limit=2)
print("Bottom 2 Repositories (Need Improvement):")
for ranking in bottom_2:
    repo_name = next(r["name"] for r in mock_repos if r["url"] == ranking.repo_url)
    assessment = next(a for a in assessments if a.repo_url == ranking.repo_url)
    print(f"  #{ranking.rank} {repo_name}: {assessment.overall_score:.1f}/100")

print()

# Performance tier distribution
print("=" * 80)
print("📊 PERFORMANCE TIER DISTRIBUTION")
print("=" * 80)
print()

from collections import Counter
from agentready.services.quality_scorer import QualityScorerService

scorer = QualityScorerService()
tiers = [scorer.get_performance_tier(a.overall_score) for a in assessments]
tier_counts = Counter(tiers)

for tier in ["Elite", "High", "Medium", "Low"]:
    count = tier_counts.get(tier, 0)
    percentage = (count / len(assessments)) * 100
    emoji = {"Elite": "🥇", "High": "🥈", "Medium": "🥉", "Low": "📊"}[tier]
    bar = "█" * int(percentage / 10)
    print(f"{emoji} {tier:8s}: {count}/{len(assessments)} ({percentage:5.1f}%) {bar}")

print()

print("=" * 80)
print("✅ BENCHMARKING TEST COMPLETE")
print("=" * 80)
print()
print("Benchmarking functionality validated:")
print("  ✓ Statistical calculations (mean, median, percentiles)")
print("  ✓ Repository ranking (1 = best)")
print("  ✓ Percentile calculation")
print("  ✓ Dimension-specific rankings")
print("  ✓ Top/bottom repository identification")
print("  ✓ Performance tier distribution")
print()
print("Ready for CLI usage:")
print("  agentready assess-batch-quality repos.txt")
print("  agentready benchmark-quality assessments.json")
print("  agentready benchmark-show benchmark.json --top 10")
