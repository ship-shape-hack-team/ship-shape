"""Assessment API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...storage.assessment_store import AssessmentStore

router = APIRouter()


class CreateAssessmentRequest(BaseModel):
    """Request body for creating an assessment."""

    repo_url: str
    assessors: Optional[List[str]] = None


@router.post("/assessments", status_code=202)
async def create_assessment(request: CreateAssessmentRequest):
    """Trigger a new assessment.

    Args:
        request: Assessment creation request

    Returns:
        Assessment details with status
    """
    # Note: Full implementation would:
    # 1. Create assessment record with status=pending
    # 2. Queue assessment task
    # 3. Return assessment ID for polling

    return {
        "id": "assessment-id-placeholder",
        "repo_url": request.repo_url,
        "status": "pending",
        "message": "Assessment queued. Poll /assessments/{id}/status for progress.",
    }


@router.get("/assessments/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    include_results: bool = Query(True),
):
    """Get assessment details.

    Args:
        assessment_id: Assessment UUID
        include_results: Include assessor results

    Returns:
        Assessment details
    """
    store = AssessmentStore()

    assessment_data = store.get(assessment_id)

    if not assessment_data:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Note: Would include assessor results if include_results=True
    return assessment_data


@router.get("/assessments/{assessment_id}/status")
async def get_assessment_status(assessment_id: str):
    """Get assessment status for polling.

    Args:
        assessment_id: Assessment UUID

    Returns:
        Status and progress
    """
    store = AssessmentStore()

    assessment_data = store.get(assessment_id)

    if not assessment_data:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "status": assessment_data["status"],
        "progress": 100 if assessment_data["status"] == "completed" else 50,
        "message": f"Assessment {assessment_data['status']}",
    }


@router.post("/assessments/{assessment_id}/cancel")
async def cancel_assessment(assessment_id: str):
    """Cancel a running assessment.

    Args:
        assessment_id: Assessment UUID

    Returns:
        Cancellation confirmation
    """
    store = AssessmentStore()

    success = store.update(assessment_id, {"status": "cancelled"})

    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {"message": "Assessment cancelled"}


@router.get("/repositories/{repo_url_encoded}/assessments")
async def get_repository_assessments(
    repo_url_encoded: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get assessment history for a repository.

    Args:
        repo_url_encoded: URL-encoded repository URL
        limit: Maximum assessments to return
        offset: Number to skip

    Returns:
        Assessment history
    """
    from urllib.parse import unquote

    repo_url = unquote(repo_url_encoded)
    store = AssessmentStore()

    assessments = store.list(
        filters={"repo_url": repo_url},
        limit=limit,
        offset=offset,
    )

    total = store.count(filters={"repo_url": repo_url})

    return {
        "assessments": assessments,
        "total": total,
    }
