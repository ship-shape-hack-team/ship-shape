/**
 * Empty state component for when no assessments have been run
 */

import React from 'react';
import {
  Card,
  CardBody,
} from '@patternfly/react-core';

interface EmptyStateProps {
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onAction }) => {
  return (
    <Card style={{ overflow: 'hidden' }}>
      <CardBody style={{ 
        textAlign: 'center', 
        padding: '3rem 2rem',
        background: 'linear-gradient(180deg, #f8f8f8 0%, #fff 100%)',
      }}>
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📦</div>
        <h2 style={{ 
          color: '#151515', 
          fontSize: '1.5rem', 
          fontWeight: 600,
          marginBottom: '0.75rem',
        }}>
          No Repositories Assessed Yet
        </h2>
        <p style={{ 
          color: '#6a6e73', 
          maxWidth: '400px', 
          margin: '0 auto 1.5rem',
          lineHeight: 1.6,
        }}>
          Get started by adding a repository URL in the input field above.
          The system will automatically assess quality across multiple dimensions.
        </p>
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '2rem',
          flexWrap: 'wrap',
          marginTop: '2rem',
          padding: '1.5rem',
          backgroundColor: '#f0f0f0',
          borderRadius: '8px',
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>🧪</div>
            <div style={{ fontSize: '0.85rem', color: '#6a6e73' }}>Test Coverage</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>📚</div>
            <div style={{ fontSize: '0.85rem', color: '#6a6e73' }}>Documentation</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>🛠️</div>
            <div style={{ fontSize: '0.85rem', color: '#6a6e73' }}>Ecosystem Tools</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>🔗</div>
            <div style={{ fontSize: '0.85rem', color: '#6a6e73' }}>Integration Tests</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>📖</div>
            <div style={{ fontSize: '0.85rem', color: '#6a6e73' }}>API Docs</div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
