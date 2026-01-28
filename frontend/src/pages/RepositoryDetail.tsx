/**
 * Repository detail page with radar chart and drill-down
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  PageSection,
  Title,
  Button,
  Grid,
  GridItem,
  Alert,
  AlertVariant,
  Breadcrumb,
  BreadcrumbItem,
} from '@patternfly/react-core';
import { ArrowLeftIcon } from '@patternfly/react-icons';
import { ScoreCard } from '../components/ScoreCard';
import { RadarChart } from '../components/RadarChart';
import { StellarChart } from '../components/StellarChart';
import { DrillDownView } from '../components/DrillDownView';
import { RecommendationsList } from '../components/RecommendationsList';
import { AssessmentDetailed, RepositorySummary } from '../types';
import { getPerformanceTier } from '../types';
import apiClient from '../services/api';

export const RepositoryDetail: React.FC = () => {
  const { assessmentId } = useParams<{ assessmentId: string }>();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<AssessmentDetailed | null>(null);
  const [repository, setRepository] = useState<RepositorySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (assessmentId) {
      loadAssessmentData(assessmentId);
    }
  }, [assessmentId]);

  const loadAssessmentData = async (id: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Get assessment with results directly
      const detailedAssessment = await apiClient.getAssessment(id, true);
      setAssessment(detailedAssessment);
      
      // Create repository summary from assessment data
      setRepository({
        repo_url: detailedAssessment.repo_url,
        name: detailedAssessment.repo_url.split('/').pop() || 'repository',
        primary_language: null,
        overall_score: detailedAssessment.overall_score,
        last_assessed: detailedAssessment.completed_at,
      });
    } catch (err) {
      console.error('Failed to load assessment:', err);
      setError('Failed to load assessment. Make sure backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <PageSection>
        <p>Loading assessment data...</p>
      </PageSection>
    );
  }

  if (!assessment || !repository) {
    return (
      <PageSection>
        <Alert variant={AlertVariant.warning} title="No Data">
          No assessment data found for this repository.
        </Alert>
      </PageSection>
    );
  }

  const tier = getPerformanceTier(assessment.overall_score);

  return (
    <>
      <PageSection variant="light">
        <Breadcrumb>
          <BreadcrumbItem to="/" onClick={() => navigate('/')}>
            Dashboard
          </BreadcrumbItem>
          <BreadcrumbItem isActive>{repository.name}</BreadcrumbItem>
        </Breadcrumb>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
          <Button variant="plain" icon={<ArrowLeftIcon />} onClick={() => navigate('/')}>
            Back
          </Button>
          <div>
            <Title headingLevel="h1" size="2xl" style={{ color: '#151515' }}>
              {repository.name}
            </Title>
            <p style={{ color: '#6a6e73' }}>{repository.repo_url}</p>
          </div>
        </div>
      </PageSection>

      {error && (
        <PageSection>
          <Alert variant={AlertVariant.warning} title="Backend Not Connected" isInline>
            {error}
          </Alert>
        </PageSection>
      )}

      <PageSection>
        <Grid hasGutter>
          <GridItem span={12}>
            <ScoreCard
              title="Overall Quality Score"
              score={assessment.overall_score}
              subtitle={`${tier} Performance`}
            />
          </GridItem>

          <GridItem span={6}>
            <StellarChart
              assessorResults={assessment.assessor_results}
              repositoryName={repository.name}
            />
          </GridItem>

          <GridItem span={6}>
            <RadarChart
              assessorResults={assessment.assessor_results}
              repositoryName={repository.name}
            />
          </GridItem>

          <GridItem span={12}>
            <Title headingLevel="h2" size="xl" style={{ marginTop: '2rem', marginBottom: '1rem', color: '#151515' }}>
              Detailed Results
            </Title>
          </GridItem>

          {assessment.assessor_results.map(result => (
            <GridItem span={6} key={result.id}>
              <DrillDownView assessorResult={result} />
            </GridItem>
          ))}

          <GridItem span={12}>
            <RecommendationsList recommendations={[]} />
          </GridItem>
        </Grid>
      </PageSection>
    </>
  );
};

