/**
 * API client service for Ship-Shape Quality Profiling API
 */

import axios, { AxiosInstance } from 'axios';

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
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
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
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

class ApiClient {
  private client: AxiosInstance;

  constructor(config: ApiClientConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Repositories
  async listRepositories(params?: {
    limit?: number;
    offset?: number;
    sort_by?: string;
    order?: string;
  }) {
    const response = await this.client.get('/repositories', { params });
    return response.data;
  }

  async createRepository(repo_url: string, trigger_assessment: boolean = true) {
    const response = await this.client.post('/repositories', {
      repo_url,
      trigger_assessment,
    });
    return response.data;
  }

  async getRepository(repo_url: string) {
    const response = await this.client.get('/repository', {
      params: { repo_url }
    });
    return response.data;
  }

  // Assessments
  async createAssessment(repo_url: string, assessors?: string[]) {
    const response = await this.client.post('/assessments', {
      repo_url,
      assessors,
    });
    return response.data;
  }

  async getAssessment(assessment_id: string, include_results: boolean = true) {
    const response = await this.client.get(`/assessments/${assessment_id}`, {
      params: { include_results },
    });
    return response.data;
  }

  async getAssessmentStatus(assessment_id: string) {
    const response = await this.client.get(`/assessments/${assessment_id}/status`);
    return response.data;
  }

  async getRepositoryAssessments(repo_url: string, limit: number = 10) {
    const response = await this.client.get('/repository/assessments', {
      params: { repo_url, limit },
    });
    return response.data;
  }

  // Export
  async exportAssessment(assessment_id: string, format: 'json' | 'csv' = 'json') {
    const response = await this.client.get(`/export/assessments/${assessment_id}`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    });
    return response.data;
  }
}

// Create singleton instance
const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = new ApiClient({
  baseURL: apiBaseURL,
});

export default apiClient;
