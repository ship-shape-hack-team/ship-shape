# 🧪 Testing Guide: Quality Assessment MVP

**Implementation Status**: ✅ Phases 1-3 Complete (MVP Ready)

## 🎯 What You Can Test Right Now

### Prerequisites

First, install the dependencies:

```bash
cd /Users/ykrimerm/hackthon1/ship-shape

# Create virtual environment (if not exists)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## 🚀 Test 1: Assess Ship-Shape Itself

The most direct test - assess the ship-shape repository:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run quality assessment on current directory
agentready assess-quality .
```

**Expected Output**:
```
🔍 Assessing repository: ship-shape
📊 Running 4 assessors...

  ⏳ Running quality_test_coverage... ✓ Score: 75.0/100
  ⏳ Running quality_integration_tests... ✓ Score: 85.0/100
  ⏳ Running quality_documentation_standards... ✓ Score: 90.0/100
  ⏳ Running quality_ecosystem_tools... ✓ Score: 95.0/100

======================================================================
QUALITY ASSESSMENT REPORT
======================================================================

Repository: ship-shape
Overall Score: 86.3/100 (High Performance)
Assessed: 2026-01-28 15:30:00

======================================================================
ASSESSOR RESULTS
======================================================================

✓ quality_test_coverage: 75.0/100
   Evidence: Line coverage: 75.0% | Test count: 55 | Test/code ratio: 0.42

✓ quality_integration_tests: 85.0/100
   Evidence: Integration test files: 8 | ✓ Database tests detected

✓ quality_documentation_standards: 90.0/100
   Evidence: README score: 100/100 | Docstring coverage: 85/100 | Architecture docs: ✓

✓ quality_ecosystem_tools: 95.0/100
   Evidence: Found: CI/CD, Code Coverage, Security Scanning, Linting, Dependency Management, Pre Commit Hooks
```

## 🚀 Test 2: Different Output Formats

```bash
# JSON format (for automation)
agentready assess-quality . --format json

# Markdown format (for documentation)
agentready assess-quality . --format markdown

# Save to file
agentready assess-quality . --format markdown -o ship-shape-quality-report.md
```

## 🚀 Test 3: Assess Another Repository

```bash
# Assess any local repository
agentready assess-quality /path/to/another/repo

# Or assess the frontend directory
agentready assess-quality ./frontend
```

## 🚀 Test 4: Run Specific Assessors

```bash
# Only test coverage
agentready assess-quality . --assessors test_coverage

# Multiple specific assessors
agentready assess-quality . --assessors test_coverage,ecosystem_tools

# Documentation and ecosystem
agentready assess-quality . --assessors documentation_standards,ecosystem_tools
```

## 🔍 What Each Assessor Will Find

### 1. Test Coverage Assessor
**Looks for**:
- `test_*.py` files
- `*_test.py` files
- `tests/` directory
- `.coverage` file
- Test framework configs

**Scores**:
- 0% coverage = 0 points
- 80%+ coverage = 100 points
- Linear scaling between

### 2. Integration Tests Assessor
**Looks for**:
- `test_integration*.py` files
- `tests/integration/` directory
- `e2e/` directory
- Test container configs
- Database test files

**Scores**:
- 0 tests = 0 points
- 10+ tests = 100 points
- +10 bonus for test containers
- +10 bonus for DB tests

### 3. Documentation Standards Assessor
**Looks for**:
- `README.md` with sections (install, usage, contributing, license)
- Docstrings (`"""` or `'''` in .py files)
- `ARCHITECTURE.md` or `docs/` directory
- `ADR/` for architecture decisions

**Scores**:
- README: 20 base + 20 per section (max 100)
- Docstrings: % of files with docstrings
- Architecture: 100 if docs exist
- Weighted: 40% README + 40% docstrings + 20% architecture

