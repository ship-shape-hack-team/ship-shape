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
import { DrillDownView } from '../components/DrillDownView';
import { RecommendationsList } from '../components/RecommendationsList';
import { AssessmentDetailed, RepositorySummary } from '../types';
import { getPerformanceTier } from '../types';
import apiClient from '../services/api';

export const RepositoryDetail: React.FC = () => {
  const { repoUrl } = useParams<{ repoUrl: string }>();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<AssessmentDetailed | null>(null);
  const [repository, setRepository] = useState<RepositorySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (repoUrl) {
      loadAssessmentData(decodeURIComponent(repoUrl));
    }
  }, [repoUrl]);

  const loadAssessmentData = async (url: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Get repository
      const repoData = await apiClient.getRepository(url);
      setRepository(repoData);

      // Get latest assessment
      const assessmentsData = await apiClient.getRepositoryAssessments(url, 1);
      
      if (assessmentsData.assessments && assessmentsData.assessments.length > 0) {
        const latestAssessmentId = assessmentsData.assessments[0].id;
        const detailedAssessment = await apiClient.getAssessment(latestAssessmentId, true);
        setAssessment(detailedAssessment);
      }
    } catch (err) {
      console.error('Failed to load assessment:', err);
      setError('Failed to load assessment data. Showing mock data for demonstration.');
      // Load mock data
      setAssessment(getMockAssessment(url));
      setRepository(getMockRepository(url));
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
            <Title headingLevel="h1" size="2xl">
              {repository.name}
            </Title>
            <p style={{ color: '#666' }}>{repository.repo_url}</p>
          </div>
        </div>
      </PageSection>

      {error && (
        <PageSection>
          <Alert variant={AlertVariant.info} title="Demo Mode" isInline>
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

          <GridItem span={12}>
            <RadarChart
              assessorResults={assessment.assessor_results}
              repositoryName={repository.name}
            />
          </GridItem>

          <GridItem span={12}>
            <Title headingLevel="h2" size="xl" style={{ marginTop: '2rem', marginBottom: '1rem' }}>
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

// Mock data for demonstration
function getMockRepository(url: string): RepositorySummary {
  return {
    repo_url: url,
    name: url.includes('model-registry') ? 'kubeflow/model-registry' : 'ship-shape',
    primary_language: url.includes('model-registry') ? 'Go' : 'Python',
    overall_score: url.includes('model-registry') ? 47.9 : 86.3,
    last_assessed: new Date().toISOString(),
  };
}

function getMockAssessment(url: string): AssessmentDetailed {
  const isModelRegistry = url.includes('model-registry');

  return {
    id: 'mock-assessment-id',
    repo_url: url,
    overall_score: isModelRegistry ? 47.9 : 86.3,
    status: 'completed',
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    assessor_results: [
      {
        id: '1',
        assessor_name: 'quality_test_coverage',
        score: isModelRegistry ? 12.7 : 75.0,
        metrics: {
          evidence: isModelRegistry
            ? 'Line coverage: 10.1% | Test count: 179'
            : 'Line coverage: 75.0% | Test count: 55',
        },
        status: 'success',
        executed_at: new Date().toISOString(),
      },
      {
        id: '2',
        assessor_name: 'quality_integration_tests',
        score: isModelRegistry ? 30.0 : 85.0,
        metrics: {
          evidence: isModelRegistry
            ? 'Integration test files: 3'
            : 'Integration test files: 8 | ✓ Database tests detected',
        },
        status: 'success',
        executed_at: new Date().toISOString(),
      },
      {
        id: '3',
        assessor_name: 'quality_documentation_standards',
        score: isModelRegistry ? 77.6 : 90.0,
        metrics: {
          evidence: isModelRegistry
            ? 'README score: 100/100 | Docstring coverage: 94/100'
            : 'README score: 100/100 | Docstring coverage: 85/100 | Architecture docs: ✓',
        },
        status: 'success',
        executed_at: new Date().toISOString(),
      },
      {
        id: '4',
        assessor_name: 'quality_ecosystem_tools',
        score: isModelRegistry ? 80.0 : 95.0,
        metrics: {
          evidence: isModelRegistry
            ? 'Found: CI/CD, Security Scanning, Linting, Dependency Management | Missing: Code Coverage'
            : 'Found: CI/CD, Code Coverage, Security Scanning, Linting, Dependency Management, Pre Commit Hooks',
        },
        status: 'success',
        executed_at: new Date().toISOString(),
      },
    ],
  };
}
