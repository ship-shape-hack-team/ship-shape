/**
 * Repository table component displaying all scanned repositories with scores
 */

import React, { useState } from 'react';
import {
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
} from '@patternfly/react-table';
import {
  EmptyState,
  EmptyStateIcon,
  EmptyStateBody,
  Title,
  Label,
} from '@patternfly/react-core';
import { CubesIcon } from '@patternfly/react-icons';
import { RepositorySummary } from '../types';
import { getScoreColor, getPerformanceTier } from '../types';
import { TrendIcon } from './TrendIcon';
import { TrendModal } from './TrendModal';

interface RepositoryTableProps {
  repositories: RepositorySummary[];
  onRowClick: (repo: RepositorySummary) => void;
  onTrendClick: (repo: RepositorySummary) => void;
  historicalData: Record<string, any[]>;
  isLoading?: boolean;
}

export const RepositoryTable: React.FC<RepositoryTableProps> = ({
  repositories,
  onRowClick,
  onTrendClick,
  historicalData,
  isLoading = false,
}) => {
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null);

  const handleTrendClick = (repo: RepositorySummary) => (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    setSelectedRepo(repo.repo_url);
  };

  const handleCloseModal = () => {
    setSelectedRepo(null);
  };
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <p>Loading repositories...</p>
      </div>
    );
  }

  if (repositories.length === 0) {
    return (
      <EmptyState>
        <EmptyStateIcon icon={CubesIcon} />
        <Title headingLevel="h4" size="lg">
          No repositories assessed yet
        </Title>
        <EmptyStateBody>
          Add a repository using the input field above to begin quality assessment.
        </EmptyStateBody>
      </EmptyState>
    );
  }

  const selectedRepoData = selectedRepo 
    ? repositories.find(r => r.repo_url === selectedRepo) 
    : null;
  const selectedHistory = selectedRepo ? historicalData[selectedRepo] || [] : [];

  return (
    <>
      <Table aria-label="Repositories table" variant="compact">
        <Thead>
          <Tr>
            <Th>Repository</Th>
            <Th>Language</Th>
            <Th>Overall Score</Th>
            <Th>Tier</Th>
            <Th>6-Month Trend</Th>
            <Th>Last Assessed</Th>
          </Tr>
        </Thead>
      <Tbody>
        {repositories.map(repo => {
          const score = repo.overall_score || 0;
          const tier = getPerformanceTier(score);
          const scoreColor = getScoreColor(score);

          return (
            <Tr
              key={repo.repo_url}
              onClick={() => onRowClick(repo)}
              style={{ cursor: 'pointer' }}
            >
              <Td dataLabel="Repository">
                <strong style={{ color: '#151515' }}>{repo.name}</strong>
                <div style={{ fontSize: '0.9em', color: '#6a6e73' }}>{repo.repo_url}</div>
              </Td>
              <Td dataLabel="Language">
                <span style={{ color: '#151515' }}>{repo.primary_language || 'Unknown'}</span>
              </Td>
              <Td dataLabel="Overall Score">
                <span style={{ fontSize: '1.2em', fontWeight: 'bold', color: scoreColor }}>
                  {score.toFixed(1)}
                </span>
                <span style={{ color: '#6a6e73' }}>/100</span>
              </Td>
              <Td dataLabel="Tier">
                <Label color={scoreColor as any}>{tier}</Label>
              </Td>
              <Td dataLabel="6-Month Trend">
                {historicalData[repo.repo_url] && historicalData[repo.repo_url].length > 1 ? (
                  <TrendIcon
                    trend={calculateTrend(historicalData[repo.repo_url])}
                    onClick={handleTrendClick(repo)}
                  />
                ) : (
                  <TrendIcon trend="no_data" onClick={handleTrendClick(repo)} />
                )}
              </Td>
              <Td dataLabel="Last Assessed">
                {repo.last_assessed
                  ? new Date(repo.last_assessed).toLocaleDateString()
                  : 'Never'}
              </Td>
            </Tr>
          );
        })}
      </Tbody>
    </Table>

    {selectedRepo && selectedRepoData && (
      <TrendModal
        isOpen={true}
        onClose={handleCloseModal}
        repositoryName={selectedRepoData.name}
        assessments={selectedHistory}
      />
    )}
  </>
  );
};

// Helper function to calculate trend from historical data
function calculateTrend(assessments: any[]): 'improving' | 'declining' | 'stable' | 'no_data' {
  if (assessments.length < 2) return 'no_data';

  const sorted = [...assessments].sort((a, b) => 
    new Date(a.started_at).getTime() - new Date(b.started_at).getTime()
  );

  const firstScore = sorted[0].overall_score;
  const lastScore = sorted[sorted.length - 1].overall_score;
  const change = lastScore - firstScore;

  if (change > 5) return 'improving';
  if (change < -5) return 'declining';
  return 'stable';
}
