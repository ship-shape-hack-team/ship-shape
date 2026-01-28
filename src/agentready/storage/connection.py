"""Database connection and session management for quality profiling.

This module provides:
- SQLite database connection setup
- Session management with context managers
- Database initialization with schema creation
- Migration support for future PostgreSQL
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


class DatabaseConnection:
    """Manages database connections and sessions."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection.

        Args:
            database_url: Database URL. If None, uses default SQLite location.
                         Format: 'sqlite:///path/to/db.sqlite' or 'postgresql://...'
        """
        self.database_url = database_url or self._get_default_database_url()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    def _get_default_database_url(self) -> str:
        """Get default SQLite database location."""
        home = Path.home()
        data_dir = home / ".ship-shape" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "assessments.db"
        return f"sqlite:///{db_path}"

    def initialize(self) -> None:
        """Initialize database engine and session factory."""
        # Create engine with appropriate configuration
        if self.database_url.startswith("sqlite"):
            # SQLite-specific configuration
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False,  # Set to True for SQL debugging
            )
            # Enable foreign key support for SQLite
            event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        else:
            # PostgreSQL or other databases
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                echo=False,
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        """Enable foreign key constraints for SQLite."""
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    def create_schema(self) -> None:
        """Create database schema from schema.sql file."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized. Call initialize() first.")

        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        # Read and execute schema SQL
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Execute schema creation
        with self.engine.begin() as connection:
            # Split by semicolons and execute each statement
            for statement in schema_sql.split(";"):
                statement = statement.strip()
                if statement:
                    connection.execute(statement)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup.

        Yields:
            SQLAlchemy Session instance

        Example:
            with db.get_session() as session:
                result = session.query(Repository).all()
        """
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Close database connection and dispose engine."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None


# Global database instance
_db_instance: Optional[DatabaseConnection] = None


def get_database(database_url: Optional[str] = None) -> DatabaseConnection:
    """Get or create global database instance.

    Args:
        database_url: Optional database URL. Uses default if not provided.

    Returns:
        DatabaseConnection instance
    """
    global _db_instance

    if _db_instance is None:
        _db_instance = DatabaseConnection(database_url)
        _db_instance.initialize()

    return _db_instance


def initialize_database(database_url: Optional[str] = None, create_schema: bool = True) -> DatabaseConnection:
    """Initialize database with schema creation.

    Args:
        database_url: Optional database URL
        create_schema: Whether to create schema tables

    Returns:
        Initialized DatabaseConnection instance
    """
    db = get_database(database_url)

    if create_schema:
        db.create_schema()

    return db


@contextmanager
def get_db_session(database_url: Optional[str] = None) -> Generator[Session, None, None]:
    """Convenience function to get a database session.

    Args:
        database_url: Optional database URL

    Yields:
        SQLAlchemy Session instance

    Example:
        with get_db_session() as session:
            repos = session.query(Repository).all()
    """
    db = get_database(database_url)
    with db.get_session() as session:
        yield session
