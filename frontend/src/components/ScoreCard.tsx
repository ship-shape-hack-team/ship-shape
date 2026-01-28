/**
 * Score card component for displaying quality scores
 */

import React from 'react';
import { Card, CardBody, CardTitle } from '@patternfly/react-core';
import { getScoreColor } from '../types';

interface ScoreCardProps {
  title: string;
  score: number;
  subtitle?: string;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ title, score, subtitle }) => {
  const color = getScoreColor(score);

  return (
    <Card isCompact>
      <CardTitle style={{ color: '#151515' }}>{title}</CardTitle>
      <CardBody>
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              fontSize: '3rem',
              fontWeight: 'bold',
              color: color,
              lineHeight: 1,
            }}
          >
            {score.toFixed(1)}
          </div>
          <div style={{ fontSize: '1.2rem', color: '#6a6e73' }}>/100</div>
          {subtitle && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#6a6e73' }}>
              {subtitle}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
};
