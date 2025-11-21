# AgentReady - Repository Quality Assessment Tool

**Purpose**: Assess repositories against agent-ready best practices and generate actionable reports.

**Last Updated**: 2025-11-21

---

## Overview

AgentReady is a Python CLI tool that evaluates repositories against 25 carefully researched attributes that make codebases more effective for AI-assisted development. It generates interactive HTML reports, version-control friendly Markdown reports, and machine-readable JSON output.

**Current Status**: v1.0.0 - Core assessment engine complete, 10/25 attributes implemented

**Self-Assessment Score**: 75.4/100 (Gold) - See `examples/self-assessment/`

---

## Quick Start

```bash
# Install in virtual environment
uv venv && source .venv/bin/activate
uv pip install -e .

# Run assessment on current directory
agentready assess .

# Run with verbose output
agentready assess . --verbose

# Assess different repository
agentready assess /path/to/repo --output-dir ./reports
```

**Outputs**:
- `.agentready/assessment-YYYYMMDD-HHMMSS.json` - Machine-readable results
- `.agentready/report-YYYYMMDD-HHMMSS.html` - Interactive web report
- `.agentready/report-YYYYMMDD-HHMMSS.md` - Git-friendly markdown report

---

## Architecture

### Core Components

```
src/agentready/
├── models/          # Data models (Repository, Attribute, Finding, Assessment)
├── services/        # Scanner orchestration and language detection
├── assessors/       # Attribute assessment implementations
│   ├── base.py      # BaseAssessor abstract class
│   ├── documentation.py   # CLAUDE.md, README assessors
│   ├── code_quality.py    # Type annotations, complexity
│   ├── testing.py         # Test coverage, pre-commit hooks
│   ├── structure.py       # Standard layout, gitignore
│   └── stub_assessors.py  # 15 not-yet-implemented assessors
├── reporters/       # Report generation (HTML, Markdown, JSON)
│   ├── html.py      # Interactive HTML with Jinja2
│   └── markdown.py  # GitHub-Flavored Markdown
├── templates/       # Jinja2 templates
│   └── report.html.j2  # Self-contained HTML report (73KB)
└── cli/             # Click-based CLI
    └── main.py      # assess, research-version, generate-config commands
```

### Data Flow

```
Repository → Scanner → Assessors → Findings → Assessment → Reporters → Reports
                ↓
         Language Detection
         (git ls-files)
```

### Scoring Algorithm

1. **Tier-Based Weighting** (50/30/15/5 distribution):
   - Tier 1 (Essential): 50% of total score
   - Tier 2 (Critical): 30% of total score
   - Tier 3 (Important): 15% of total score
   - Tier 4 (Advanced): 5% of total score

2. **Attribute Scoring**: Each attribute returns 0-100 score
3. **Weighted Aggregation**: `final_score = Σ(attribute_score × weight)`
4. **Certification Levels**:
   - Platinum: 90-100
   - Gold: 75-89
   - Silver: 60-74
   - Bronze: 40-59
   - Needs Improvement: 0-39

---

## Development

### Setup

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Install development tools
uv pip install pytest black isort ruff
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/agentready --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v
```

**Current Coverage**: 37% (focused on core logic)

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
ruff check src/ tests/

# Run all linters
black src/ tests/ && isort src/ tests/ && ruff check src/ tests/
```

### Adding New Assessors

1. **Expand a stub assessor** in `src/agentready/assessors/stub_assessors.py`
2. **Create new assessor class** inheriting from `BaseAssessor`
3. **Implement required methods**:
   - `attribute_id` property
   - `assess(repository)` method
   - `is_applicable(repository)` method (optional)
4. **Add tests** in `tests/unit/test_assessors_*.py`
5. **Register** in scanner's assessor list

**Example**:
```python
class MyAssessor(BaseAssessor):
    @property
    def attribute_id(self) -> str:
        return "my_attribute_id"

    def assess(self, repository: Repository) -> Finding:
        # Implement assessment logic
        if condition_met:
            return Finding.create_pass(self.attribute, ...)
        else:
            return Finding.create_fail(self.attribute, ...)
```

---

## Project Structure

```
agentready/
├── src/agentready/          # Source code
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # End-to-end tests
├── examples/               # Example reports
│   └── self-assessment/    # AgentReady's own assessment
├── specs/                  # Feature specifications
├── pyproject.toml          # Python package configuration
├── CLAUDE.md              # This file
├── README.md              # User-facing documentation
├── BACKLOG.md             # Future features and enhancements
└── GITHUB_ISSUES.md       # GitHub-ready issue templates
```

