"""Ecosystem tools assessor for quality profiling."""

from pathlib import Path
from typing import Dict, List

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class EcosystemToolsAssessor(BaseAssessor):
    """Assess ecosystem tool usage (CI/CD, security, testing tools)."""

    @property
    def attribute_id(self) -> str:
        return "quality_ecosystem_tools"

    @property
    def tier(self) -> int:
        return 1  # Essential
    
    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Ecosystem Tools",
            category="DevOps",
            tier=self.tier,
            description="CI/CD, code coverage, security scanning, linting, and dependency management",
            criteria="CI/CD present, coverage tracking, security scanning configured",
            default_weight=0.20,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess ecosystem tools for the repository."""
        try:
            repo_path = Path(repository.path)

            tools_found = self._detect_tools(repo_path)
            score = self._calculate_score(tools_found)
            evidence_str = self._format_evidence(tools_found)
            remediation_str = self._generate_remediation(tools_found)

            if score >= 70:
                return Finding(
                    attribute=self.attribute,
                    status="pass",
                    score=score,
                    measured_value=score,
                    threshold=70,
                    evidence=[evidence_str],
                    remediation=remediation_str,
                    error_message=None,
                )
            else:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
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
                reason=f"Ecosystem tools assessment failed: {str(e)}"
            )

    def _detect_tools(self, repo_path: Path) -> Dict[str, bool]:
        """Detect presence of ecosystem tools."""
        tools = {
            "ci_cd": self._check_ci_cd(repo_path),
            "code_coverage": self._check_coverage_tools(repo_path),
            "security_scanning": self._check_security_tools(repo_path),
            "linting": self._check_linting_tools(repo_path),
            "dependency_management": self._check_dependency_tools(repo_path),
            "pre_commit_hooks": self._check_pre_commit(repo_path),
        }

        return tools

    def _check_ci_cd(self, repo_path: Path) -> bool:
        """Check for CI/CD configuration."""
        ci_indicators = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".travis.yml",
            "Jenkinsfile",
            ".circleci",
            "azure-pipelines.yml",
        ]

        for indicator in ci_indicators:
            if (repo_path / indicator).exists():
                return True

        return False

    def _check_coverage_tools(self, repo_path: Path) -> bool:
        """Check for coverage tools."""
        coverage_indicators = [
            ".coveragerc",
            ".coverage",
            "codecov.yml",
            ".codecov.yml",
            "coverage.xml",
        ]

        for indicator in coverage_indicators:
            if (repo_path / indicator).exists():
                return True

        # Check in config files
        for config_file in [".github/workflows/*.yml", "*.yml"]:
            for file in repo_path.glob(config_file):
                try:
                    content = file.read_text().lower()
                    if "codecov" in content or "coveralls" in content:
                        return True
                except Exception:
                    continue

        return False

    def _check_security_tools(self, repo_path: Path) -> bool:
        """Check for security scanning tools."""
        security_indicators = [
            ".snyk",
            "snyk.yml",
            ".github/dependabot.yml",
            ".github/workflows/security.yml",
        ]

        for indicator in security_indicators:
            if (repo_path / indicator).exists():
                return True

        # Check GitHub Actions for security scans
        gh_workflows = repo_path / ".github" / "workflows"
        if gh_workflows.exists():
            for workflow in gh_workflows.glob("*.yml"):
                try:
                    content = workflow.read_text().lower()
                    if any(tool in content for tool in ["snyk", "dependabot", "codeql", "trivy", "bandit"]):
                        return True
                except Exception:
                    continue

        return False

    def _check_linting_tools(self, repo_path: Path) -> bool:
        """Check for linting/formatting tools."""
        linting_indicators = [
            ".eslintrc",
            ".eslintrc.json",
            ".pylintrc",
            ".flake8",
            "pyproject.toml",  # Often contains black/ruff config
            ".prettierrc",
            "ruff.toml",
        ]

        for indicator in linting_indicators:
            for file in repo_path.glob(f"**/{indicator}"):
                if file.exists():
                    return True

        return False

    def _check_dependency_tools(self, repo_path: Path) -> bool:
        """Check for dependency management."""
        dep_files = [
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "Gemfile.lock",
            "go.sum",
            "Cargo.lock",
        ]

        for dep_file in dep_files:
            if (repo_path / dep_file).exists():
                return True

        return False

    def _check_pre_commit(self, repo_path: Path) -> bool:
        """Check for pre-commit hooks."""
        return (repo_path / ".pre-commit-config.yaml").exists()

    def _calculate_score(self, tools: Dict[str, bool]) -> float:
        """Calculate score based on tools found."""
        weights = {
            "ci_cd": 30,
            "code_coverage": 20,
            "security_scanning": 20,
            "linting": 15,
            "dependency_management": 10,
            "pre_commit_hooks": 5,
        }

        score = sum(weights[tool] for tool, present in tools.items() if present)
        return min(100, score)

    def _format_evidence(self, tools: Dict[str, bool]) -> str:
        """Format evidence string."""
        found = [tool.replace("_", " ").title() for tool, present in tools.items() if present]
        missing = [tool.replace("_", " ").title() for tool, present in tools.items() if not present]

        evidence_parts = []
        if found:
            evidence_parts.append(f"Found: {', '.join(found)}")
        if missing:
            evidence_parts.append(f"Missing: {', '.join(missing)}")

        return " | ".join(evidence_parts)

    def _generate_remediation(self, tools: Dict[str, bool]) -> str:
        """Generate remediation advice."""
        missing_critical = []

        if not tools["ci_cd"]:
            missing_critical.append("Add CI/CD (GitHub Actions, GitLab CI, etc.)")

        if not tools["security_scanning"]:
            missing_critical.append("Add security scanning (Snyk, Dependabot)")

        if not tools["code_coverage"]:
            missing_critical.append("Add coverage tracking (Codecov, Coveralls)")

        if missing_critical:
            return "Critical: " + "; ".join(missing_critical)

        missing_recommended = []
        if not tools["linting"]:
            missing_recommended.append("Add linting tools (ESLint, Pylint, etc.)")

        if not tools["pre_commit_hooks"]:
            missing_recommended.append("Add pre-commit hooks")

        if missing_recommended:
            return "Recommended: " + "; ".join(missing_recommended)

        return "Good ecosystem tool coverage. All critical tools present."
