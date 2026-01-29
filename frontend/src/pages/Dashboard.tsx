/**
 * Dashboard page - main landing page with repository input and table
 */

import React, { useEffect, useState } from 'react';
import {
  PageSection,
  Title,
  Alert,
  AlertVariant,
} from '@patternfly/react-core';
import { useNavigate } from 'react-router-dom';
import { RepositoryInput } from '../components/RepositoryInput';
import { RepositoryTable } from '../components/RepositoryTable';
import { EmptyState } from '../components/EmptyState';
import { RepositorySummary } from '../types';
import apiClient from '../services/api';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [repositories, setRepositories] = useState<RepositorySummary[]>([]);
  const [historicalData, setHistoricalData] = useState<Record<string, any[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load repositories on mount
  useEffect(() => {
    loadRepositories();
  }, []);

  const loadRepositories = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.listRepositories({
        limit: 100,
        sort_by: 'last_assessed',
        order: 'desc',
      });

      setRepositories(data.repositories || []);
      
      // Load historical data for each repository
      const historical: Record<string, any[]> = {};
      for (const repo of data.repositories || []) {
        try {
          const history = await apiClient.getRepositoryAssessments(repo.repo_url, 50);
          historical[repo.repo_url] = history.assessments || [];
        } catch (err) {
          console.error(`Failed to load history for ${repo.name}:`, err);
          historical[repo.repo_url] = [];
        }
      }
      setHistoricalData(historical);
      
      // If no repositories in database, show helpful message
      if (data.repositories.length === 0) {
        setError('No repositories assessed yet. Run: agentready assess-quality /path/to/repo');
      }
    } catch (err) {
      console.error('Failed to load repositories:', err);
      setError('API server not running. Start it with: uvicorn agentready.api.app:app --reload --port 8000');
      setRepositories([]);
      setHistoricalData({});
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddRepository = async (repoUrl: string) => {
    await apiClient.createRepository(repoUrl, true);
    
    // Reload repositories
    await loadRepositories();
  };

  const handleRowClick = (repo: RepositorySummary) => {
    // Navigate to detail page using assessment ID
    if (repo.latest_assessment_id) {
      navigate(`/assessment/${repo.latest_assessment_id}`);
    } else {
      alert('No assessment found for this repository');
    }
  };

  return (
    <>
      <PageSection variant="light">
        <Title headingLevel="h1" size="2xl" style={{ color: '#151515' }}>
          Quality Profiling Dashboard
        </Title>
        <p style={{ marginTop: '0.5rem', color: '#6a6e73' }}>
          Assess and compare repository quality across multiple dimensions
        </p>
      </PageSection>

      <PageSection>
        {error && (
          <Alert
            variant={AlertVariant.warning}
            title="Backend Not Connected"
            isInline
            style={{ marginBottom: '1rem' }}
          >
            {error}
          </Alert>
        )}

        <RepositoryInput onSubmit={handleAddRepository} />

        {repositories.length === 0 && !isLoading ? (
          <EmptyState />
        ) : (
          <RepositoryTable
            repositories={repositories}
            onRowClick={handleRowClick}
            onTrendClick={() => {}}
            historicalData={historicalData}
            isLoading={isLoading}
          />
        )}
      </PageSection>
    </>
  );
};

