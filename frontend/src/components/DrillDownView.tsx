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

// Helper function to format metrics as bullet points
function formatMetricsAsBullets(metrics: Record<string, any>): string[] {
  const bullets: string[] = [];

  // Add other metrics as key-value pairs (skip evidence and status)
  Object.entries(metrics).forEach(([key, value]) => {
    if (key === 'evidence' || key === 'status') return; // Skip these
    
    if (typeof value === 'boolean') {
      bullets.push(`${formatKey(key)}: ${value ? '✓ Yes' : '✗ No'}`);
    } else if (typeof value === 'number') {
      bullets.push(`${formatKey(key)}: ${value}`);
    } else if (typeof value === 'string') {
      bullets.push(`${formatKey(key)}: ${value}`);
    } else if (typeof value === 'object' && value !== null) {
      // For nested objects, flatten one level
      Object.entries(value).forEach(([subKey, subValue]) => {
        bullets.push(`${formatKey(key)} - ${formatKey(subKey)}: ${subValue}`);
      });
    }
  });

  return bullets.length > 0 ? bullets : ['No detailed metrics available'];
}

function formatKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const DrillDownView: React.FC<DrillDownViewProps> = ({ assessorResult }) => {
  const color = getScoreColor(assessorResult.score);

  return (
    <Card>
      <CardTitle style={{ color: '#151515' }}>{formatAssessorName(assessorResult.assessor_name)}</CardTitle>
      <CardBody>
        <div style={{ marginBottom: '1rem' }}>
          <span style={{ fontSize: '2rem', fontWeight: 'bold', color }}>
            {assessorResult.score.toFixed(1)}
          </span>
          <span style={{ fontSize: '1.2rem', color: '#666' }}>/100</span>
        </div>

        <DescriptionList isHorizontal>
          <DescriptionListGroup>
            <DescriptionListTerm style={{ color: '#151515' }}>Status</DescriptionListTerm>
            <DescriptionListDescription style={{ color: '#151515' }}>
              {assessorResult.status.toUpperCase()}
            </DescriptionListDescription>
          </DescriptionListGroup>

          <DescriptionListGroup>
            <DescriptionListTerm style={{ color: '#151515' }}>Executed At</DescriptionListTerm>
            <DescriptionListDescription style={{ color: '#6a6e73' }}>
              {new Date(assessorResult.executed_at).toLocaleString()}
            </DescriptionListDescription>
          </DescriptionListGroup>

          {assessorResult.metrics.evidence && (
            <DescriptionListGroup>
              <DescriptionListTerm style={{ color: '#151515' }}>Evidence</DescriptionListTerm>
              <DescriptionListDescription>
                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#151515' }}>
                  {assessorResult.metrics.evidence.split('|').map((item: string, idx: number) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>
                      {item.trim()}
                    </li>
                  ))}
                </ul>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}

          {Object.keys(assessorResult.metrics).filter(k => k !== 'evidence' && k !== 'status').length > 0 && (
            <DescriptionListGroup>
              <DescriptionListTerm style={{ color: '#151515' }}>Additional Metrics</DescriptionListTerm>
              <DescriptionListDescription>
                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#151515' }}>
                  {formatMetricsAsBullets(assessorResult.metrics).map((item, idx) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>
                      {item}
                    </li>
                  ))}
                </ul>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
        </DescriptionList>
      </CardBody>
    </Card>
  );
};
