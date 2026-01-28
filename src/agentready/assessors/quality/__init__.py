"""Quality profiling assessors for repository assessment.

This package contains assessors for:
- Test coverage analysis
- Integration test detection
- Documentation standards
- Ecosystem tool usage
"""

from .test_coverage import TestCoverageAssessor
from .integration_tests import IntegrationTestsAssessor
from .documentation import DocumentationStandardsAssessor
from .ecosystem_tools import EcosystemToolsAssessor

__all__ = [
    "TestCoverageAssessor",
    "IntegrationTestsAssessor",
    "DocumentationStandardsAssessor",
    "EcosystemToolsAssessor",
]
