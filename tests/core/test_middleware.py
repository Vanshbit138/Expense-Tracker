"""
Tests for middleware module.
"""

from unittest.mock import MagicMock

import pytest

from src.core.middleware import RequestLoggingMiddleware, UserContextMiddleware


class TestRequestLoggingMiddleware:
    """Test cases for RequestLoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_request_logging_middleware_dispatch(self):
        """Test RequestLoggingMiddleware dispatch method."""
        middleware = RequestLoggingMiddleware(app=MagicMock())

        # Create mock request
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com/api/test"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create async call_next mock
        async def mock_call_next(request):
            return mock_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response == mock_response
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_request_logging_middleware_no_client(self):
        """Test RequestLoggingMiddleware when request has no client."""
        middleware = RequestLoggingMiddleware(app=MagicMock())

        # Create mock request without client
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url = "http://test.com/api/create"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.client = None

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 201

        # Create async call_next mock
        async def mock_call_next(request):
            return mock_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response == mock_response
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_request_logging_middleware_error_response(self):
        """Test RequestLoggingMiddleware with error response."""
        middleware = RequestLoggingMiddleware(app=MagicMock())

        # Create mock request
        mock_request = MagicMock()
        mock_request.method = "DELETE"
        mock_request.url = "http://test.com/api/delete/123"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.client = MagicMock()
        mock_request.client.host = "192.168.1.1"

        # Create mock error response
        mock_response = MagicMock()
        mock_response.status_code = 404

        # Create async call_next mock
        async def mock_call_next(request):
            return mock_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response == mock_response
        assert response.status_code == 404


class TestUserContextMiddleware:
    """Test cases for UserContextMiddleware."""

    @pytest.mark.asyncio
    async def test_user_context_middleware_dispatch(self):
        """Test UserContextMiddleware dispatch method."""
        middleware = UserContextMiddleware(app=MagicMock())

        # Create mock request
        mock_request = MagicMock()

        # Create mock response
        mock_response = MagicMock()

        # Create async call_next mock
        async def mock_call_next(request):
            return mock_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response == mock_response

    @pytest.mark.asyncio
    async def test_user_context_middleware_passthrough(self):
        """Test UserContextMiddleware passes through without modification."""
        middleware = UserContextMiddleware(app=MagicMock())

        # Create mock request with headers
        mock_request = MagicMock()
        mock_request.headers = {"authorization": "Bearer token123"}

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create async call_next mock
        async def mock_call_next(request):
            return mock_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Should pass through unchanged
        assert response == mock_response
        assert response.status_code == 200
