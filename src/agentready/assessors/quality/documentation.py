"""Documentation standards assessor for quality profiling."""

from pathlib import Path

from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class DocumentationStandardsAssessor(BaseAssessor):
    """Assess documentation standards and completeness."""

    @property
    def attribute_id(self) -> str:
        return "quality_documentation_standards"

    @property
    def tier(self) -> int:
        return 1  # Essential

    def assess(self, repository: Repository) -> Finding:
        """Assess documentation for the repository."""
        try:
            repo_path = Path(repository.path)

            readme_score = self._assess_readme(repo_path)
            docstring_score = self._assess_docstrings(repo_path)
            architecture_docs = self._check_architecture_docs(repo_path)

            # Calculate overall score (weighted average)
            overall_score = (readme_score * 0.4 + docstring_score * 0.4 + architecture_docs * 0.2)

            evidence_parts = [
                f"README score: {readme_score}/100",
                f"Docstring coverage: {docstring_score}/100",
                f"Architecture docs: {'✓' if architecture_docs > 50 else '✗'}",
            ]

            evidence = " | ".join(evidence_parts)

            remediation = self._generate_remediation(readme_score, docstring_score, architecture_docs)

            if overall_score >= 70:
                return Finding.pass_(
                    attribute_id=self.attribute_id,
                    score=overall_score,
                    evidence=evidence,
                    remediation=remediation
                )
            else:
                return Finding.fail(
                    attribute_id=self.attribute_id,
                    score=overall_score,
                    evidence=evidence,
                    remediation=remediation
                )

        except Exception as e:
            return Finding.error(
                attribute_id=self.attribute_id,
                error_message=f"Documentation assessment failed: {str(e)}"
            )

    def _assess_readme(self, repo_path: Path) -> float:
        """Assess README.md quality."""
        readme_path = repo_path / "README.md"

        if not readme_path.exists():
            return 0

        try:
            content = readme_path.read_text()
            score = 20  # Base score for existence

            # Check for key sections
            required_sections = {
                "installation": ["install", "setup", "getting started"],
                "usage": ["usage", "example", "quick start"],
                "contributing": ["contribut", "development"],
                "license": ["license"],
            }

            for section, keywords in required_sections.items():
                if any(kw in content.lower() for kw in keywords):
                    score += 20

            return min(100, score)

        except Exception:
            return 20  # Exists but couldn't read

    def _assess_docstrings(self, repo_path: Path) -> float:
        """Estimate docstring coverage."""
        python_files = list(repo_path.rglob("*.py"))

        if not python_files:
            return 50  # N/A, give neutral score

        files_with_docstrings = 0

        for py_file in python_files[:50]:  # Sample first 50 files
            try:
                content = py_file.read_text()
                # Simple heuristic: check for triple quotes
                if '"""' in content or "'''" in content:
                    files_with_docstrings += 1
            except Exception:
                continue

        if not python_files:
            return 50

        coverage = (files_with_docstrings / min(len(python_files), 50)) * 100
        return coverage

    def _check_architecture_docs(self, repo_path: Path) -> float:
        """Check for architecture documentation."""
        score = 0

        # Check for common architecture doc files
        arch_files = [
            "ARCHITECTURE.md",
            "docs/architecture.md",
            "DESIGN.md",
            "docs/design.md",
            "ADR",  # Architecture Decision Records
            "docs/adr",
        ]

        for arch_file in arch_files:
            if (repo_path / arch_file).exists() or (repo_path / arch_file.lower()).exists():
                score = 100
                break

        # Check for docs/ directory
        docs_dir = repo_path / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            doc_count = len(list(docs_dir.rglob("*.md")))
            if doc_count > 0:
                score = max(score, min(100, doc_count * 20))

        return score

    def _generate_remediation(self, readme_score: float, docstring_score: float, arch_score: float) -> str:
        """Generate remediation advice."""
        issues = []

        if readme_score < 60:
            issues.append("Improve README with installation, usage, and contributing sections")

        if docstring_score < 50:
            issues.append("Add docstrings to functions and classes")

        if arch_score < 50:
            issues.append("Create architecture documentation (ARCHITECTURE.md or docs/)")

        if not issues:
            return "Good documentation coverage. Consider adding API documentation and examples."

        return "; ".join(issues)
