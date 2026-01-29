/**
 * Bar chart component for visualizing quality dimensions
 */

import React from 'react';
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
  // Transform assessor results into chart data (with null safety)
  const dimensions = (assessorResults || []).map(result => ({
    name: formatAssessorName(result.assessor_name),
    score: result.score ?? 0,
    result: result.result,
  }));

  // Calculate averages
  const avgScore = dimensions.length > 0 
    ? dimensions.reduce((sum, d) => sum + d.score, 0) / dimensions.length 
    : 0;
  const passCount = dimensions.filter(d => d.result === 'pass' || d.score >= 70).length;

  return (
    <Card style={{ height: '100%' }}>
      <CardTitle style={{ color: '#151515', fontWeight: 600 }}>
        📈 Quality Dimensions
      </CardTitle>
      <CardBody style={{ display: 'flex', flexDirection: 'column', minHeight: '420px' }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem 0' }}>
          {dimensions.map((dim, index) => {
            const percentage = dim.score;
            const color = percentage >= 75 ? '#3E8635' : percentage >= 60 ? '#F0AB00' : '#C9190B';
            const bgColor = percentage >= 75 ? 'rgba(62, 134, 53, 0.1)' : percentage >= 60 ? 'rgba(240, 171, 0, 0.1)' : 'rgba(201, 25, 11, 0.1)';

            return (
              <div 
                key={index} 
                style={{ 
                  marginBottom: '0.75rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '6px',
                  backgroundColor: bgColor,
                  border: `1px solid ${color}20`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ 
                    fontWeight: 500, 
                    color: '#151515', 
                    fontSize: '0.85rem',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    maxWidth: '70%',
                  }}>
                    {dim.name}
                  </span>
                  <span style={{ fontWeight: 'bold', color, fontSize: '0.85rem' }}>
                    {percentage.toFixed(0)}
                  </span>
                </div>
                <div
                  style={{
                    width: '100%',
                    height: '6px',
                    backgroundColor: '#e8e8e8',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${percentage}%`,
                      height: '100%',
                      backgroundColor: color,
                      transition: 'width 0.3s ease',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        
        <div style={{ 
          marginTop: 'auto',
          paddingTop: '0.75rem', 
          borderTop: '1px solid #e8e8e8',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.85rem',
          color: '#6a6e73'
        }}>
          <span>✅ Passing: <strong style={{ color: '#3E8635' }}>{passCount}/{dimensions.length}</strong></span>
          <span>Avg: <strong style={{ color: avgScore >= 70 ? '#3E8635' : '#C9190B' }}>{avgScore.toFixed(0)}</strong></span>
        </div>
      </CardBody>
    </Card>
  );
};
