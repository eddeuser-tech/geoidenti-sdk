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
        assert __version__ == "1.1.0"

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
            "status": "updated"
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.label_identity("vec-123", "John Doe")

        assert result["status"] == "updated"
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

    @patch('geoidenti_sdk.requests.Session.request')
    def test_analyze_with_optional_params(self, mock_request):
        """Test that analyze() includes all optional params in the payload."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "object_id": "obj-1",
            "vector_id": "vec-1",
            "face_vector": [0.1] * 128,
            "location": {"city": "Seattle", "country": "USA"},
            "timestamp": "2026-04-18T12:00:00Z",
            "inferred_identity": True,
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.analyze(
            "https://example.com/photo.jpg",
            identity_name="Sarah",
            relationship="spouse",
            optional_search_field_1="badge-99",
            city="Seattle",
            country="USA",
        )

        _args, kwargs = mock_request.call_args
        payload = kwargs["json"]
        assert payload["image_url"] == "https://example.com/photo.jpg"
        assert payload["identity_name"] == "Sarah"
        assert payload["relationship"] == "spouse"
        assert payload["optional_search_field_1"] == "badge-99"
        assert payload["city"] == "Seattle"
        assert payload["country"] == "USA"
        assert result["inferred_identity"] is True

    @patch('geoidenti_sdk.requests.Session.request')
    def test_search_with_optional_params(self, mock_request):
        """Test that search() forwards all optional params as query params."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                "image_url": "https://example.com/photo1.jpg",
                "identity_name": "Sarah",
                "city": "Seattle",
                "confidence": 0.95,
                "region": "Pacific Northwest",
                "display_name": "Sarah J.",
                "latitude": 47.6062,
                "longitude": -122.3321,
            }
        ]
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        results = client.search(
            identity_name="Sarah",
            relationship="spouse",
            country="USA",
            semantic_query="park",
            face_weight=0.7,
        )

        _args, kwargs = mock_request.call_args
        params = kwargs["params"]
        assert params["identity_name"] == "Sarah"
        assert params["relationship"] == "spouse"
        assert params["country"] == "USA"
        assert params["semantic_query"] == "park"
        assert params["face_weight"] == 0.7
        assert results[0]["region"] == "Pacific Northwest"
        assert results[0]["display_name"] == "Sarah J."
        assert results[0]["latitude"] == 47.6062
        assert results[0]["longitude"] == -122.3321

    @patch('geoidenti_sdk.requests.Session.request')
    def test_search_vector_success(self, mock_request):
        """Test successful search_vector request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"identity_name": "Sarah", "confidence": 0.92, "city": "Seattle"}
        ]
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        results = client.search_vector(
            [0.1] * 128,
            semantic_query="park",
            limit=5,
        )

        _args, kwargs = mock_request.call_args
        assert _args[0] == "POST"
        assert _args[1].endswith("/search/vector")
        payload = kwargs["json"]
        assert len(payload["face_vector"]) == 128
        assert payload["semantic_query"] == "park"
        assert payload["limit"] == 5
        assert isinstance(results, list)
        assert results[0]["identity_name"] == "Sarah"

    @patch('geoidenti_sdk.requests.Session.request')
    def test_update_metadata_success(self, mock_request):
        """Test successful update_metadata request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "vector_id": "vec-123",
            "name": "Sarah",
            "relationship": "spouse",
            "status": "updated",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.update_metadata(
            "vec-123", "Sarah", relationship="spouse"
        )

        _args, kwargs = mock_request.call_args
        assert _args[0] == "PATCH"
        assert _args[1].endswith("/metadata")
        payload = kwargs["json"]
        assert payload["vector_id"] == "vec-123"
        assert payload["relationship"] == "spouse"
        assert result["status"] == "updated"

    @patch('geoidenti_sdk.requests.Session.request')
    def test_propagate_label_success(self, mock_request):
        """Test successful propagate_label request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "updated_count": 3,
            "dry_run": True,
            "threshold_used": 0.85,
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.propagate_label(
            "vec-123",
            "Sarah",
            similarity_threshold=0.85,
            dry_run=True,
        )

        _args, kwargs = mock_request.call_args
        assert _args[0] == "PATCH"
        assert _args[1].endswith("/label/propagate")
        payload = kwargs["json"]
        assert payload["vector_id"] == "vec-123"
        assert payload["identity_name"] == "Sarah"
        assert payload["similarity_threshold"] == 0.85
        assert payload["dry_run"] is True
        assert result["updated_count"] == 3

    @patch('geoidenti_sdk.requests.Session.request')
    def test_propagate_from_image_success(self, mock_request):
        """Test successful propagate_from_image request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "updated_count": 5,
            "vector_ids_updated": ["vec-1", "vec-2", "vec-3", "vec-4", "vec-5"],
            "conflicts": [],
            "dry_run": True,
            "threshold_used": 0.8,
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.propagate_from_image(
            "https://example.com/photo.jpg",
            "Sarah",
            dry_run=True,
        )

        _args, kwargs = mock_request.call_args
        assert _args[0] == "POST"
        assert _args[1].endswith("/analyze/propagate")
        payload = kwargs["json"]
        assert payload["image_url"] == "https://example.com/photo.jpg"
        assert payload["identity_name"] == "Sarah"
        assert payload["dry_run"] is True
        assert result["updated_count"] == 5
        assert len(result["vector_ids_updated"]) == 5
        assert result["conflicts"] == []
        assert result["dry_run"] is True
