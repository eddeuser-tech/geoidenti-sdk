"""
Tests for GeoIdenti SDK
"""

import pytest
import requests
from unittest.mock import Mock, patch
from geoidenti_sdk import GeoIdenti, __version__


class TestGeoIdenti:
    """Test cases for the GeoIdenti client."""

    def test_initialization(self):
        """Test client initialization with default parameters."""
        client = GeoIdenti(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.geoidenti.com/v1/"
        assert client.timeout == 30.0
        assert client.retries == 3

    def test_initialization_custom_params(self):
        """Test client initialization with custom parameters."""
        client = GeoIdenti(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            timeout=60.0,
            retries=5
        )
        assert client.base_url == "https://custom.api.com/v1/"
        assert client.timeout == 60.0
        assert client.retries == 5

    def test_version(self):
        """Test that version is accessible."""
        assert __version__ == "1.0.0"

    @patch('geoidenti_sdk.requests.Session.request')
    def test_analyze_success(self, mock_request):
        """Test successful analyze request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "object_id": "test-object",
            "vector_id": "test-vector",
            "face_vector": [0.1] * 128,
            "location": {"city": "Seattle", "country": "USA"},
            "timestamp": "2026-04-09T12:00:00Z"
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.analyze("https://example.com/image.jpg")

        assert result["object_id"] == "test-object"
        assert result["location"]["city"] == "Seattle"
        mock_request.assert_called_once()

    @patch('geoidenti_sdk.requests.Session.request')
    def test_search_success(self, mock_request):
        """Test successful search request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                "image_url": "https://example.com/photo1.jpg",
                "identity_name": "Sarah",
                "city": "Seattle",
                "confidence": 0.95
            }
        ]
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        results = client.search(identity_name="Sarah", city="Seattle", limit=10)

        assert len(results) == 1
        assert results[0]["identity_name"] == "Sarah"
        assert results[0]["city"] == "Seattle"

    @patch('geoidenti_sdk.requests.Session.request')
    def test_label_identity_success(self, mock_request):
        """Test successful label identity request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "vector_id": "vec-123",
            "name": "John Doe",
            "status": "labeled"
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.label_identity("vec-123", "John Doe")

        assert result["status"] == "labeled"
        assert result["name"] == "John Doe"

    @patch('geoidenti_sdk.requests.Session.request')
    def test_status_success(self, mock_request):
        """Test successful status request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "healthy",
            "user": "test-user",
            "role": "analyst"
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.status()

        assert result["status"] == "healthy"
        assert result["role"] == "analyst"

    @patch('geoidenti_sdk.requests.get')
    def test_health_success(self, mock_get):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2026-04-09T12:00:00Z"
        }
        mock_get.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.health()

        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"

    @patch('geoidenti_sdk.requests.get')
    def test_health_with_custom_base_url(self, mock_get):
        """Test health endpoint with a custom base URL."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "2.0.0"
        }
        mock_get.return_value = mock_response

        client = GeoIdenti(api_key="test-key", base_url="https://custom.api.com/v1")
        result = client.health()

        assert result["version"] == "2.0.0"
        mock_get.assert_called_once_with(
            "https://custom.api.com/health",
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )

    @patch('geoidenti_sdk.requests.Session.request')
    def test_analyze_http_error_raises(self, mock_request):
        """Test that analyze raises HTTPError on non-success status."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        with pytest.raises(requests.HTTPError):
            client.analyze("https://example.com/image.jpg")

    @patch('geoidenti_sdk.requests.Session.request')
    def test_retry_logic(self, mock_request):
        """Test that retry logic works on failures."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "success"}
        mock_request.side_effect = [
            requests.RequestException("Network error"),
            requests.RequestException("Timeout"),
            mock_response
        ]

        client = GeoIdenti(api_key="test-key", retries=3)
        result = client.status()

        assert result["status"] == "success"
        assert mock_request.call_count == 3

    @patch('geoidenti_sdk.requests.Session.request')
    def test_retry_logic_fails_after_max_retries(self, mock_request):
        """Test that repeated request failures raise after retries."""
        mock_request.side_effect = requests.RequestException("Network down")

        client = GeoIdenti(api_key="test-key", retries=2)
        with pytest.raises(requests.RequestException):
            client.analyze("https://example.com/image.jpg")

        assert mock_request.call_count == 2
