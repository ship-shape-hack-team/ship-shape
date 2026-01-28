"""Integration test assessor for quality profiling."""

from pathlib import Path

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class IntegrationTestsAssessor(BaseAssessor):
    """Assess integration test presence and quality."""

    @property
    def attribute_id(self) -> str:
        return "quality_integration_tests"

    @property
    def tier(self) -> int:
        return 1  # Essential
    
    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Integration Tests",
            category="Testing",
            tier=self.tier,
            description="Integration test coverage for APIs, databases, and services",
            criteria="10+ integration tests with proper mocking and containers",
            default_weight=0.20,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess integration tests for the repository."""
        try:
            repo_path = Path(repository.path)

            # Look for integration test indicators
            integration_test_count = self._count_integration_tests(repo_path)
            has_test_containers = self._check_test_containers(repo_path)
            has_db_tests = self._check_database_tests(repo_path)

            if integration_test_count == 0:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=0,
                    measured_value=0,
                    threshold=10,
                    evidence=["No integration tests found"],
                    remediation="Add integration tests to verify component interactions, database operations, and API endpoints",
                    error_message=None,
                )

            # Calculate score
            score = min(100, (integration_test_count / 10) * 100)  # 10+ integration tests = 100

            evidence_parts = [
                f"Integration test files: {integration_test_count}",
            ]

            if has_test_containers:
                evidence_parts.append("✓ Test containers detected")
                score = min(100, score + 10)

            if has_db_tests:
                evidence_parts.append("✓ Database tests detected")
                score = min(100, score + 10)

            evidence_list = evidence_parts

            if score >= 70:
                return Finding(
                    attribute=self.attribute,
                    status="pass",
                    score=score,
                    measured_value=integration_test_count,
                    threshold=10,
                    evidence=evidence_list,
                    remediation="Good integration test coverage. Consider adding contract tests for external APIs.",
                    error_message=None,
                )
            else:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=score,
                    measured_value=integration_test_count,
                    threshold=10,
                    evidence=evidence_list,
                    remediation=f"Add more integration tests (found {integration_test_count}, recommend 10+). Test API endpoints, database operations, and service interactions.",
                    error_message=None,
                )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"Integration test assessment failed: {str(e)}"
            )

    def _count_integration_tests(self, repo_path: Path) -> int:
        """Count integration test files."""
        count = 0

        integration_patterns = [
            "**/test_integration*.py",
            "**/integration_test*.py",
            "**/tests/integration/**/*.py",
            "**/e2e/**/*.py",
            "**/integration/**/*test*.py",
        ]

        for pattern in integration_patterns:
            count += len(list(repo_path.glob(pattern)))

        return count

    def _check_test_containers(self, repo_path: Path) -> bool:
        """Check for Testcontainers or similar."""
        indicators = [
            "testcontainers",
            "docker-compose.test",
            "test-compose",
        ]

        for file in repo_path.rglob("*"):
            if file.is_file():
                content = file.name.lower()
                if any(ind in content for ind in indicators):
                    return True

        return False

    def _check_database_tests(self, repo_path: Path) -> bool:
        """Check for database integration tests."""
        db_indicators = [
            "test_db",
            "test_database",
            "db_test",
            "database_test",
        ]

        for file in repo_path.rglob("*.py"):
            file_content = file.name.lower()
            if any(ind in file_content for ind in db_indicators):
                return True

        return False

