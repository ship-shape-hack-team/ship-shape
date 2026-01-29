# Quickstart: Quality Profiling and Benchmarking with UI

**Feature**: 003-quality-profiling-ui | **Date**: 2026-01-28

This guide gets you up and running with the quality profiling feature in under 5 minutes.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm/yarn installed (for UI)
- Git repository to assess
- `uv` package manager (recommended) or `pip`

## Quick Setup

### 1. Install Backend (Python)

```bash
# Navigate to ship-shape repository
cd /path/to/ship-shape

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies with uv (recommended)
uv pip install -e ".[quality]"

# OR with pip
pip install -e ".[quality]"
```

### 2. Install Frontend (React/TypeScript)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# OR
yarn install

# Generate API client from OpenAPI spec
npm run generate-api
```

### 3. Run Your First Assessment

```bash
# Activate virtual environment (if not already)
source .venv/bin/activate

# Assess a repository (CLI)
ship-shape assess https://github.com/owner/repo

# View results in JSON
ship-shape assess https://github.com/owner/repo --format json

# View results in formatted report
ship-shape assess https://github.com/owner/repo --format markdown
```

### 4. Start the API Server

```bash
# Start FastAPI backend
uvicorn agentready.api.app:app --reload --port 8000

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 5. Start the UI

```bash
# In a new terminal
cd frontend

# Start development server
npm run dev
# OR
yarn dev

# UI will be available at http://localhost:5173
```

## Basic Usage

### CLI Workflow

```bash
# Assess a single repository
ship-shape assess https://github.com/owner/repo

# Assess with specific assessors only
ship-shape assess https://github.com/owner/repo \
  --assessors test_coverage,documentation_standards

# Assess multiple repositories (batch)
ship-shape assess-batch repos.txt

# Generate benchmark from assessed repositories
ship-shape benchmark --output benchmark.json

# View benchmark rankings
ship-shape benchmark-show benchmark.json --top 10
```

### UI Workflow

1. **Open Dashboard**: Navigate to http://localhost:5173
2. **Add Repository**: Enter GitHub/GitLab URL in input field at top
3. **View Table**: See all assessed repositories with scores
4. **Drill Down**: Click any repository row to view detailed assessor results
5. **View Radar Chart**: See quality dimensions visualized in radar chart
6. **Compare**: Select multiple repositories to compare side-by-side

### API Workflow

```bash
# Add a repository and trigger assessment
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/owner/repo", "trigger_assessment": true}'

# Get assessment status (use assessment_id from previous response)
curl http://localhost:8000/api/v1/assessments/{assessment_id}/status

# Get full assessment results
curl http://localhost:8000/api/v1/assessments/{assessment_id}?include_results=true

# List all repositories
curl http://localhost:8000/api/v1/repositories

# Create benchmark snapshot
curl -X POST http://localhost:8000/api/v1/benchmarks

# Get latest benchmark rankings
curl http://localhost:8000/api/v1/benchmarks/latest
```

## Example Output

### CLI Assessment Output

```
Assessing repository: https://github.com/owner/repo
✓ Cloning repository...
✓ Running assessors...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY ASSESSMENT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository: owner/repo
Overall Score: 78.5 / 100 (High Performance)
Assessed: 2026-01-28 14:30:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSESSOR RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Test Coverage: 85.0 / 100
  - Line Coverage: 87.5%
  - Branch Coverage: 82.3%
  - Function Coverage: 90.1%
  - Test Count: 342

✓ Integration Tests: 70.0 / 100
  - Integration Test Count: 45
  - API Endpoint Coverage: 75.0%
  - Database Test Coverage: 60.0%

✓ Documentation Standards: 75.0 / 100
  - README Score: 80
  - API Documentation: 70%
  - Docstring Coverage: 65.0%

✓ Ecosystem Tools: 80.0 / 100
  - CI/CD: GitHub Actions (present)
  - Code Coverage: Codecov (configured)
  - Security: Dependabot, Snyk (present)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDATIONS (4 HIGH, 3 MEDIUM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 HIGH: Increase branch coverage to >80% for critical paths
   Category: testing
   Files: src/auth/login.py, src/auth/session.py

🔴 HIGH: Add contract tests for external API dependencies
   Category: testing
   Suggested Tools: Pact, Spring Cloud Contract

🟡 MEDIUM: Update README with usage examples
   Category: documentation

🟡 MEDIUM: Increase database interaction test coverage to 80%
   Category: testing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Assessment ID: a3f5c8e2-4d7b-4a9e-9f3c-6e8d2a1b5c7d
Full report: ~/.ship-shape/reports/owner-repo-20260128-143000.json
```

