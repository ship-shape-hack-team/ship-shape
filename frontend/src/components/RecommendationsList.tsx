/**
 * Recommendations list component - minimized with load more
 */

import React, { useState } from 'react';
import {
  Card,
  CardBody,
  CardTitle,
  Label,
  List,
  ListItem,
  Button,
} from '@patternfly/react-core';

interface Recommendation {
  id?: string;
  title?: string;
  category: string;
  severity: string;
  problem?: string;
  description?: string;
  solution?: string;
}

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

const INITIAL_SHOW = 3;

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
  recommendations,
}) => {
  const [showAll, setShowAll] = useState(false);

  if (recommendations.length === 0) {
    return (
      <Card>
        <CardTitle style={{ color: '#151515' }}>Recommendations</CardTitle>
        <CardBody>
          <p style={{ color: '#3e8635' }}>✅ No critical issues found. Your code quality looks good!</p>
        </CardBody>
      </Card>
    );
  }

  // Sort by severity (critical first)
  const severityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
  const sorted = [...recommendations].sort((a, b) => 
    (severityOrder[a.severity] ?? 4) - (severityOrder[b.severity] ?? 4)
  );

  const severityColors: Record<string, 'red' | 'orange' | 'gold' | 'blue'> = {
    critical: 'red',
    high: 'orange',
    medium: 'gold',
    low: 'blue',
  };

  const severityIcons: Record<string, string> = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🔵',
  };

  // Count by severity for summary
  const counts = {
    critical: recommendations.filter(r => r.severity === 'critical').length,
    high: recommendations.filter(r => r.severity === 'high').length,
    medium: recommendations.filter(r => r.severity === 'medium').length,
    low: recommendations.filter(r => r.severity === 'low').length,
  };

  // Show limited items initially
  const displayItems = showAll ? sorted : sorted.slice(0, INITIAL_SHOW);
  const hiddenCount = sorted.length - INITIAL_SHOW;

  return (
    <Card>
      <CardTitle style={{ color: '#151515' }}>
        📋 Recommendations ({recommendations.length})
      </CardTitle>
      <CardBody>
        {/* Summary badges */}
        <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {counts.critical > 0 && <Label color="red">{counts.critical} Critical</Label>}
          {counts.high > 0 && <Label color="orange">{counts.high} High</Label>}
          {counts.medium > 0 && <Label color="gold">{counts.medium} Medium</Label>}
          {counts.low > 0 && <Label color="blue">{counts.low} Low</Label>}
        </div>

        {/* Consolidated list */}
        <List isPlain>
          {displayItems.map((rec, index) => {
            const text = rec.description || rec.problem || rec.title || 'Recommendation';
            
            return (
              <ListItem 
                key={rec.id || index}
                style={{ 
                  padding: '0.75rem',
                  marginBottom: '0.5rem',
                  backgroundColor: '#fafafa',
                  borderRadius: '4px',
                  borderLeft: `3px solid ${
                    rec.severity === 'critical' ? '#c9190b' :
                    rec.severity === 'high' ? '#f0ab00' :
                    rec.severity === 'medium' ? '#f4c030' : '#0066cc'
                  }`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <span style={{ fontSize: '1rem' }}>{severityIcons[rec.severity] || '📌'}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: '#151515' }}>{text}</div>
                  </div>
                  <Label color={severityColors[rec.severity] || 'grey'} isCompact>
                    {rec.severity}
                  </Label>
                </div>
              </ListItem>
            );
          })}
        </List>

        {/* Load more / Show less button */}
        {sorted.length > INITIAL_SHOW && (
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <Button 
              variant="link" 
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? '▲ Show less' : `▼ Show ${hiddenCount} more`}
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
};
