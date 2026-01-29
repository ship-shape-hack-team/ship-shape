/**
 * TypeScript type definitions for the application
 */

export interface Repository {
  repo_url: string;
  name: string;
  description?: string | null;
  primary_language?: string | null;
  last_assessed?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface RepositorySummary {
  repo_url: string;
  name: string;
  primary_language?: string | null;
  last_assessed?: string | null;
  overall_score?: number | null;
  latest_assessment_id?: string | null;
}

export interface Assessment {
  id: string;
  repo_url: string;
  overall_score: number;
  status: AssessmentStatus;
  started_at: string;
  completed_at?: string | null;
}

export interface AssessorResult {
  id: string;
  assessor_name: string;
  score: number;
  metrics: Record<string, any>;
  status: 'success' | 'failed' | 'skipped';
  executed_at: string;
}

export interface AssessmentDetailed extends Assessment {
  assessor_results: AssessorResult[];
}

export type AssessmentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface RadarChartDataPoint {
  dimension: string;
  score: number;
  fullMark: number;
}

export interface RadarChartData {
  repository: string;
  data: RadarChartDataPoint[];
}

// Utility functions
export function formatAssessorName(assessor_name: string): string {
  return assessor_name
    .replace('quality_', '')
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function getScoreColor(score: number): string {
  if (score >= 90) return 'green';
  if (score >= 75) return 'blue';
  if (score >= 60) return 'gold';
  return 'red';
}

export function getPerformanceTier(score: number): string {
  if (score >= 90) return 'Elite';
  if (score >= 75) return 'High';
  if (score >= 60) return 'Medium';
  return 'Low';
}
