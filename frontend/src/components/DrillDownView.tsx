/**
 * Drill-down view component for detailed assessor results
 */

import React from 'react';
import {
  Card,
  CardBody,
  CardTitle,
} from '@patternfly/react-core';
import { AssessorResult } from '../types';
import { formatAssessorName, getScoreColor } from '../types';

interface DrillDownViewProps {
  assessorResult: AssessorResult;
}

// Helper function to format metrics as bullet points
function formatMetricsAsBullets(metrics: Record<string, any>): string[] {
  const bullets: string[] = [];

  Object.entries(metrics).forEach(([key, value]) => {
    if (key === 'evidence' || key === 'status') return;
    
    if (typeof value === 'boolean') {
      bullets.push(`${formatKey(key)}: ${value ? '✓ Yes' : '✗ No'}`);
    } else if (typeof value === 'number') {
      bullets.push(`${formatKey(key)}: ${value}`);
    } else if (typeof value === 'string') {
      bullets.push(`${formatKey(key)}: ${value}`);
    } else if (typeof value === 'object' && value !== null) {
      Object.entries(value).forEach(([subKey, subValue]) => {
        bullets.push(`${formatKey(key)} - ${formatKey(subKey)}: ${subValue}`);
      });
    }
  });

  return bullets;
}

function formatKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const DrillDownView: React.FC<DrillDownViewProps> = ({ assessorResult }) => {
  const score = assessorResult.score ?? 0;
  const color = getScoreColor(score);
  const resultStatus = assessorResult.result;
  
  const statusConfig = {
    pass: { icon: '✅', label: 'PASS', color: '#3e8635', bg: 'rgba(62, 134, 53, 0.08)' },
    fail: { icon: '❌', label: 'FAIL', color: '#c9190b', bg: 'rgba(201, 25, 11, 0.08)' },
    not_applicable: { icon: '⏭️', label: 'N/A', color: '#6a6e73', bg: 'rgba(106, 110, 115, 0.08)' },
  };
  
  const status = statusConfig[resultStatus as keyof typeof statusConfig] || statusConfig.fail;

  const evidence = assessorResult.metrics?.evidence;
  const evidenceList = evidence 
    ? (Array.isArray(evidence) ? evidence : String(evidence).split('|').map(s => s.trim()))
    : [];
  
  const additionalMetrics = formatMetricsAsBullets(assessorResult.metrics || {});

  return (
    <Card style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardTitle style={{ 
        color: '#151515', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        fontWeight: 600,
      }}>
        <span style={{ fontSize: '0.95rem' }}>
          {formatAssessorName(assessorResult.assessor_name)}
        </span>
        <span style={{ 
          fontSize: '0.75rem', 
          padding: '0.25rem 0.5rem', 
          borderRadius: '4px',
          backgroundColor: status.bg,
          color: status.color,
          fontWeight: 600,
        }}>
          {status.icon} {status.label}
        </span>
      </CardTitle>
      <CardBody style={{ flex: 1, display: 'flex', flexDirection: 'column', paddingTop: '0.5rem' }}>
        {/* Score Display */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'baseline', 
          marginBottom: '1rem',
          paddingBottom: '0.75rem',
          borderBottom: '1px solid #e8e8e8',
        }}>
          <span style={{ fontSize: '2rem', fontWeight: 'bold', color }}>
            {score.toFixed(0)}
          </span>
          <span style={{ fontSize: '1rem', color: '#6a6e73', marginLeft: '0.25rem' }}>/100</span>
          
          {/* Progress bar */}
          <div style={{ 
            flex: 1, 
            marginLeft: '1rem', 
            height: '8px', 
            backgroundColor: '#e8e8e8', 
            borderRadius: '4px',
            overflow: 'hidden',
          }}>
            <div style={{ 
              width: `${score}%`, 
              height: '100%', 
              backgroundColor: color,
              borderRadius: '4px',
              transition: 'width 0.3s ease',
            }} />
          </div>
        </div>

        {/* Evidence Section */}
        {evidenceList.length > 0 && (
          <div style={{ marginBottom: '0.75rem' }}>
            <div style={{ fontSize: '0.8rem', color: '#6a6e73', marginBottom: '0.35rem', fontWeight: 500 }}>
              Evidence
            </div>
            <ul style={{ 
              margin: 0, 
              paddingLeft: '1.25rem', 
              fontSize: '0.85rem',
              color: '#151515',
              maxHeight: '100px',
              overflowY: 'auto',
            }}>
              {evidenceList.slice(0, 4).map((item: string, idx: number) => (
                <li key={idx} style={{ marginBottom: '0.2rem' }}>
                  {String(item).trim()}
                </li>
              ))}
              {evidenceList.length > 4 && (
                <li style={{ color: '#6a6e73', fontStyle: 'italic' }}>
                  +{evidenceList.length - 4} more...
                </li>
              )}
            </ul>
          </div>
        )}

        {/* Additional Metrics */}
        {additionalMetrics.length > 0 && (
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.8rem', color: '#6a6e73', marginBottom: '0.35rem', fontWeight: 500 }}>
              Metrics
            </div>
            <ul style={{ 
              margin: 0, 
              paddingLeft: '1.25rem', 
              fontSize: '0.85rem',
              color: '#151515',
              maxHeight: '80px',
              overflowY: 'auto',
            }}>
              {additionalMetrics.slice(0, 5).map((item, idx) => (
                <li key={idx} style={{ marginBottom: '0.2rem' }}>
                  {item}
                </li>
              ))}
              {additionalMetrics.length > 5 && (
                <li style={{ color: '#6a6e73', fontStyle: 'italic' }}>
                  +{additionalMetrics.length - 5} more...
                </li>
              )}
            </ul>
          </div>
        )}

        {/* Timestamp */}
        <div style={{ 
          marginTop: 'auto', 
          paddingTop: '0.5rem', 
          fontSize: '0.75rem', 
          color: '#6a6e73',
          borderTop: '1px solid #f0f0f0',
        }}>
          🕐 {new Date(assessorResult.executed_at).toLocaleString()}
        </div>
      </CardBody>
    </Card>
  );
};
