"""CLI command for quality assessment with new quality assessors."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from ..assessors.quality import (
    DocumentationStandardsAssessor,
    EcosystemToolsAssessor,
    IntegrationTestsAssessor,
    TestCoverageAssessor,
)
from ..models.assessment import Assessment
from ..models.assessor_result import AssessorResult
from ..models.quality_profile import QualityProfile
from ..models.repository import Repository as QualityRepository
from ..services.quality_scorer import QualityScorerService
from ..services.recommendation_engine import RecommendationEngine
from ..services.repository_service import RepositoryService
from ..storage.connection import initialize_database


@click.command("assess-quality")
@click.argument("repo_path")
@click.option("--format", type=click.Choice(["text", "json", "markdown"]), default="text", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--assessors", help="Comma-separated list of specific assessors to run")
def assess_quality(repo_path: str, format: str, output: Optional[str], assessors: Optional[str]):
    """Assess repository quality using enhanced quality assessors.

    This command runs quality profiling assessors including:
    - Test coverage
    - Integration tests
    - Documentation standards
    - Ecosystem tools

    Examples:
        \b
        # Assess current directory
        agentready assess-quality .

        \b
        # Assess specific repository
        agentready assess-quality /path/to/repo

        \b
        # Output as JSON
        agentready assess-quality . --format json

        \b
        # Save to file
        agentready assess-quality . --format markdown -o report.md

        \b
        # Run specific assessors only
        agentready assess-quality . --assessors test_coverage,documentation_standards
    """
    try:
        # Initialize database
        initialize_database()

        # Extract repository info
        repo_service = RepositoryService()
        quality_repo = repo_service.extract_repo_info(repo_path)

        # Convert to internal Repository model for assessors
        from ..models.repository import Repository

        repo = Repository(
            url=quality_repo.repo_url,
            path=str(Path(repo_path).resolve()),
            name=quality_repo.name,
            languages=[quality_repo.primary_language] if quality_repo.primary_language else [],
            metadata={}
        )

        # Create assessors
        all_assessors = {
            "test_coverage": TestCoverageAssessor(),
            "integration_tests": IntegrationTestsAssessor(),
            "documentation_standards": DocumentationStandardsAssessor(),
            "ecosystem_tools": EcosystemToolsAssessor(),
        }

        # Filter assessors if specified
        if assessors:
            selected = assessors.split(",")
            assessor_list = [all_assessors[name.strip()] for name in selected if name.strip() in all_assessors]
        else:
            assessor_list = list(all_assessors.values())

        if not assessor_list:
            click.echo("Error: No valid assessors specified", err=True)
            sys.exit(1)

        click.echo(f"🔍 Assessing repository: {quality_repo.name}")
        click.echo(f"📊 Running {len(assessor_list)} assessors...\n")

        # Run assessments
        assessor_results = []

        for assessor in assessor_list:
            click.echo(f"  ⏳ Running {assessor.attribute_id}...", nl=False)

            finding = assessor.assess(repo)

            result = AssessorResult(
                assessment_id="cli_run",
                assessor_name=assessor.attribute_id,
                score=finding.score if finding.score is not None else 0,
                metrics={
                    "status": finding.status,
                    "evidence": finding.evidence,
                },
                status="success" if finding.status in ["pass", "fail"] else finding.status,
                executed_at=datetime.utcnow(),
            )

            assessor_results.append(result)
            click.echo(f" ✓ Score: {result.score:.1f}/100")

        # Calculate overall score
        scorer = QualityScorerService()
        overall_score = scorer.calculate_overall_score(assessor_results)
        tier = scorer.get_performance_tier(overall_score)

        # Create assessment
        assessment = Assessment(
            repo_url=quality_repo.repo_url,
            overall_score=overall_score,
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

        # Create quality profile
        profile = QualityProfile(
            repository=quality_repo,
            assessment=assessment,
            assessor_results=assessor_results,
        )

        # Output results
        if format == "json":
            output_content = json.dumps(profile.to_dict(), indent=2, default=str)
        elif format == "markdown":
            output_content = format_markdown(profile, tier)
        else:
            output_content = format_text(profile, tier)

        if output:
            Path(output).write_text(output_content)
            click.echo(f"\n✅ Report saved to: {output}")
        else:
            click.echo(f"\n{output_content}")

    except Exception as e:
        click.echo(f"❌ Assessment failed: {str(e)}", err=True)
        sys.exit(1)


def format_text(profile: QualityProfile, tier: str) -> str:
    """Format quality profile as plain text."""
    lines = []
    lines.append("=" * 70)
    lines.append("QUALITY ASSESSMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"\nRepository: {profile.repository.name}")
    lines.append(f"Overall Score: {profile.assessment.overall_score:.1f}/100 ({tier} Performance)")
    lines.append(f"Assessed: {profile.assessment.completed_at}")
    lines.append("\n" + "=" * 70)
    lines.append("ASSESSOR RESULTS")
    lines.append("=" * 70 + "\n")

    for result in profile.assessor_results:
        status_icon = "✓" if result.score >= 70 else "✗"
        lines.append(f"{status_icon} {result.assessor_name}: {result.score:.1f}/100")

        if result.metrics.get("evidence"):
            lines.append(f"   Evidence: {result.metrics['evidence']}")

        lines.append("")

    return "\n".join(lines)


def format_markdown(profile: QualityProfile, tier: str) -> str:
    """Format quality profile as Markdown."""
    lines = []
    lines.append("# Quality Assessment Report\n")
    lines.append(f"**Repository**: {profile.repository.name}  ")
    lines.append(f"**Overall Score**: {profile.assessment.overall_score:.1f}/100 ({tier})  ")
    lines.append(f"**Assessed**: {profile.assessment.completed_at}\n")
    lines.append("## Assessor Results\n")

    for result in profile.assessor_results:
        status = "✅" if result.score >= 70 else "❌"
        lines.append(f"### {status} {result.assessor_name}\n")
        lines.append(f"**Score**: {result.score:.1f}/100\n")

        if result.metrics.get("evidence"):
            lines.append(f"**Evidence**: {result.metrics['evidence']}\n")

    return "\n".join(lines)
