/**
 * Trend icon component showing quality trend over time
 */

import React from 'react';
import { Button } from '@patternfly/react-core';
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  LongArrowAltRightIcon 
} from '@patternfly/react-icons';

interface TrendIconProps {
  trend: 'improving' | 'declining' | 'stable' | 'no_data';
  onClick: (e: React.MouseEvent) => void;
}

export const TrendIcon: React.FC<TrendIconProps> = ({ trend, onClick }) => {
  const iconConfig = {
    improving: {
      icon: <ArrowUpIcon />,
      color: '#3E8635', // green
      label: 'Improving',
    },
    declining: {
      icon: <ArrowDownIcon />,
      color: '#C9190B', // red
      label: 'Declining',
    },
    stable: {
      icon: <LongArrowAltRightIcon />,
      color: '#F0AB00', // yellow
      label: 'Stable',
    },
    no_data: {
      icon: <span>—</span>,
      color: '#6a6e73', // gray
      label: 'No data',
    },
  };

  const config = iconConfig[trend];

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick(e);
  };

  return (
    <Button
      variant="plain"
      onClick={handleClick}
      style={{ 
        color: config.color,
        padding: '0.25rem',
        minWidth: '40px',
      }}
      aria-label={`Trend: ${config.label}`}
    >
      {config.icon}
    </Button>
  );
};
