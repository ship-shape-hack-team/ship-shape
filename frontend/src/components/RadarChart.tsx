/**
 * Radar chart component for visualizing quality dimensions
 */

import React from 'react';
import {
  Chart,
  ChartArea,
  ChartAxis,
  ChartGroup,
} from '@patternfly/react-charts';
import { Card, CardBody, CardTitle } from '@patternfly/react-core';
import { AssessorResult } from '../types';
import { formatAssessorName } from '../types';

interface RadarChartProps {
  assessorResults: AssessorResult[];
  repositoryName: string;
}

export const RadarChart: React.FC<RadarChartProps> = ({
  assessorResults,
  repositoryName,
}) => {
  // Transform assessor results into chart data
  const dimensions = assessorResults.map(result => ({
    name: formatAssessorName(result.assessor_name),
    score: result.score,
  }));

  // PatternFly Charts uses Victory, which doesn't have built-in radar
  // We'll use a simple visualization instead
  return (
    <Card>
      <CardTitle style={{ color: '#151515' }}>Quality Dimensions (Bar View)</CardTitle>
      <CardBody>
        <div style={{ padding: '2rem' }}>
          {dimensions.map((dim, index) => {
            const percentage = dim.score;
            const color = percentage >= 75 ? '#3E8635' : percentage >= 60 ? '#F0AB00' : '#C9190B';

            return (
              <div key={index} style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 500, color: '#151515' }}>{dim.name}</span>
                  <span style={{ fontWeight: 'bold', color }}>{percentage.toFixed(1)}/100</span>
                </div>
                <div
                  style={{
                    width: '100%',
                    height: '20px',
                    backgroundColor: '#f0f0f0',
                    borderRadius: '4px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${percentage}%`,
                      height: '100%',
                      backgroundColor: color,
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </CardBody>
    </Card>
  );
};