---

## Technologies

- **Python 3.11+** (only N and N-1 versions supported)
- **Click** - CLI framework
- **Jinja2** - HTML template engine
- **Pytest** - Testing framework
- **Black** - Code formatter
- **isort** - Import sorter
- **Ruff** - Fast Python linter

---

## Contributing

### Workflow

1. **Create feature branch** from `main`
2. **Implement changes** with tests
3. **Run linters**: `black . && isort . && ruff check .`
4. **Run tests**: `pytest`
5. **Commit** with conventional commit messages
6. **Push** and create PR

### Conventional Commits

```
feat: Add new assessor for dependency freshness
fix: Correct type annotation detection in Python 3.12
docs: Update CLAUDE.md with architecture details
test: Add integration test for HTML report generation
refactor: Extract common assessor logic to base class
chore: Update dependencies
```

### Test Requirements

- All new assessors must have unit tests
- Integration tests for new reporters
- Maintain >80% coverage for new code
- All tests must pass before merge

---

## CI/CD

**GitHub Actions** (planned):
- Run tests on PR
- Run linters (black, isort, ruff)
- Generate coverage report
- Run AgentReady self-assessment
- Post assessment results as PR comment

**Current**: Manual workflow (tests run locally before push)

---

## Known Issues & Limitations

1. **Stub Assessors**: 15/25 assessors return "not_applicable" - need implementation
2. **No Lock File**: Intentionally excluded for library project
3. **No Pre-commit Hooks**: Not yet configured (planned P0 fix)
4. **HTML Report Design**: Current color scheme needs improvement (P0 fix)
5. **Report Metadata**: Missing repository context in header (P0 fix)

---

## Roadmap

### v1.1 - Critical UX Fixes (Next Sprint)
- **P0**: Add report header with repository metadata
- **P0**: Redesign HTML report (larger fonts, better colors)

### v1.2 - Automation & Integration
- **P1**: Implement `agentready align` subcommand (automated remediation)
- **P2**: GitHub App integration (badges, status checks, PR comments)
- **P2**: Interactive dashboard (one-click remediation)

### v1.3 - Assessor Expansion
- Expand 15 stub assessors
- Add AI-powered assessors (type annotations, docstrings)
- Improve test coverage to >80%

### v2.0 - Enterprise Features
- Report schema versioning
- Customizable HTML themes with dark/light toggle
- Organization-wide dashboards
- Historical trend analysis

See `BACKLOG.md` for full feature list.

---

## Getting Help

- **Issues**: Create GitHub issue using templates in `GITHUB_ISSUES.md`
- **Documentation**: See `README.md` for user guide
- **Examples**: View `examples/self-assessment/` for reference reports
- **Research**: Read `agent-ready-codebase-attributes.md` for attribute definitions

---

## Related Documents

- **BACKLOG.md** - Future features and enhancements (11 items)
- **GITHUB_ISSUES.md** - GitHub-ready issue templates
- **README.md** - User-facing documentation
- **specs/** - Feature specifications and design documents
- **examples/self-assessment/** - AgentReady's own assessment (75.4/100 Gold)

---

## Notes for Claude Code Agents

**When working on AgentReady**:

1. **Read before modifying**: Always read existing assessors before implementing new ones
2. **Follow patterns**: Use `CLAUDEmdAssessor` and `READMEAssessor` as reference implementations
3. **Test thoroughly**: Add unit tests for all new assessors
4. **Maintain backwards compatibility**: Don't change Assessment model without schema version bump
5. **Stub assessors first**: Check if attribute already has stub before creating new class
6. **Proportional scoring**: Use `calculate_proportional_score()` for partial compliance
7. **Graceful degradation**: Return "skipped" if tools missing, don't crash
8. **Rich remediation**: Provide actionable steps, tools, commands, examples, citations

**Key Principles**:
- Library-first architecture (no global state)
- Strategy pattern for assessors (each is independent)
- Fail gracefully (missing tools → skip, don't crash)
- User-focused (actionable remediation over theoretical guidance)

---

**Last Updated**: 2025-11-21 by Jeremy Eder
**AgentReady Version**: 1.0.0
**Self-Assessment**: 75.4/100 (Gold) ✨
