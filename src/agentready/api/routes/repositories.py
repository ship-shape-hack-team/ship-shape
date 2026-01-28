"""Repository management API routes."""

from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...models.repository import Repository as QualityRepository
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
    """List all repositories.

    Args:
        limit: Maximum number of repositories to return
        offset: Number of repositories to skip
        sort_by: Field to sort by
        order: Sort order (asc or desc)

    Returns:
        List of repositories with pagination info
    """
    store = AssessmentStore()

    # Note: Full implementation would query database
    # For now, return empty list
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
    repo = repo_service.extract_repo_info(request.repo_url)

    # Store in database
    store.create_repository(
        repo_url=repo.repo_url,
        name=repo.name,
        description=repo.description,
        primary_language=repo.primary_language,
    )

    return repo.to_dict()


@router.get("/repositories/{repo_url_encoded}")
async def get_repository(repo_url_encoded: str):
    """Get repository details.

    Args:
        repo_url_encoded: URL-encoded repository URL

    Returns:
        Repository details
    """
    repo_url = unquote(repo_url_encoded)
    store = AssessmentStore()

    repo_data = store.get_repository(repo_url)

    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found")

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
