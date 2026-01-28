"""CLI command for batch quality assessment."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import click

from ..assessors.quality import (
    DocumentationStandardsAssessor,
    EcosystemToolsAssessor,
    IntegrationTestsAssessor,
    TestCoverageAssessor,
)
from ..models.assessment import Assessment
from ..models.assessor_result import AssessorResult
from ..models.repository import Repository as QualityRepository
from ..services.quality_scorer import QualityScorerService
from ..services.repository_service import RepositoryService
from ..storage.connection import initialize_database


@click.command("assess-batch-quality")
@click.argument("repos_file", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--progress/--no-progress", default=True, help="Show progress")
def assess_batch_quality(repos_file: str, format: str, output: str, progress: bool):
    """Assess multiple repositories from a file.

    REPOS_FILE should contain one repository path or URL per line.

    Examples:
        \b
        # Create repos.txt with paths
        echo "/path/to/repo1" > repos.txt
        echo "/path/to/repo2" >> repos.txt

        \b
        # Run batch assessment
        agentready assess-batch-quality repos.txt

        \b
        # Output as JSON
        agentready assess-batch-quality repos.txt --format json -o results.json
    """
    try:
        # Initialize database
        initialize_database()

        # Read repository list
        repo_paths = Path(repos_file).read_text().strip().split("\n")
        repo_paths = [p.strip() for p in repo_paths if p.strip() and not p.startswith("#")]

        if not repo_paths:
            click.echo("❌ No repositories found in file", err=True)
            sys.exit(1)

        if progress:
            click.echo(f"📦 Found {len(repo_paths)} repositories to assess")
            click.echo()

        # Services
        repo_service = RepositoryService()
        scorer = QualityScorerService()

        # Assessors
        assessors = [
            TestCoverageAssessor(),
            IntegrationTestsAssessor(),
            DocumentationStandardsAssessor(),
            EcosystemToolsAssessor(),
        ]

        # Assess each repository
        results = []

        for idx, repo_path in enumerate(repo_paths, 1):
            if progress:
                click.echo(f"[{idx}/{len(repo_paths)}] Assessing {repo_path}...")

            try:
                # Get repo info
                quality_repo = repo_service.extract_repo_info(repo_path)

                # Convert to internal model
                from ..models.repository import Repository

                repo = Repository(
                    url=quality_repo.repo_url,
                    path=str(Path(repo_path).resolve()) if Path(repo_path).exists() else repo_path,
                    name=quality_repo.name,
                    languages=[quality_repo.primary_language] if quality_repo.primary_language else [],
                    metadata={}
                )

                # Run assessments
                assessor_results = []

                for assessor in assessors:
                    finding = assessor.assess(repo)

                    result = AssessorResult(
                        assessment_id=f"batch_{idx}",
                        assessor_name=assessor.attribute_id,
                        score=finding.score if finding.score is not None else 0,
                        metrics={"status": finding.status, "evidence": finding.evidence},
                        status="success" if finding.status in ["pass", "fail"] else finding.status,
                        executed_at=datetime.utcnow(),
                    )

                    assessor_results.append(result)

                # Calculate overall score
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

                results.append({
                    "repository": quality_repo.to_dict(),
                    "assessment": assessment.to_dict(),
                    "assessor_results": [r.to_dict() for r in assessor_results],
                    "tier": tier,
                })

                if progress:
                    click.echo(f"  ✓ Score: {overall_score:.1f}/100 ({tier})")

            except Exception as e:
                if progress:
                    click.echo(f"  ✗ Failed: {str(e)}")
                
                results.append({
                    "repository": {"repo_url": repo_path, "name": repo_path},
                    "error": str(e),
                })

        # Output results
        if format == "json":
            output_content = json.dumps({
                "assessed_at": datetime.utcnow().isoformat(),
                "total_repositories": len(repo_paths),
                "successful": len([r for r in results if "error" not in r]),
                "failed": len([r for r in results if "error" in r]),
                "results": results,
            }, indent=2, default=str)
        else:
            output_content = format_batch_text(results)

        if output:
            Path(output).write_text(output_content)
            click.echo(f"\n✅ Results saved to: {output}")
        else:
            click.echo(f"\n{output_content}")

    except Exception as e:
        click.echo(f"❌ Batch assessment failed: {str(e)}", err=True)
        sys.exit(1)


def format_batch_text(results: List[Dict]) -> str:
    """Format batch results as plain text."""
    lines = []
    lines.append("=" * 70)
    lines.append("BATCH QUALITY ASSESSMENT RESULTS")
    lines.append("=" * 70)
    lines.append()

    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]

    lines.append(f"Total Repositories: {len(results)}")
    lines.append(f"Successful: {len(successful)}")
    lines.append(f"Failed: {len(failed)}")
    lines.append()

    if successful:
        lines.append("=" * 70)
        lines.append("REPOSITORY SCORES")
        lines.append("=" * 70)
        lines.append()

        # Sort by score descending
        sorted_results = sorted(successful, key=lambda r: r["assessment"]["overall_score"], reverse=True)

        for idx, result in enumerate(sorted_results, 1):
            repo_name = result["repository"]["name"]
            score = result["assessment"]["overall_score"]
            tier = result["tier"]
            
            lines.append(f"{idx}. {repo_name}: {score:.1f}/100 ({tier})")

        lines.append()

    if failed:
        lines.append("=" * 70)
        lines.append("FAILED ASSESSMENTS")
        lines.append("=" * 70)
        lines.append()

        for result in failed:
            repo = result["repository"]["name"]
            error = result.get("error", "Unknown error")
            lines.append(f"✗ {repo}: {error}")

        lines.append()

    return "\n".join(lines)
