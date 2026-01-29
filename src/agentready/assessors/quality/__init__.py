"""Quality profiling assessors for repository assessment.

This package contains assessors for:
- Test coverage analysis
- Integration test detection
- Documentation standards
- Ecosystem tool usage
- API documentation completeness
- Unit test naming conventions
- Integration test structure
"""

from .test_coverage import TestCoverageAssessor
from .integration_tests import IntegrationTestsAssessor
from .documentation import DocumentationStandardsAssessor
from .ecosystem_tools import EcosystemToolsAssessor
from .api_documentation import APIDocumentationAssessor
from .unit_test_naming import UnitTestNamingAssessor
from .integration_test_structure import IntegrationTestStructureAssessor
from .test_fixtures import TestFixturesAssessor
from .integration_db_setup import IntegrationDatabaseSetupAssessor
from .test_performance_benchmarks import TestPerformanceBenchmarksAssessor
from .contract_testing import ContractTestingAssessor
from .mutation_testing import MutationTestingAssessor

__all__ = [
    "TestCoverageAssessor",
    "IntegrationTestsAssessor",
    "DocumentationStandardsAssessor",
    "EcosystemToolsAssessor",
    "APIDocumentationAssessor",
    "UnitTestNamingAssessor",
    "IntegrationTestStructureAssessor",
    "TestFixturesAssessor",
    "IntegrationDatabaseSetupAssessor",
    "TestPerformanceBenchmarksAssessor",
    "ContractTestingAssessor",
    "MutationTestingAssessor",
]
