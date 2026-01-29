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
import { AssessmentDetailed, RepositorySummary, AssessorResult } from '../types';
import { getPerformanceTier, formatAssessorName } from '../types';
import apiClient from '../services/api';

// Generate detailed, actionable recommendations from failed assessors
function generateRecommendations(assessorResults: AssessorResult[]) {
  const recommendations: Array<{
    id: string;
    category: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    description: string;
  }> = [];

  assessorResults.forEach((result, index) => {
    const resultStatus = result.result || result.metrics?.status;
    const score = result.score ?? 0;
    
    // Only generate recommendations for failed assessors
    if (resultStatus === 'fail' || (resultStatus !== 'pass' && score < 70)) {
      // Determine severity based on score
      let severity: 'critical' | 'high' | 'medium' | 'low';
      if (score < 25) {
        severity = 'critical';
      } else if (score < 50) {
        severity = 'high';
      } else if (score < 70) {
        severity = 'medium';
      } else {
        severity = 'low';
      }

      // Get evidence from metrics
      const evidence = result.metrics?.evidence;
      const evidenceList = evidence 
        ? (Array.isArray(evidence) ? evidence : String(evidence).split('|').map(s => s.trim()))
        : [];

      // Generate specific, actionable recommendations
      const actionItems = getActionableRecommendations(result.assessor_name, score, evidenceList);

      actionItems.forEach((action, actionIndex) => {
        recommendations.push({
          id: `rec-${index}-${actionIndex}`,
          category: getCategoryFromAssessor(result.assessor_name),
          severity: actionIndex === 0 ? severity : 'medium', // First item gets main severity
          description: action,
        });
      });
    }
  });

  // Sort by severity (critical first)
  const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
  return recommendations.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
}

function getCategoryFromAssessor(assessorName: string): string {
  if (assessorName.includes('test') || assessorName.includes('coverage')) return 'testing';
  if (assessorName.includes('doc')) return 'documentation';
  if (assessorName.includes('security')) return 'security';
  if (assessorName.includes('ecosystem') || assessorName.includes('tool')) return 'ecosystem';
  return 'code_quality';
}

function getActionableRecommendations(assessorName: string, score: number, evidence: string[]): string[] {
  const actions: string[] = [];
  
  switch (assessorName) {
    case 'quality_test_coverage':
      const estimatedCoverage = Math.round(score * 0.8);
      actions.push(`📊 Test Coverage is ~${estimatedCoverage}% (need 80%+)`);
      actions.push('➕ Add unit tests for uncovered functions - focus on business logic first');
      actions.push('🔧 Install coverage tools: npm install --save-dev jest @types/jest ts-jest');
      actions.push('📝 Add coverage threshold to jest.config.js: coverageThreshold: { global: { lines: 80 } }');
      if (evidence.some(e => e.includes('unit'))) {
        const match = evidence.find(e => e.includes('unit'));
        if (match) actions.push(`ℹ️ Current: ${match}`);
      }
      break;
      
    case 'quality_integration_tests':
      actions.push('🔗 No integration tests found in standard locations');
      actions.push('➕ Create tests/integration/ or __tests__/integration/ directory');
      actions.push('➕ Add API endpoint tests using supertest or testing-library');
      actions.push('➕ Add database integration tests with test containers');
      actions.push('📝 Example file: tests/integration/api.test.ts');
      actions.push('🔧 Consider adding Playwright or Cypress for E2E tests');
      break;
      
    case 'quality_documentation_standards':
      actions.push(`📚 Documentation score: ${score.toFixed(0)}/100`);
      if (score < 30) {
        actions.push('➕ Add a comprehensive README.md with: Installation, Usage, API docs, Contributing');
      }
      actions.push('➕ Add JSDoc/TSDoc comments to exported functions');
      actions.push('➕ Create CONTRIBUTING.md with development setup instructions');
      actions.push('➕ Add inline comments for complex logic');
      if (evidence.length > 0) {
        evidence.slice(0, 2).forEach(e => actions.push(`ℹ️ ${e}`));
      }
      break;
      
    case 'quality_ecosystem_tools':
      actions.push(`🛠️ Ecosystem tools score: ${score.toFixed(0)}/100`);
      actions.push('➕ Add ESLint: npm install --save-dev eslint @typescript-eslint/parser');
      actions.push('➕ Add Prettier: npm install --save-dev prettier');
      actions.push('➕ Add pre-commit hooks: npx husky-init && npm install');
      actions.push('📝 Create .eslintrc.js and .prettierrc config files');
      if (evidence.length > 0) {
        const configured = evidence.find(e => e.includes('configured') || e.includes('Linters'));
        if (configured) actions.push(`ℹ️ ${configured}`);
      }
      break;
      
    default:
      actions.push(`${formatAssessorName(assessorName)}: Score ${score.toFixed(0)}/100 (needs 70+)`);
      if (evidence.length > 0) {
        evidence.slice(0, 3).forEach(e => actions.push(`• ${e}`));
      }
      actions.push(`➕ Review and improve ${formatAssessorName(assessorName).toLowerCase()}`);
  }
  
  return actions;
}

interface AIRecommendation {
  title: string;
  severity: string;
  category: string;
  problem: string;
  solution: string;
  code_example?: string;
  estimated_effort?: string;
}

export const RepositoryDetail: React.FC = () => {
  const { assessmentId } = useParams<{ assessmentId: string }>();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<AssessmentDetailed | null>(null);
  const [repository, setRepository] = useState<RepositorySummary | null>(null);
  const [aiRecommendations, setAiRecommendations] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (assessmentId) {
      loadAssessmentData(assessmentId);
      loadAIRecommendations(assessmentId);
    }
  }, [assessmentId]);

  const loadAIRecommendations = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/assessments/${id}/recommendations?max_recommendations=10`);
      if (response.ok) {
        const data = await response.json();
        setAiRecommendations(data.recommendations || []);
      }
    } catch (err) {
      console.log('AI recommendations not available:', err);
    }
  };

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
              assessorResults={assessment.assessor_results || []}
              repositoryName={repository.name}
            />
          </GridItem>

          <GridItem span={6}>
            <RadarChart
              assessorResults={assessment.assessor_results || []}
              repositoryName={repository.name}
            />
          </GridItem>

          <GridItem span={12}>
            <Title headingLevel="h2" size="xl" style={{ marginTop: '2rem', marginBottom: '1rem', color: '#151515' }}>
              Detailed Results
            </Title>
          </GridItem>

          {(assessment.assessor_results || []).map(result => (
            <GridItem span={6} key={result.id}>
              <DrillDownView assessorResult={result} />
            </GridItem>
          ))}

          <GridItem span={12}>
            <RecommendationsList 
              recommendations={
                aiRecommendations.length > 0 
                  ? aiRecommendations 
                  : generateRecommendations(assessment.assessor_results || [])
              } 
            />
          </GridItem>
        </Grid>
      </PageSection>
    </>
  );
};