### UI Dashboard

The UI displays:
- **Input Field**: Enter repository URL at top
- **Repository Table**: 
  - Column: Repository Name
  - Column: Primary Language
  - Column: Overall Score (color-coded: Elite=green, High=blue, Medium=yellow, Low=red)
  - Column: Last Assessed
  - Action: Click to drill down

- **Drill-Down View**:
  - Radar chart with 8 dimensions (test coverage, integration tests, documentation, etc.)
  - Score cards for each assessor
  - Recommendations grouped by severity
  - Historical trend chart

## Configuration

### Backend Configuration

Create `.ship-shape/config.yaml`:

```yaml
# Assessment configuration
assessment:
  default_assessors:
    - test_coverage
    - integration_tests
    - documentation_standards
    - ecosystem_tools
  
  # Scoring weights (must sum to 1.0)
  weights:
    test_coverage: 0.20
    integration_tests: 0.15
    documentation_standards: 0.15
    ecosystem_tools: 0.15
    code_quality: 0.10
    security_best_practices: 0.15
    dora_metrics: 0.05
    maintainability: 0.05

# Storage configuration
storage:
  type: sqlite  # or postgresql
  path: ~/.ship-shape/data/assessments.db
  # For PostgreSQL:
  # host: localhost
  # port: 5432
  # database: shipshape
  # user: shipshape
  # password: ${DB_PASSWORD}

# API configuration
api:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - http://localhost:5173
    - http://localhost:3000

# UI configuration
ui:
  default_sort: last_assessed
  default_order: desc
  items_per_page: 50
```

### Frontend Configuration

Create `frontend/.env`:

```bash
# API endpoint
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Feature flags
VITE_ENABLE_BENCHMARK=true
VITE_ENABLE_EXPORT=true
VITE_ENABLE_COMPARISON=true

# Radar chart configuration
VITE_RADAR_DIMENSIONS=8
```

## Testing

### Run Backend Tests

```bash
# Unit tests
pytest tests/unit/assessors/quality/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/test_quality_assessment_e2e.py

# With coverage
pytest --cov=agentready.assessors.quality --cov-report=html
```

### Run Frontend Tests

```bash
cd frontend

# Unit tests (components)
npm test
# OR
yarn test

# E2E tests (Playwright)
npm run test:e2e
# OR
yarn test:e2e

# With coverage
npm run test:coverage
```

## Troubleshooting

### Assessment Fails

**Problem**: Assessment fails with "Cannot detect test framework"

**Solution**: Ensure repository has test framework configuration file (pytest.ini, jest.config.js, etc.)

---

**Problem**: Assessment fails with "Permission denied"

**Solution**: Ensure repository is publicly accessible or provide authentication credentials

### UI Cannot Connect to API

**Problem**: UI shows "Network Error" when loading repositories

**Solution**:
1. Verify API is running: `curl http://localhost:8000/api/v1/health`
2. Check CORS configuration in `.ship-shape/config.yaml`
3. Verify frontend `.env` has correct `VITE_API_BASE_URL`

### Database Errors

**Problem**: "Database is locked" error

**Solution**: SQLite is locked by another process. Stop all ship-shape instances and retry.

---

**Problem**: "No such table: repositories"

**Solution**: Run database migrations:
```bash
ship-shape db migrate
```

## Next Steps

- **Customize Assessors**: See `docs/developer-guide.md` for adding custom assessors
- **Deploy to Production**: See `docs/deployment.md` for production setup
- **API Reference**: Full API documentation at `/docs/api-reference.md`
- **Contributing**: See `CONTRIBUTING.md` for development guidelines

## Getting Help

- **Documentation**: `/docs/user-guide.md`
- **GitHub Issues**: https://github.com/ship-shape/ship-shape/issues
- **Discord**: https://discord.gg/ship-shape

---

**Estimated Setup Time**: 5 minutes
**First Assessment Time**: 30 seconds (for typical repo)
