"""Test fixtures and mocks assessor for quality profiling."""

import re
from pathlib import Path
from typing import Dict, List, Set

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class TestFixturesAssessor(BaseAssessor):
    """Assess test fixtures, mocks, and test data factories."""

    @property
    def attribute_id(self) -> str:
        return "quality_test_fixtures"

    @property
    def tier(self) -> int:
        return 2  # Important

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Test Fixtures and Mocks",
            category="Testing",
            tier=self.tier,
            description="pytest fixtures, mock/stub libraries, test data factories, fixture documentation",
            criteria="Comprehensive fixture usage with proper mocking and test data generation",
            default_weight=0.08,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess test fixtures and mocks.

        Args:
            repository: Repository to assess

        Returns:
            Finding with test fixtures metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Check for test files first
            test_files = self._find_test_files(repo_path)
            if not test_files:
                return Finding(
                    attribute=self.attribute,
                    status="skipped",
                    score=0,
                    measured_value=0,
                    threshold=70,
                    evidence=["No test files found in repository"],
                    remediation="N/A - Add tests first before using fixtures",
                    error_message=None,
                )

            # Analyze fixture usage
            analysis = self._analyze_fixtures(repo_path, test_files)
            score = self._calculate_score(analysis)
            evidence_str = self._format_evidence(analysis)
            remediation_str = self._generate_remediation(analysis)

            status = "pass" if score >= 70 else "fail"

            return Finding(
                attribute=self.attribute,
                status=status,
                score=score,
                measured_value=score,
                threshold=70,
                evidence=[evidence_str],
                remediation=remediation_str,
                error_message=None,
            )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"Test fixtures assessment failed: {str(e)}"
            )

    def _find_test_files(self, repo_path: Path) -> List[Path]:
        """Find test files."""
        test_patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/*.test.js",
            "**/*.test.ts",
            "**/*.spec.js",
            "**/*.spec.ts",
            "**/*_test.go",
            "**/*Test.java",
        ]

        test_files = []
        seen = set()

        for pattern in test_patterns:
            for file in repo_path.glob(pattern):
                if file.is_file() and str(file) not in seen:
                    path_parts = file.parts
                    if any(exclude in path_parts for exclude in ["node_modules", "vendor", ".venv", "venv"]):
                        continue
                    test_files.append(file)
                    seen.add(str(file))

        return test_files

    def _analyze_fixtures(self, repo_path: Path, test_files: List[Path]) -> Dict:
        """Analyze fixture usage in tests."""
        analysis = {
            "has_conftest": False,
            "conftest_files": [],
            "fixture_count": 0,
            "mock_library_used": False,
            "mock_patterns_found": [],
            "has_factories": False,
            "factory_files": [],
            "fixture_documentation": False,
            "test_files_using_fixtures": 0,
            "total_test_files": len(test_files),
        }

        # Find conftest.py files (pytest fixtures)
        conftest_files = list(repo_path.glob("**/conftest.py"))
        if conftest_files:
            analysis["has_conftest"] = True
            analysis["conftest_files"] = [str(f.relative_to(repo_path)) for f in conftest_files]
            
            # Count fixtures in conftest files
            for conftest in conftest_files:
                content = self._read_file_safe(conftest)
                analysis["fixture_count"] += len(re.findall(r'@pytest\.fixture', content))
                if '"""' in content or "'''" in content:
                    analysis["fixture_documentation"] = True

        # Check for mock library usage
        mock_patterns = {
            "unittest.mock": r'from\s+unittest\.mock\s+import|import\s+unittest\.mock',
            "pytest-mock": r'from\s+pytest_mock|@pytest\.fixture.*mock',
            "jest.mock": r'jest\.mock\(|jest\.spyOn\(',
            "sinon": r'import.*sinon|from.*sinon',
            "gomock": r'import.*gomock|github\.com/golang/mock',
            "mockito": r'import.*mockito|@Mock\s',
        }

        for test_file in test_files[:50]:  # Sample first 50 files
            content = self._read_file_safe(test_file)
            
            for mock_name, pattern in mock_patterns.items():
                if re.search(pattern, content):
                    analysis["mock_library_used"] = True
                    if mock_name not in analysis["mock_patterns_found"]:
                        analysis["mock_patterns_found"].append(mock_name)
            
            # Check if test uses fixtures
            if self._uses_fixtures(content):
                analysis["test_files_using_fixtures"] += 1

        # Check for factory patterns
        factory_patterns = [
            "**/factories.py",
            "**/factory.py",
            "**/*_factory.py",
            "**/test_factories.py",
            "**/factories/*.py",
        ]

        factory_files = []
        for pattern in factory_patterns:
            factory_files.extend(repo_path.glob(pattern))

        if factory_files:
            analysis["has_factories"] = True
            analysis["factory_files"] = [str(f.relative_to(repo_path)) for f in factory_files[:5]]

        return analysis

    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _uses_fixtures(self, content: str) -> bool:
        """Check if test file uses fixtures."""
        fixture_indicators = [
            r'@pytest\.fixture',
            r'def\s+\w+\([^)]*\w+_fixture',
            r'def\s+\w+\([^)]*mock',
            r'jest\.mock\(',
            r'beforeEach\(',
            r'@Mock',
            r'@InjectMocks',
        ]

        return any(re.search(pattern, content) for pattern in fixture_indicators)

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate score based on fixture usage.
        
        Scoring:
        - 30 points: Has conftest.py or fixture files
        - 25 points: Mock library properly used
        - 20 points: Test data factories exist
        - 15 points: Fixture documentation present
        - 10 points: High fixture usage ratio (>50% of tests)
        """
        score = 0

        # Has conftest/fixtures (30 points)
        if analysis["has_conftest"]:
            score += 30

        # Mock library used (25 points)
        if analysis["mock_library_used"]:
            score += 25

        # Has factories (20 points)
        if analysis["has_factories"]:
            score += 20

        # Fixture documentation (15 points)
        if analysis["fixture_documentation"]:
            score += 15

        # Fixture usage ratio (10 points)
        if analysis["total_test_files"] > 0:
            usage_ratio = analysis["test_files_using_fixtures"] / analysis["total_test_files"]
            if usage_ratio > 0.5:
                score += 10
            elif usage_ratio > 0.3:
                score += 5

        return min(100, score)

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        if analysis["has_conftest"]:
            parts.append(f"✓ Fixtures: {analysis['fixture_count']} in {len(analysis['conftest_files'])} conftest files")
        else:
            parts.append("✗ No conftest.py files")

        if analysis["mock_library_used"]:
            mocks = ", ".join(analysis["mock_patterns_found"][:3])
            parts.append(f"✓ Mocks: {mocks}")
        else:
            parts.append("✗ No mock libraries detected")

        if analysis["has_factories"]:
            parts.append(f"✓ Factories: {len(analysis['factory_files'])} files")
        else:
            parts.append("✗ No factory files")

        if analysis["total_test_files"] > 0:
            usage_pct = (analysis["test_files_using_fixtures"] / analysis["total_test_files"]) * 100
            parts.append(f"Usage: {usage_pct:.0f}% of tests")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        if (analysis["has_conftest"] and analysis["mock_library_used"] and 
            analysis["has_factories"] and analysis["fixture_documentation"]):
            return "Excellent fixture and mock usage. Maintain this practice for new tests."

        issues = []

        if not analysis["has_conftest"]:
            issues.append("Create conftest.py files to define reusable pytest fixtures")

        if not analysis["mock_library_used"]:
            issues.append("Use mock libraries (unittest.mock, jest.mock) to isolate unit tests from external dependencies")

        if not analysis["has_factories"]:
            issues.append("Create factory files to generate consistent test data (e.g., factories.py, FactoryBoy, faker)")

        if not analysis["fixture_documentation"]:
            issues.append("Document fixtures with docstrings explaining their purpose and usage")

        if analysis["total_test_files"] > 0:
            usage_ratio = analysis["test_files_using_fixtures"] / analysis["total_test_files"]
            if usage_ratio < 0.3:
                issues.append("Increase fixture usage across test files to reduce code duplication")

        return "; ".join(issues)
