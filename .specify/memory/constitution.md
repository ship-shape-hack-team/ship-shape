# AgentReady Constitution

<!--
SYNC IMPACT REPORT:
Version: 1.0.0 → 1.0.1 (Template consistency improvement)
Rationale: PATCH version - Improved plan-template.md constitution check section for clarity

CHANGES:
- Enhanced plan-template.md Constitution Check section with specific gate checklist
- No changes to core principles or governance procedures
- Improved template alignment for better constitution compliance verification

TEMPLATE CONSISTENCY STATUS:
- ✅ plan-template.md - Constitution check section now includes specific gate checklist
- ✅ spec-template.md - Requirements structure supports measurable criteria
- ✅ tasks-template.md - Task categorization supports TDD and incremental delivery
- ✅ All command files - Generic guidance compatible with principles

DEFERRED ITEMS: None
-->

## Core Principles

### I. Evidence-Based Design

Every attribute, metric, and recommendation MUST be grounded in authoritative research. No "best
practices" without citations. Claims require supporting evidence from academic papers (ArXiv,
IEEE/ACM), industry leaders (Google, Microsoft, GitHub, Anthropic), or empirical data.

**Rationale**: Building a tool that evaluates code quality requires our own methodology to be
beyond reproach. Evidence-based design ensures credibility and prevents cargo-culting.

### II. Measurable Quality

Every quality attribute MUST have:
- Clear, objective criteria (not subjective opinions)
- Automated tooling for measurement where possible
- Quantifiable thresholds (e.g., ">80% coverage", "<10 cyclomatic complexity")
- Good vs. bad examples demonstrating the attribute

**Rationale**: You cannot improve what you cannot measure. Subjective quality assessments lead to
inconsistent results and lost user trust.

### III. Tool-First Mindset

Features MUST be implemented as libraries first, with CLI interfaces second. Each library must be:
- Self-contained and independently testable
- Documented with clear purpose and API
- Usable without the broader agentready toolchain
- Text-based I/O (stdin/args → stdout, errors → stderr)

**Rationale**: Libraries enable composition and reuse. CLI tools provide accessibility. Together,
they create a toolkit that serves both developers and automation pipelines.

### IV. Test-Driven Development (NON-NEGOTIABLE)

TDD is MANDATORY for all implementation work:
1. Write tests FIRST (red phase)
2. Get user approval of test scenarios
3. Verify tests FAIL as expected
4. Implement to make tests pass (green phase)
5. Refactor for quality (refactor phase)

No code may be written before tests exist and fail.

**Rationale**: Testing first ensures we build what users need, not what we assume they need. It
prevents scope creep and provides regression safety for AI-assisted development.

### V. Structured Output

All output MUST support both machine-readable and human-readable formats:
- JSON for automation and parsing
- Markdown/text for human consumption
- Structured logging with consistent field names
- Error messages include context, guidance, and request IDs

**Rationale**: AI agents and automation tools need structured data. Humans need readable formats.
Supporting both maximizes utility and debuggability.

### VI. Incremental Delivery

Features MUST be broken into independently deliverable user stories:
- Each story delivers measurable value on its own
- Stories prioritized P1 (MVP), P2, P3+ (enhancements)
- P1 story alone should constitute viable minimum product
- Stories can be developed, tested, deployed independently

**Rationale**: Incremental delivery enables faster feedback, reduces risk, and allows pivoting
based on user needs. MVP-first prevents over-engineering.

### VII. Documentation as Code

Documentation lives alongside code and is versioned, reviewed, and tested:
- README with quick start (<5 minute setup)
- CLAUDE.md with project context and conventions
- ADRs for architectural decisions
- Inline docstrings with "why" not "what"
- Examples and quickstarts in all guides

**Rationale**: Stale docs are worse than no docs. Documentation-as-code ensures accuracy through
automated validation and review processes.

## Development Workflow

### Quality Gates

All changes MUST pass:
1. **Constitution Check**: Verify compliance with core principles
2. **Linting**: black, isort, flake8, mypy (Python), markdownlint (docs)
3. **Tests**: All tests pass, coverage >80% for new code
4. **Security**: No critical/high vulnerabilities (bandit, safety, Dependabot)
5. **Documentation**: Updated for behavior changes, examples tested

### Implementation Phases

1. **Phase 0 - Research**: Gather evidence, citations, and requirements
2. **Phase 1 - Design**: Data models, contracts, quickstart, architecture
3. **Phase 2 - Tasks**: Generate dependency-ordered task list from designs
4. **Phase 3 - Implementation**: Execute tasks following TDD red-green-refactor
5. **Phase N - Polish**: Cross-cutting concerns, optimization, hardening

### Code Review Requirements

- All PRs require review approval
- Reviewers verify Constitution Check compliance
- Breaking changes require ADR documentation
- New features require tests and documentation
- Performance regressions blocked unless justified

## Constraints

### Technology Standards

- **Language**: Python 3.11+ (only N and N-1 versions supported)
- **Dependency Management**: uv preferred over pip
- **Virtual Environments**: MANDATORY - never modify system Python
- **Version Control**: Git with conventional commits (type(scope): description)
- **CI/CD**: GitHub Actions with required status checks
- **Container Runtime**: Podman preferred over Docker

### Complexity Limits

- **File Size**: <300 lines per file (exceptions: generated code, data)
- **Function Length**: <50 lines (warning), <100 lines (hard limit)
- **Cyclomatic Complexity**: <10 (target), <25 (hard limit)
- **Projects**: Prefer single project; justify if multiple needed
- **Dependencies**: Minimal necessary; audit for vulnerabilities quarterly

### Security & Compliance

- No hardcoded secrets (use .env files, secret managers)
- Pre-commit hooks include secret scanning (detect-secrets)
- Dependabot enabled for automated dependency updates
- Security scan in CI/CD fails on high/critical issues
- Vulnerability SLA: High severity fixed within 7 days

## Governance

This Constitution supersedes all other development practices. Amendments require:
- Documented rationale (why change is needed)
- Version increment (semantic versioning: MAJOR.MINOR.PATCH)
- Migration plan for projects affected by changes
- Approval from project maintainers
- Update to all dependent templates and documentation

All code reviews, PRs, and design decisions MUST verify Constitution compliance. Complexity
that violates principles MUST be explicitly justified with trade-off analysis.

Use `.specify/templates/agent-file-template.md` for agent-specific runtime guidance. This
Constitution applies to all agents and developers working on agentready.

**Version**: 1.0.1 | **Ratified**: 2025-11-20 | **Last Amended**: 2026-01-27
