"""
Middleware for request logging and user context.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request start and end."""
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())

        # Log request start
        start_time = time.time()
        logger.info(
            "Request started",
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("user-agent"),
            client_ip=request.client.host if request.client else None,
        )

        # Process request
        response = await call_next(request)

        # Log request end
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2),
        )

        return response


class UserContextMiddleware(BaseHTTPMiddleware):
    """Middleware for adding user context to logs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add user context to request."""
        # For now, we'll just pass through
        # In a real implementation, this would extract user info from JWT
        response = await call_next(request)
        return response
