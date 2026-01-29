# Implementation Plan: Quality Profiling and Benchmarking with UI

**Branch**: `003-quality-profiling-ui` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-quality-profiling-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature extends ship-shape with enhanced quality profiling assessors and an interactive web UI for visualizing and comparing repository quality metrics. The system will assess repositories using enhanced assessors for unit test coverage, integration tests, documentation standards, and ecosystem tool usage (GitHub Actions, Codecov, Snyk, Cypress). Results will be visualized through a React/TypeScript/PatternFly web interface featuring a landing page with repository input, a table of scanned repositories with quality scores, and drill-down capability to view detailed assessor results via radar charts. The implementation also includes investigating current quality frameworks to identify and propose additional assessors for comprehensive software quality evaluation.

## Technical Context

**Language/Version**: Python 3.11+ (backend assessors), TypeScript 5.x+ (frontend UI)
**Primary Dependencies**: 
- Backend: Existing ship-shape BaseAssessor framework, coverage.py, NEEDS CLARIFICATION (test framework detection libraries)
- Frontend: React 18+, TypeScript, PatternFly 5, NEEDS CLARIFICATION (charting library for radar charts)
- API: NEEDS CLARIFICATION (REST framework - FastAPI vs Flask)
**Storage**: NEEDS CLARIFICATION (JSON files vs SQLite vs PostgreSQL for assessment history and benchmarking data)
**Testing**: 
- Backend: pytest (existing ship-shape standard)
- Frontend: NEEDS CLARIFICATION (Jest/React Testing Library vs Vitest)
- E2E: NEEDS CLARIFICATION (Playwright vs Cypress for UI testing)
**Target Platform**: 
- Backend: Linux/macOS (Python CLI and API server)
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (React frontend + Python backend API + CLI)
**Performance Goals**: 
- CLI: Assess single repo in <30 seconds for repos <10k files
- API: UI load/display results in <2 seconds
- Batch: Process 10 repos in <5 minutes
- UI: Support comparison of up to 10 repositories without performance degradation
**Constraints**: 
- Must extend existing BaseAssessor framework without breaking changes
- UI must be accessible (WCAG 2.1 AA compliance via PatternFly)
- Assessment data must be persistable for historical tracking (12+ months)
- Radar charts must support 8+ quality dimensions simultaneously
**Scale/Scope**: 
- Support assessment of repositories up to 100k files
- Handle batch processing of 100+ repositories
- Store historical data for 1000+ repositories
- UI supports 10 concurrent repository comparisons

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research) ✓

Verify compliance with all core principles from `.specify/memory/constitution.md`:

- [x] **Evidence-Based Design**: Technical choices will be backed by research in Phase 0 (testing frameworks, coverage tools, charting libraries, quality frameworks)
- [x] **Measurable Quality**: Success criteria in spec are quantifiable (95% coverage calculation accuracy, 90% ecosystem tool detection, <2s UI load, etc.)
- [x] **Tool-First Mindset**: Assessors implemented as libraries extending BaseAssessor, CLI wraps libraries, UI consumes library output via API
- [x] **Test-Driven Development**: TDD mandatory - tests written first for each assessor, API endpoint, and UI component
- [x] **Structured Output**: Assessors output JSON for machines, formatted reports for humans; UI provides interactive visualization plus JSON/CSV export
- [x] **Incremental Delivery**: Feature spec defines P1 (assessors), P2 (benchmarking), P3 (UI) - each independently deliverable
- [x] **Documentation as Code**: Will generate README updates, quickstart guide, API documentation, and component documentation

**Technology Standards Compliance**:
- [x] Language version aligns with constitution (Python 3.11+ for backend, TypeScript 5+ for frontend)
- [x] Dependency management follows standards (uv for Python, npm/yarn for frontend with lock files)
- [x] Complexity limits respected (file size <300 lines, function <100 lines target, cyclomatic <25)

**Quality Gates** (must pass before implementation):
- [x] Constitution Check: ✓ (this section)
- [x] Linting: Configured (black, isort, ruff for Python; ESLint, Prettier for TypeScript)
- [x] Tests: pytest for backend, Jest/Vitest for frontend, >80% coverage target
- [x] Security: Existing ship-shape security scanning (bandit, safety) will cover backend; npm audit for frontend
- [x] Documentation: Structure defined (will generate in Phase 1: quickstart.md, API contracts, component docs)

**Violations**: None identified. Feature aligns with all constitution principles.

---

### Post-Design Re-Evaluation ✓

After completing Phase 0 (research) and Phase 1 (design), re-verify constitution compliance:

#### Evidence-Based Design ✓
**Status**: PASS - All technical decisions backed by research evidence
- FastAPI chosen based on performance benchmarks (3x faster than Flask)
- Vitest chosen based on TypeScript performance (10x faster than Jest)
- PatternFly Charts chosen for WCAG 2.1 AA compliance
- 8 assessors proposed based on ISO 25010, DORA, CISQ, Microsoft SDL frameworks
- Each assessor metric has research citations (Google, Microsoft, DORA, GitHub studies)

#### Measurable Quality ✓
**Status**: PASS - All metrics are quantifiable
- Data model defines strict validation rules (scores 0-100, status enums, etc.)
- Each assessor has specific, measurable metrics (coverage percentages, test counts, etc.)
- API contracts enforce validation through OpenAPI schema
- Statistical benchmarking uses percentiles, mean, median, std_dev

