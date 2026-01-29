/**
 * Repository table component displaying all scanned repositories with scores
 */

import React, { useState } from 'react';

type SortColumn = 'name' | 'language' | 'status' | 'score' | 'tier' | 'trend' | 'last_assessed';
type SortDirection = 'asc' | 'desc';
import {
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
} from '@patternfly/react-table';
import {
  Label,
  Button,
  Spinner,
} from '@patternfly/react-core';
import { RedoIcon, InProgressIcon, CheckCircleIcon, ExclamationCircleIcon, TrashIcon } from '@patternfly/react-icons';
import { RepositorySummary } from '../types';
import { getScoreColor, getPerformanceTier, getStatusBadgeColor, getStatusLabel } from '../types';
import { TrendIcon } from './TrendIcon';
import { TrendModal } from './TrendModal';

interface RepositoryTableProps {
  repositories: RepositorySummary[];
  onRowClick: (repo: RepositorySummary) => void;
  onTrendClick: (repo: RepositorySummary) => void;
  onReassess: (repo: RepositorySummary) => void;
  onDelete: (repo: RepositorySummary) => void;
  historicalData: Record<string, any[]>;
  isLoading?: boolean;
  reassessingRepos?: Set<string>;
}

export const RepositoryTable: React.FC<RepositoryTableProps> = ({
  repositories,
  onRowClick,
  onTrendClick,
  onReassess,
  onDelete,
  historicalData,
  isLoading = false,
  reassessingRepos = new Set(),
}) => {
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null);
  const [sortColumn, setSortColumn] = useState<SortColumn>('score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc'); // Lowest to Highest

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (column: SortColumn) => {
    if (sortColumn === column) {
      return sortDirection === 'asc' ? ' ▲' : ' ▼';
    }
    return ' ⇅';
  };

  const handleTrendClick = (repo: RepositorySummary) => (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    setSelectedRepo(repo.repo_url);
  };

  const handleReassessClick = (repo: RepositorySummary) => (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click
    onReassess(repo);
  };

  const handleDeleteClick = (repo: RepositorySummary) => (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent row click

    // Confirm deletion
    if (window.confirm(`Are you sure you want to delete ${repo.name}? This will remove all assessment history for this repository.`)) {
      onDelete(repo);
    }
  };

  const handleCloseModal = () => {
    setSelectedRepo(null);
  };

  // Sort repositories
  const sortedRepositories = [...repositories].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    switch (sortColumn) {
      case 'name':
        aValue = a.name.toLowerCase();
        bValue = b.name.toLowerCase();
        break;
      case 'language':
        aValue = a.primary_language || 'zzz';
        bValue = b.primary_language || 'zzz';
        break;
      case 'status':
        const statusOrder = { 'pending': 0, 'running': 1, 'completed': 2, 'failed': 3, 'cancelled': 4, 'Unknown': 5 };
        aValue = statusOrder[getStatusLabel(a.assessment_status, !!a.latest_assessment_id) as keyof typeof statusOrder] || 5;
        bValue = statusOrder[getStatusLabel(b.assessment_status, !!b.latest_assessment_id) as keyof typeof statusOrder] || 5;
        break;
      case 'score':
        aValue = a.overall_score || 0;
        bValue = b.overall_score || 0;
        break;
      case 'tier':
        const tierOrder: Record<string, number> = { 'Low': 0, 'Medium': 1, 'High': 2, 'Elite': 3 };
        aValue = tierOrder[getPerformanceTier(a.overall_score || 0)] || 0;
        bValue = tierOrder[getPerformanceTier(b.overall_score || 0)] || 0;
        break;
      case 'trend':
        const aTrend = calculateTrend(historicalData[a.repo_url] || []);
        const bTrend = calculateTrend(historicalData[b.repo_url] || []);
        const trendOrder = { 'declining': 0, 'stable': 1, 'improving': 2, 'no_data': 3 };
        aValue = trendOrder[aTrend];
        bValue = trendOrder[bTrend];
        break;
      case 'last_assessed':
        aValue = a.last_assessed ? new Date(a.last_assessed).getTime() : 0;
        bValue = b.last_assessed ? new Date(b.last_assessed).getTime() : 0;
        break;
      default:
        return 0;
    }

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <p>Loading repositories...</p>
      </div>
    );
  }

  if (repositories.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#6a6e73' }}>
        No repositories to display
      </div>
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
            <Th 
              onClick={() => handleSort('status')}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              Status{getSortIcon('status')}
            </Th>
            <Th 
              onClick={() => handleSort('score')}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              Overall Score{getSortIcon('score')}
            </Th>
            <Th 
              onClick={() => handleSort('tier')}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              Tier{getSortIcon('tier')}
            </Th>
            <Th 
              onClick={() => handleSort('trend')}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              6-Month Trend{getSortIcon('trend')}
            </Th>
            <Th 
              onClick={() => handleSort('last_assessed')}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              Last Assessed{getSortIcon('last_assessed')}
            </Th>
            <Th modifier="fitContent">Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {sortedRepositories.map(repo => {
            const score = repo.overall_score || 0;
            const tier = getPerformanceTier(score);
            const scoreColor = getScoreColor(score);
            const statusColor = getStatusBadgeColor(repo.assessment_status);
            const statusLabel = getStatusLabel(repo.assessment_status, !!repo.latest_assessment_id);
            const isInProgress = repo.assessment_status === 'pending' ||
                                 repo.assessment_status === 'running' ||
                                 (repo.assessment_status === null && !repo.latest_assessment_id);

            return (
              <Tr
                key={repo.repo_url}
                onClick={() => onRowClick(repo)}
                style={{ 
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = ''}
              >
                <Td dataLabel="Repository">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {isInProgress && <Spinner size="md" />}
                    <div>
                      <strong style={{ color: '#151515' }}>{repo.name}</strong>
                      <div style={{ fontSize: '0.9em', color: '#6a6e73' }}>{repo.repo_url}</div>
                    </div>
                  </div>
                </Td>
                <Td dataLabel="Language">
                  <span style={{ color: '#151515' }}>{repo.primary_language || 'Unknown'}</span>
                </Td>
                <Td dataLabel="Status">
                  <Label
                    color={statusColor as any}
                    icon={
                      repo.assessment_status === 'running' ? <InProgressIcon /> :
                      repo.assessment_status === 'completed' ? <CheckCircleIcon /> :
                      repo.assessment_status === 'failed' ? <ExclamationCircleIcon /> :
                      undefined
                    }
                  >
                    {statusLabel}
                  </Label>
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
                <Td dataLabel="Actions" modifier="fitContent">
                  <Button
                    variant="link"
                    size="sm"
                    onClick={handleReassessClick(repo)}
                    isDisabled={reassessingRepos.has(repo.repo_url)}
                    aria-label={`Reassess ${repo.name}`}
                    icon={reassessingRepos.has(repo.repo_url) ? <Spinner size="sm" /> : <RedoIcon />}
                    isInline
                  />
                  <Button
                    variant="link"
                    size="sm"
                    onClick={handleDeleteClick(repo)}
                    aria-label={`Delete ${repo.name}`}
                    icon={<TrashIcon />}
                    isDanger
                    isInline
                  />
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
