"""Repository management API routes."""

import asyncio
from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from ...models.repository_record import RepositoryRecord
from ...services.assessment_runner import AssessmentRunner
from ...services.repository_service import RepositoryService
from ...storage.assessment_store import AssessmentStore

router = APIRouter()


class CreateRepositoryRequest(BaseModel):
    """Request body for creating a repository."""

    repo_url: str
    trigger_assessment: bool = True


@router.get("/repositories")
async def list_repositories(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("last_assessed", regex="^(name|last_assessed|overall_score)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
):
    """List all repositories with their latest assessment scores.

    Args:
        limit: Maximum number of repositories to return
        offset: Number of repositories to skip
        sort_by: Field to sort by
        order: Sort order (asc or desc)

    Returns:
        List of repositories with pagination info
    """
    from ...storage.connection import get_db_session
    from sqlalchemy import text

    try:
        with get_db_session() as session:
            # Query repositories with latest assessment using stored ID
            query = text("""
                SELECT 
                    r.repo_url,
                    r.name,
                    r.primary_language,
                    r.last_assessed,
                    r.latest_assessment_id,
                    (
                        SELECT a.overall_score
                        FROM assessments a
                        WHERE a.id = r.latest_assessment_id
                        LIMIT 1
                    ) as overall_score
                FROM repositories r
                ORDER BY r.last_assessed DESC
                LIMIT :limit OFFSET :offset
            """)
            
            results = session.execute(query, {"limit": limit, "offset": offset}).fetchall()
            
            # Count total
            count_query = text("SELECT COUNT(*) FROM repositories")
            total = session.execute(count_query).fetchone()[0]
            
            repositories = [
                {
                    "repo_url": row[0],
                    "name": row[1],
                    "primary_language": row[2],
                    "last_assessed": row[3],
                    "latest_assessment_id": row[4],
                    "overall_score": row[5],
                }
                for row in results
            ]
            
            return {
                "repositories": repositories,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
    except Exception as e:
        # Fallback to empty list if database not initialized
        return {
            "repositories": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }


@router.post("/repositories", status_code=201)
async def create_repository(request: CreateRepositoryRequest, background_tasks: BackgroundTasks):
    """Add a new repository.

    Args:
        request: Repository creation request
        background_tasks: FastAPI background tasks

    Returns:
        Created repository
    """
    import traceback
    
    try:
        repo_service = RepositoryService()
        store = AssessmentStore()

        # Extract repository info
        print(f"DEBUG: Extracting repo info for {request.repo_url}")
        repo_record = repo_service.extract_repo_info(request.repo_url)
        print(f"DEBUG: Got repo_record: {repo_record}")

        # Store in database
        print(f"DEBUG: Storing in database...")
        store.create_repository(
            repo_url=repo_record.repo_url,
            name=repo_record.name,
            description=repo_record.description,
            primary_language=repo_record.primary_language,
        )
        print(f"DEBUG: Stored successfully")

        # Trigger assessment in background if requested
        if request.trigger_assessment:
            print(f"DEBUG: Triggering assessment...")
            runner = AssessmentRunner()
            background_tasks.add_task(
                runner.run_assessment,
                repo_record.repo_url,
                repo_record.name,
                repo_record.primary_language,
            )

        return repo_record.to_dict()
    except Exception as e:
        print(f"ERROR in create_repository: {e}")
        print(traceback.format_exc())
        raise


@router.get("/repository")
async def get_repository(repo_url: str = Query(..., description="Repository URL")):
    """Get repository details using query parameter.

    Args:
        repo_url: Repository URL (query parameter to avoid path encoding issues)

    Returns:
        Repository details
    """
    print(f"DEBUG: Looking for repo_url: '{repo_url}'")
    
    store = AssessmentStore()
    repo_data = store.get_repository(repo_url)
    
    print(f"DEBUG: Found repo_data: {repo_data}")

    if not repo_data:
        raise HTTPException(status_code=404, detail=f"Repository not found: {repo_url}")

    return repo_data


@router.post("/repositories/reassess", status_code=202)
async def reassess_repository(
    repo_url: str = Query(..., description="Repository URL to reassess"),
    background_tasks: BackgroundTasks = None
):
    """Trigger a reassessment for an existing repository.

    Args:
        repo_url: Repository URL (query parameter)
        background_tasks: FastAPI background tasks

    Returns:
        Assessment trigger confirmation
    """
    import traceback
    
    try:
        store = AssessmentStore()
        
        # Get repository from database
        repo_data = store.get_repository(repo_url)
        
        if not repo_data:
            raise HTTPException(status_code=404, detail=f"Repository not found: {repo_url}")
        
        # Trigger assessment in background
        runner = AssessmentRunner()
        background_tasks.add_task(
            runner.run_assessment,
            repo_data.get("repo_url"),
            repo_data.get("name", "Unknown"),
            repo_data.get("primary_language", "Unknown"),
        )
        
        return {
            "message": "Assessment triggered",
            "repo_url": repo_url,
            "status": "queued"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in reassess_repository: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to trigger reassessment: {str(e)}")


@router.delete("/repositories/{repo_url_encoded}", status_code=204)
async def delete_repository(repo_url_encoded: str):
    """Delete a repository.

    Args:
        repo_url_encoded: URL-encoded repository URL
    """
    repo_url = unquote(repo_url_encoded)
    # Note: Would implement cascade delete of assessments
    pass