#### Tool-First Mindset ✓
**Status**: PASS - Libraries first, CLI/API second
- Assessors extend BaseAssessor as libraries (src/agentready/assessors/quality/)
- CLI wraps library calls (ship-shape assess command)
- API provides REST interface to libraries (FastAPI endpoints)
- UI consumes API (React frontend independent of backend)

#### Test-Driven Development ✓
**Status**: PASS - Testing strategy defined
- Testing frameworks selected: pytest (backend), Vitest (frontend), Playwright (E2E)
- Test structure defined in project layout (tests/unit/, tests/integration/, tests/e2e/)
- >80% coverage target established
- Quickstart includes test execution commands

#### Structured Output ✓
**Status**: PASS - Both machine and human formats
- Assessors output JSON (data-model.md defines schemas)
- CLI provides formatted Markdown reports
- API provides JSON responses (OpenAPI spec)
- UI provides interactive visualization + JSON/CSV export endpoints

#### Incremental Delivery ✓
**Status**: PASS - Feature broken into deliverable stories
- P1: Enhanced assessors (independently testable via CLI)
- P2: Benchmarking (builds on P1, testable without UI)
- P3: UI (builds on P1+P2, independently deployable)
- Each priority can be delivered and validated independently

#### Documentation as Code ✓
**Status**: PASS - Documentation generated in Phase 1
- quickstart.md created with <5 minute setup
- data-model.md documents all entities, relationships, validation
- contracts/openapi.yaml defines API specification (auto-generates Swagger docs)
- contracts/types.ts provides TypeScript definitions
- contracts/README.md explains API usage

#### Technology Standards ✓
**Status**: PASS - All standards met
- Python 3.11+ (constitution requirement met)
- TypeScript 5+ (modern, type-safe)
- uv for dependency management (constitution preference)
- SQLite with PostgreSQL migration path (start simple, scale later)
- File complexity will be monitored (<300 lines target)

#### Complexity Tracking ✓
**Status**: PASS - No violations
- Web application structure justified (frontend + backend)
- No additional complexity beyond constitution limits
- All new code fits within existing ship-shape patterns

---

### Final Constitution Verdict: ✅ PASS

All constitution principles satisfied after design phase. No violations identified. Implementation may proceed to Phase 2 (tasks generation).

**Review Date**: 2026-01-28
**Reviewed By**: speckit.plan workflow (automated)
**Next Review**: After Phase 2 (tasks) before implementation begins

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Backend: Extend existing ship-shape structure
src/agentready/
├── assessors/
│   ├── quality/                    # NEW: Quality profiling assessors
│   │   ├── __init__.py
│   │   ├── test_coverage.py        # Unit test coverage assessor
│   │   ├── integration_tests.py    # Integration test assessor
│   │   ├── documentation.py        # Documentation standards assessor
│   │   └── ecosystem_tools.py      # Ecosystem tool detection assessor
│   └── [existing assessors...]
├── models/
│   ├── quality_profile.py          # NEW: QualityProfile entity
│   ├── benchmark.py                # NEW: BenchmarkData entity
│   └── [existing models...]
├── services/
│   ├── quality_scorer.py           # NEW: Quality scoring service
│   ├── benchmarking.py             # NEW: Benchmarking service
│   └── [existing services...]
├── api/                            # NEW: REST API for UI
│   ├── __init__.py
│   ├── app.py                      # API server setup
│   ├── routes/
│   │   ├── assessments.py          # Assessment endpoints
│   │   ├── benchmarks.py           # Benchmark endpoints
│   │   └── repositories.py         # Repository management
│   └── middleware/
└── storage/                        # NEW: Data persistence layer
    ├── __init__.py
    └── assessment_store.py         # Assessment history storage

tests/
├── unit/
│   ├── assessors/
│   │   └── quality/                # Tests for new assessors
│   ├── services/
│   │   ├── test_quality_scorer.py
│   │   └── test_benchmarking.py
│   └── api/                        # API unit tests
├── integration/
│   ├── test_quality_assessment_e2e.py
│   └── test_api_integration.py
└── [existing test structure...]

# Frontend: NEW React/TypeScript/PatternFly UI
frontend/
├── src/
│   ├── components/
│   │   ├── RepositoryInput.tsx     # Input field for repo link
│   │   ├── RepositoryTable.tsx     # Table of scanned repos
│   │   ├── ScoreCard.tsx           # Quality score display
│   │   ├── RadarChart.tsx          # Assessor results radar chart
│   │   └── DrillDownView.tsx       # Detailed drill-down view
│   ├── pages/
│   │   ├── Dashboard.tsx           # Landing page
│   │   └── RepositoryDetail.tsx    # Drill-down page
│   ├── services/
│   │   ├── api.ts                  # API client
│   │   └── types.ts                # TypeScript interfaces
│   ├── App.tsx
│   └── index.tsx
├── tests/
│   ├── components/                 # Component unit tests
│   └── e2e/                        # End-to-end tests
├── package.json
├── tsconfig.json
└── vite.config.ts                  # Build configuration
```

**Structure Decision**: Web application structure with backend extending existing ship-shape codebase and new frontend as separate React application. Backend assessors and services integrate into existing `src/agentready/` structure to leverage BaseAssessor framework. Frontend lives in new `frontend/` directory as independent SPA that communicates with backend API. This allows independent development and deployment while maintaining compatibility with existing ship-shape CLI tools.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations identified. All complexity is justified within constitution limits:
- Web application structure is standard for frontend + backend applications
- File organization follows existing ship-shape patterns
- New assessors extend BaseAssessor framework as designed
- UI components are modular and independently testable
- API layer provides necessary decoupling between CLI/library and web interface

No exceptions required.
