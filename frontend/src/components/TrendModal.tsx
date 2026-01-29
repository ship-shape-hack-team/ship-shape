/**
 * Trend modal showing historical assessment scores over time
 */

import React from 'react';
import { Modal, ModalVariant } from '@patternfly/react-core';
import {
  Chart,
  ChartAxis,
  ChartGroup,
  ChartLine,
  ChartThemeColor,
  ChartVoronoiContainer,
} from '@patternfly/react-charts';

interface Assessment {
  id: string;
  started_at: string;
  overall_score: number;
}

interface TrendModalProps {
  isOpen: boolean;
  onClose: () => void;
  repositoryName: string;
  assessments: Assessment[];
}

export const TrendModal: React.FC<TrendModalProps> = ({
  isOpen,
  onClose,
  repositoryName,
  assessments,
}) => {
  // Prepare chart data
  const chartData = assessments.map(assessment => ({
    x: new Date(assessment.started_at),
    y: assessment.overall_score,
    name: `${new Date(assessment.started_at).toLocaleDateString()}: ${assessment.overall_score.toFixed(1)}`,
  }));

  // Sort by date
  chartData.sort((a, b) => a.x.getTime() - b.x.getTime());

  return (
    <Modal
      variant={ModalVariant.large}
      title={`Quality Trend for ${repositoryName}`}
      isOpen={isOpen}
      onClose={onClose}
      actions={[]}
    >
      <div style={{ padding: '1rem' }}>
        <p style={{ marginBottom: '1rem', color: '#6a6e73' }}>
          Showing {assessments.length} assessment{assessments.length !== 1 ? 's' : ''} over the last 6 months
        </p>

        {chartData.length > 0 ? (
          <Chart
            ariaDesc="Quality score trend over time"
            ariaTitle="Assessment history chart"
            containerComponent={
              <ChartVoronoiContainer
                labels={({ datum }) => datum.name}
                constrainToVisibleArea
              />
            }
            height={300}
            maxDomain={{ y: 100 }}
            minDomain={{ y: 0 }}
            padding={{
              bottom: 75,
              left: 75,
              right: 50,
              top: 50,
            }}
            themeColor={ChartThemeColor.blue}
            width={800}
          >
            <ChartAxis
              label="Date"
              tickFormat={(t) => {
                const date = new Date(t);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <ChartAxis
              dependentAxis
              showGrid
              label="Quality Score"
              tickFormat={(t) => `${t}`}
            />
            <ChartGroup>
              <ChartLine
                data={chartData}
                style={{
                  data: {
                    stroke: '#0066CC',
                    strokeWidth: 2,
                  },
                }}
              />
            </ChartGroup>
          </Chart>
        ) : (
          <p style={{ textAlign: 'center', padding: '2rem', color: '#6a6e73' }}>
            No historical data available
          </p>
        )}

        {/* Summary stats */}
        {chartData.length >= 2 && (
          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', color: '#151515' }}>
              <div>
                <div style={{ fontSize: '0.9em', color: '#6a6e73' }}>First Score</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>
                  {chartData[0].y.toFixed(1)}
                </div>
                <div style={{ fontSize: '0.85em', color: '#6a6e73' }}>
                  {chartData[0].x.toLocaleDateString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9em', color: '#6a6e73' }}>Latest Score</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>
                  {chartData[chartData.length - 1].y.toFixed(1)}
                </div>
                <div style={{ fontSize: '0.85em', color: '#6a6e73' }}>
                  {chartData[chartData.length - 1].x.toLocaleDateString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9em', color: '#6a6e73' }}>Change</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: chartData[chartData.length - 1].y > chartData[0].y ? '#3E8635' : chartData[chartData.length - 1].y < chartData[0].y ? '#C9190B' : '#F0AB00' }}>
                  {chartData[chartData.length - 1].y > chartData[0].y ? '+' : ''}
                  {(chartData[chartData.length - 1].y - chartData[0].y).toFixed(1)}
                </div>
                <div style={{ fontSize: '0.85em', color: '#6a6e73' }}>
                  points
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
