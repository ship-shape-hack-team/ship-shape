/**
 * Drill-down view component for detailed assessor results
 */

import React from 'react';
import {
  Card,
  CardBody,
  CardTitle,
  DescriptionList,
  DescriptionListGroup,
  DescriptionListTerm,
  DescriptionListDescription,
} from '@patternfly/react-core';
import { AssessorResult } from '../types';
import { formatAssessorName, getScoreColor } from '../types';

interface DrillDownViewProps {
  assessorResult: AssessorResult;
}

export const DrillDownView: React.FC<DrillDownViewProps> = ({ assessorResult }) => {
  const color = getScoreColor(assessorResult.score);

  return (
    <Card>
      <CardTitle>{formatAssessorName(assessorResult.assessor_name)}</CardTitle>
      <CardBody>
        <div style={{ marginBottom: '1rem' }}>
          <span style={{ fontSize: '2rem', fontWeight: 'bold', color }}>
            {assessorResult.score.toFixed(1)}
          </span>
          <span style={{ fontSize: '1.2rem', color: '#666' }}>/100</span>
        </div>

        <DescriptionList isHorizontal>
          <DescriptionListGroup>
            <DescriptionListTerm>Status</DescriptionListTerm>
            <DescriptionListDescription>
              {assessorResult.status.toUpperCase()}
            </DescriptionListDescription>
          </DescriptionListGroup>

          <DescriptionListGroup>
            <DescriptionListTerm>Executed At</DescriptionListTerm>
            <DescriptionListDescription>
              {new Date(assessorResult.executed_at).toLocaleString()}
            </DescriptionListDescription>
          </DescriptionListGroup>

          {assessorResult.metrics.evidence && (
            <DescriptionListGroup>
              <DescriptionListTerm>Evidence</DescriptionListTerm>
              <DescriptionListDescription>
                {assessorResult.metrics.evidence}
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}

          {Object.keys(assessorResult.metrics).length > 0 && (
            <DescriptionListGroup>
              <DescriptionListTerm>Metrics</DescriptionListTerm>
              <DescriptionListDescription>
                <pre style={{ fontSize: '0.9em', backgroundColor: '#f5f5f5', padding: '0.5rem', borderRadius: '4px' }}>
                  {JSON.stringify(assessorResult.metrics, null, 2)}
                </pre>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
        </DescriptionList>
      </CardBody>
    </Card>
  );
};
