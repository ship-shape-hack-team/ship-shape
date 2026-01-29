"""Integration test directory structure assessor for quality profiling."""

from pathlib import Path
from typing import Dict, List, Set

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class IntegrationTestStructureAssessor(BaseAssessor):
    """Assess integration test directory structure and organization."""

    @property
    def attribute_id(self) -> str:
        return "quality_integration_test_structure"

    @property
    def tier(self) -> int:
        return 1  # Critical

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Integration Test Directory Structure",
            category="Testing",
            tier=self.tier,
            description="Dedicated integration test directory, separate from unit tests, with proper markers/tags",
            criteria="Dedicated integration test directory with test markers configured",
            default_weight=0.10,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess integration test directory structure.

        Args:
            repository: Repository to assess

        Returns:
            Finding with integration test structure metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Check for test files first
            has_tests = self._has_test_files(repo_path)
            if not has_tests:
                return Finding(
                    attribute=self.attribute,
                    status="skipped",
                    score=0,
                    measured_value=0,
                    threshold=100,
                    evidence=["No test files found in repository"],
                    remediation="N/A - Add tests first before organizing integration tests",
                    error_message=None,
                )

            # Analyze integration test structure
            analysis = self._analyze_integration_structure(repo_path)
            score = self._calculate_score(analysis)
            evidence_str = self._format_evidence(analysis)
            remediation_str = self._generate_remediation(analysis)

            status = "pass" if score >= 100 else "fail"

            return Finding(
                attribute=self.attribute,
                status=status,
                score=score,
                measured_value=score,
                threshold=100,
                evidence=[evidence_str],
                remediation=remediation_str,
                error_message=None,
            )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"Integration test structure assessment failed: {str(e)}"
            )

    def _has_test_files(self, repo_path: Path) -> bool:
        """Check if repository has any test files."""
        test_patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/*_test.go",
            "**/*.test.js",
            "**/*.test.ts",
            "**/*Test.java",
        ]

        for pattern in test_patterns:
            if list(repo_path.glob(pattern))[:1]:  # Check if at least one exists
                return True
        return False

    def _analyze_integration_structure(self, repo_path: Path) -> Dict:
        """Analyze integration test directory structure."""
        analysis = {
            "has_dedicated_dir": False,
            "integration_dir_path": None,
            "integration_test_count": 0,
            "has_markers": False,
            "marker_config_files": [],
            "separation_from_unit": False,
            "has_unit_and_integration": False,
        }

        # Common integration test directory patterns
        integration_dirs = [
            "tests/integration",
            "test/integration",
            "tests/integrations",
            "test/integrations",
            "integration_tests",
            "integration-tests",
            "tests/e2e",
            "test/e2e",
            "e2e",
        ]

        # Check for dedicated integration test directory
        for dir_pattern in integration_dirs:
            test_dir = repo_path / dir_pattern
            if test_dir.exists() and test_dir.is_dir():
                analysis["has_dedicated_dir"] = True
                analysis["integration_dir_path"] = dir_pattern
                
                # Count integration test files
                analysis["integration_test_count"] = self._count_test_files_in_dir(test_dir)
                break

        # Check for test markers/tags configuration
        marker_files = [
            "pytest.ini",
            "setup.cfg",
            "pyproject.toml",
            "jest.config.js",
            "jest.config.ts",
            "vitest.config.ts",
            "go.mod",
            ".testconfig",
        ]

        for marker_file in marker_files:
            file_path = repo_path / marker_file
            if file_path.exists():
                content = self._read_file_safe(file_path)
                if self._has_integration_markers(content, marker_file):
                    analysis["has_markers"] = True
                    analysis["marker_config_files"].append(marker_file)

        # Check separation: both unit and integration directories exist
        unit_dirs = ["tests/unit", "test/unit", "tests/units", "test/units"]
        has_unit_dir = any((repo_path / d).exists() for d in unit_dirs)
        
        if has_unit_dir and analysis["has_dedicated_dir"]:
            analysis["separation_from_unit"] = True
            analysis["has_unit_and_integration"] = True

        return analysis

    def _count_test_files_in_dir(self, directory: Path) -> int:
        """Count test files in a directory."""
        test_patterns = [
            "**/*test*.py",
            "**/*test*.js",
            "**/*test*.ts",
            "**/*test*.go",
            "**/*Test*.java",
        ]

        test_files = set()
        for pattern in test_patterns:
            for file in directory.glob(pattern):
                if file.is_file():
                    test_files.add(file)

        return len(test_files)

    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _has_integration_markers(self, content: str, filename: str) -> bool:
        """Check if file contains integration test markers/tags configuration."""
        integration_keywords = [
            "integration",
            "integrations",
            "@integration",
            "mark.integration",
            "markers",
            "testEnvironment",
            "-tags=integration",
            "e2e",
            "@e2e",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in integration_keywords)

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate score based on integration test structure.
        
        Scoring:
        - 50 points: Has dedicated integration test directory
        - 30 points: Separation from unit tests
        - 20 points: Has markers/tags configured
        """
        score = 0

        # Dedicated directory (50 points)
        if analysis["has_dedicated_dir"]:
            score += 50

        # Separation from unit tests (30 points)
        if analysis["separation_from_unit"]:
            score += 30

        # Markers configured (20 points)
        if analysis["has_markers"]:
            score += 20

        return score

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        if analysis["has_dedicated_dir"]:
            dir_path = analysis["integration_dir_path"]
            test_count = analysis["integration_test_count"]
            parts.append(f"✓ Dedicated directory: {dir_path} ({test_count} tests)")
        else:
            parts.append("✗ No dedicated integration test directory")

        if analysis["separation_from_unit"]:
            parts.append("✓ Separated from unit tests")
        else:
            parts.append("✗ Not separated from unit tests")

        if analysis["has_markers"]:
            marker_files = ", ".join(analysis["marker_config_files"])
            parts.append(f"✓ Markers configured: {marker_files}")
        else:
            parts.append("✗ No test markers configured")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        if analysis["has_dedicated_dir"] and analysis["separation_from_unit"] and analysis["has_markers"]:
            return "Excellent integration test structure. Maintain this organization for new tests."

        issues = []

        if not analysis["has_dedicated_dir"]:
            issues.append("Create dedicated integration test directory (e.g., tests/integration/)")

        if not analysis["separation_from_unit"]:
            issues.append("Separate unit and integration tests into different directories (tests/unit/ and tests/integration/)")

        if not analysis["has_markers"]:
            issues.append("Configure test markers in pytest.ini (Python) or jest.config.js (JavaScript) to tag integration tests")

        return "; ".join(issues)
