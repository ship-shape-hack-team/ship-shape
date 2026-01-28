"""CLI command for quality benchmarking."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from ..models.assessment import Assessment
from ..models.assessor_result import AssessorResult
from ..services.benchmarking import BenchmarkingService


@click.command("benchmark-quality")
@click.argument("assessments_file", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--top", type=int, default=10, help="Number of top repositories to show")
def benchmark_quality(assessments_file: str, format: str, output: Optional[str], top: int):
    """Generate benchmark from assessment results.

    ASSESSMENTS_FILE should be a JSON file from assess-batch-quality --format json

    Examples:
        \b
        # Run batch assessment and save results
        agentready assess-batch-quality repos.txt --format json -o assessments.json

        \b
        # Generate benchmark
        agentready benchmark-quality assessments.json

        \b
        # Show top 20 repositories
        agentready benchmark-quality assessments.json --top 20

        \b
        # Output as JSON
        agentready benchmark-quality assessments.json --format json -o benchmark.json
    """
    try:
        # Load assessment results
        data = json.loads(Path(assessments_file).read_text())

        if "results" not in data:
            click.echo("❌ Invalid assessments file format", err=True)
            sys.exit(1)

        # Filter successful assessments
        successful_results = [r for r in data["results"] if "error" not in r]

        if not successful_results:
            click.echo("❌ No successful assessments to benchmark", err=True)
            sys.exit(1)

        click.echo(f"📊 Generating benchmark from {len(successful_results)} repositories...")

        # Convert to Assessment and AssessorResult models
        assessments = []
        assessor_results_map = {}

        for result in successful_results:
            assessment_data = result["assessment"]
            assessment = Assessment.from_dict(assessment_data)
            assessments.append(assessment)

            # Convert assessor results
            assessor_results = [
                AssessorResult.from_dict(ar)
                for ar in result.get("assessor_results", [])
            ]
            assessor_results_map[assessment.id] = assessor_results

        # Create benchmark
        benchmarking_service = BenchmarkingService()
        benchmark = benchmarking_service.create_benchmark(assessments, assessor_results_map)
        rankings = benchmarking_service.calculate_rankings(benchmark, assessments, assessor_results_map)

        click.echo(f"✅ Benchmark created with {len(rankings)} repositories")
        click.echo()

        # Output results
        if format == "json":
            output_content = json.dumps({
                "benchmark": benchmark.to_dict(),
                "rankings": [r.to_dict() for r in rankings],
            }, indent=2, default=str)
        else:
            output_content = format_benchmark_text(benchmark, rankings, top, successful_results)

        if output:
            Path(output).write_text(output_content)
            click.echo(f"✅ Benchmark saved to: {output}")
        else:
            click.echo(output_content)

    except Exception as e:
        click.echo(f"❌ Benchmark generation failed: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def format_benchmark_text(benchmark, rankings, top_n, results_data) -> str:
    """Format benchmark as plain text."""
    lines = []
    lines.append("=" * 70)
    lines.append("QUALITY BENCHMARK REPORT")
    lines.append("=" * 70)
    lines.append()
    lines.append(f"Benchmark ID: {benchmark.id}")
    lines.append(f"Created: {benchmark.created_at}")
    lines.append(f"Repositories: {benchmark.repository_count}")
    lines.append()

    # Statistical summary
    if benchmark.statistical_summary:
        stats = benchmark.statistical_summary.overall_score
        lines.append("=" * 70)
        lines.append("STATISTICAL SUMMARY")
        lines.append("=" * 70)
        lines.append()
        lines.append(f"Mean Score: {stats.mean:.1f}/100")
        lines.append(f"Median Score: {stats.median:.1f}/100")
        lines.append(f"Std Deviation: {stats.std_dev:.1f}")
        lines.append(f"Range: {stats.min:.1f} - {stats.max:.1f}")
        lines.append()
        lines.append("Percentiles:")
        for p, value in stats.percentiles.items():
            lines.append(f"  {p.upper()}: {value:.1f}")
        lines.append()

    # Top repositories
    lines.append("=" * 70)
    lines.append(f"TOP {min(top_n, len(rankings))} REPOSITORIES")
    lines.append("=" * 70)
    lines.append()

    top_rankings = rankings[:top_n]

    for ranking in top_rankings:
        # Find repo name from results
        repo_name = ranking.repo_url
        for r in results_data:
            if r["repository"]["repo_url"] == ranking.repo_url:
                repo_name = r["repository"]["name"]
                break

        lines.append(f"#{ranking.rank} {repo_name}")
        lines.append(f"   Score: {ranking.percentile:.1f}th percentile")
        
        # Show dimension scores
        if ranking.dimension_scores:
            lines.append("   Dimensions:")
            for dim_name, dim_score in ranking.dimension_scores.items():
                clean_name = dim_name.replace("quality_", "").replace("_", " ").title()
                lines.append(f"     • {clean_name}: {dim_score.score:.1f} (#{dim_score.rank})")
        
        lines.append()

    return "\n".join(lines)


@click.command("benchmark-show")
@click.argument("benchmark_file", type=click.Path(exists=True))
@click.option("--top", type=int, default=10, help="Number of top repositories to show")
@click.option("--bottom", type=int, default=0, help="Number of bottom repositories to show")
def benchmark_show(benchmark_file: str, top: int, bottom: int):
    """Display benchmark results.

    Examples:
        \b
        # Show top 10
        agentready benchmark-show benchmark.json

        \b
        # Show top 20
        agentready benchmark-show benchmark.json --top 20

        \b
        # Show top 10 and bottom 5
        agentready benchmark-show benchmark.json --top 10 --bottom 5
    """
    try:
        data = json.loads(Path(benchmark_file).read_text())

        benchmark_data = data.get("benchmark", {})
        rankings_data = data.get("rankings", [])

        click.echo("=" * 70)
        click.echo("BENCHMARK SUMMARY")
        click.echo("=" * 70)
        click.echo()
        click.echo(f"Benchmark ID: {benchmark_data.get('id', 'unknown')}")
        click.echo(f"Repositories: {benchmark_data.get('repository_count', 0)}")
        click.echo(f"Created: {benchmark_data.get('created_at', 'unknown')}")
        click.echo()

        # Show statistical summary
        if "statistical_summary" in benchmark_data:
            stats = benchmark_data["statistical_summary"]["overall_score"]
            click.echo("Overall Score Statistics:")
            click.echo(f"  Mean: {stats['mean']:.1f}")
            click.echo(f"  Median: {stats['median']:.1f}")
            click.echo(f"  Range: {stats['min']:.1f} - {stats['max']:.1f}")
            click.echo()

        # Show top repositories
        if top > 0:
            click.echo(f"🏆 TOP {min(top, len(rankings_data))} REPOSITORIES")
            click.echo("-" * 70)
            for i, ranking in enumerate(rankings_data[:top], 1):
                click.echo(f"{i}. {ranking['repo_url']}")
                click.echo(f"   Rank: #{ranking['rank']} | Percentile: {ranking['percentile']:.1f}th")
            click.echo()

        # Show bottom repositories
        if bottom > 0 and len(rankings_data) > bottom:
            click.echo(f"📉 BOTTOM {bottom} REPOSITORIES")
            click.echo("-" * 70)
            for i, ranking in enumerate(rankings_data[-bottom:], 1):
                click.echo(f"{i}. {ranking['repo_url']}")
                click.echo(f"   Rank: #{ranking['rank']} | Percentile: {ranking['percentile']:.1f}th")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to display benchmark: {str(e)}", err=True)
        sys.exit(1)
