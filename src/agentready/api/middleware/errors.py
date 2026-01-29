"""Error handling middleware for API.

This module provides centralized error handling and logging for all API requests.
"""

import logging
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ...storage.base import (
    DuplicateRecordError,
    RecordNotFoundError,
    StorageError,
    ValidationError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agentready.api")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and exceptions across all endpoints."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint handler

        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)
            return response

        except RecordNotFoundError as e:
            logger.warning(f"Record not found: {e}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Not Found",
                    "message": str(e),
                    "details": None,
                },
            )

        except DuplicateRecordError as e:
            logger.warning(f"Duplicate record: {e}")
            return JSONResponse(
                status_code=409,
                content={
                    "error": "Conflict",
                    "message": str(e),
                    "details": None,
                },
            )

        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(e),
                    "details": None,
                },
            )

        except StorageError as e:
            logger.error(f"Storage error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "Database operation failed",
                    "details": str(e) if logger.level == logging.DEBUG else None,
                },
            )

        except ValueError as e:
            logger.warning(f"Value error: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(e),
                    "details": None,
                },
            )

        except Exception as e:
            # Log full traceback for unexpected errors
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "details": str(e) if logger.level == logging.DEBUG else None,
                },
            )


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    logger.setLevel(numeric_level)
