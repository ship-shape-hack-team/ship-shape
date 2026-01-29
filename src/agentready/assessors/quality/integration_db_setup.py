"""Integration test database setup assessor for quality profiling."""

from pathlib import Path
from typing import Dict, List

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class IntegrationDatabaseSetupAssessor(BaseAssessor):
    """Assess integration test database setup and configuration."""

    @property
    def attribute_id(self) -> str:
        return "quality_integration_db_setup"

    @property
    def tier(self) -> int:
        return 2  # Important

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Integration Test Database Setup",
            category="Testing",
            tier=self.tier,
            description="Test database configuration, Docker Compose for dependencies, migrations, seeding",
            criteria="Proper test database setup with containerized dependencies and data management",
            default_weight=0.08,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess integration test database setup.

        Args:
            repository: Repository to assess

        Returns:
            Finding with database setup metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Check if repository likely uses a database
            has_database = self._has_database_indicators(repo_path)
            if not has_database:
                return Finding(
                    attribute=self.attribute,
                    status="skipped",
                    score=0,
                    measured_value=0,
                    threshold=70,
                    evidence=["No database usage detected in repository"],
                    remediation="N/A - Repository does not appear to use a database",
                    error_message=None,
                )

            # Analyze database setup
            analysis = self._analyze_db_setup(repo_path)
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
                reason=f"Integration database setup assessment failed: {str(e)}"
            )

    def _has_database_indicators(self, repo_path: Path) -> bool:
        """Check if repository uses a database."""
        db_indicators = [
            # Database configuration files
            "**/database.yml",
            "**/db/",
            "**/migrations/",
            "**/alembic/",
            "**/schema.sql",
            # ORM files
            "**/models.py",
            "**/model/*.py",
            # Database libraries in requirements
            "**/requirements.txt",
            "**/pyproject.toml",
            "**/package.json",
            "**/go.mod",
        ]

        db_keywords = [
            "sqlalchemy",
            "django.db",
            "psycopg",
            "pymongo",
            "redis",
            "elasticsearch",
            "mongoose",
            "sequelize",
            "typeorm",
            "prisma",
            "gorm",
            "database/sql",
        ]

        # Check for database files
        for pattern in db_indicators[:7]:  # Check file patterns
            if list(repo_path.glob(pattern))[:1]:
                return True

        # Check for database libraries in dependency files
        for pattern in db_indicators[7:]:
            for file in repo_path.glob(pattern):
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore').lower()
                    if any(keyword in content for keyword in db_keywords):
                        return True
                except Exception:
                    continue

        return False

    def _analyze_db_setup(self, repo_path: Path) -> Dict:
        """Analyze database setup for testing."""
        analysis = {
            "has_test_db_config": False,
            "config_files": [],
            "has_docker_compose": False,
            "docker_files": [],
            "has_migrations": False,
            "migration_dirs": [],
            "has_seed_data": False,
            "seed_files": [],
        }

        # Check for test database configuration
        test_db_configs = [
            "**/test_settings.py",
            "**/settings/test.py",
            "**/config/test.yml",
            "**/config/test.yaml",
            "**/.env.test",
            "**/database.test.yml",
            "**/pytest.ini",
            "**/conftest.py",
        ]

        for pattern in test_db_configs:
            config_files = list(repo_path.glob(pattern))
            if config_files:
                for config_file in config_files:
                    content = self._read_file_safe(config_file)
                    if self._has_test_db_config(content):
                        analysis["has_test_db_config"] = True
                        analysis["config_files"].append(config_file.name)

        # Check for Docker Compose
        docker_patterns = [
            "**/docker-compose.yml",
            "**/docker-compose.yaml",
            "**/docker-compose.test.yml",
            "**/docker-compose.test.yaml",
            "**/.testcontainers",
        ]

        for pattern in docker_patterns:
            docker_files = list(repo_path.glob(pattern))
            if docker_files:
                for docker_file in docker_files:
                    content = self._read_file_safe(docker_file)
                    if self._has_test_containers(content):
                        analysis["has_docker_compose"] = True
                        analysis["docker_files"].append(docker_file.name)

        # Check for database migrations
        migration_patterns = [
            "**/migrations/",
            "**/alembic/",
            "**/db/migrate/",
            "**/prisma/migrations/",
        ]

        for pattern in migration_patterns:
            for migration_dir in repo_path.glob(pattern):
                if migration_dir.is_dir():
                    analysis["has_migrations"] = True
                    analysis["migration_dirs"].append(str(migration_dir.relative_to(repo_path)))

        # Check for test data seeding
        seed_patterns = [
            "**/seeds/",
            "**/seed.py",
            "**/fixtures/",
            "**/test_data/",
            "**/factories/",
        ]

        for pattern in seed_patterns:
            for seed_item in repo_path.glob(pattern):
                if seed_item.exists():
                    analysis["has_seed_data"] = True
                    analysis["seed_files"].append(seed_item.name)

        return analysis

    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _has_test_db_config(self, content: str) -> bool:
        """Check if file contains test database configuration."""
        test_db_keywords = [
            "test_database",
            "database_test",
            "test_db",
            "db_test",
            "testing_db",
            "sqlite:///:memory:",
            "postgresql://test",
            "mysql://test",
            "mongodb://test",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in test_db_keywords)

    def _has_test_containers(self, content: str) -> bool:
        """Check if Docker Compose file is for testing."""
        container_keywords = [
            "postgres",
            "mysql",
            "mongodb",
            "redis",
            "elasticsearch",
            "mariadb",
            "cassandra",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in container_keywords)

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate score based on database setup.
        
        Scoring:
        - 35 points: Test database configuration
        - 35 points: Docker Compose for test dependencies
        - 15 points: Database migrations
        - 15 points: Test data seeding
        """
        score = 0

        # Test database configuration (35 points)
        if analysis["has_test_db_config"]:
            score += 35

        # Docker Compose (35 points)
        if analysis["has_docker_compose"]:
            score += 35

        # Migrations (15 points)
        if analysis["has_migrations"]:
            score += 15

        # Seed data (15 points)
        if analysis["has_seed_data"]:
            score += 15

        return score

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        if analysis["has_test_db_config"]:
            config_files = ", ".join(analysis["config_files"][:2])
            parts.append(f"✓ Test DB config: {config_files}")
        else:
            parts.append("✗ No test database configuration")

        if analysis["has_docker_compose"]:
            docker_files = ", ".join(analysis["docker_files"][:2])
            parts.append(f"✓ Docker: {docker_files}")
        else:
            parts.append("✗ No Docker Compose")

        if analysis["has_migrations"]:
            parts.append(f"✓ Migrations: {len(analysis['migration_dirs'])} dirs")
        else:
            parts.append("✗ No migrations")

        if analysis["has_seed_data"]:
            parts.append(f"✓ Seed data: {len(analysis['seed_files'])} sources")
        else:
            parts.append("✗ No seed data")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        if (analysis["has_test_db_config"] and analysis["has_docker_compose"] and 
            analysis["has_migrations"] and analysis["has_seed_data"]):
            return "Excellent database test setup. Maintain this infrastructure for reliable integration tests."

        issues = []

        if not analysis["has_test_db_config"]:
            issues.append("Configure test database in test_settings.py or .env.test with isolated test database")

        if not analysis["has_docker_compose"]:
            issues.append("Add docker-compose.test.yml to provide containerized database for tests")

        if not analysis["has_migrations"]:
            issues.append("Set up database migrations (Alembic, Django migrations, Prisma) to manage schema changes")

        if not analysis["has_seed_data"]:
            issues.append("Create test data seeding scripts or fixtures for consistent test data")

        return "; ".join(issues)
