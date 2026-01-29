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
  const size = 600;
  const center = size / 2;
  const radius = 150; // Smaller radius to leave more room for labels

  // Prepare data points (with null safety)
  const results = assessorResults || [];
  const dataPoints = results.map((result, index) => {
    const angle = (index / (results.length || 1)) * 2 * Math.PI - Math.PI / 2;
    const scoreValue = result.score ?? 0;
    const score = scoreValue / 100; // Normalize to 0-1

    return {
      name: formatAssessorName(result.assessor_name),
      score: scoreValue,
      normalizedScore: score,
      angle: angle,
      x: center + Math.cos(angle) * radius * score,
      y: center + Math.sin(angle) * radius * score,
      labelX: center + Math.cos(angle) * (radius + 100),
      labelY: center + Math.sin(angle) * (radius + 100),
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
  const avgScore = dataPoints.length > 0 
    ? dataPoints.reduce((sum, p) => sum + p.score, 0) / dataPoints.length 
    : 0;
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

              // Split long text into multiple lines if needed
              const maxCharsPerLine = 12;
              const words = point.name.split(' ');
              const lines: string[] = [];
              let currentLine = '';

              words.forEach(word => {
                if ((currentLine + word).length > maxCharsPerLine && currentLine.length > 0) {
                  lines.push(currentLine.trim());
                  currentLine = word + ' ';
                } else {
                  currentLine += word + ' ';
                }
              });
              if (currentLine) lines.push(currentLine.trim());
              
              // Limit to max 3 lines
              if (lines.length > 3) {
                lines.splice(2, lines.length - 2, lines.slice(2).join(' '));
              }

              return (
                <g key={index}>
                  {lines.map((line, lineIndex) => (
                    <text
                      key={lineIndex}
                      x={point.labelX}
                      y={point.labelY + (lineIndex - lines.length / 2 + 0.5) * 14}
                      fontSize="10"
                      fontWeight="500"
                      fill="#151515"
                      textAnchor={textAnchor}
                      dominantBaseline="middle"
                    >
                      {line}
                    </text>
                  ))}
                  <text
                    x={point.labelX}
                    y={point.labelY + (lines.length / 2 + 0.5) * 13}
                    fontSize="12"
                    fontWeight="bold"
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
