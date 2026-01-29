"""Assessment data store implementation.

This module provides persistent storage for quality assessment data including
repositories, assessments, assessor results, and benchmarks.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .base import (
    BaseStore,
    DuplicateRecordError,
    RecordNotFoundError,
    StorageError,
    ValidationError,
)
from .connection import get_db_session


class AssessmentStore(BaseStore):
    """Storage implementation for assessment data."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize assessment store.

        Args:
            database_url: Optional database URL. Uses default if not provided.
        """
        self.database_url = database_url

    def _serialize_json(self, data: Any) -> str:
        """Serialize data to JSON string."""
        return json.dumps(data) if data is not None else None

    def _deserialize_json(self, json_str: str) -> Any:
        """Deserialize JSON string to Python object."""
        return json.loads(json_str) if json_str else None

    def create(self, data: Dict[str, Any]) -> str:
        """Create a new assessment record.

        Args:
            data: Assessment data dictionary with keys:
                - repo_url: Repository URL (required)
                - overall_score: Score 0-100 (required)
                - status: Assessment status (required)
                - metadata: Optional metadata dict

        Returns:
            Assessment ID (UUID)

        Raises:
            ValidationError: If required fields missing or invalid
            DuplicateRecordError: If assessment already exists
            StorageError: If creation fails
        """
        # Validate required fields
        required_fields = ["repo_url", "overall_score", "status"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Required field missing: {field}")

        # Validate score range
        score = data["overall_score"]
        if not 0 <= score <= 100:
            raise ValidationError(f"Score must be 0-100, got: {score}")

        # Validate status
        valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
        status = data["status"]
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}. Must be one of: {valid_statuses}")

        # Generate UUID for assessment
        assessment_id = str(uuid.uuid4())

        try:
            with get_db_session(self.database_url) as session:
                # Serialize metadata to JSON
                metadata_json = self._serialize_json(data.get("metadata"))

                # Insert assessment
                query = text(
                    """
                    INSERT INTO assessments (id, repo_url, overall_score, status, started_at, completed_at, metadata)
                    VALUES (:id, :repo_url, :overall_score, :status, :started_at, :completed_at, :metadata)
                    """
                )

                session.execute(
                    query,
                    {
                        "id": assessment_id,
                        "repo_url": data["repo_url"],
                        "overall_score": data["overall_score"],
                        "status": data["status"],
                        "started_at": data.get("started_at", datetime.utcnow()),
                        "completed_at": data.get("completed_at"),
                        "metadata": metadata_json,
                    },
                )

                return assessment_id

        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                raise DuplicateRecordError(f"Assessment already exists for repo: {data['repo_url']}")
            raise StorageError(f"Failed to create assessment: {e}")
        except SQLAlchemyError as e:
            raise StorageError(f"Database error creating assessment: {e}")

    def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an assessment by ID.

        Args:
            record_id: Assessment UUID

        Returns:
            Assessment data dictionary, or None if not found
        """
        try:
            with get_db_session(self.database_url) as session:
                query = text(
                    """
                    SELECT id, repo_url, overall_score, status, started_at, completed_at, metadata
                    FROM assessments
                    WHERE id = :id
                    """
                )

                result = session.execute(query, {"id": record_id}).fetchone()

                if result is None:
                    return None

                return {
                    "id": result[0],
                    "repo_url": result[1],
                    "overall_score": result[2],
                    "status": result[3],
                    "started_at": result[4],
                    "completed_at": result[5],
                    "metadata": self._deserialize_json(result[6]),
                }

        except SQLAlchemyError as e:
            raise StorageError(f"Database error retrieving assessment: {e}")

    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Update an assessment record.

        Args:
            record_id: Assessment UUID
            data: Fields to update

        Returns:
            True if updated, False if not found

        Raises:
            ValidationError: If data invalid
            StorageError: If update fails
        """
        # Validate score if provided
        if "overall_score" in data:
            score = data["overall_score"]
            if not 0 <= score <= 100:
                raise ValidationError(f"Score must be 0-100, got: {score}")

        # Validate status if provided
        if "status" in data:
            valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
            status = data["status"]
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status: {status}")

        try:
            with get_db_session(self.database_url) as session:
                # Build dynamic UPDATE query
                update_fields = []
                params = {"id": record_id}

                for key, value in data.items():
                    if key in ["overall_score", "status", "completed_at"]:
                        update_fields.append(f"{key} = :{key}")
                        params[key] = value
                    elif key == "metadata":
                        update_fields.append("metadata = :metadata")
                        params["metadata"] = self._serialize_json(value)

                if not update_fields:
                    return True  # No fields to update

                query = text(
                    f"""
                    UPDATE assessments
                    SET {', '.join(update_fields)}
                    WHERE id = :id
                    """
                )

                result = session.execute(query, params)
                return result.rowcount > 0

        except SQLAlchemyError as e:
            raise StorageError(f"Database error updating assessment: {e}")

    def delete(self, record_id: str) -> bool:
        """Delete an assessment and all related data.

        Args:
            record_id: Assessment UUID

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            with get_db_session(self.database_url) as session:
                query = text("DELETE FROM assessments WHERE id = :id")
                result = session.execute(query, {"id": record_id})
                return result.rowcount > 0

        except SQLAlchemyError as e:
            raise StorageError(f"Database error deleting assessment: {e}")

    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List assessments with optional filtering.

        Args:
            filters: Optional filters (repo_url, status)
            limit: Maximum records to return
            offset: Number of records to skip

        Returns:
            List of assessment dictionaries
        """
        try:
            with get_db_session(self.database_url) as session:
                # Build query with filters
                where_clauses = []
                params = {"limit": limit, "offset": offset}

                if filters:
                    if "repo_url" in filters:
                        where_clauses.append("repo_url = :repo_url")
                        params["repo_url"] = filters["repo_url"]
                    if "status" in filters:
                        where_clauses.append("status = :status")
                        params["status"] = filters["status"]

                where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

                query = text(
                    f"""
                    SELECT id, repo_url, overall_score, status, started_at, completed_at, metadata
                    FROM assessments
                    {where_sql}
                    ORDER BY started_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                )

                results = session.execute(query, params).fetchall()

                return [
                    {
                        "id": row[0],
                        "repo_url": row[1],
                        "overall_score": row[2],
                        "status": row[3],
                        "started_at": row[4],
                        "completed_at": row[5],
                        "metadata": self._deserialize_json(row[6]),
                    }
                    for row in results
                ]

        except SQLAlchemyError as e:
            raise StorageError(f"Database error listing assessments: {e}")

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count assessments matching filters.

        Args:
            filters: Optional filters (repo_url, status)

        Returns:
            Number of matching assessments
        """
        try:
            with get_db_session(self.database_url) as session:
                # Build query with filters
                where_clauses = []
                params = {}

                if filters:
                    if "repo_url" in filters:
                        where_clauses.append("repo_url = :repo_url")
                        params["repo_url"] = filters["repo_url"]
                    if "status" in filters:
                        where_clauses.append("status = :status")
                        params["status"] = filters["status"]

                where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

                query = text(f"SELECT COUNT(*) FROM assessments {where_sql}")
                result = session.execute(query, params).fetchone()
                return result[0] if result else 0

        except SQLAlchemyError as e:
            raise StorageError(f"Database error counting assessments: {e}")

    def create_repository(self, repo_url: str, name: str, **kwargs) -> None:
        """Create or update a repository record.

        Args:
            repo_url: Repository URL (primary key)
            name: Repository name
            **kwargs: Optional fields (description, primary_language)

        Raises:
            StorageError: If creation fails
        """
        try:
            with get_db_session(self.database_url) as session:
                query = text(
                    """
                    INSERT INTO repositories (repo_url, name, description, primary_language, created_at, updated_at)
                    VALUES (:repo_url, :name, :description, :primary_language, :created_at, :updated_at)
                    ON CONFLICT(repo_url) DO UPDATE SET
                        name = :name,
                        description = :description,
                        primary_language = :primary_language,
                        updated_at = :updated_at
                    """
                )

                now = datetime.utcnow()
                session.execute(
                    query,
                    {
                        "repo_url": repo_url,
                        "name": name,
                        "description": kwargs.get("description"),
                        "primary_language": kwargs.get("primary_language"),
                        "created_at": now,
                        "updated_at": now,
                    },
                )

        except SQLAlchemyError as e:
            raise StorageError(f"Database error creating repository: {e}")

    def get_repository(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """Get repository by URL.

        Args:
            repo_url: Repository URL

        Returns:
            Repository data dictionary, or None if not found
        """
        try:
            with get_db_session(self.database_url) as session:
                query = text(
                    """
                    SELECT repo_url, name, description, primary_language, last_assessed, created_at, updated_at
                    FROM repositories
                    WHERE repo_url = :repo_url
                    """
                )

                result = session.execute(query, {"repo_url": repo_url}).fetchone()

                if result is None:
                    return None

                return {
                    "repo_url": result[0],
                    "name": result[1],
                    "description": result[2],
                    "primary_language": result[3],
                    "last_assessed": result[4],
                    "created_at": result[5],
                    "updated_at": result[6],
                }

        except SQLAlchemyError as e:
            raise StorageError(f"Database error retrieving repository: {e}")
