"""Background assessment runner service.

This module handles cloning repositories and running quality assessments
in the background when repositories are added through the API.
"""

import json
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..assessors.quality import (
    DocumentationStandardsAssessor,
    EcosystemToolsAssessor,
    IntegrationTestsAssessor,
    TestCoverageAssessor,
)
from ..models.assessment import Assessment
from ..models.assessor_result import AssessorResult
from ..models.repository import Repository
from ..services.quality_scorer import QualityScorerService
from ..storage.assessment_store import AssessmentStore
from sqlalchemy import text


class AssessmentRunner:
    """Runs quality assessments on repositories."""

    def __init__(self):
        """Initialize assessment runner."""
        self.assessors = [
            TestCoverageAssessor(),
            IntegrationTestsAssessor(),
            DocumentationStandardsAssessor(),
            EcosystemToolsAssessor(),
        ]
        self.scorer = QualityScorerService()
        self.store = AssessmentStore()

    def clone_repository(self, repo_url: str, target_dir: Path) -> bool:
        """Clone a git repository.

        Args:
            repo_url: Repository URL to clone
            target_dir: Directory to clone into

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use subprocess to clone the repository
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"Failed to clone repository: {e}")
            return False

    def run_assessment(
        self,
        repo_url: str,
        repo_name: str,
        primary_language: Optional[str] = None,
    ) -> Optional[str]:
        """Run quality assessment on a repository.

        Args:
            repo_url: Repository URL
            repo_name: Repository name
            primary_language: Primary programming language

        Returns:
            Assessment ID if successful, None otherwise
        """
        temp_dir = None
        assessment_id = str(uuid.uuid4())

        try:
            # Create assessment record with pending status
            self._create_pending_assessment(assessment_id, repo_url)

            # Update status to running
            self._update_assessment_status(assessment_id, "running")

            # Clone repository to temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="shipshape_"))
            print(f"Cloning {repo_url} to {temp_dir}...")

            if not self.clone_repository(repo_url, temp_dir):
                self._update_assessment_status(assessment_id, "failed")
                return None

            # Create Repository model for assessors
            repo = Repository(
                path=temp_dir,
                name=repo_name,
                url=repo_url,
                branch="main",
                commit_hash="unknown",
                languages={primary_language: 1} if primary_language else {},
                total_files=0,
                total_lines=0,
            )

            # Run assessors
            print(f"Running {len(self.assessors)} assessors on {repo_name}...")
            assessor_results = []

            for assessor in self.assessors:
                print(f"  Running {assessor.attribute_id}...")
                finding = assessor.assess(repo)

                # Extract evidence
                evidence_str = (
                    " | ".join(finding.evidence)
                    if isinstance(finding.evidence, list)
                    else str(finding.evidence)
                )

                # Map Finding status to AssessorResult status
                if finding.status in ["pass", "fail"]:
                    result_status = "success"
                elif finding.status == "error":
                    result_status = "failed"
                else:
                    result_status = "skipped"

                result = AssessorResult(
                    assessment_id=assessment_id,
                    assessor_name=assessor.attribute_id,
                    score=finding.score if finding.score is not None else 0,
                    metrics={
                        "status": finding.status,
                        "evidence": evidence_str,
                    },
                    status=result_status,
                    executed_at=datetime.utcnow(),
                )

                assessor_results.append(result)
                print(f"    Score: {result.score:.1f}/100")

            # Calculate overall score
            overall_score = self.scorer.calculate_overall_score(assessor_results)

            # Update assessment with results
            self._complete_assessment(assessment_id, overall_score, assessor_results, repo_url)

            print(f"✓ Assessment completed: {assessment_id} (Score: {overall_score:.1f}/100)")
            return assessment_id

        except Exception as e:
            print(f"Assessment failed: {e}")
            self._update_assessment_status(assessment_id, "failed")
            return None

        finally:
            # Cleanup temp directory
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Failed to cleanup temp directory: {e}")

    def _create_pending_assessment(self, assessment_id: str, repo_url: str):
        """Create a pending assessment record."""
        from ..storage.connection import get_db_session

        with get_db_session(self.store.database_url) as session:
            query = text(
                """
                INSERT INTO assessments (id, repo_url, overall_score, status, started_at)
                VALUES (:id, :repo_url, 0, 'pending', :started_at)
                """
            )
            session.execute(
                query,
                {
                    "id": assessment_id,
                    "repo_url": repo_url,
                    "started_at": datetime.utcnow(),
                },
            )

    def _update_assessment_status(self, assessment_id: str, status: str):
        """Update assessment status."""
        from ..storage.connection import get_db_session

        with get_db_session(self.store.database_url) as session:
            query = text(
                """
                UPDATE assessments
                SET status = :status
                WHERE id = :id
                """
            )
            session.execute(query, {"id": assessment_id, "status": status})

    def _complete_assessment(
        self,
        assessment_id: str,
        overall_score: float,
        assessor_results: List[AssessorResult],
        repo_url: str,
    ):
        """Complete assessment and save results."""
        from ..storage.connection import get_db_session

        with get_db_session(self.store.database_url) as session:
            # Update assessment
            query = text(
                """
                UPDATE assessments
                SET overall_score = :score,
                    status = 'completed',
                    completed_at = :completed_at
                WHERE id = :id
                """
            )
            session.execute(
                query,
                {
                    "id": assessment_id,
                    "score": overall_score,
                    "completed_at": datetime.utcnow(),
                },
            )

            # Save assessor results
            for result in assessor_results:
                result_query = text(
                    """
                    INSERT INTO assessor_results
                    (id, assessment_id, assessor_name, score, metrics, status, executed_at)
                    VALUES (:id, :assessment_id, :assessor_name, :score, :metrics, :status, :executed_at)
                    """
                )
                session.execute(
                    result_query,
                    {
                        "id": str(uuid.uuid4()),
                        "assessment_id": assessment_id,
                        "assessor_name": result.assessor_name,
                        "score": result.score,
                        "metrics": json.dumps(result.metrics),  # Use json.dumps instead of str
                        "status": result.status,
                        "executed_at": result.executed_at,
                    },
                )

            # Update repository with latest assessment
            repo_query = text(
                """
                UPDATE repositories
                SET latest_assessment_id = :assessment_id,
                    last_assessed = :last_assessed
                WHERE repo_url = :repo_url
                """
            )
            session.execute(
                repo_query,
                {
                    "assessment_id": assessment_id,
                    "last_assessed": datetime.utcnow(),
                    "repo_url": repo_url,
                },
            )
