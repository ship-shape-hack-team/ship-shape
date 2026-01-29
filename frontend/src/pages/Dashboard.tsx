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
  const [reassessingRepos, setReassessingRepos] = useState<Set<string>>(new Set());

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

  const handleReassess = async (repo: RepositorySummary) => {
    // Add to reassessing set
    setReassessingRepos(prev => new Set(prev).add(repo.repo_url));
    
    try {
      await apiClient.reassessRepository(repo.repo_url);
      
      // Poll for completion (simple approach - check every 5 seconds for 5 minutes)
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes
      const pollInterval = 5000; // 5 seconds
      
      const pollForCompletion = setInterval(async () => {
        attempts++;
        
        try {
          // Reload repositories to get updated assessment
          const data = await apiClient.listRepositories({
            limit: 100,
            sort_by: 'last_assessed',
            order: 'desc',
          });
          
          const updatedRepo = data.repositories.find((r: RepositorySummary) => r.repo_url === repo.repo_url);
          
          // Check if last_assessed has been updated (comparing dates)
          if (updatedRepo && updatedRepo.last_assessed !== repo.last_assessed) {
            clearInterval(pollForCompletion);
            setReassessingRepos(prev => {
              const next = new Set(prev);
              next.delete(repo.repo_url);
              return next;
            });
            await loadRepositories();
          }
          
          if (attempts >= maxAttempts) {
            clearInterval(pollForCompletion);
            setReassessingRepos(prev => {
              const next = new Set(prev);
              next.delete(repo.repo_url);
              return next;
            });
            console.log('Polling timeout - assessment may still be in progress');
          }
        } catch (err) {
          console.error('Error polling for assessment completion:', err);
        }
      }, pollInterval);
      
    } catch (err) {
      console.error('Failed to trigger reassessment:', err);
      setReassessingRepos(prev => {
        const next = new Set(prev);
        next.delete(repo.repo_url);
        return next;
      });
      alert('Failed to trigger reassessment. Please try again.');
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
            onReassess={handleReassess}
            historicalData={historicalData}
            isLoading={isLoading}
            reassessingRepos={reassessingRepos}
          />
        )}
      </PageSection>
    </>
  );
};

