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
        """Count integration test files across all languages.
        
        Uses the same flexible detection as test_coverage assessor - 
        looks for 'integration' keyword in path/filename plus specific patterns.
        """
        import os
        
        count = 0
        seen_files = set()
        
        # Source/test file extensions
        test_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.kt',
            '.rs', '.rb', '.cs', '.php', '.swift'
        }
        
        # Integration test indicators (substring match in path or filename)
        integration_indicators = [
            'integration', 'integ_test', 'test_integration', 'integrationtest',
        ]
        
        # E2E test indicators (also count as integration-level tests)
        e2e_indicators = [
            'e2e', 'cypress', 'playwright', 'selenium', 'end-to-end', 
            'e2e-tests', 'e2e_tests', 'endtoend'
        ]
        
        # Directories to skip
        skip_dirs = {
            '.git', 'node_modules', '.venv', 'venv', '__pycache__',
            'vendor', 'target', 'build', 'dist', '.gradle', 'bin', 'obj',
            '.tox', '.pytest_cache', '.mypy_cache', 'coverage'
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip non-source directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            root_lower = root.lower()
            
            for file in files:
                file_ext = os.path.splitext(file)[1]
                
                if file_ext in test_extensions:
                    file_lower = file.lower()
                    full_path = os.path.join(root, file)
                    
                    # Check if it's an integration test
                    is_integration = any(
                        indicator in file_lower or indicator in root_lower
                        for indicator in integration_indicators
                    )
                    
                    # Check if it's an E2E test (counts as integration)
                    is_e2e = any(
                        indicator in file_lower or indicator in root_lower
                        for indicator in e2e_indicators
                    )
                    
                    if (is_integration or is_e2e) and full_path not in seen_files:
                        seen_files.add(full_path)
                        count += 1
        
        return count

    def _check_test_containers(self, repo_path: Path) -> bool:
        """Check for Testcontainers or similar across languages."""
        # File name indicators
        file_indicators = [
            "testcontainers",
            "docker-compose.test",
            "docker-compose.integration",
            "docker-compose.e2e",
            "test-compose",
            "compose.test",
            "compose.integration",
        ]

        for file in repo_path.rglob("*"):
            if file.is_file():
                content = file.name.lower()
                if any(ind in content for ind in file_indicators):
                    return True

        # Check dependency files for testcontainers libraries
        dep_files = [
            ("requirements*.txt", ["testcontainers"]),
            ("pyproject.toml", ["testcontainers"]),
            ("package.json", ["testcontainers", "@testcontainers"]),
            ("pom.xml", ["testcontainers"]),
            ("build.gradle", ["testcontainers"]),
            ("build.gradle.kts", ["testcontainers"]),
            ("go.mod", ["testcontainers"]),
            ("Cargo.toml", ["testcontainers"]),
            ("*.csproj", ["Testcontainers"]),
            ("Gemfile", ["testcontainers"]),
            ("composer.json", ["testcontainers"]),
        ]

        for pattern, keywords in dep_files:
            for dep_file in repo_path.glob(f"**/{pattern}"):
                try:
                    content = dep_file.read_text(errors="ignore").lower()
                    if any(kw.lower() in content for kw in keywords):
                        return True
                except Exception:
                    continue

        return False

    def _check_database_tests(self, repo_path: Path) -> bool:
        """Check for database integration tests across languages."""
        # File name patterns indicating database tests
        db_file_patterns = [
            "test_db", "test_database", "db_test", "database_test",
            "db.test", "database.test", "db.spec", "database.spec",
            "repository.test", "repository.spec", "repo.test", "repo.spec",
            "persistence.test", "persistence.spec",
            "dao.test", "dao.spec", "dal.test", "dal.spec",
            "model.test", "model.spec", "models.test", "models.spec",
            "migration.test", "migrations.test",
            "sqlite", "postgres", "mysql", "mongodb", "redis",
        ]

        # Check multiple file extensions
        test_extensions = [
            "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", 
            "*.go", "*.java", "*.kt", "*.cs", "*.rb", "*.php", "*.rs"
        ]
        
        for ext in test_extensions:
            for file in repo_path.rglob(ext):
                file_lower = file.name.lower()
                if any(ind in file_lower for ind in db_file_patterns):
                    return True

        # Also check for test fixtures directory with db-related content
        fixture_patterns = [
            "**/fixtures/**/*db*",
            "**/fixtures/**/*database*",
            "**/fixtures/**/*.sql",
            "**/test/fixtures/**/*.sql",
            "**/tests/fixtures/**/*.sql",
            "**/__fixtures__/**/*.sql",
            "**/seeds/**/*.sql",
            "**/migrations/**/test*.sql",
        ]
        
        for pattern in fixture_patterns:
            if list(repo_path.glob(pattern)):
                return True

        return False

