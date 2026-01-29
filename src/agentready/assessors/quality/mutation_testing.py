"""Mutation testing assessor for quality profiling."""

from pathlib import Path
from typing import Dict

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class MutationTestingAssessor(BaseAssessor):
    """Assess mutation testing setup and coverage."""

    @property
    def attribute_id(self) -> str:
        return "quality_mutation_testing"

    @property
    def tier(self) -> int:
        return 4  # Advanced

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Mutation Testing",
            category="Testing",
            tier=self.tier,
            description="Mutation testing tools configured, mutation score tracked, CI integration",
            criteria="Mutation testing setup with minimum score threshold",
            default_weight=0.02,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess mutation testing.

        Args:
            repository: Repository to assess

        Returns:
            Finding with mutation testing metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Analyze mutation testing
            analysis = self._analyze_mutation_testing(repo_path)
            
            if not analysis["has_mutation_testing"]:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=0,
                    measured_value=0,
                    threshold=60,
                    evidence=["No mutation testing configured"],
                    remediation="Configure mutation testing with mutmut (Python), Stryker (JavaScript), or PITest (Java) to measure test quality",
                    error_message=None,
                )

            score = self._calculate_score(analysis)
            evidence_str = self._format_evidence(analysis)
            remediation_str = self._generate_remediation(analysis)

            status = "pass" if score >= 60 else "fail"

            return Finding(
                attribute=self.attribute,
                status=status,
                score=score,
                measured_value=score,
                threshold=60,
                evidence=[evidence_str],
                remediation=remediation_str,
                error_message=None,
            )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"Mutation testing assessment failed: {str(e)}"
            )

    def _analyze_mutation_testing(self, repo_path: Path) -> Dict:
        """Analyze mutation testing setup."""
        analysis = {
            "has_mutation_testing": False,
            "mutation_tool": None,
            "has_config": False,
            "config_files": [],
            "has_score_tracking": False,
            "has_ci_integration": False,
        }

        # Check for mutation testing configuration files
        config_patterns = {
            ".mutmut-cache": "mutmut",
            "mutmut_config.py": "mutmut",
            "stryker.conf.js": "Stryker",
            "stryker.conf.json": "Stryker",
            ".stryker-tmp": "Stryker",
            "pitest.xml": "PITest",
        }

        for config_file, tool in config_patterns.items():
            if (repo_path / config_file).exists():
                analysis["has_mutation_testing"] = True
                analysis["mutation_tool"] = tool
                analysis["has_config"] = True
                analysis["config_files"].append(config_file)

        # Check for mutation testing in dependency files
        dep_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "package.json",
            "pom.xml",
            "build.gradle",
        ]

        for dep_file in dep_files:
            file_path = repo_path / dep_file
            if file_path.exists():
                content = self._read_file_safe(file_path)
                tool = self._detect_mutation_tool(content)
                if tool:
                    analysis["has_mutation_testing"] = True
                    if not analysis["mutation_tool"]:
                        analysis["mutation_tool"] = tool

        # Check for mutation score tracking (reports directory)
        tracking_patterns = [
            ".mutmut-cache/",
            "mutation-report/",
            "reports/mutation/",
            ".stryker-tmp/",
        ]

        for pattern in tracking_patterns:
            if list(repo_path.glob(pattern))[:1]:
                analysis["has_score_tracking"] = True

        # Check CI configuration for mutation testing
        ci_files = [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".gitlab-ci.yml",
        ]

        for pattern in ci_files:
            for ci_file in repo_path.glob(pattern):
                content = self._read_file_safe(ci_file)
                if self._has_mutation_in_ci(content):
                    analysis["has_ci_integration"] = True

        return analysis

    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _detect_mutation_tool(self, content: str) -> str:
        """Detect mutation testing tool from dependency file."""
        tools = {
            "mutmut": "mutmut",
            "stryker": "Stryker",
            "@stryker-mutator": "Stryker",
            "pitest": "PITest",
            "mutation-testing": "MutationTesting",
        }

        content_lower = content.lower()
        for keyword, tool in tools.items():
            if keyword in content_lower:
                return tool

        return None

    def _has_mutation_in_ci(self, content: str) -> bool:
        """Check if CI includes mutation testing."""
        mutation_keywords = [
            "mutmut",
            "stryker",
            "pitest",
            "mutation",
            "mutation-test",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in mutation_keywords)

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate score based on mutation testing.
        
        Scoring:
        - 50 points: Mutation testing tool configured
        - 25 points: Score tracking enabled
        - 25 points: CI integration
        """
        score = 0

        # Mutation testing configured (50 points)
        if analysis["has_mutation_testing"]:
            score += 50

        # Score tracking (25 points)
        if analysis["has_score_tracking"]:
            score += 25

        # CI integration (25 points)
        if analysis["has_ci_integration"]:
            score += 25

        return score

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        if analysis["has_mutation_testing"]:
            tool = analysis["mutation_tool"] or "Unknown"
            parts.append(f"✓ Tool: {tool}")
        else:
            parts.append("✗ No mutation testing")

        if analysis["has_config"]:
            config = ", ".join(analysis["config_files"][:2])
            parts.append(f"✓ Config: {config}")
        else:
            parts.append("✗ No config")

        if analysis["has_score_tracking"]:
            parts.append("✓ Score tracking")
        else:
            parts.append("✗ No tracking")

        if analysis["has_ci_integration"]:
            parts.append("✓ CI integration")
        else:
            parts.append("✗ No CI")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        if (analysis["has_mutation_testing"] and analysis["has_score_tracking"] and 
            analysis["has_ci_integration"]):
            return "Excellent mutation testing setup. Monitor mutation score to maintain high test quality."

        issues = []

        if not analysis["has_mutation_testing"]:
            issues.append("Configure mutation testing tool (mutmut for Python, Stryker for JavaScript, PITest for Java)")

        if not analysis["has_score_tracking"]:
            issues.append("Enable mutation score tracking to monitor test effectiveness over time")

        if not analysis["has_ci_integration"]:
            issues.append("Add mutation testing to CI pipeline to catch weak tests")

        return "; ".join(issues)
