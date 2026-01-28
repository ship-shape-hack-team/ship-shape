/**
 * Repository table component displaying all scanned repositories with scores
 */

import React from 'react';
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

interface RepositoryTableProps {
  repositories: RepositorySummary[];
  onRowClick: (repo: RepositorySummary) => void;
  isLoading?: boolean;
}

export const RepositoryTable: React.FC<RepositoryTableProps> = ({
  repositories,
  onRowClick,
  isLoading = false,
}) => {
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

  return (
    <Table aria-label="Repositories table" variant="compact">
      <Thead>
        <Tr>
          <Th>Repository</Th>
          <Th>Language</Th>
          <Th>Overall Score</Th>
          <Th>Tier</Th>
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
              isHoverable
              isClickable
              onRowClick={() => onRowClick(repo)}
              style={{ cursor: 'pointer' }}
            >
              <Td dataLabel="Repository">
                <strong>{repo.name}</strong>
                <div style={{ fontSize: '0.9em', color: '#666' }}>{repo.repo_url}</div>
              </Td>
              <Td dataLabel="Language">{repo.primary_language || 'Unknown'}</Td>
              <Td dataLabel="Overall Score">
                <span style={{ fontSize: '1.2em', fontWeight: 'bold', color: scoreColor }}>
                  {score.toFixed(1)}
                </span>
                <span style={{ color: '#666' }}>/100</span>
              </Td>
              <Td dataLabel="Tier">
                <Label color={scoreColor as any}>{tier}</Label>
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
  );
};
