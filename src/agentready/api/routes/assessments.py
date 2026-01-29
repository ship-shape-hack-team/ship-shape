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
    """Get assessment details with assessor results.

    Args:
        assessment_id: Assessment UUID
        include_results: Include assessor results

    Returns:
        Assessment details with assessor results
    """
    from ...storage.connection import get_db_session
    from sqlalchemy import text
    import json
    
    try:
        with get_db_session() as session:
            # Get assessment
            query = text("SELECT id, repo_url, overall_score, status, started_at, completed_at, metadata FROM assessments WHERE id = :id")
            assessment_row = session.execute(query, {"id": assessment_id}).fetchone()
            
            if not assessment_row:
                raise HTTPException(status_code=404, detail="Assessment not found")
            
            assessment_data = {
                "id": assessment_row[0],
                "repo_url": assessment_row[1],
                "overall_score": assessment_row[2],
                "status": assessment_row[3],
                "started_at": assessment_row[4],
                "completed_at": assessment_row[5],
                "metadata": json.loads(assessment_row[6]) if assessment_row[6] else None,
            }
            
            # Include assessor results if requested
            if include_results:
                results_query = text("SELECT id, assessor_name, score, metrics, status, executed_at FROM assessor_results WHERE assessment_id = :id")
                results_rows = session.execute(results_query, {"id": assessment_id}).fetchall()
                
                assessor_results = []
                for row in results_rows:
                    # Try to parse metrics as JSON, fallback to eval for old Python dict format
                    metrics_str = row[3]
                    metrics_data = {}
                    if metrics_str:
                        try:
                            metrics_data = json.loads(metrics_str)
                        except json.JSONDecodeError:
                            # Handle old Python dict string format
                            try:
                                import ast
                                metrics_data = ast.literal_eval(metrics_str)
                            except (ValueError, SyntaxError):
                                metrics_data = {"raw": metrics_str}
                    
                    assessor_results.append({
                        "id": row[0],
                        "assessor_name": row[1],
                        "score": row[2],
                        "metrics": metrics_data,
                        "status": row[4],
                        "executed_at": row[5],
                    })
                
                assessment_data["assessor_results"] = assessor_results
            
            return assessment_data
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assessment: {str(e)}")


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


@router.get("/repository/assessments")
async def get_repository_assessments(
    repo_url: str = Query(..., description="Repository URL"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get assessment history for a repository using query parameter.

    Args:
        repo_url: Repository URL (query parameter)
        limit: Maximum assessments to return
        offset: Number to skip

    Returns:
        Assessment history with IDs for fetching details
    """
    from ...storage.connection import get_db_session
    from sqlalchemy import text
    
    try:
        with get_db_session() as session:
            # Get assessments for this repo
            query = text("""
                SELECT id, repo_url, overall_score, status, started_at, completed_at
                FROM assessments
                WHERE repo_url = :repo_url
                ORDER BY started_at DESC
                LIMIT :limit OFFSET :offset
            """)
            
            results = session.execute(query, {
                "repo_url": repo_url,
                "limit": limit,
                "offset": offset
            }).fetchall()
            
            # Count total
            count_query = text("SELECT COUNT(*) FROM assessments WHERE repo_url = :repo_url")
            total = session.execute(count_query, {"repo_url": repo_url}).fetchone()[0]
            
            assessments = [
                {
                    "id": row[0],
                    "repo_url": row[1],
                    "overall_score": row[2],
                    "status": row[3],
                    "started_at": row[4],
                    "completed_at": row[5],
                }
                for row in results
            ]
            
            return {
                "assessments": assessments,
                "total": total,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assessments: {str(e)}")