### 4. Ecosystem Tools Assessor
**Looks for**:
- CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`
- Coverage: `.coveragerc`, `codecov.yml`
- Security: `.snyk`, `dependabot.yml`
- Linting: `.eslintrc`, `.pylintrc`, `pyproject.toml`
- Dependencies: Lock files
- Pre-commit: `.pre-commit-config.yaml`

**Scores**:
- CI/CD: 30 points
- Coverage tracking: 20 points
- Security scanning: 20 points
- Linting: 15 points
- Dependency management: 10 points
- Pre-commit hooks: 5 points

## 📊 Understanding Your Scores

### Performance Tiers

- **🥇 Elite (90-100)**: Top 10% of repositories
  - Comprehensive testing, excellent docs, all tools present
  
- **🥈 High (75-89)**: Next 25% of repositories  
  - Good testing, solid docs, most tools present
  
- **🥉 Medium (60-74)**: Middle 40% of repositories
  - Basic testing, acceptable docs, some tools missing
  
- **📊 Low (0-59)**: Bottom 25% of repositories
  - Limited testing, poor docs, critical tools missing

### Score Interpretation

| Score | What It Means | Actions Needed |
|-------|---------------|----------------|
| 90-100 | Excellent quality engineering | Maintain and share practices |
| 80-89 | Strong foundation | Minor improvements in weak areas |
| 70-79 | Good baseline | Focus on coverage and tools |
| 60-69 | Needs attention | Add tests and documentation |
| <60 | Significant gaps | Start with critical tests and CI/CD |

## 🧪 Test Scenarios

### Scenario 1: Well-Tested Repository
**Characteristics**:
- Has tests/ directory
- Uses pytest or similar
- Has CI/CD in .github/workflows
- Good README

**Expected Score**: 85-95/100 (High to Elite)

### Scenario 2: Documentation-Heavy Repository
**Characteristics**:
- Excellent README
- API documentation
- Architecture docs
- But minimal tests

**Expected Score**: 60-70/100 (Medium)

### Scenario 3: Minimal Repository
**Characteristics**:
- Basic README
- No tests
- No CI/CD

**Expected Score**: 20-40/100 (Low)

## 📦 Files You Can Inspect

All implementation files are in:

```
src/agentready/
├── assessors/quality/
│   ├── test_coverage.py       # Test coverage logic
│   ├── integration_tests.py    # Integration test detection
│   ├── documentation.py        # Docs quality assessment
│   └── ecosystem_tools.py      # Tool detection
├── services/
│   ├── quality_scorer.py       # Score calculation
│   ├── recommendation_engine.py # Recommendation generation
│   └── repository_service.py   # Repo metadata extraction
└── cli/
    └── assess_quality.py       # CLI command implementation
```

## 🔧 Troubleshooting

### "No module named 'agentready'"
**Solution**: Install in development mode
```bash
pip install -e ".[dev]"
```

### "No module named 'sqlalchemy'"
**Solution**: Install missing dependencies
```bash
pip install sqlalchemy fastapi uvicorn
```

### "Command not found: agentready"
**Solution**: Ensure virtual environment is activated
```bash
source .venv/bin/activate
which agentready  # Should show path in .venv
```

### Assessor returns 0 score
**Possible causes**:
- Repository has no tests → TestCoverageAssessor returns 0
- No README.md → DocumentationStandardsAssessor scores low
- No CI/CD → EcosystemToolsAssessor penalizes

**This is correct behavior!** The assessors identify real quality gaps.

## ✅ Success Criteria

After testing, you should be able to:

- ✅ Run `agentready assess-quality .` without errors
- ✅ See scores for all 4 assessors
- ✅ Get an overall quality score
- ✅ See evidence for each score
- ✅ Get remediation suggestions
- ✅ Output in text, JSON, or Markdown format
- ✅ Assess any local repository

## 🎊 What You've Achieved

**MVP Complete**: You now have a working quality profiling tool that:

1. **Assesses 4 Key Quality Dimensions**:
   - Test coverage
   - Integration testing
   - Documentation standards
   - Ecosystem tool adoption

2. **Provides Actionable Insights**:
   - Numerical scores (0-100)
   - Performance tiers (Elite/High/Medium/Low)
   - Evidence for each assessment
   - Remediation guidance

3. **Flexible Output**:
   - Terminal-friendly text
   - Machine-readable JSON
   - Documentation-ready Markdown

4. **Production-Ready Infrastructure**:
   - SQLite database for persistence
   - FastAPI for future API endpoints
   - Extensible assessor framework

## 🚀 Next Steps

**Immediate**:
1. Install dependencies and test with your repositories
2. Try different repositories to see varying scores
3. Use JSON output for automation

**Future Phases**:
- **Phase 4 (User Story 2)**: Benchmarking and ranking multiple repositories
- **Phase 5 (User Story 3)**: Web UI with radar charts and drill-down views

**You now have a functional quality profiling MVP!** 🎉
