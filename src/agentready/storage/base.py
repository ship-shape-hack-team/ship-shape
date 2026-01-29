"""Base storage interface for data persistence.

This module defines the abstract base class for storage implementations,
providing a consistent interface for data access across the application.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseStore(ABC):
    """Abstract base class for storage implementations."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> str:
        """Create a new record.

        Args:
            data: Dictionary containing record data

        Returns:
            ID of created record

        Raises:
            StorageError: If creation fails
        """
        pass

    @abstractmethod
    def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a record by ID.

        Args:
            record_id: Unique identifier for the record

        Returns:
            Record data as dictionary, or None if not found
        """
        pass

    @abstractmethod
    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Update an existing record.

        Args:
            record_id: Unique identifier for the record
            data: Dictionary containing fields to update

        Returns:
            True if update successful, False if record not found

        Raises:
            StorageError: If update fails
        """
        pass

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """Delete a record.

        Args:
            record_id: Unique identifier for the record

        Returns:
            True if deletion successful, False if record not found

        Raises:
            StorageError: If deletion fails
        """
        pass

    @abstractmethod
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List records with optional filtering and pagination.

        Args:
            filters: Optional dictionary of field:value filters
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of record dictionaries
        """
        pass

    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching optional filters.

        Args:
            filters: Optional dictionary of field:value filters

        Returns:
            Number of matching records
        """
        pass


class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class RecordNotFoundError(StorageError):
    """Raised when a requested record is not found."""

    pass


class DuplicateRecordError(StorageError):
    """Raised when attempting to create a duplicate record."""

    pass


class ValidationError(StorageError):
    """Raised when record data fails validation."""

    pass
