"""Quality profiling assessors for repository assessment.

This package contains assessors for:
- Test coverage analysis
- Integration test detection
- Documentation standards
- Ecosystem tool usage
- API documentation completeness
- Unit test naming conventions
"""

from .test_coverage import TestCoverageAssessor
from .integration_tests import IntegrationTestsAssessor
from .documentation import DocumentationStandardsAssessor
from .ecosystem_tools import EcosystemToolsAssessor
from .api_documentation import APIDocumentationAssessor
from .unit_test_naming import UnitTestNamingAssessor

__all__ = [
    "TestCoverageAssessor",
    "IntegrationTestsAssessor",
    "DocumentationStandardsAssessor",
    "EcosystemToolsAssessor",
    "APIDocumentationAssessor",
    "UnitTestNamingAssessor",
]
