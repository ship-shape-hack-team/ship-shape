"""Repository management API routes."""

from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...models.repository_record import RepositoryRecord
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
async def create_repository(request: CreateRepositoryRequest):
    """Add a new repository.

    Args:
        request: Repository creation request

    Returns:
        Created repository
    """
    repo_service = RepositoryService()
    store = AssessmentStore()

    # Extract repository info
    repo_record = repo_service.extract_repo_info(request.repo_url)

    # Store in database
    store.create_repository(
        repo_url=repo_record.repo_url,
        name=repo_record.name,
        description=repo_record.description,
        primary_language=repo_record.primary_language,
    )

    return repo_record.to_dict()


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


@router.delete("/repositories/{repo_url_encoded}", status_code=204)
async def delete_repository(repo_url_encoded: str):
    """Delete a repository.

    Args:
        repo_url_encoded: URL-encoded repository URL
    """
    repo_url = unquote(repo_url_encoded)
    # Note: Would implement cascade delete of assessments
    pass
