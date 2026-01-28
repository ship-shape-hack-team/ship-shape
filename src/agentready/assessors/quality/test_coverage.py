"""Test coverage assessor for quality profiling."""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class TestCoverageAssessor(BaseAssessor):
    """Assess unit test coverage metrics."""

    @property
    def attribute_id(self) -> str:
        return "quality_test_coverage"

    @property
    def tier(self) -> int:
        return 1  # Essential

    def assess(self, repository: Repository) -> Finding:
        """Assess test coverage for the repository.

        Args:
            repository: Repository to assess

        Returns:
            Finding with coverage metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Check if tests exist
            if not self._has_tests(repo_path):
                return Finding.fail(
                    attribute_id=self.attribute_id,
                    score=0,
                    evidence="No test files found in repository",
                    remediation="Add unit tests using pytest, unittest, or similar framework"
                )

            # Try to detect and run coverage
            coverage_metrics = self._detect_coverage(repo_path)

            if coverage_metrics is None:
                return Finding.fail(
                    attribute_id=self.attribute_id,
                    score=0,
                    evidence="Tests found but coverage could not be determined",
                    remediation="Install coverage.py and run: pip install coverage; coverage run -m pytest; coverage report"
                )

            # Calculate score based on line coverage
            line_coverage = coverage_metrics.get("line_coverage", 0)
            score = min(100, (line_coverage / 80) * 100)  # 80% coverage = 100 score

            evidence = self._format_evidence(coverage_metrics)
            remediation = self._generate_remediation(coverage_metrics)

            if line_coverage >= 80:
                return Finding.pass_(
                    attribute_id=self.attribute_id,
                    score=score,
                    evidence=evidence,
                    remediation=remediation
                )
            else:
                return Finding.fail(
                    attribute_id=self.attribute_id,
                    score=score,
                    evidence=evidence,
                    remediation=remediation
                )

        except Exception as e:
            return Finding.error(
                attribute_id=self.attribute_id,
                error_message=f"Coverage assessment failed: {str(e)}"
            )

    def _has_tests(self, repo_path: Path) -> bool:
        """Check if repository has test files."""
        test_patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/tests/**/*.py",
            "**/__tests__/**/*.js",
            "**/__tests__/**/*.ts",
            "**/test/**/*.py",
        ]

        for pattern in test_patterns:
            if list(repo_path.glob(pattern)):
                return True

        return False

    def _detect_coverage(self, repo_path: Path) -> Dict[str, Any]:
        """Detect test coverage metrics.

        Args:
            repo_path: Path to repository

        Returns:
            Coverage metrics dict or None if not available
        """
        # Check for existing coverage files
        coverage_file = repo_path / ".coverage"
        if coverage_file.exists():
            metrics = self._parse_coverage_file(repo_path)
            if metrics:
                return metrics

        # Try to estimate from test file ratio
        return self._estimate_from_test_ratio(repo_path)

    def _parse_coverage_file(self, repo_path: Path) -> Dict[str, Any]:
        """Parse .coverage file if exists."""
        try:
            # Try to run coverage report
            result = subprocess.run(
                ["coverage", "report", "--format=json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                return {
                    "line_coverage": data.get("totals", {}).get("percent_covered", 0),
                    "branch_coverage": 0,  # Not always available
                    "function_coverage": 0,
                    "test_count": 0,
                }
        except Exception:
            pass

        return None

    def _estimate_from_test_ratio(self, repo_path: Path) -> Dict[str, Any]:
        """Estimate coverage from test file to source file ratio."""
        test_files = 0
        source_files = 0

        for root, dirs, files in os.walk(repo_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__']]

            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    if 'test' in file.lower() or 'test' in root.lower():
                        test_files += 1
                    else:
                        source_files += 1

        if source_files == 0:
            return {"line_coverage": 0, "test_count": test_files}

        # Rough estimate: if you have 1 test file per 2 source files, assume ~50% coverage
        ratio = test_files / source_files if source_files > 0 else 0
        estimated_coverage = min(100, ratio * 50)

        return {
            "line_coverage": estimated_coverage,
            "branch_coverage": 0,
            "function_coverage": 0,
            "test_count": test_files,
            "test_to_code_ratio": ratio,
        }

    def _format_evidence(self, metrics: Dict[str, Any]) -> str:
        """Format coverage metrics as evidence string."""
        parts = [
            f"Line coverage: {metrics.get('line_coverage', 0):.1f}%",
        ]

        if metrics.get("branch_coverage"):
            parts.append(f"Branch coverage: {metrics['branch_coverage']:.1f}%")

        if metrics.get("test_count"):
            parts.append(f"Test count: {metrics['test_count']}")

        if metrics.get("test_to_code_ratio"):
            parts.append(f"Test/code ratio: {metrics['test_to_code_ratio']:.2f}")

        return " | ".join(parts)

    def _generate_remediation(self, metrics: Dict[str, Any]) -> str:
        """Generate remediation advice based on metrics."""
        line_coverage = metrics.get("line_coverage", 0)

        if line_coverage < 50:
            return "Critical: Add comprehensive unit tests. Aim for at least 80% line coverage. Start with critical business logic and error paths."
        elif line_coverage < 80:
            return f"Increase test coverage from {line_coverage:.0f}% to 80%. Focus on untested modules and edge cases."
        else:
            return f"Good coverage at {line_coverage:.0f}%. Consider adding more edge case tests and improving branch coverage."
