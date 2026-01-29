# API Contracts

This directory contains the API contracts for the Ship-Shape Quality Profiling feature.

## Files

### openapi.yaml

OpenAPI 3.0 specification for the REST API. This specification defines:
- All API endpoints and operations
- Request/response schemas
- Validation rules and constraints
- Error responses

**Usage**:
- **Backend**: Use FastAPI to auto-generate API from this spec
- **Frontend**: Generate TypeScript API client using `openapi-generator-cli`
- **Documentation**: Host Swagger UI at `/api/docs` endpoint

**Generate TypeScript Client**:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i contracts/openapi.yaml \
  -g typescript-axios \
  -o frontend/src/generated/api
```

### types.ts

TypeScript type definitions for frontend development. These types:
- Mirror the OpenAPI schema definitions
- Include assessor-specific metric types
- Provide UI component prop types
- Define API client configuration

**Usage**:
```typescript
import { 
  Repository, 
  AssessmentDetailed, 
  RadarChartData 
} from '@/contracts/types';
```

## API Endpoints Summary

### Repositories
- `GET /repositories` - List all repositories
- `POST /repositories` - Add a new repository
- `GET /repositories/{repo_url_encoded}` - Get repository details
- `DELETE /repositories/{repo_url_encoded}` - Delete a repository

### Assessments
- `POST /assessments` - Trigger a new assessment
- `GET /assessments/{assessment_id}` - Get assessment details
- `GET /assessments/{assessment_id}/status` - Poll assessment status
- `POST /assessments/{assessment_id}/cancel` - Cancel running assessment
- `GET /repositories/{repo_url_encoded}/assessments` - Get assessment history

### Benchmarks
- `GET /benchmarks` - List benchmark snapshots
- `POST /benchmarks` - Create a new benchmark
- `GET /benchmarks/{benchmark_id}` - Get benchmark details
- `GET /benchmarks/{benchmark_id}/rankings` - Get repository rankings
- `GET /benchmarks/latest` - Get latest benchmark

### Export
- `GET /export/assessments/{assessment_id}` - Export assessment data (JSON, CSV, PDF)

## Authentication

Currently unauthenticated. Future versions will support JWT bearer tokens via the `bearerAuth` security scheme.

## Validation

All endpoints enforce validation rules defined in the data model:
- Scores must be in range [0.0, 100.0]
- Status enums are strictly validated
- Required fields are enforced
- Foreign key relationships are validated

## Versioning

API version is specified in the URL path: `/api/v1`

Breaking changes will increment the major version (e.g., `/api/v2`).
