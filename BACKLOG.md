# AgentReady Backlog

**Purpose**: Track future features and improvements for the agentready tool.

---

## Future Features

### Bootstrap New GitHub Repositories

**Priority**: P5 (Future Enhancement)

**Description**: Create functionality to bootstrap new GitHub repositories with agentready tooling and best practices from the start.

**Requirements**:
- Initialize new repository with agent-ready structure
- Create initial CLAUDE.md, README, .gitignore from templates
- Set up pre-commit hooks
- Configure GitHub Actions for agentready assessment
- Set up Dependabot
- Create PR/Issue templates
- Generate initial pyproject.toml or package.json with recommended dependencies

**Use Case**:
```bash
# Bootstrap new repository
agentready init --repo ambient-code/new-project --language python

# This would:
# 1. Create repository structure matching standard layout
# 2. Add CLAUDE.md, README.md, .gitignore templates
# 3. Configure CI/CD with agentready assessment workflow
# 4. Set up development environment configuration
```

**Related**: Initial repository creation, onboarding automation

**Notes**:
- Should support multiple languages (Python, JavaScript, TypeScript, Go, Java)
- Templates should be customizable
- Could integrate with GitHub CLI (gh) for repository creation
- Consider integration with `gh repo create` workflow

---

## Schema & Configuration

### Report Schema Versioning

**Priority**: P3 (Important)

**Description**: Define and version the JSON/HTML/Markdown report schemas to ensure backwards compatibility and enable schema evolution.

**Requirements**:
- JSON schema for assessment reports (contracts/assessment-schema.json exists)
- HTML schema for interactive reports (contracts/report-html-schema.md exists)
- Markdown schema for version control reports (contracts/report-markdown-schema.md exists)
- Schema versioning strategy (semantic versioning)
- Backwards compatibility testing
- Schema migration tools for major version changes

**Use Case**:
```bash
# Validate report against schema
agentready validate-report assessment-2025-11-20.json

# Migrate old report to new schema version
agentready migrate-report --from 1.0.0 --to 2.0.0 old-report.json
```

**Related**: Report generation, data model evolution

**Notes**:
- Schemas exist in contracts/ directory but need formal versioning
- Consider using JSON Schema Draft 2020-12
- Tool should validate generated reports against bundled schema
- Breaking schema changes should trigger major version bump

---

### Research Report Generator/Updater Utility

**Priority**: P4 (Enhancement)

**Description**: Create a utility tool to help maintain and update the research report (agent-ready-codebase-attributes.md) following the validation schema defined in contracts/research-report-schema.md.

**Requirements**:
- Generate new research reports from templates
- Validate existing reports against schema (contracts/research-report-schema.md)
- Update/add attributes while maintaining schema compliance
- Automatically format citations and references
- Extract tier assignments and metadata
- Verify 25 attributes, 4 tiers, 20+ references
- Check for required sections (Definition, Measurable Criteria, Impact on Agent Behavior)

**Use Case**:
```bash
# Validate existing research report
agentready research validate agent-ready-codebase-attributes.md

# Generate new research report from template
agentready research init --output new-research.md

# Add new attribute to research report
agentready research add-attribute \
  --id "attribute_26" \
  --name "New Attribute" \
  --tier 2 \
  --file research.md

# Update metadata (version, date)
agentready research bump-version --type minor

# Lint and format research report
agentready research format research.md
```

**Features**:
- Schema validation (errors vs warnings per research-report-schema.md)
- Automated metadata header generation (version, date in YAML frontmatter)
- Attribute numbering consistency checks (1.1, 1.2, ..., 15.1)
- Citation deduplication and formatting
- Tier distribution balance warnings
- Category coverage analysis
- Markdown formatting enforcement (consistent structure)
- Reference URL reachability checks

**Related**: Research report maintenance, schema compliance, documentation quality

**Notes**:
- Must follow contracts/research-report-schema.md validation rules
- Should prevent invalid reports from being committed
- Could integrate with pre-commit hooks for research report changes
- Consider CLI commands under `agentready research` subcommand
- Tool should be self-documenting (help users fix validation errors)
- Future: Could use LLMs to help generate attribute descriptions from academic papers

---

### Repomix Integration

