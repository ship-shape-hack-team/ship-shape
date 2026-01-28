/**
 * Recommendations list component
 */

import React from 'react';
import {
  Card,
  CardBody,
  CardTitle,
  List,
  ListItem,
  Label,
} from '@patternfly/react-core';

interface Recommendation {
  id: string;
  category: string;
  severity: string;
  description: string;
}

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
  recommendations,
}) => {
  if (recommendations.length === 0) {
    return (
      <Card>
        <CardTitle>Recommendations</CardTitle>
        <CardBody>
          <p>✅ No critical recommendations. Quality looks good!</p>
        </CardBody>
      </Card>
    );
  }

  // Group by severity
  const bySeverity = {
    critical: recommendations.filter(r => r.severity === 'critical'),
    high: recommendations.filter(r => r.severity === 'high'),
    medium: recommendations.filter(r => r.severity === 'medium'),
    low: recommendations.filter(r => r.severity === 'low'),
  };

  const severityColors: Record<string, any> = {
    critical: 'red',
    high: 'orange',
    medium: 'gold',
    low: 'blue',
  };

  return (
    <Card>
      <CardTitle>Recommendations ({recommendations.length})</CardTitle>
      <CardBody>
        <List>
          {(['critical', 'high', 'medium', 'low'] as const).map(severity => {
            const items = bySeverity[severity];
            if (items.length === 0) return null;

            return (
              <React.Fragment key={severity}>
                {items.map(rec => (
                  <ListItem key={rec.id}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                      <Label color={severityColors[severity]}>
                        {severity.toUpperCase()}
                      </Label>
                      <div>
                        <div style={{ fontWeight: 500 }}>{rec.description}</div>
                        <div style={{ fontSize: '0.9em', color: '#666', marginTop: '0.25rem' }}>
                          Category: {rec.category}
                        </div>
                      </div>
                    </div>
                  </ListItem>
                ))}
              </React.Fragment>
            );
          })}
        </List>
      </CardBody>
    </Card>
  );
};
