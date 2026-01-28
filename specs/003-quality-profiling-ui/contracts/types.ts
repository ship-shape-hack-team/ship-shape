/**
 * TypeScript type definitions for Ship-Shape Quality Profiling API
 * Generated from OpenAPI specification
 */

// ============================================================================
// Core Entities
// ============================================================================

export interface Repository {
  repo_url: string;
  name: string;
  description?: string | null;
  primary_language?: string | null;
  last_assessed?: string | null;
  created_at: string;
  updated_at: string;
  latest_assessment?: AssessmentSummary | null;
}

export interface RepositorySummary {
  repo_url: string;
  name: string;
  primary_language?: string | null;
  last_assessed?: string | null;
  overall_score?: number | null;
}

export interface Assessment {
  id: string;
  repo_url: string;
  overall_score?: number | null;
  status: AssessmentStatus;
  started_at: string;
  completed_at?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface AssessmentSummary {
  id: string;
  overall_score: number;
  status: AssessmentStatus;
  completed_at?: string | null;
}

export interface AssessmentDetailed extends Assessment {
  metadata: AssessmentMetadata;
  assessor_results: AssessorResult[];
}

export interface AssessmentMetadata {
  commit_count?: number | null;
  head_commit_sha: string;
  file_count: number;
  line_count: number;
  languages: Record<string, number>;
  contributor_count?: number | null;
}

export interface AssessorResult {
  id: string;
  assessor_name: string;
  score: number;
  metrics: Record<string, unknown>;
  status: AssessorStatus;
  executed_at: string;
  recommendations?: Recommendation[];
}

export interface Recommendation {
  id: string;
  category: RecommendationCategory;
  severity: RecommendationSeverity;
  description: string;
  metadata?: Record<string, unknown> | null;
}

export interface BenchmarkSnapshot {
  id: string;
  created_at: string;
  repository_count: number;
  statistical_summary?: StatisticalSummary | null;
}

export interface BenchmarkDetailed extends BenchmarkSnapshot {
  statistical_summary: StatisticalSummary;
}

export interface StatisticalSummary {
  overall_score?: Statistics;
  test_coverage?: Statistics;
  integration_tests?: Statistics;
  documentation_standards?: Statistics;
  ecosystem_tools?: Statistics;
  [key: string]: Statistics | undefined;
}

export interface Statistics {
  mean: number;
  median: number;
  std_dev: number;
  min: number;
  max: number;
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
  };
}

export interface BenchmarkRanking {
  id: string;
  repo_url: string;
  rank: number;
  percentile: number;
  dimension_scores: Record<string, DimensionScore>;
  repository?: RepositorySummary;
}

export interface DimensionScore {
  score: number;
  rank: number;
  percentile: number;
}

// ============================================================================
// Enums and Literals
// ============================================================================

export type AssessmentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export type AssessorStatus = 'success' | 'failed' | 'skipped';

export type RecommendationCategory = 
  | 'testing' 
  | 'documentation' 
  | 'security' 
  | 'code_quality' 
  | 'ecosystem' 
  | 'maintainability';

export type RecommendationSeverity = 'critical' | 'high' | 'medium' | 'low';

export type ExportFormat = 'json' | 'csv' | 'pdf';

export type SortBy = 'name' | 'last_assessed' | 'overall_score';

export type SortOrder = 'asc' | 'desc';

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface ListRepositoriesParams {
  limit?: number;
  offset?: number;
  sort_by?: SortBy;
  order?: SortOrder;
}

export interface ListRepositoriesResponse {
  repositories: RepositorySummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface CreateRepositoryRequest {
  repo_url: string;
  trigger_assessment?: boolean;
}

export interface CreateAssessmentRequest {
  repo_url: string;
  assessors?: string[];
}

export interface GetAssessmentParams {
  include_results?: boolean;
}

export interface GetAssessmentStatusResponse {
  status: AssessmentStatus;
  progress: number;
  message?: string;
}

export interface GetRepositoryAssessmentsParams {
  limit?: number;
  offset?: number;
}

export interface GetRepositoryAssessmentsResponse {
  assessments: Assessment[];
  total: number;
}

export interface ListBenchmarksParams {
  limit?: number;
}

export interface ListBenchmarksResponse {
  benchmarks: BenchmarkSnapshot[];
}

export interface GetBenchmarkRankingsParams {
  limit?: number;
  offset?: number;
}

export interface GetBenchmarkRankingsResponse {
  rankings: BenchmarkRanking[];
  total: number;
}

export interface ExportAssessmentParams {
  format?: ExportFormat;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown> | null;
}

// ============================================================================
// Assessor-Specific Metric Types
// ============================================================================

export interface TestCoverageMetrics {
  line_coverage: number;
  branch_coverage: number;
  function_coverage: number;
  test_to_code_ratio: number;
  test_count: number;
  test_execution_time_seconds: number;
}

export interface IntegrationTestsMetrics {
  integration_test_count: number;
  api_endpoint_coverage: number;
  database_test_coverage: number;
  external_service_mocking: boolean;
  contract_testing_present: boolean;
}

export interface DocumentationStandardsMetrics {
  readme_score: number;
  api_documentation_completeness: number;
  architecture_docs_present: boolean;
  docstring_coverage: number;
  comment_quality_score: number;
  documentation_freshness_days: number;
}

export interface EcosystemToolsMetrics {
  ci_cd: {
    present: boolean;
    platform: string;
    test_execution: boolean;
    coverage_reporting: boolean;
    quality_score: number;
  };
  code_coverage_tracking: {
    present: boolean;
    tool: string;
    configured_properly: boolean;
  };
  security_scanning: {
    present: boolean;
    tools: string[];
    auto_fix_enabled: boolean;
  };
  e2e_testing: {
    present: boolean;
    tool: string;
    coverage: number;
  };
  code_quality_tools?: {
    present: boolean;
    tools: string[];
    pre_commit_hooks: boolean;
  };
}

export interface CodeQualityMetrics {
  average_cyclomatic_complexity: number;
  functions_exceeding_complexity_threshold: number;
  code_duplication_percentage: number;
  linting_violations: number;
  code_smells: number;
  technical_debt_minutes: number;
}

export interface SecurityBestPracticesMetrics {
  dependency_vulnerabilities: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  secrets_detected: number;
  security_headers_present: boolean;
  authentication_strength: string;
  input_validation_coverage: number;
}

export interface DORAMetrics {
  deployment_frequency: string;
  lead_time_for_changes_hours: number;
  change_failure_rate_percentage: number;
  mttr_hours: number;
  performance_tier: string;
}

export interface MaintainabilityMetrics {
  active_contributors_90d: number;
  median_pr_merge_time_hours: number;
  median_issue_resolution_time_days: number;
  code_churn_percentage: number;
  outdated_dependencies: number;
}

// ============================================================================
// Radar Chart Data Types
// ============================================================================

export interface RadarChartDataPoint {
  dimension: string;
  score: number;
  fullMark: number;
}

export interface RadarChartData {
  repository: string;
  data: RadarChartDataPoint[];
}

// ============================================================================
// UI Component Props Types
// ============================================================================

export interface RepositoryTableRow extends RepositorySummary {
  status?: string;
  last_assessed_relative?: string;
}

export interface ComparisonData {
  repositories: RepositorySummary[];
  assessments: AssessmentDetailed[];
  benchmark?: BenchmarkRanking[];
}

// ============================================================================
// API Client Configuration
// ============================================================================

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}
