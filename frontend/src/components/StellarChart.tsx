/**
 * Stellar/Star chart component for visualizing quality dimensions in a radial star pattern
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
  const size = 400;
  const center = size / 2;
  const radius = size / 2 - 60;

  // Prepare data points
  const dataPoints = assessorResults.map((result, index) => {
    const angle = (index / assessorResults.length) * 2 * Math.PI - Math.PI / 2;
    const score = result.score / 100; // Normalize to 0-1

    return {
      name: formatAssessorName(result.assessor_name),
      score: result.score,
      normalizedScore: score,
      angle: angle,
      x: center + Math.cos(angle) * radius * score,
      y: center + Math.sin(angle) * radius * score,
      labelX: center + Math.cos(angle) * (radius + 40),
      labelY: center + Math.sin(angle) * (radius + 40),
    };
  });

  // Generate star path
  const starPath = dataPoints.map((point, index) => {
    const command = index === 0 ? 'M' : 'L';
    return `${command} ${point.x} ${point.y}`;
  }).join(' ') + ' Z';

  // Generate reference circles
  const referenceCircles = [25, 50, 75, 100].map(percent => {
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
        strokeDasharray={percent === 100 ? "none" : "4,4"}
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
      stroke="#d0d0d0"
      strokeWidth="1"
    />
  ));

  // Determine fill color based on average score
  const avgScore = dataPoints.reduce((sum, p) => sum + p.score, 0) / dataPoints.length;
  const fillColor = avgScore >= 75 ? 'rgba(62, 134, 53, 0.3)' : 
                    avgScore >= 60 ? 'rgba(240, 171, 0, 0.3)' : 
                    'rgba(201, 25, 11, 0.3)';
  
  const strokeColor = avgScore >= 75 ? '#3E8635' : 
                      avgScore >= 60 ? '#F0AB00' : 
                      '#C9190B';

  return (
    <Card>
      <CardTitle>Quality Stellar Chart for {repositoryName}</CardTitle>
      <CardBody>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
            {/* Reference circles */}
            {referenceCircles}

            {/* Axis lines */}
            {axisLines}

            {/* Reference circle labels */}
            <text x={center + 5} y={center - radius} fontSize="10" fill="#999" textAnchor="middle">
              100
            </text>
            <text x={center + 5} y={center - radius * 0.75} fontSize="10" fill="#999" textAnchor="middle">
              75
            </text>
            <text x={center + 5} y={center - radius * 0.5} fontSize="10" fill="#999" textAnchor="middle">
              50
            </text>
            <text x={center + 5} y={center - radius * 0.25} fontSize="10" fill="#999" textAnchor="middle">
              25
            </text>

            {/* Data star */}
            <path
              d={starPath}
              fill={fillColor}
              stroke={strokeColor}
              strokeWidth="2"
            />

            {/* Data points */}
            {dataPoints.map((point, index) => (
              <circle
                key={index}
                cx={point.x}
                cy={point.y}
                r="4"
                fill={strokeColor}
              />
            ))}

            {/* Labels */}
            {dataPoints.map((point, index) => {
              // Adjust text anchor based on position
              const textAnchor = 
                point.labelX > center + 10 ? 'start' :
                point.labelX < center - 10 ? 'end' :
                'middle';

              return (
                <g key={index}>
                  <text
                    x={point.labelX}
                    y={point.labelY}
                    fontSize="12"
                    fontWeight="500"
                    fill="#151515"
                    textAnchor={textAnchor}
                    dominantBaseline="middle"
                  >
                    {point.name}
                  </text>
                  <text
                    x={point.labelX}
                    y={point.labelY + 14}
                    fontSize="11"
                    fill="#6a6e73"
                    textAnchor={textAnchor}
                    dominantBaseline="middle"
                  >
                    {point.score.toFixed(1)}
                  </text>
                </g>
              );
            })}

            {/* Center point */}
            <circle cx={center} cy={center} r="3" fill="#151515" />
          </svg>
        </div>

        {/* Legend */}
        <div style={{ marginTop: '1rem', textAlign: 'center', color: '#6a6e73', fontSize: '0.9em' }}>
          <strong style={{ color: '#151515' }}>Average Score:</strong> {avgScore.toFixed(1)}/100
        </div>
      </CardBody>
    </Card>
  );
};
