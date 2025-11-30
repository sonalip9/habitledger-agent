"""
Unit tests for FastAPI application.

Tests the REST API endpoints for HabitLedger Cloud Run deployment.
"""

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_api_info(self):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "HabitLedger" in data["name"]
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"

    def test_root_includes_endpoints(self):
        """Test root endpoint includes endpoint list."""
        response = client.get("/")
        data = response.json()
        assert "endpoints" in data
        assert "chat" in data["endpoints"]
        assert "health" in data["endpoints"]
        assert "docs" in data["endpoints"]


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_returns_healthy(self):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "habitledger-agent"


class TestChatEndpoint:
    """Tests for chat endpoint."""

    @pytest.mark.asyncio
    async def test_chat_with_valid_request(self):
        """Test chat endpoint with valid request."""
        response = client.post(
            "/chat",
            json={"user_id": "test_user", "message": "I want to save money"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert "response" in data
        assert "session_id" in data
        assert data["status"] == "success"

    def test_chat_with_missing_user_id(self):
        """Test chat endpoint with missing user_id field."""
        response = client.post("/chat", json={"message": "I want to save money"})
        assert response.status_code == 422  # Validation error

    def test_chat_with_missing_message(self):
        """Test chat endpoint with missing message field."""
        response = client.post("/chat", json={"user_id": "test_user"})
        assert response.status_code == 422  # Validation error

    def test_chat_with_empty_body(self):
        """Test chat endpoint with empty request body."""
        response = client.post("/chat", json={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_with_different_users(self):
        """Test chat endpoint maintains separate sessions for different users."""
        # First user
        response1 = client.post(
            "/chat",
            json={
                "user_id": "user_1",
                "message": "I keep ordering food delivery",
            },
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["user_id"] == "user_1"

        # Second user
        response2 = client.post(
            "/chat",
            json={"user_id": "user_2", "message": "I want to start investing"},
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["user_id"] == "user_2"

        # Sessions should be different
        assert data1["session_id"] != data2["session_id"]

    @pytest.mark.asyncio
    async def test_chat_response_structure(self):
        """Test chat endpoint returns correctly structured response."""
        response = client.post(
            "/chat",
            json={
                "user_id": "structure_test",
                "message": "I spend too much on impulse purchases",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify all required fields
        assert "user_id" in data
        assert "response" in data
        assert "session_id" in data
        assert "status" in data

        # Verify types
        assert isinstance(data["user_id"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["session_id"], str)
        assert isinstance(data["status"], str)

        # Verify response is not empty
        assert len(data["response"]) > 0


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""

    def test_openapi_schema_available(self):
        """Test OpenAPI schema endpoint is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "HabitLedger Agent API"

    def test_swagger_ui_available(self):
        """Test Swagger UI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert b"Swagger UI" in response.content or b"swagger" in response.content

    def test_redoc_available(self):
        """Test ReDoc documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert b"ReDoc" in response.content or b"redoc" in response.content


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self):
        """Test CORS headers are present in responses."""
        response = client.options(
            "/chat",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        # CORS middleware should handle OPTIONS requests
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_post(self):
        """Test CORS allows POST requests."""
        response = client.post(
            "/health",
            headers={"Origin": "https://example.com"},
        )
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_endpoint_returns_404(self):
        """Test accessing non-existent endpoint returns 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_method_returns_405(self):
        """Test using wrong HTTP method returns 405."""
        response = client.put("/health")
        assert response.status_code == 405

    def test_malformed_json_returns_422(self):
        """Test sending malformed JSON returns 422."""
        response = client.post(
            "/chat",
            data="not valid json",  # type: ignore
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
