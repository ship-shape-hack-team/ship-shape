"""Contract testing assessor for quality profiling."""

import re
from pathlib import Path
from typing import Dict

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class ContractTestingAssessor(BaseAssessor):
    """Assess contract testing (Pact, consumer-driven contracts)."""

    @property
    def attribute_id(self) -> str:
        return "quality_contract_testing"

    @property
    def tier(self) -> int:
        return 4  # Advanced

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Contract Testing",
            category="Testing",
            tier=self.tier,
            description="Pact or similar contract testing, consumer-driven contracts, schema validation",
            criteria="Contract tests for API/service boundaries with verification in CI",
            default_weight=0.03,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess contract testing.

        Args:
            repository: Repository to assess

        Returns:
            Finding with contract testing metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Analyze contract testing
            analysis = self._analyze_contract_testing(repo_path)
            
            if not analysis["has_contract_tests"]:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=0,
                    measured_value=0,
                    threshold=60,
                    evidence=["No contract tests found"],
                    remediation="Implement contract testing with Pact, Spring Cloud Contract, or OpenAPI schema validation for API boundaries",
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
                reason=f"Contract testing assessment failed: {str(e)}"
            )

    def _analyze_contract_testing(self, repo_path: Path) -> Dict:
        """Analyze contract testing setup."""
        analysis = {
            "has_contract_tests": False,
            "contract_tool": None,
            "contract_test_count": 0,
            "has_schema_validation": False,
            "has_ci_verification": False,
        }

        # Check for Pact files
        pact_patterns = [
            "**/pacts/",
            "**/*pact*.py",
            "**/*pact*.js",
            "**/*pact*.ts",
            "**/*contract*.test.js",
            "**/*contract*.spec.ts",
        ]

        contract_files = []
        for pattern in pact_patterns:
            for file in repo_path.glob(pattern):
                if file.is_file():
                    content = self._read_file_safe(file)
                    if self._is_contract_test(content):
                        contract_files.append(file)
                        analysis["has_contract_tests"] = True
                        
                        # Detect tool
                        if "pact" in content.lower():
                            analysis["contract_tool"] = "Pact"
                        elif "spring-cloud-contract" in content.lower():
                            analysis["contract_tool"] = "Spring Cloud Contract"
                elif file.is_dir() and "pact" in file.name.lower():
                    analysis["has_contract_tests"] = True
                    analysis["contract_tool"] = "Pact"

        analysis["contract_test_count"] = len(contract_files)

        # Check for schema validation
        schema_patterns = [
            "**/*schema*.json",
            "**/*schema*.yaml",
            "**/openapi*.yaml",
            "**/swagger*.yaml",
        ]

        for pattern in schema_patterns:
            if list(repo_path.glob(pattern))[:1]:
                analysis["has_schema_validation"] = True
                break

        # Check CI configuration for contract verification
        ci_files = [
            ".github/workflows/*.yml",
            ".gitlab-ci.yml",
        ]

        for pattern in ci_files:
            for ci_file in repo_path.glob(pattern):
                content = self._read_file_safe(ci_file)
                if self._has_contract_verification(content):
                    analysis["has_ci_verification"] = True

        return analysis

    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _is_contract_test(self, content: str) -> bool:
        """Check if file contains contract tests."""
        contract_keywords = [
            "@pact",
            "pactWith",
            "pact.verify",
            "contract.verify",
            "given(",
            "uponReceiving",
            "willRespondWith",
            "@ContractTest",
        ]

        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in contract_keywords)

    def _has_contract_verification(self, content: str) -> bool:
        """Check if CI includes contract verification."""
        verification_keywords = [
            "pact",
            "contract",
            "pact-broker",
            "can-i-deploy",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in verification_keywords)

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate score based on contract testing.
        
        Scoring:
        - 50 points: Contract tests exist
        - 25 points: Schema validation
        - 25 points: CI verification
        """
        score = 0

        # Contract tests exist (50 points)
        if analysis["has_contract_tests"]:
            score += 50

        # Schema validation (25 points)
        if analysis["has_schema_validation"]:
            score += 25

        # CI verification (25 points)
        if analysis["has_ci_verification"]:
            score += 25

        return score

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        if analysis["has_contract_tests"]:
            tool = analysis["contract_tool"] or "Unknown"
            parts.append(f"✓ Contract tests: {analysis['contract_test_count']} ({tool})")
        else:
            parts.append("✗ No contract tests")

        if analysis["has_schema_validation"]:
            parts.append("✓ Schema validation")
        else:
            parts.append("✗ No schema validation")

        if analysis["has_ci_verification"]:
            parts.append("✓ CI verification")
        else:
            parts.append("✗ No CI verification")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        if (analysis["has_contract_tests"] and analysis["has_schema_validation"] and 
            analysis["has_ci_verification"]):
            return "Excellent contract testing setup. Maintain contracts for all service boundaries."

        issues = []

        if not analysis["has_contract_tests"]:
            issues.append("Implement contract tests with Pact or Spring Cloud Contract for API boundaries")

        if not analysis["has_schema_validation"]:
            issues.append("Add OpenAPI/JSON Schema validation for API contracts")

        if not analysis["has_ci_verification"]:
            issues.append("Add contract verification to CI pipeline to catch breaking changes")

        return "; ".join(issues)
