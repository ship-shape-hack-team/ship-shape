# AgentReady - GitHub Issues Template

**Purpose**: GitHub-ready issue descriptions for all backlog items, organized by priority.

**Instructions**: Copy each issue block below into a new GitHub issue.

---

## P0 - Critical Issues (Blocking Adoption)

### Issue #1: Add Report Header with Repository Metadata

**Labels**: `P0-critical`, `ux`, `reports`, `bug`

**Title**: Add prominent report header showing repository name, path, and assessment metadata

**Description**:

Currently, AgentReady reports (HTML, Markdown, JSON) lack context about what repository was assessed. Users cannot immediately identify:
- What repository was scanned
- When the assessment was run
- Which branch/commit was assessed
- Who executed the assessment

This blocks adoption in multi-repository workflows and CI/CD environments.

**Expected Behavior**:

All reports should have a **prominent header section** at the top showing:
- Repository name (bold, large)
- Repository path (filesystem path or GitHub URL)
- Assessment timestamp (human-readable)
- Git branch and commit hash
- AgentReady version
- User who ran assessment (username@hostname)
- Command executed

**Implementation**:

HTML Report Header:
```html
<header class="report-header">
  <h1>AgentReady Assessment Report</h1>
  <div class="repo-name">Repository: agentready</div>
  <div class="repo-path">/Users/jeder/repos/sk/agentready</div>
  <div class="repo-git">Branch: main | Commit: abc123</div>
  <div class="meta">
    Assessed: November 21, 2025 at 2:11 AM
    AgentReady: v1.0.0
    By: jeder@macbook
  </div>
</header>
```

**Files to Modify**:
- `src/agentready/models/assessment.py` - Add metadata field
- `src/agentready/services/scanner.py` - Collect metadata (version, user, command)
- `src/agentready/templates/report.html.j2` - Add header section
- `src/agentready/reporters/markdown.py` - Add header to markdown
- `src/agentready/reporters/html.py` - Pass metadata to template

**Acceptance Criteria**:
- [ ] Repository name and path visible at top of all reports
- [ ] Assessment timestamp in human-readable format
- [ ] Git context (branch, commit) included
- [ ] AgentReady version tracked
- [ ] Header positioned before score summary
- [ ] All three report formats updated (HTML, Markdown, JSON)

**Priority Justification**: Users are confused about what reports show. This blocks real-world usage.

---

### Issue #2: Redesign HTML Report - Fix Font Sizes and Color Scheme

**Labels**: `P0-critical`, `ux`, `design`, `reports`, `accessibility`

**Title**: Increase font sizes (+4pt) and replace color scheme with professional dark blue/purple/white palette

**Description**:

Current HTML report has two critical UX problems:
1. **Font sizes too small** - Base font is 14px, headings are small, hard to read
2. **Color scheme problems** - Purple gradient everywhere is overwhelming and unprofessional

User feedback: "the color scheme is hideous"

