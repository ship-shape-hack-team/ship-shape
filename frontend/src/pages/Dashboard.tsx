/**
 * Dashboard page - main landing page with repository input and table
 */

import React, { useState, useEffect } from 'react';
import {
  PageSection,
  Title,
  Alert,
  AlertVariant,
  Card,
  CardBody,
  CardTitle,
} from '@patternfly/react-core';
import { useNavigate } from 'react-router-dom';
import { RepositoryInput } from '../components/RepositoryInput';
import { RepositoryTable } from '../components/RepositoryTable';
import { EmptyState } from '../components/EmptyState';
import { RepositorySummary } from '../types';
import apiClient from '../services/api';
import { usePollRepositories } from '../hooks/usePollRepositories';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Use polling hook for automatic updates
  const { repositories, isLoading, error, refresh, hasInProgressAssessments } = usePollRepositories({
    pollingInterval: 3000, // Poll every 3 seconds
    enabled: true,
  });

  const [historicalData, setHistoricalData] = useState<Record<string, any[]>>({});
  const [reassessingRepos, setReassessingRepos] = useState<Set<string>>(new Set());

  // Calculate stats
  const totalRepos = repositories.length;
  const avgScore = totalRepos > 0 
    ? repositories.reduce((sum, r) => sum + (r.overall_score || 0), 0) / totalRepos 
    : 0;
  const passingRepos = repositories.filter(r => (r.overall_score || 0) >= 70).length;
  const needsWorkRepos = repositories.filter(r => (r.overall_score || 0) < 70 && r.overall_score !== null).length;

  // Load historical data when repositories change
  useEffect(() => {
    const loadHistoricalData = async () => {
      const historical: Record<string, any[]> = {};
      for (const repo of repositories) {
        try {
          const history = await apiClient.getRepositoryAssessments(repo.repo_url, 50);
          historical[repo.repo_url] = history.assessments || [];
        } catch (err) {
          console.error(`Failed to load history for ${repo.name}:`, err);
          historical[repo.repo_url] = [];
        }
      }
      setHistoricalData(historical);
    };

    if (repositories.length > 0) {
      loadHistoricalData();
    }
  }, [repositories]);

  const handleAddRepository = async (repoUrl: string) => {
    await apiClient.createRepository(repoUrl, true);

    // Refresh repositories immediately
    await refresh();
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
          await refresh();

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

      // Stop reassessing indicator after 30 seconds regardless
      setTimeout(() => {
        setReassessingRepos(prev => {
          const next = new Set(prev);
          next.delete(repo.repo_url);
          return next;
        });
      }, 30000);

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

  const handleDelete = async (repo: RepositorySummary) => {
    try {
      await apiClient.deleteRepository(repo.repo_url);

      // Refresh repositories to remove deleted repo from UI
      await refresh();
    } catch (err) {
      console.error('Failed to delete repository:', err);
      alert('Failed to delete repository. Please try again.');
    }
  };

  return (
    <>
      {/* Hero Header */}
      <PageSection variant="light" style={{ paddingTop: '2rem', paddingBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '2.5rem' }}>🚢</span>
          <div>
            <Title headingLevel="h1" size="2xl" style={{ color: '#C9190B', margin: 0, fontWeight: 700 }}>
              Quality Profiling Dashboard
            </Title>
            <p style={{ marginTop: '0.5rem', color: '#6a6e73', marginBottom: 0 }}>
              Assess and compare repository quality across multiple dimensions
            </p>
          </div>
        </div>
      </PageSection>

      <PageSection style={{ paddingTop: '1.5rem' }}>
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

        {hasInProgressAssessments && (
          <Alert
            variant={AlertVariant.info}
            title="Assessments in Progress"
            isInline
            style={{ marginBottom: '1rem' }}
          >
            Some assessments are currently running. The table will automatically update when they complete.
          </Alert>
        )}

        {/* Stats Cards */}
        {repositories.length > 0 && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(4, 1fr)', 
            gap: '1rem', 
            marginBottom: '1.5rem' 
          }}>
            <Card style={{ textAlign: 'center', overflow: 'hidden' }}>
              <CardBody style={{ padding: '1rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0066CC' }}>
                  {totalRepos}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6a6e73', marginTop: '0.25rem' }}>
                  📊 Total Repositories
                </div>
              </CardBody>
            </Card>
            <Card style={{ textAlign: 'center', overflow: 'hidden' }}>
              <CardBody style={{ padding: '1rem' }}>
                <div style={{ 
                  fontSize: '2rem', 
                  fontWeight: 'bold', 
                  color: avgScore >= 70 ? '#3E8635' : avgScore >= 50 ? '#F0AB00' : '#C9190B' 
                }}>
                  {avgScore.toFixed(0)}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6a6e73', marginTop: '0.25rem' }}>
                  ⭐ Average Score
                </div>
              </CardBody>
            </Card>
            <Card style={{ textAlign: 'center', overflow: 'hidden' }}>
              <CardBody style={{ padding: '1rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3E8635' }}>
                  {passingRepos}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6a6e73', marginTop: '0.25rem' }}>
                  ✅ Passing (70+)
                </div>
              </CardBody>
            </Card>
            <Card style={{ textAlign: 'center', overflow: 'hidden' }}>
              <CardBody style={{ padding: '1rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#C9190B' }}>
                  {needsWorkRepos}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6a6e73', marginTop: '0.25rem' }}>
                  ⚠️ Needs Work
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Add Repository Card */}
        <Card style={{ marginBottom: '1.5rem' }}>
          <CardTitle style={{ color: '#151515', fontWeight: 600 }}>
            ➕ Add Repository
          </CardTitle>
          <CardBody>
            <RepositoryInput onSubmit={handleAddRepository} />
          </CardBody>
        </Card>

        {/* Repository List */}
        {repositories.length === 0 && !isLoading ? (
          <EmptyState />
        ) : (
          <Card>
            <CardTitle style={{ color: '#151515', fontWeight: 600 }}>
              📋 Repositories ({repositories.length})
            </CardTitle>
            <CardBody style={{ padding: 0 }}>
              <RepositoryTable
                repositories={repositories}
                onRowClick={handleRowClick}
                onTrendClick={() => {}}
                onReassess={handleReassess}
                onDelete={handleDelete}
                historicalData={historicalData}
                isLoading={isLoading}
                reassessingRepos={reassessingRepos}
              />
            </CardBody>
          </Card>
        )}
      </PageSection>
    </>
  );
};
