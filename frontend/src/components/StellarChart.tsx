/**
 * Stellar/Star chart component for visualizing quality dimensions
 */

import React from 'react';
import { Card, CardBody, CardTitle } from '@patternfly/react-core';
import { AssessorResult } from '../types';
import { formatAssessorName } from '../types';

interface StellarChartProps {
  assessorResults: AssessorResult[];
  repositoryName: string;
}

export const StellarChart: React.FC<StellarChartProps> = ({
  assessorResults,
  repositoryName,
}) => {
  // Larger viewBox to accommodate labels
  const size = 500;
  const center = size / 2;
  const radius = 130;
  const labelDistance = 65; // Distance from radius to labels

  // Prepare data points (with null safety)
  const results = assessorResults || [];
  const dataPoints = results.map((result, index) => {
    const angle = (index / (results.length || 1)) * 2 * Math.PI - Math.PI / 2;
    const scoreValue = result.score ?? 0;
    const score = scoreValue / 100;

    return {
      name: formatAssessorName(result.assessor_name),
      score: scoreValue,
      normalizedScore: score,
      angle: angle,
      x: center + Math.cos(angle) * radius * score,
      y: center + Math.sin(angle) * radius * score,
      labelX: center + Math.cos(angle) * (radius + labelDistance),
      labelY: center + Math.sin(angle) * (radius + labelDistance),
    };
  });

  // Generate star path
  const starPath = dataPoints.map((point, index) => {
    const command = index === 0 ? 'M' : 'L';
    return `${command} ${point.x} ${point.y}`;
  }).join(' ') + ' Z';

  // Generate reference circles
  const referenceCircles = [50, 100].map(percent => {
    const r = radius * (percent / 100);
    return (
      <circle
        key={percent}
        cx={center}
        cy={center}
        r={r}
        fill="none"
        stroke="#e0e0e0"
        strokeWidth="1"
        strokeDasharray={percent === 100 ? "none" : "3,3"}
      />
    );
  });

  // Generate axis lines
  const axisLines = dataPoints.map((point, index) => (
    <line
      key={index}
      x1={center}
      y1={center}
      x2={center + Math.cos(point.angle) * radius}
      y2={center + Math.sin(point.angle) * radius}
      stroke="#e8e8e8"
      strokeWidth="1"
    />
  ));

  // Determine fill color based on average score
  const avgScore = dataPoints.length > 0 
    ? dataPoints.reduce((sum, p) => sum + p.score, 0) / dataPoints.length 
    : 0;
  const fillColor = avgScore >= 75 ? 'rgba(62, 134, 53, 0.25)' : 
                    avgScore >= 60 ? 'rgba(240, 171, 0, 0.25)' : 
                    'rgba(201, 25, 11, 0.25)';
  
  const strokeColor = avgScore >= 75 ? '#3E8635' : 
                      avgScore >= 60 ? '#F0AB00' : 
                      '#C9190B';

  return (
    <Card style={{ height: '100%' }}>
      <CardTitle style={{ color: '#151515', fontWeight: 600 }}>
        📊 Quality Radar
      </CardTitle>
      <CardBody style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '420px' }}>
        <svg 
          width="100%" 
          height="400" 
          viewBox={`0 0 ${size} ${size}`}
          style={{ maxWidth: '500px', overflow: 'visible' }}
        >
          {/* Reference circles */}
          {referenceCircles}

          {/* Axis lines */}
          {axisLines}

          {/* Data star */}
          {dataPoints.length > 0 && (
            <path
              d={starPath}
              fill={fillColor}
              stroke={strokeColor}
              strokeWidth="2"
            />
          )}

          {/* Data points */}
          {dataPoints.map((point, index) => (
            <circle
              key={index}
              cx={point.x}
              cy={point.y}
              r="6"
              fill={strokeColor}
            />
          ))}

          {/* Labels */}
          {dataPoints.map((point, index) => {
            // Determine text anchor based on position
            const isRight = point.labelX > center + 10;
            const isLeft = point.labelX < center - 10;
            const textAnchor = isRight ? 'start' : isLeft ? 'end' : 'middle';

            // Format name - allow longer names now
            const shortName = point.name.length > 20 
              ? point.name.substring(0, 17) + '...' 
              : point.name;

            return (
              <g key={index}>
                <text
                  x={point.labelX}
                  y={point.labelY - 8}
                  fontSize="12"
                  fontWeight="500"
                  fill="#151515"
                  textAnchor={textAnchor}
                >
                  {shortName}
                </text>
                <text
                  x={point.labelX}
                  y={point.labelY + 12}
                  fontSize="14"
                  fontWeight="bold"
                  fill={strokeColor}
                  textAnchor={textAnchor}
                >
                  {point.score.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* Center point */}
          <circle cx={center} cy={center} r="4" fill="#151515" />
        </svg>

        <div style={{ marginTop: '0.5rem', textAlign: 'center', color: '#6a6e73', fontSize: '0.85rem' }}>
          Average: <strong style={{ color: strokeColor }}>{avgScore.toFixed(0)}/100</strong>
        </div>
      </CardBody>
    </Card>
  );
};