**Current Problems**:
- Body text: 14px (too small for modern displays)
- Purple gradient background used everywhere (#667eea → #764ba2)
- Low contrast in some areas
- Not suitable for Red Hat engineering presentations

**Required Changes**:

**1. Font Size Increases** (minimum +4pt):
```css
body: 14px → 18px
h1: 28px → 36px
h2: 24px → 30px
h3: 20px → 26px
.score: 48px → 56px
.attribute-name: 16px → 22px
```

**2. New Color Scheme** (Dark/Professional):
```css
/* Replace current purple gradient with: */
--background: #0a0e27;      /* Almost black with blue tint */
--surface: #1a1f3a;         /* Dark blue surface */
--primary: #8b5cf6;         /* Purple (accent only) */
--text-primary: #f8fafc;    /* Almost white */
--success: #10b981;         /* Green (pass) */
--danger: #ef4444;          /* Red (fail) */
```

**Design Direction**: Mostly black, dark blue, purple accents, white text - professional and clean.

**Files to Modify**:
- `src/agentready/templates/report.html.j2` - Update all CSS

**Acceptance Criteria**:
- [ ] Base font size increased to 18px minimum
- [ ] All headings increased by 4pt+
- [ ] Purple gradient removed from backgrounds
- [ ] Dark blue (#1a1f3a) used for surfaces
- [ ] Purple (#8b5cf6) used sparingly as accent
- [ ] White text (#f8fafc) on dark backgrounds
- [ ] WCAG 2.1 AA contrast ratios maintained
- [ ] Professional appearance suitable for stakeholder presentations

**Priority Justification**: Visual design blocks adoption. This is the first thing users see.

**Related Issues**: #3 (Theme system will build on this foundation)

---

## P1 - Critical Features

### Issue #3: Implement `agentready align` Subcommand for Automated Remediation

**Labels**: `P1-critical`, `feature`, `cli`, `automation`

**Title**: Add `agentready align` command to automatically fix failing attributes

**Description**:

Users need an automated way to improve their repository scores. The `align` subcommand should generate and apply fixes for failing attributes.

**Vision**: One command to align repository with best practices.

**Proposed Interface**:
```bash
agentready align .                           # Fix all failures
agentready align . --dry-run                 # Preview changes
agentready align . --create-pr               # Create GitHub PR
agentready align . --interactive             # Confirm each fix
agentready align . --attributes claude_md_file,precommit_hooks
```

**Supported Fix Types**:

1. **Template-based** (auto-applicable):
   - CLAUDE.md generation
   - .gitignore patterns
   - .pre-commit-config.yaml
   - README scaffolding
   - GitHub issue/PR templates

2. **Command-based** (execute commands):
   - Generate lock files (`npm install`, `poetry lock`)
   - Install pre-commit hooks
   - Update dependencies

3. **AI-powered** (optional, requires --ai):
   - Add type annotations
   - Generate docstrings
   - Refactor high-complexity functions

**Workflow Example**:
```
$ agentready align . --dry-run

Repository: my-project
Current Score: 62.4/100 (Silver)
Projected Score: 84.7/100 (Gold) 🎯

Changes:
  ✅ claude_md_file (+10 pts) - CREATE CLAUDE.md
  ✅ precommit_hooks (+3 pts) - CREATE .pre-commit-config.yaml
  ✅ gitignore (+3 pts) - UPDATE .gitignore

Apply changes? [y/N]
```

**Implementation Phases**:

**Phase 1**: Template-based fixes
- Create `src/agentready/fixers/` module
- Implement base fixer class
- Add template-based fixers (CLAUDE.md, .gitignore, pre-commit)
- Add `align` CLI command
- Support --dry-run flag

**Phase 2**: Command execution & GitHub PR
- Execute shell commands safely
- Add --create-pr flag
- Implement GitHub PR creation via `gh` CLI
- Show before/after scores

**Phase 3**: AI-powered fixes (future)
- Integrate with LLM APIs
- Add type annotation fixer
- Add docstring generator
- Require explicit --ai flag

**Files to Create**:
- `src/agentready/fixers/base.py` - BaseFixer abstract class
- `src/agentready/fixers/template.py` - Template-based fixers
- `src/agentready/fixers/command.py` - Command execution
- `src/agentready/cli/align.py` - CLI command
- `src/agentready/templates/fixes/` - Fix templates directory
- `tests/unit/test_fixers.py` - Fixer tests

**Acceptance Criteria**:
- [ ] `agentready align .` applies all fixable failures
- [ ] `--dry-run` shows preview without applying changes
- [ ] `--create-pr` creates GitHub PR with fixes
- [ ] Score improvement projection shown
- [ ] Template-based fixes working (CLAUDE.md, .gitignore, pre-commit)
- [ ] Comprehensive tests

**Priority Justification**: Most requested feature. Dramatically improves value proposition.

**Related**: Interactive Dashboard (#8)

---

## P2 - High Value Features

### Issue #4: Create Interactive Dashboard with One-Click Remediation

**Labels**: `P2-high`, `feature`, `dashboard`, `ux`, `github-integration`

**Title**: Build interactive dashboard for live assessment updates and one-click GitHub issue/PR creation

**Description**:

Transform static HTML report into interactive dashboard with:
- Real-time assessment updates (WebSocket)
- "Fix This" button on each failure → creates GitHub issue + draft PR
- Historical trend visualization
- Live filtering/sorting (already implemented)

**Vision**: Click "Fix This" → GitHub issue created → Draft PR with proposed changes

**Implementation Phases**:

**Phase 1**: Enhanced Static Report
- Add "Copy gh command" buttons to HTML report
- Generate `gh issue create` commands for each failure
- Include fix templates in issue descriptions

**Phase 2**: Local Dashboard Server
- Flask/FastAPI server serving dashboard
- WebSocket for live updates
- GitHub integration via `gh` CLI
- Preview diffs before applying fixes

**Phase 3**: Cloud Service (future)
- Hosted dashboard at agentready.redhat.com
- GitHub App installation
- Continuous monitoring
- Team collaboration

**Acceptance Criteria (Phase 1)**:
- [ ] "Copy Command" button for each failure
- [ ] Generated `gh` commands create properly formatted issues
- [ ] Fix templates embedded in issue descriptions
- [ ] Links to AgentReady documentation

**Priority Justification**: Significantly improves workflow - users can fix issues with one click.

**Related**: Align command (#3), GitHub App (#9)

---

### Issue #5: Implement GitHub App Integration (Badge & Status Checks)

**Labels**: `P2-high`, `feature`, `github-integration`, `ci-cd`

**Title**: Create GitHub App for repository badges, PR status checks, and automated comments

**Description**:

Provide GitHub integration for visibility and CI/CD workflows:
- Repository badges showing certification level
- GitHub Actions integration
- PR status checks (block merge if score < threshold)
- Automated PR comments with score deltas

**Core Features**:

1. **Badge Service**
   - Endpoint: `https://agentready.redhat.com/badge/{owner}/{repo}.svg`
   - Dynamic color based on certification (Platinum, Gold, Silver, Bronze)
   - Shields.io-compatible format

2. **GitHub Actions**
   - Official `agentready/assess-action`
   - Run on PR events and pushes
   - Upload artifacts (HTML/JSON reports)

3. **PR Status Checks**
   - Use GitHub Checks API
   - Configurable thresholds
   - Link to detailed report

4. **PR Comments**
   - Automated bot comments
   - Score delta: "72.4 → 78.3 (+5.9)"
   - New failures/fixes listed

**Implementation**:

**Phase 1**: GitHub Actions Integration
```yaml
# Create .github/workflows/agentready.yml
- uses: agentready/assess-action@v1
  with:
    threshold: 75
    post-comment: true
```

**Phase 2**: Badge Service
- FastAPI endpoint generating SVG badges
- Fetch latest assessment from GitHub Actions artifacts

**Phase 3**: GitHub App
- App installation via Red Hat GitHub Enterprise
- Dashboard at agentready.redhat.com
- Red Hat SSO authentication

**Acceptance Criteria**:
- [ ] GitHub Action published and working
- [ ] Badge service generating SVGs
- [ ] Status checks posted to PRs
- [ ] Comments show score deltas
- [ ] Integration with Red Hat infrastructure

**Priority Justification**: Critical for CI/CD adoption and visibility within Red Hat.

**Notes**: All infrastructure stays within Red Hat (no external services).

---

## P3 - Important Enhancements

### Issue #6: Implement Report Schema Versioning

**Labels**: `P3-important`, `schema`, `contracts`, `backwards-compatibility`

**Title**: Define and version JSON/HTML/Markdown report schemas for backwards compatibility

**Description**:

Formalize report schemas and establish versioning to ensure backwards compatibility as the tool evolves.

**Requirements**:
- JSON schema for assessment reports
- HTML schema documentation
- Markdown schema documentation
- Semantic versioning strategy
- Schema migration tools

**Files**:
- `contracts/assessment-schema.json` (already exists, needs versioning)
- `contracts/report-html-schema.md` (exists)
- `contracts/report-markdown-schema.md` (exists)

**Acceptance Criteria**:
- [ ] JSON Schema Draft 2020-12 used
- [ ] `agentready validate-report` command
- [ ] Schema version in report metadata
- [ ] Migration tools for major version changes

**Priority Justification**: Important for enterprise adoption and long-term maintenance.

---

### Issue #7: Create AgentReady Repository Development Agent

**Labels**: `P3-important`, `developer-experience`, `claude-code`

**Title**: Build specialized Claude Code agent for AgentReady development tasks

**Description**:

Create `.claude/agents/agentready-dev.md` agent with deep knowledge of AgentReady architecture to assist with:
- Implementing new assessors
- Writing tests
- Debugging assessment issues
- Optimizing performance

**Acceptance Criteria**:
- [ ] Agent specification created
- [ ] Links to design docs (data-model.md, plan.md)
- [ ] Common development patterns documented
- [ ] Test structure examples included

**Priority Justification**: Accelerates development and helps contributors.

---

## P4 - Nice-to-Have Enhancements

### Issue #8: Build Research Report Generator/Updater Utility

**Labels**: `P4-enhancement`, `tooling`, `documentation`

**Title**: Create utility to maintain research report (agent-ready-codebase-attributes.md)

**Description**:

Build CLI tool to validate and update research report:
- `agentready research validate`
- `agentready research add-attribute`
- `agentready research format`

**Acceptance Criteria**:
- [ ] Schema validation against contracts/research-report-schema.md
- [ ] Automated metadata generation
- [ ] Attribute numbering checks
- [ ] Citation deduplication

**Priority Justification**: Improves research report quality and maintainability.

---

### Issue #9: Integrate Repomix for Repository Context Generation

**Labels**: `P4-enhancement`, `ai-integration`, `tooling`

**Title**: Add Repomix integration for AI-optimized repository context files

**Description**:

Integrate with Repomix (https://github.com/yamadashy/repomix) to generate repository context:
- `agentready repomix-generate`
- Include in bootstrapped repositories
- GitHub Actions integration

**Acceptance Criteria**:
- [ ] Generate Repomix output for existing repos
- [ ] Include in bootstrap workflow
- [ ] GitHub Actions workflow template

**Priority Justification**: Enhances AI-assisted development workflow.

---

### Issue #10: Implement Customizable HTML Report Themes

**Labels**: `P4-enhancement`, `ux`, `accessibility`, `theming`

**Title**: Add theme system with dark/light mode toggle and custom color schemes

**Description**:

Allow users to customize HTML report appearance:
- **Theme dropdown** in top-right corner
- **Quick dark/light toggle button**
- Multiple built-in themes (solarized, dracula, high-contrast)
- localStorage persistence

**Note**: This builds on Issue #2 (P0) which establishes the base dark theme.

**Acceptance Criteria**:
- [ ] Theme dropdown in HTML report
- [ ] Dark/light toggle button
- [ ] 5+ built-in themes
- [ ] localStorage saves preference
- [ ] All themes WCAG 2.1 AA compliant

**Priority Justification**: Improves user experience and accessibility.

---

## P5 - Future Enhancements

### Issue #11: Bootstrap New GitHub Repositories with AgentReady

**Labels**: `P5-future`, `feature`, `onboarding`

**Title**: Create `agentready init` command to bootstrap new repositories with best practices

**Description**:

Generate new repository structure with AgentReady tooling:
- `agentready init --repo my-project --language python`
- Creates CLAUDE.md, README, .gitignore from templates
- Sets up pre-commit hooks
- Configures GitHub Actions

**Acceptance Criteria**:
- [ ] Support Python, JavaScript, TypeScript, Go, Java
- [ ] Template customization
- [ ] GitHub CLI integration

**Priority Justification**: Valuable for onboarding, but lower priority than fixing existing repos.

---

## Issue Creation Checklist

When creating GitHub issues from this template:

1. **Copy the entire issue block** (including title, labels, description, acceptance criteria)
2. **Set labels** as specified in each issue
3. **Set milestone**: Create milestones for v1.1 (P0), v1.2 (P1-P2), v1.3 (P3-P4)
4. **Assign**: Assign P0 issues immediately
5. **Link related issues**: Use "Related to #X" in issue descriptions
6. **Add to project board**: Create columns for P0, P1, P2, P3+

## Label Definitions

Create these labels in GitHub:
- `P0-critical` (red) - Blocking adoption
- `P1-critical` (orange) - Critical features
- `P2-high` (yellow) - High value
- `P3-important` (blue) - Important enhancements
- `P4-enhancement` (green) - Nice to have
- `P5-future` (gray) - Future work
- `ux` - User experience
- `reports` - Report generation
- `feature` - New feature
- `bug` - Bug fix
- `cli` - CLI changes
- `automation` - Automation features
- `github-integration` - GitHub integration
- `accessibility` - Accessibility improvements

## Milestones

**v1.1 - Critical UX Fixes** (Target: Week 1)
- Issue #1: Report Header Metadata
- Issue #2: HTML Design Improvements

**v1.2 - Automation & Integration** (Target: Week 2-3)
- Issue #3: Align Subcommand
- Issue #4: Interactive Dashboard (Phase 1)
- Issue #5: GitHub App Integration (Phase 1)

**v1.3 - Polish & Documentation** (Target: Week 4+)
- Issue #6: Schema Versioning
- Issue #7: Development Agent
- Issue #8-11: Enhancements
