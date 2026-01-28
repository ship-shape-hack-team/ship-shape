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
    } catch (err) {
      console.error('Failed to load repositories:', err);
      setError('Failed to load repositories. Make sure the API server is running.');
      // Show mock data for demo purposes
      setRepositories(getMockRepositories());
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
    // Navigate to detail page
    navigate(`/repository/${encodeURIComponent(repo.repo_url)}`);
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
            variant={AlertVariant.info}
            title="Demo Mode"
            isInline
            style={{ marginBottom: '1rem' }}
          >
            {error} Showing mock data for demonstration.
          </Alert>
        )}

        <RepositoryInput onSubmit={handleAddRepository} />

        {repositories.length === 0 && !isLoading ? (
          <EmptyState />
        ) : (
          <RepositoryTable
            repositories={repositories}
            onRowClick={handleRowClick}
            isLoading={isLoading}
          />
        )}
      </PageSection>
    </>
  );
};

// Mock data for demonstration when API is not available
function getMockRepositories(): RepositorySummary[] {
  return [
    {
      repo_url: 'https://github.com/kubeflow/model-registry',
      name: 'kubeflow/model-registry',
      primary_language: 'Go',
      overall_score: 47.9,
      last_assessed: new Date().toISOString(),
    },
    {
      repo_url: 'file:///Users/ykrimerm/hackthon1/ship-shape',
      name: 'ship-shape',
      primary_language: 'Python',
      overall_score: 86.3,
      last_assessed: new Date().toISOString(),
    },
  ];
}
