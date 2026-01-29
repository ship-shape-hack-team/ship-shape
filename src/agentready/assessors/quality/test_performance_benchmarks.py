"""Test performance benchmarks assessor for quality profiling."""

import re
from pathlib import Path
from typing import Dict, List

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class TestPerformanceBenchmarksAssessor(BaseAssessor):
    """Assess test performance benchmarks and regression detection."""

    @property
    def attribute_id(self) -> str:
        return "quality_test_performance_benchmarks"

    @property
    def tier(self) -> int:
        return 3  # Nice-to-have

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Test Performance Benchmarks",
            category="Testing",
            tier=self.tier,
            description="Performance/benchmark tests, configuration, historical tracking, regression detection",
            criteria="Performance benchmarks with tracking and regression detection",
            default_weight=0.05,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess performance benchmark tests.

        Args:
            repository: Repository to assess

        Returns:
            Finding with performance benchmark metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Analyze benchmark tests
            analysis = self._analyze_benchmarks(repo_path)
            
            if analysis["benchmark_test_count"] == 0 and not analysis["has_benchmark_config"]:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=0,
                    measured_value=0,
                    threshold=50,
                    evidence=["No performance benchmark tests found"],
                    remediation="Add performance benchmark tests using pytest-benchmark, JMH, go test -bench, or similar tools",
                    error_message=None,
                )

            score = self._calculate_score(analysis)
            evidence_str = self._format_evidence(analysis)
            remediation_str = self._generate_remediation(analysis)

            status = "pass" if score >= 50 else "fail"

            return Finding(
                attribute=self.attribute,
                status=status,
                score=score,
                measured_value=score,
                threshold=50,
                evidence=[evidence_str],
                remediation=remediation_str,
                error_message=None,
            )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"Performance benchmark assessment failed: {str(e)}"
            )

    def _analyze_benchmarks(self, repo_path: Path) -> Dict:
        """Analyze performance benchmark tests."""
        analysis = {
            "benchmark_test_count": 0,
            "has_benchmark_config": False,
            "config_files": [],
            "has_historical_tracking": False,
            "tracking_files": [],
            "has_regression_detection": False,
        }

        # Find benchmark test files
        benchmark_patterns = [
            "**/bench_*.py",
            "**/*_bench.py",
            "**/*_benchmark.py",
            "**/*Benchmark.java",
            "**/*_test.go",  # Will check content for benchmark
            "**/benchmark*.js",
            "**/benchmark*.ts",
        ]

        benchmark_files = []
        for pattern in benchmark_patterns:
            for file in repo_path.glob(pattern):
                if file.is_file():
                    path_parts = file.parts
                    if any(exclude in path_parts for exclude in ["node_modules", "vendor", ".venv"]):
                        continue
                    
                    content = self._read_file_safe(file)
                    if self._is_benchmark_file(content, file.suffix):
                        benchmark_files.append(file)

        analysis["benchmark_test_count"] = len(benchmark_files)

        # Check for benchmark configuration
        config_patterns = [
            "**/pytest.ini",
            "**/setup.cfg",
            "**/pyproject.toml",
            "**/.benchmarkrc",
            "**/benchmark.json",
            "**/jmh.gradle",
        ]

        for pattern in config_patterns:
            for config_file in repo_path.glob(pattern):
                content = self._read_file_safe(config_file)
                if self._has_benchmark_config(content):
                    analysis["has_benchmark_config"] = True
                    analysis["config_files"].append(config_file.name)

        # Check for historical tracking
        tracking_patterns = [
            "**/.benchmarks/",
            "**/benchmarks/",
            "**/.benchmark_history/",
            "**/benchmark_results/",
        ]

        for pattern in tracking_patterns:
            for tracking_dir in repo_path.glob(pattern):
                if tracking_dir.is_dir():
                    analysis["has_historical_tracking"] = True
                    analysis["tracking_files"].append(str(tracking_dir.relative_to(repo_path)))

        # Check for regression detection in CI
        ci_files = [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
        ]

        for pattern in ci_files:
            for ci_file in repo_path.glob(pattern):
                content = self._read_file_safe(ci_file)
                if self._has_regression_detection(content):
                    analysis["has_regression_detection"] = True

        return analysis

    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _is_benchmark_file(self, content: str, suffix: str) -> bool:
        """Check if file contains benchmark tests."""
        benchmark_patterns = {
            ".py": [r'@pytest\.mark\.benchmark', r'def\s+bench_', r'benchmark\('],
            ".go": [r'func\s+Benchmark\w+\(b\s+\*testing\.B\)'],
            ".java": [r'@Benchmark', r'@BenchmarkMode'],
            ".js": [r'benchmark\(', r'suite\.add\('],
            ".ts": [r'benchmark\(', r'suite\.add\('],
        }

        patterns = benchmark_patterns.get(suffix, [])
        return any(re.search(pattern, content) for pattern in patterns)

    def _has_benchmark_config(self, content: str) -> bool:
        """Check if configuration file has benchmark settings."""
        benchmark_keywords = [
            "pytest-benchmark",
            "benchmark",
            "jmh",
            "benchmarkMode",
            "warmupIterations",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in benchmark_keywords)

    def _has_regression_detection(self, content: str) -> bool:
        """Check if CI configuration includes regression detection."""
        regression_keywords = [
            "benchmark",
            "performance",
            "regression",
            "compare-bench",
            "benchcmp",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in regression_keywords)

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate score based on benchmark tests.
        
        Scoring:
        - 40 points: Benchmark tests exist
        - 20 points: Benchmark configuration
        - 20 points: Historical tracking
        - 20 points: Regression detection in CI
        """
        score = 0

        # Benchmark tests exist (40 points)
        if analysis["benchmark_test_count"] > 0:
            score += 40

        # Benchmark configuration (20 points)
        if analysis["has_benchmark_config"]:
            score += 20

        # Historical tracking (20 points)
        if analysis["has_historical_tracking"]:
            score += 20

        # Regression detection (20 points)
        if analysis["has_regression_detection"]:
            score += 20

        return score

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        if analysis["benchmark_test_count"] > 0:
            parts.append(f"✓ Benchmark tests: {analysis['benchmark_test_count']}")
        else:
            parts.append("✗ No benchmark tests")

        if analysis["has_benchmark_config"]:
            config = ", ".join(analysis["config_files"][:2])
            parts.append(f"✓ Config: {config}")
        else:
            parts.append("✗ No config")

        if analysis["has_historical_tracking"]:
            parts.append("✓ Historical tracking")
        else:
            parts.append("✗ No tracking")

        if analysis["has_regression_detection"]:
            parts.append("✓ Regression detection")
        else:
            parts.append("✗ No regression detection")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        if (analysis["benchmark_test_count"] > 0 and analysis["has_benchmark_config"] and 
            analysis["has_historical_tracking"] and analysis["has_regression_detection"]):
            return "Excellent performance benchmark setup. Continue monitoring performance regressions."

        issues = []

        if analysis["benchmark_test_count"] == 0:
            issues.append("Add performance benchmark tests for critical code paths")

        if not analysis["has_benchmark_config"]:
            issues.append("Configure benchmarking tool (pytest-benchmark, JMH, go test -bench)")

        if not analysis["has_historical_tracking"]:
            issues.append("Enable historical tracking to monitor performance trends over time")

        if not analysis["has_regression_detection"]:
            issues.append("Add CI checks to detect performance regressions automatically")

        return "; ".join(issues)
