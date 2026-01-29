"""Unit test naming convention assessor for quality profiling."""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class UnitTestNamingAssessor(BaseAssessor):
    """Assess unit test naming conventions and organization."""

    @property
    def attribute_id(self) -> str:
        return "quality_unit_test_naming"

    @property
    def tier(self) -> int:
        return 1  # Critical

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Unit Test Naming Conventions",
            category="Testing",
            tier=self.tier,
            description="Test files and functions follow standard naming conventions with descriptive names",
            criteria="90%+ of tests follow naming conventions with descriptive function names",
            default_weight=0.10,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess unit test naming conventions.

        Args:
            repository: Repository to assess

        Returns:
            Finding with test naming metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Find test files
            test_files = self._find_test_files(repo_path)

            if not test_files:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=0,
                    measured_value=0,
                    threshold=90,
                    evidence=["No test files found"],
                    remediation="Add unit tests following standard naming conventions (test_*.py, *_test.go, *.test.ts, *.spec.js)",
                    error_message=None,
                )

            # Analyze test naming
            analysis = self._analyze_test_naming(test_files, repo_path)
            score = self._calculate_score(analysis)
            evidence_str = self._format_evidence(analysis)
            remediation_str = self._generate_remediation(analysis)

            status = "pass" if score >= 90 else "fail"

            return Finding(
                attribute=self.attribute,
                status=status,
                score=score,
                measured_value=score,
                threshold=90,
                evidence=[evidence_str],
                remediation=remediation_str,
                error_message=None,
            )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"Unit test naming assessment failed: {str(e)}"
            )

    def _find_test_files(self, repo_path: Path) -> List[Path]:
        """Find test files following standard naming patterns."""
        test_patterns = [
            # Python
            "**/test_*.py",
            "**/*_test.py",
            "**/tests/**/*.py",
            # JavaScript/TypeScript
            "**/*.test.js",
            "**/*.test.ts",
            "**/*.test.jsx",
            "**/*.test.tsx",
            "**/*.spec.js",
            "**/*.spec.ts",
            "**/*.spec.jsx",
            "**/*.spec.tsx",
            # Go
            "**/*_test.go",
            # Java
            "**/*Test.java",
            "**/*Tests.java",
            # Rust
            "**/*_test.rs",
            # Ruby
            "**/*_test.rb",
            "**/*_spec.rb",
        ]

        test_files = []
        seen = set()

        for pattern in test_patterns:
            for file in repo_path.glob(pattern):
                if file.is_file() and str(file) not in seen:
                    # Exclude vendor, node_modules, etc.
                    path_parts = file.parts
                    if any(exclude in path_parts for exclude in ["node_modules", "vendor", ".venv", "venv", "__pycache__", ".git"]):
                        continue
                    test_files.append(file)
                    seen.add(str(file))

        return test_files

    def _analyze_test_naming(self, test_files: List[Path], repo_path: Path) -> Dict:
        """Analyze test file and function naming conventions."""
        analysis = {
            "total_files": len(test_files),
            "properly_named_files": 0,
            "total_test_functions": 0,
            "descriptive_test_functions": 0,
            "organized_by_module": False,
            "language_breakdown": {},
        }

        # File naming patterns by language
        file_naming_patterns = {
            "python": [r"test_.*\.py$", r".*_test\.py$"],
            "javascript": [r".*\.test\.(js|ts|jsx|tsx)$", r".*\.spec\.(js|ts|jsx|tsx)$"],
            "go": [r".*_test\.go$"],
            "java": [r".*Test\.java$", r".*Tests\.java$"],
            "rust": [r".*_test\.rs$"],
            "ruby": [r".*_test\.rb$", r".*_spec\.rb$"],
        }

        for test_file in test_files:
            # Check file naming
            file_name = test_file.name
            language = self._detect_language(test_file)
            
            if language:
                analysis["language_breakdown"][language] = analysis["language_breakdown"].get(language, 0) + 1
                
                # Check if file follows naming convention
                patterns = file_naming_patterns.get(language, [])
                if any(re.search(pattern, file_name) for pattern in patterns):
                    analysis["properly_named_files"] += 1

            # Analyze test functions
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                test_funcs = self._extract_test_functions(content, language)
                
                analysis["total_test_functions"] += len(test_funcs)
                
                for func_name in test_funcs:
                    if self._is_descriptive_test_name(func_name, language):
                        analysis["descriptive_test_functions"] += 1
                        
            except Exception:
                continue

        # Check organization
        analysis["organized_by_module"] = self._check_organization(test_files, repo_path)

        return analysis

    def _detect_language(self, file_path: Path) -> str:
        """Detect language from file extension."""
        ext = file_path.suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".jsx": "javascript",
            ".tsx": "javascript",
            ".go": "go",
            ".java": "java",
            ".rs": "rust",
            ".rb": "ruby",
        }
        return language_map.get(ext, "unknown")

    def _extract_test_functions(self, content: str, language: str) -> List[str]:
        """Extract test function names from file content."""
        test_functions = []

        if language == "python":
            # Python: def test_*, async def test_*
            pattern = r"(?:async\s+)?def\s+(test_\w+)\s*\("
            test_functions = re.findall(pattern, content)

        elif language == "javascript":
            # JavaScript/TypeScript: test('...'), it('...'), describe('...')
            patterns = [
                r"(?:test|it)\s*\(\s*['\"](.+?)['\"]",
                r"describe\s*\(\s*['\"](.+?)['\"]",
            ]
            for pattern in patterns:
                test_functions.extend(re.findall(pattern, content))

        elif language == "go":
            # Go: func Test*
            pattern = r"func\s+(Test\w+)\s*\("
            test_functions = re.findall(pattern, content)

        elif language == "java":
            # Java: @Test public void test*
            pattern = r"@Test\s+(?:public\s+)?(?:void\s+)?(\w+)\s*\("
            test_functions = re.findall(pattern, content)

        elif language == "rust":
            # Rust: #[test] fn test_*
            pattern = r"#\[test\]\s*(?:async\s+)?fn\s+(\w+)\s*\("
            test_functions = re.findall(pattern, content)

        elif language == "ruby":
            # Ruby: def test_*, test "..."
            patterns = [
                r"def\s+(test_\w+)",
                r"(?:test|it)\s+['\"](.+?)['\"]",
            ]
            for pattern in patterns:
                test_functions.extend(re.findall(pattern, content))

        return test_functions

    def _is_descriptive_test_name(self, func_name: str, language: str) -> bool:
        """Check if test function name is descriptive.
        
        Criteria:
        - For function names: at least 3 words or 15 characters
        - For string descriptions (JS/Ruby): at least 3 words
        - Contains meaningful words (not just test123)
        - Uses underscores or camelCase properly
        """
        # For string-based test names (JavaScript, Ruby)
        if " " in func_name:
            words = func_name.split()
            # At least 3 words, avoid generic names
            return len(words) >= 3 and not all(w.lower() in ["test", "should", "it", "the"] for w in words)

        # For function names (Python, Go, Java, Rust)
        # Remove 'test_' prefix if present
        name = func_name
        if name.lower().startswith("test_"):
            name = name[5:]
        elif name.lower().startswith("test"):
            name = name[4:]

        # Check length (descriptive names are usually longer)
        if len(name) < 10:
            return False

        # Count meaningful parts (words)
        # Split by underscore or camelCase
        if "_" in name:
            parts = name.split("_")
        else:
            # Split camelCase
            parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)", name)

        # Filter out very short parts and numbers
        meaningful_parts = [p for p in parts if len(p) > 2 and not p.isdigit()]

        # At least 3 meaningful parts
        return len(meaningful_parts) >= 3

    def _check_organization(self, test_files: List[Path], repo_path: Path) -> bool:
        """Check if tests are organized by module/feature."""
        # Check if tests are in dedicated directories
        test_dirs = {"test", "tests", "__tests__", "spec", "specs"}
        
        organized_count = 0
        for test_file in test_files:
            # Check if file is in a test directory
            path_parts = set(test_file.relative_to(repo_path).parts)
            if any(test_dir in path_parts for test_dir in test_dirs):
                organized_count += 1

        # Consider organized if > 80% are in test directories
        return organized_count / len(test_files) > 0.8 if test_files else False

    def _calculate_score(self, analysis: Dict) -> float:
        """Calculate overall naming convention score."""
        score = 0

        # File naming (30 points)
        if analysis["total_files"] > 0:
            file_naming_ratio = analysis["properly_named_files"] / analysis["total_files"]
            score += file_naming_ratio * 30

        # Function naming (50 points)
        if analysis["total_test_functions"] > 0:
            func_naming_ratio = analysis["descriptive_test_functions"] / analysis["total_test_functions"]
            score += func_naming_ratio * 50

        # Organization (20 points)
        if analysis["organized_by_module"]:
            score += 20

        return min(100, score)

    def _format_evidence(self, analysis: Dict) -> str:
        """Format evidence string."""
        parts = []

        # File naming
        file_ratio = 0
        if analysis["total_files"] > 0:
            file_ratio = (analysis["properly_named_files"] / analysis["total_files"]) * 100
        parts.append(f"Files: {analysis['properly_named_files']}/{analysis['total_files']} ({file_ratio:.0f}%) properly named")

        # Function naming
        func_ratio = 0
        if analysis["total_test_functions"] > 0:
            func_ratio = (analysis["descriptive_test_functions"] / analysis["total_test_functions"]) * 100
            parts.append(f"Functions: {analysis['descriptive_test_functions']}/{analysis['total_test_functions']} ({func_ratio:.0f}%) descriptive")

        # Organization
        org_status = "✓ Organized" if analysis["organized_by_module"] else "✗ Not organized"
        parts.append(org_status)

        # Language breakdown
        if analysis["language_breakdown"]:
            langs = ", ".join(f"{lang}({count})" for lang, count in sorted(analysis["language_breakdown"].items()))
            parts.append(f"Languages: {langs}")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict) -> str:
        """Generate remediation advice."""
        issues = []

        # File naming issues
        if analysis["total_files"] > 0:
            file_ratio = analysis["properly_named_files"] / analysis["total_files"]
            if file_ratio < 0.9:
                issues.append(f"Rename {analysis['total_files'] - analysis['properly_named_files']} test files to follow conventions (test_*.py, *.test.js, *_test.go)")

        # Function naming issues
        if analysis["total_test_functions"] > 0:
            func_ratio = analysis["descriptive_test_functions"] / analysis["total_test_functions"]
            if func_ratio < 0.9:
                poor_names = analysis["total_test_functions"] - analysis["descriptive_test_functions"]
                issues.append(f"Make {poor_names} test function names more descriptive (use at least 3 words describing what is tested)")

        # Organization issues
        if not analysis["organized_by_module"]:
            issues.append("Organize tests in dedicated test directories (tests/, __tests__/, spec/)")

        if not issues:
            return "Excellent test naming conventions. Keep following these standards for new tests."

        return "; ".join(issues)
