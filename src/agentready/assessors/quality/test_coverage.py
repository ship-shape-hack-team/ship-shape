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
        """Check if repository has test files across multiple languages and test types."""
        test_patterns = [
            # Python (unit, integration, e2e)
            "**/test_*.py",
            "**/*_test.py",
            "**/tests/**/*.py",
            "**/test/**/*.py",
            # JavaScript/TypeScript (unit, integration, e2e)
            "**/*.test.js",
            "**/*.test.ts",
            "**/*.test.jsx",
            "**/*.test.tsx",
            "**/*.spec.js",
            "**/*.spec.ts",
            "**/*.spec.jsx",
            "**/*.spec.tsx",
            "**/__tests__/**/*.js",
            "**/__tests__/**/*.ts",
            "**/__tests__/**/*.jsx",
            "**/__tests__/**/*.tsx",
            # E2E/UI tests
            "**/e2e/**/*.js",
            "**/e2e/**/*.ts",
            "**/cypress/**/*.js",
            "**/cypress/**/*.ts",
            "**/*.e2e.js",
            "**/*.e2e.ts",
            "**/playwright/**/*.ts",
            "**/playwright/**/*.js",
            # Go
            "**/*_test.go",
            # Java
            "**/src/test/**/*Test.java",
            "**/src/test/**/*Tests.java",
            "**/test/**/*Test.java",
            # Rust
            "**/*_test.rs",
            "**/tests/**/*.rs",
            # Ruby
            "**/*_spec.rb",
            "**/spec/**/*.rb",
            # C/C++
            "**/test_*.c",
            "**/test_*.cpp",
            "**/tests/**/*.c",
            "**/tests/**/*.cpp",
            # PHP
            "**/*Test.php",
            "**/tests/**/*Test.php",
            # C#
            "**/*Test.cs",
            "**/*Tests.cs",
            "**/test/**/*.cs",
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
        """Estimate coverage from test file to source file ratio across all languages and test types."""
        test_files = 0
        source_files = 0
        test_files_by_type = {
            'unit': 0,
            'integration': 0,
            'e2e': 0,
        }
        
        # Multi-language source and test extensions
        source_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.rs', '.rb', 
            '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.swift', '.kt'
        }
        
        # Test file indicators by type
        unit_test_indicators = ['test_', '_test.', '.test.', '.spec.', '__tests__', '/tests/', '/test/', '/spec/']
        integration_indicators = ['integration', 'integ_test', 'test_integration']
        e2e_indicators = ['e2e', 'cypress', 'playwright', 'selenium', 'end-to-end', 'e2e-tests']

        for root, dirs, files in os.walk(repo_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in [
                '.git', 'node_modules', '.venv', 'venv', '__pycache__', 
                'vendor', 'target', 'build', 'dist', '.gradle', 'bin', 'obj'
            ]]

            for file in files:
                file_ext = os.path.splitext(file)[1]
                
                if file_ext in source_extensions:
                    file_lower = file.lower()
                    root_lower = root.lower()
                    
                    # Determine test type
                    is_e2e = any(indicator in file_lower or indicator in root_lower 
                                for indicator in e2e_indicators)
                    is_integration = any(indicator in file_lower or indicator in root_lower 
                                       for indicator in integration_indicators)
                    is_unit_test = any(indicator in file_lower or indicator in root_lower 
                                     for indicator in unit_test_indicators)
                    
                    if is_e2e:
                        test_files += 1
                        test_files_by_type['e2e'] += 1
                    elif is_integration:
                        test_files += 1
                        test_files_by_type['integration'] += 1
                    elif is_unit_test:
                        test_files += 1
                        test_files_by_type['unit'] += 1
                    else:
                        source_files += 1

        if source_files == 0:
            return {
                "line_coverage": 0, 
                "test_count": test_files,
                "unit_tests": test_files_by_type['unit'],
                "integration_tests": test_files_by_type['integration'],
                "e2e_tests": test_files_by_type['e2e'],
            }

        # Improved estimate accounting for all test types
        # E2E tests count more (cover more code) than unit tests
        weighted_test_count = (
            test_files_by_type['unit'] * 1.0 +
            test_files_by_type['integration'] * 1.5 +
            test_files_by_type['e2e'] * 2.0
        )
        
        ratio = weighted_test_count / source_files if source_files > 0 else 0
        
        # Better coverage estimation with weighted tests
        if ratio >= 1.0:
            estimated_coverage = min(100, 80 + (ratio - 1) * 20)
        elif ratio >= 0.5:
            estimated_coverage = 50 + (ratio - 0.5) * 60
        else:
            estimated_coverage = ratio * 100

        return {
            "line_coverage": estimated_coverage,
            "branch_coverage": 0,
            "function_coverage": 0,
            "test_count": test_files,
            "unit_tests": test_files_by_type['unit'],
            "integration_tests": test_files_by_type['integration'],
            "e2e_tests": test_files_by_type['e2e'],
            "source_count": source_files,
            "test_to_code_ratio": ratio,
        }

    def _format_evidence(self, metrics: Dict[str, Any]) -> str:
        """Format coverage metrics as evidence string."""
        parts = [
            f"Line coverage: {metrics.get('line_coverage', 0):.1f}%",
        ]

        if metrics.get("test_count"):
            total = metrics['test_count']
            unit = metrics.get('unit_tests', 0)
            integration = metrics.get('integration_tests', 0)
            e2e = metrics.get('e2e_tests', 0)
            
            if unit or integration or e2e:
                parts.append(f"Tests: {total} total ({unit} unit, {integration} integration, {e2e} e2e)")
            else:
                parts.append(f"Test count: {total}")

        if metrics.get("source_count"):
            parts.append(f"Source files: {metrics['source_count']}")

        if metrics.get("test_to_code_ratio"):
            parts.append(f"Ratio: {metrics['test_to_code_ratio']:.2f}")

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
