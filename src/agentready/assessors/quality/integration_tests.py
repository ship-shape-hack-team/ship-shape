"""Integration test assessor for quality profiling."""

from pathlib import Path

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

    def assess(self, repository: Repository) -> Finding:
        """Assess integration tests for the repository."""
        try:
            repo_path = Path(repository.path)

            # Look for integration test indicators
            integration_test_count = self._count_integration_tests(repo_path)
            has_test_containers = self._check_test_containers(repo_path)
            has_db_tests = self._check_database_tests(repo_path)

            if integration_test_count == 0:
                return Finding.fail(
                    attribute_id=self.attribute_id,
                    score=0,
                    evidence="No integration tests found",
                    remediation="Add integration tests to verify component interactions, database operations, and API endpoints"
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

            evidence = " | ".join(evidence_parts)

            if score >= 70:
                return Finding.pass_(
                    attribute_id=self.attribute_id,
                    score=score,
                    evidence=evidence,
                    remediation="Good integration test coverage. Consider adding contract tests for external APIs."
                )
            else:
                return Finding.fail(
                    attribute_id=self.attribute_id,
                    score=score,
                    evidence=evidence,
                    remediation=f"Add more integration tests (found {integration_test_count}, recommend 10+). Test API endpoints, database operations, and service interactions."
                )

        except Exception as e:
            return Finding.error(
                attribute_id=self.attribute_id,
                error_message=f"Integration test assessment failed: {str(e)}"
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