**Priority**: P4 (Enhancement)

**Description**: Integrate with Repomix (https://github.com/yamadashy/repomix) to generate AI-optimized repository context files for both new and existing repositories.

**Requirements**:
- Generate Repomix output for existing repositories
- Include Repomix configuration in bootstrapped new repositories
- Optional GitHub Actions integration for automatic regeneration
- Support Repomix configuration customization
- Integrate with agentready assessment workflow

**Use Case**:
```bash
# Generate Repomix output for current repository
agentready repomix-generate

# Bootstrap new repo with Repomix integration
agentready init --repo my-project --language python --repomix

# This would:
# 1. Set up Repomix configuration
# 2. Add GitHub Action for automatic regeneration
# 3. Generate initial repository context file
# 4. Include Repomix output in .gitignore appropriately
```

**Features**:
- Automatic Repomix configuration based on repository language
- GitHub Actions workflow for CI/CD integration
- Custom ignore patterns aligned with agentready assessment
- Support for both markdown and XML output formats
- Integration with agentready bootstrap command

**Related**: Repository initialization, AI-assisted development workflows

**Notes**:
- Repomix generates optimized repository context for LLMs
- Could enhance CLAUDE.md with reference to Repomix output
- Should align with existing .gitignore patterns
- Consider adding Repomix freshness check to assessment attributes
- May improve agentready's own repository understanding

---

### AgentReady Repository Agent

**Priority**: P3 (Important)

**Description**: Create a specialized Claude Code agent for the AgentReady repository to assist with development, testing, and maintenance tasks.

**Requirements**:
- Agent with deep knowledge of AgentReady architecture
- Understands assessment workflow, scoring logic, and report generation
- Can help with:
  - Implementing new assessors
  - Enhancing existing assessors
  - Writing tests for new features
  - Debugging assessment issues
  - Improving report templates
  - Optimizing performance

**Use Case**:
```bash
# In Claude Code, use the agentready-dev agent
/agentready-dev implement new assessor for dependency security scanning
/agentready-dev debug why Python type annotation detection is failing
/agentready-dev optimize assessment performance for large repositories
```

**Features**:
- Pre-loaded context about AgentReady codebase structure
- Knowledge of assessment attributes and scoring algorithm
- Understanding of tier-based weighting system
- Familiar with reporter implementations (HTML, Markdown)
- Can generate new assessors following established patterns

**Implementation**:
- Create `.claude/agents/agentready-dev.md` with agent specification
- Include links to key design documents (data-model.md, plan.md, research.md)
- Provide common development patterns and examples
- Reference test structure and coverage requirements

**Related**: Development workflow, code generation, testing

**Notes**:
- Agent should follow constitution principles (library-first, TDD when requested)
- Should know about stub assessors and how to expand them
- Can help with performance benchmarking and optimization
- Should understand the research report structure and attribute definitions

---

### Customizable HTML Report Themes

**Priority**: P4 (Enhancement)

**Description**: Allow users to customize the appearance of HTML reports with themes, color schemes, and layout options.

**Requirements**:
- Theme system for HTML reports
- Pre-built themes (default, dark mode, high contrast, colorblind-friendly)
- Custom theme support via configuration
- Maintain accessibility standards (WCAG 2.1 AA)
- Preview themes before applying

**Use Case**:
```yaml
# .agentready-config.yaml
report_theme: dark  # or 'light', 'high-contrast', 'custom'

custom_theme:
  primary_color: "#2563eb"
  success_color: "#10b981"
  warning_color: "#f59e0b"
  danger_color: "#ef4444"
  background: "#1e293b"
  text: "#e2e8f0"
  font_family: "Inter, sans-serif"
```

**Features**:
- **Theme dropdown in top-right corner of HTML report** (runtime switching)
- **Quick dark/light mode toggle button** (one-click switching between dark and light)
- Multiple built-in themes (light, dark, high-contrast, solarized, dracula)
- Dark mode support with proper color inversion
- Custom color palettes
- Font selection (system fonts + web-safe fonts)
- Layout density options (compact, comfortable, spacious)
- Logo/branding customization
- Export theme as reusable configuration
- Save theme preference to localStorage (persists across reports)

**Implementation**:
- CSS custom properties (variables) for theming
- JavaScript theme switcher in HTML report (no page reload)
- Theme loader in HTMLReporter
- Validate theme configurations
- Preserve accessibility in all themes (WCAG 2.1 AA)
- Add theme preview command: `agentready theme-preview dark`
- Embed all theme CSS in single HTML file (offline-capable)

**Related**: HTML report generation, user experience

**Notes**:
- All themes must maintain WCAG 2.1 AA contrast ratios
- Dark mode should invert appropriately, not just be dark
- Consider colorblind-friendly palettes (Viridis, ColorBrewer)
- Custom themes should be shareable (export/import)
- Could add theme gallery in documentation

---

### Align Subcommand (Automated Remediation)

**Priority**: P1 (Critical)

**Description**: Implement `agentready align` subcommand that automatically fixes failing attributes by generating and applying changes to the repository.

**Vision**: One command to align your repository with best practices - automatically create missing files, configure tooling, and improve code quality.

**Core Command**:

```bash
# Align repository to best practices
agentready align .

# Preview changes without applying
agentready align . --dry-run

# Apply specific attributes only
agentready align . --attributes claude_md_file,precommit_hooks

# Create GitHub PR instead of direct changes
agentready align . --create-pr

# Interactive mode (confirm each change)
agentready align . --interactive
```

**Supported Fixes**:

1. **Template-Based Fixes** (Auto-applicable):
   - `claude_md_file`: Generate CLAUDE.md from repository analysis
   - `gitignore_completeness`: Add missing patterns to .gitignore
   - `precommit_hooks`: Create .pre-commit-config.yaml with language-specific hooks
   - `readme_structure`: Scaffold missing README sections
   - `lock_files`: Generate lock files (package-lock.json, requirements.txt, etc.)
   - `issue_pr_templates`: Create .github/ISSUE_TEMPLATE and PULL_REQUEST_TEMPLATE
   - `conventional_commits`: Add commitlint configuration

2. **Command-Based Fixes** (Execute commands):
   - `lock_files`: Run `npm install`, `poetry lock`, `go mod tidy`
   - `precommit_hooks`: Run `pre-commit install`
   - `dependency_freshness`: Run `npm update`, `pip install --upgrade`

3. **AI-Powered Fixes** (Require LLM, optional):
   - `type_annotations`: Add type hints to Python functions
   - `inline_documentation`: Generate docstrings from function signatures
   - `cyclomatic_complexity`: Refactor high-complexity functions
   - `file_size_limits`: Split large files into smaller modules

**Workflow**:

```bash
# User runs alignment
$ agentready align . --dry-run

AgentReady Alignment Preview
============================

Repository: /Users/jeder/my-project
Current Score: 62.4/100 (Silver)
Projected Score: 84.7/100 (Gold) 🎯

Changes to be applied:

  ✅ claude_md_file (10 points)
     CREATE CLAUDE.md (1.2 KB)

  ✅ precommit_hooks (3 points)
     CREATE .pre-commit-config.yaml (845 bytes)
     RUN pre-commit install

  ✅ gitignore_completeness (3 points)
     MODIFY .gitignore (+15 patterns)

  ⚠️  type_annotations (10 points) - requires AI
     MODIFY 23 Python files (add type hints)
     Use --ai to enable AI-powered fixes

Total: 3 automatic fixes, 1 AI fix available
Apply changes? [y/N]
```

**Implementation**:

```python
# src/agentready/fixers/base.py
class BaseFixer(ABC):
    """Base class for attribute fixers."""

    @abstractmethod
    def can_fix(self, finding: Finding) -> bool:
        """Check if this fixer can fix the finding."""
        pass

    @abstractmethod
    def generate_fix(self, repository: Repository, finding: Finding) -> Fix:
        """Generate fix for the finding."""
        pass

# src/agentready/fixers/template_fixer.py
class TemplateFixer(BaseFixer):
    """Fixer that generates files from templates."""

    def generate_fix(self, repository: Repository, finding: Finding) -> Fix:
        template = self.load_template(finding.attribute.id)
        content = self.render_template(template, repository)
        return FileCreationFix(path="CLAUDE.md", content=content)

# src/agentready/cli/align.py
@cli.command()
@click.argument("repository", type=click.Path(exists=True), default=".")
@click.option("--dry-run", is_flag=True, help="Preview changes without applying")
@click.option("--create-pr", is_flag=True, help="Create GitHub PR instead of direct changes")
@click.option("--interactive", is_flag=True, help="Confirm each change")
@click.option("--attributes", help="Comma-separated attribute IDs to fix")
@click.option("--ai", is_flag=True, help="Enable AI-powered fixes (requires API key)")
def align(repository, dry_run, create_pr, interactive, attributes, ai):
    """Align repository with best practices by applying automatic fixes."""

    # Run assessment first
    assessment = run_assessment(repository)

    # Identify fixable failures
    failures = [f for f in assessment.findings if f.status == "fail"]
    fixable = identify_fixable_failures(failures, enable_ai=ai)

    # Generate fixes
    fixes = [fixer.generate_fix(repo, finding) for finding in fixable]

    # Preview changes
    show_fix_preview(fixes, assessment.overall_score, projected_score)

    if dry_run:
        return

    if interactive and not confirm_each_fix(fixes):
        return

    # Apply fixes
    if create_pr:
        create_github_pr_with_fixes(fixes)
    else:
        apply_fixes(fixes)

    # Re-run assessment to show improvement
    new_assessment = run_assessment(repository)
    show_improvement(assessment.overall_score, new_assessment.overall_score)
```

**Fix Types**:

```python
class Fix(ABC):
    """Base class for fixes."""
    attribute_id: str
    description: str

class FileCreationFix(Fix):
    """Create a new file."""
    path: Path
    content: str

class FileModificationFix(Fix):
    """Modify existing file."""
    path: Path
    changes: List[TextChange]

class CommandFix(Fix):
    """Execute command."""
    command: str
    working_dir: Path

class MultiStepFix(Fix):
    """Combination of multiple fixes."""
    steps: List[Fix]
```

**GitHub PR Integration**:

```bash
# Create PR with fixes
$ agentready align . --create-pr

Creating fix branch: agentready-align-20251121
Applying 3 fixes...
  ✅ Created CLAUDE.md
  ✅ Created .pre-commit-config.yaml
  ✅ Modified .gitignore

Committing changes...
Pushing to origin...

Created PR: https://github.com/redhat/my-project/pull/42
  Title: "Improve AgentReady score from 62.4 to 84.7 (Silver → Gold)"
  Score improvement: +22.3 points
  Attributes fixed: 3
```

**Configuration**:

```yaml
# .agentready-config.yaml
align:
  enabled: true

  auto_fix:
    # Attributes to automatically fix without confirmation
    - claude_md_file
    - gitignore_completeness
    - precommit_hooks

  confirm_before_fix:
    # Attributes requiring confirmation
    - type_annotations
    - cyclomatic_complexity

  never_fix:
    # Attributes to skip (user will fix manually)
    - container_setup
    - openapi_specs

  ai_fixes:
    enabled: false  # Require --ai flag
    provider: "anthropic"  # or "openai"
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
```

**Use Cases**:

**Use Case 1: New Repository Setup**
```bash
# Clone new project
git clone github.com/redhat/new-project
cd new-project

# Align to best practices
agentready align . --interactive

# Review and commit changes
git add .
git commit -m "chore: Align repository with AgentReady best practices"
```

**Use Case 2: Continuous Improvement**
```bash
# Weekly CI job to check and create alignment PRs
agentready align . --create-pr --dry-run
# If score < threshold, create PR automatically
```

**Use Case 3: Pre-commit Hook**
```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: agentready-align
      name: AgentReady Alignment Check
      entry: agentready align --dry-run
      language: system
      pass_filenames: false
```

**Safety Features**:

- **Dry-run by default** for destructive operations
- **Git worktree** for isolated changes (optional)
- **Backup creation** before modifying files
- **Rollback support** if fixes fail
- **Validation** of generated files before writing
- **Interactive confirmation** for AI-powered fixes

**Related**: Automated remediation, repository improvement, onboarding

**Notes**:
- Start with template-based fixes (highest ROI, lowest risk)
- AI-powered fixes require API key and user consent
- Some attributes cannot be automatically fixed (requires human judgment)
- Consider integration with `git stash` for safety
- Could generate shell script of changes for manual review
- Align with Red Hat's AI-assisted development workflow

---

### Interactive Dashboard with Automated Remediation

**Priority**: P2 (High Value)

**Description**: Transform the static HTML report into an interactive dashboard that enables one-click remediation via automated GitHub issue creation and draft PR generation.

**Vision**: "How to Align Your Repo with Best Practices" - Click a button → Open GitHub issue with draft PR containing fixes.

**Core Features**:

1. **Interactive Dashboard Mode**
   - Real-time assessment (WebSocket updates)
   - Live filtering and sorting (already have this)
   - Action buttons on each failing attribute
   - Progress tracking across multiple runs
   - Historical trend visualization

2. **One-Click Remediation Actions**
   - "Fix This" button on each failing attribute
   - Generates GitHub issue automatically
   - Creates draft PR with proposed changes
   - Links issue to PR
   - Assigns to repository owner/team

3. **Automated Fix Generation**
   - Template-based fixes for common issues:
     - Missing .gitignore → Generate language-specific .gitignore
     - No CLAUDE.md → Generate template with repo analysis
     - Missing pre-commit hooks → Add .pre-commit-config.yaml
     - No lock files → Generate appropriate lock file
     - Missing README sections → Scaffold missing sections
   - AI-powered fixes for complex issues:
     - Refactor high-complexity functions
     - Add type annotations to functions
     - Generate docstrings from function signatures
     - Split large files

4. **GitHub Integration**
   - OAuth authentication with GitHub
   - gh CLI integration for seamless workflow
   - Create issues via GitHub API
   - Create draft PRs via GitHub API
   - Auto-label issues (e.g., `agentready`, `automated-fix`, `tier-1-essential`)
   - Link to AgentReady assessment report

**Technical Architecture**:

```yaml
# New components needed:

Backend (Optional - could be fully client-side with gh CLI):
  - GitHub OAuth app for authentication
  - Issue/PR template generator
  - Fix generator service (template-based + AI-powered)
  - Assessment history tracker

Frontend (Enhanced HTML report):
  - Action buttons with loading states
  - GitHub auth flow UI
  - Progress indicators
  - Toast notifications for actions
  - Modal dialogs for fix preview

CLI Extensions:
  - agentready dashboard .  # Launch local web server
  - agentready fix <attribute-id>  # Generate fix for specific attribute
  - agentready create-issue <attribute-id>  # Create GitHub issue
  - agentready create-pr <attribute-id>  # Create draft PR
```

**Use Cases**:

**Use Case 1: Quick Fixes**
```bash
# User runs assessment
agentready assess . --dashboard

# Opens dashboard in browser at http://localhost:8000
# User clicks "Fix This" on "Missing CLAUDE.md"
# → Creates issue: "Add CLAUDE.md configuration file"
# → Creates draft PR with generated CLAUDE.md template
# → PR includes: project analysis, detected languages, suggested structure
```

**Use Case 2: Batch Remediation**
```bash
# Dashboard shows all failures
# User selects multiple attributes
# Clicks "Fix All Selected"
# → Creates single issue: "Improve AgentReady Score from Silver to Gold"
# → Creates draft PR with all fixes
# → PR description includes before/after score projection
```

**Use Case 3: CI/CD Integration**
```bash
# GitHub Action runs assessment
# Posts comment on PR with assessment results
# Includes links to create remediation issues
# Can auto-create draft PR for improvements
```

**Implementation Approach**:

**Phase 1: Client-Side with gh CLI** (Simplest, no backend needed)
- Use JavaScript in HTML report to call gh CLI via local proxy
- Generate fix files locally
- Use `gh issue create` and `gh pr create`
- Works for users with gh CLI installed

**Phase 2: Dashboard Server** (Enhanced UX)
- Flask/FastAPI server serving dashboard
- WebSocket for live updates
- GitHub OAuth for authentication
- Background workers for fix generation

**Phase 3: Cloud Service** (SaaS offering)
- Hosted dashboard at agentready.dev
- GitHub App installation
- Webhook integration for continuous monitoring
- Team collaboration features

**Fix Templates by Attribute**:

```yaml
claude_md_file:
  type: template
  generates:
    - file: CLAUDE.md
      content: |
        # {repository_name}

        ## Overview
        {auto_generated_description}

        ## Architecture
        {detected_patterns}

        ## Development
        {build_commands}

lock_files:
  type: command
  commands:
    - condition: has_package_json
      run: npm install
    - condition: has_pyproject_toml
      run: poetry lock || pip freeze > requirements.txt

precommit_hooks:
  type: template
  generates:
    - file: .pre-commit-config.yaml
      content: {language_specific_hooks}

readme_structure:
  type: enhancement
  modifies: README.md
  adds_sections:
    - Installation
    - Usage
    - Development
    - Contributing

type_annotations:
  type: ai_powered
  uses: ast_analysis + llm
  modifies: "*.py"
  adds: type_hints
```

**Dashboard vs Report Decision**:

**Keep Both**:
- Static reports for CI/CD, documentation, archiving
- Dashboard for interactive development workflow
- Reports can link to dashboard for remediation
- Dashboard can export static reports

**Benefits of Dashboard**:
- ✅ Interactive remediation workflow
- ✅ Live assessment updates
- ✅ Progress tracking over time
- ✅ Team collaboration (comments, assignments)
- ✅ Automated fix preview before applying
- ✅ Integration with existing tools (GitHub, IDEs)

**Challenges**:
- Authentication complexity (GitHub OAuth)
- Fix generation quality (need good templates + AI)
- PR review overhead (lots of automated PRs)
- Maintaining fix templates as best practices evolve

**Recommended Approach**:

1. **Start with enhanced static report**:
   - Add "Create Issue" buttons that generate gh CLI commands
   - Users copy/paste commands to create issues
   - Include fix templates in issue descriptions

2. **Add local dashboard** (Phase 2):
   - Flask server with WebSocket updates
   - GitHub integration via gh CLI
   - Generate fixes, preview diffs, create PRs

3. **Consider hosted service** (Phase 3+):
   - If adoption is high
   - SaaS model for teams
   - Continuous monitoring and recommendations

**Related**: GitHub integration, automation, remediation, UX

**Notes**:
- This is a MAJOR feature that could become a standalone product
- Consider MVP: "Copy this gh command" buttons in HTML report
- AI-powered fix generation requires careful validation
- Some fixes (like refactoring) need human review
- Could integrate with existing tools (Dependabot, Renovate)
- May want to partner with GitHub for official integration

---

### GitHub App Integration (Badge & Status Checks)

**Priority**: P2 (High Value)

**Description**: Create a GitHub App that provides badge integration, PR status checks, and automated assessment comments to help Red Hat engineering teams track and improve repository quality.

**Core Features**:

1. **Repository Badge**
   - Shields.io-compatible SVG badge showing certification level
   - Endpoint: `https://agentready.redhat.com/badge/{owner}/{repo}.svg`
   - Dynamic color based on certification (Platinum=purple, Gold=yellow, Silver=silver, Bronze=brown)
   - Include score: "AgentReady: 85.2 (Gold)"
   - Click badge to view latest assessment report

2. **GitHub Actions Integration**
   - Create official `agentready/assess-action` GitHub Action
   - Run assessment on PR events (opened, synchronized, reopened)
   - Run assessment on push to main/master
   - Support custom triggers via workflow_dispatch

3. **PR Status Checks**
   - Use GitHub Commit Status API to report assessment results
   - Set check status: success (>90), warning (75-89), failure (<75)
   - Configurable thresholds via `.agentready-config.yaml`
   - Block PR merge if score below threshold (optional)
   - Link to detailed HTML report in check details

4. **PR Comments**
   - Automated bot comments on PRs with assessment summary
   - Show score delta: "Score changed: 72.4 → 78.3 (+5.9)"
   - List new failures and fixes
   - Collapsible sections for full findings
   - Trend chart showing last 10 assessments (ASCII or embedded image)
   - Include remediation suggestions for new failures

**Technical Implementation**:

**Phase 1: GitHub Actions Integration**
```yaml
# .github/workflows/agentready.yml
name: AgentReady Assessment
on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, master]

jobs:
  assess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: agentready/assess-action@v1
        with:
          threshold: 75
          post-comment: true
          update-status: true
```

**Phase 2: Badge Service**
```python
# FastAPI endpoint for badge generation
@app.get("/badge/{owner}/{repo}.svg")
async def get_badge(owner: str, repo: str):
    # Fetch latest assessment from GitHub Actions artifacts
    # Or run quick assessment on-demand
    score, level = get_latest_assessment(owner, repo)
    color = LEVEL_COLORS[level]
    return SVGResponse(generate_badge(score, level, color))
```

**Phase 3: GitHub App**
- App permissions: Contents (read), Checks (write), Pull requests (write)
- Webhook events: push, pull_request
- Installed via GitHub Marketplace (Red Hat internal)
- Dashboard at agentready.redhat.com showing:
  - Repository list with scores
  - Historical trends
  - Organization-wide statistics
  - Top repositories by improvement

**Integration Points**:

1. **GitHub Actions Artifacts**
   - Store assessment reports as workflow artifacts
   - Keep last 30 days of reports for trend analysis
   - Generate downloadable HTML/JSON/Markdown reports

2. **GitHub Status API**
   ```python
   POST /repos/{owner}/{repo}/statuses/{commit_sha}
   {
     "state": "success",  # or "pending", "failure", "error"
     "target_url": "https://agentready.redhat.com/reports/{run_id}",
     "description": "AgentReady: 85.2 (Gold)",
     "context": "agentready/assessment"
   }
   ```

3. **GitHub Checks API** (preferred over Status API)
   ```python
   POST /repos/{owner}/{repo}/check-runs
   {
     "name": "AgentReady Assessment",
     "status": "completed",
     "conclusion": "success",
     "output": {
       "title": "Score: 85.2/100 (Gold)",
       "summary": "Passed 20/25 attributes",
       "text": "Detailed findings..."
     }
   }
   ```

**Use Cases**:

**Use Case 1: Add Badge to README**
```markdown
# My Project

[![AgentReady](https://agentready.redhat.com/badge/redhat/my-project.svg)](https://agentready.redhat.com/reports/redhat/my-project)
```

**Use Case 2: Enforce Quality Gates**
```yaml
# .agentready-config.yaml
github:
  status_checks:
    enabled: true
    min_score: 75  # Block merge if score < 75
    require_improvement: true  # Block if score decreased
```

**Use Case 3: Track Organization Progress**
- Dashboard shows all repos in Red Hat org
- Filter by team, language, certification level
- Identify repos needing attention
- Celebrate improvements (score increases)

**Configuration**:

```yaml
# .agentready-config.yaml
github:
  badge:
    enabled: true
    style: flat-square  # or flat, plastic, for-the-badge
    label: "AgentReady"

  actions:
    enabled: true
    trigger_on: [pull_request, push]
    post_comment: true
    update_status: true
    upload_artifacts: true

  status_checks:
    enabled: true
    min_score: 75
    require_improvement: false

  comments:
    enabled: true
    show_delta: true
    show_trend: true
    collapse_details: true
```

**Implementation Checklist**:

- [ ] Create `agentready/assess-action` GitHub Action
- [ ] Implement badge generation service
- [ ] Add GitHub Status API integration
- [ ] Add GitHub Checks API integration
- [ ] Implement PR comment generation
- [ ] Add score delta calculation
- [ ] Create assessment artifact storage
- [ ] Build organization dashboard
- [ ] Add Red Hat SSO authentication
- [ ] Deploy to Red Hat infrastructure
- [ ] Create documentation for Red Hat teams
- [ ] Add to Red Hat developer onboarding

**Related**: CI/CD integration, automation, visibility, quality gates

**Notes**:
- Focus on internal Red Hat adoption first
- Badge service could be hosted on Red Hat infrastructure
- Dashboard should integrate with Red Hat IdM for authentication
- Consider integration with Red Hat's existing code quality tools
- GitHub App should be installable via Red Hat GitHub Enterprise
- All data stays within Red Hat infrastructure (no external services)
- Align with Red Hat's OpenShift AI strategy for agentic development
- Could become part of Red Hat's AI-assisted development workflow

---

## Backlog Metadata

**Created**: 2025-11-21
**Last Updated**: 2025-11-21
**Total Items**: 9
