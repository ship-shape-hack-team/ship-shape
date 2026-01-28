/**
 * Empty state component for when no assessments have been run
 */

import React from 'react';
import {
  EmptyState as PFEmptyState,
  EmptyStateIcon,
  EmptyStateBody,
  Title,
  Button,
} from '@patternfly/react-core';
import { CubesIcon } from '@patternfly/react-icons';

interface EmptyStateProps {
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onAction }) => {
  return (
    <PFEmptyState>
      <EmptyStateIcon icon={CubesIcon} />
      <Title headingLevel="h1" size="lg">
        No Repositories Assessed
      </Title>
      <EmptyStateBody>
        Get started by adding a repository URL in the input field above.
        The system will automatically assess the repository's quality across multiple dimensions.
      </EmptyStateBody>
      {onAction && (
        <Button variant="primary" onClick={onAction}>
          Get Started
        </Button>
      )}
    </PFEmptyState>
  );
};
