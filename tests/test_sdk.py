"""Tests for GeoIdenti SDK."""

from unittest.mock import Mock, patch

import pytest
import requests

from geoidenti_sdk import GeoIdenti, __version__


class TestGeoIdenti:
    """Test cases for the GeoIdenti client."""

    def test_initialization(self):
        client = GeoIdenti(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.geoidenti.com/v1/"
        assert client.timeout == 30.0
        assert client.retries == 3

    def test_initialization_custom_params(self):
        client = GeoIdenti(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            timeout=60.0,
            retries=5,
        )
        assert client.base_url == "https://custom.api.com/v1/"
        assert client.timeout == 60.0
        assert client.retries == 5

    def test_version(self):
        assert __version__ == "2.0.0"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_analyze_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "object_id": "test-object",
            "vector_id": "test-vector",
            "face_vector": [0.1] * 128,
            "location": {"city": "Seattle", "country": "USA"},
            "timestamp": "2026-04-09T12:00:00Z",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.analyze("https://example.com/image.jpg")

        assert result["object_id"] == "test-object"
        assert result["location"]["city"] == "Seattle"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_analyze_with_privacy_fields(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True}
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        client.analyze(
            "https://example.com/image.jpg",
            jurisdiction="EU",
            purpose="investigation",
        )

        _args, kwargs = mock_request.call_args
        payload = kwargs["json"]
        assert payload["jurisdiction"] == "EU"
        assert payload["purpose"] == "investigation"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_analyze_multi_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "faces": [{"vector_id": "vec-1"}],
            "faces_detected": 1,
            "faces_stored": 1,
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.analyze_multi("https://example.com/group.jpg")

        _args, _kwargs = mock_request.call_args
        assert _args[0] == "POST"
        assert _args[1].endswith("/analyze/multi")
        assert result["faces_detected"] == 1

    @patch("geoidenti_sdk.requests.Session.request")
    def test_search_envelope_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "items": [
                {
                    "image_url": "https://example.com/photo1.jpg",
                    "identity_name": "Sarah",
                    "city": "Seattle",
                    "match_confidence": 0.95,
                }
            ],
            "applied_face_weight": 0.62,
            "weight_source": "adaptive",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        results = client.search(identity_name="Sarah", city="Seattle", limit=10)

        assert len(results["items"]) == 1
        assert results["items"][0]["identity_name"] == "Sarah"
        assert results["weight_source"] == "adaptive"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_search_geo_time_params(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"items": []}
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        client.search(
            semantic_query="beach",
            near_lat=47.6,
            near_lon=-122.3,
            radius_km=10.0,
            after="2024-01-01",
            before="2024-12-31",
        )

        _args, kwargs = mock_request.call_args
        params = kwargs["params"]
        assert params["near_lat"] == 47.6
        assert params["near_lon"] == -122.3
        assert params["radius_km"] == 10.0
        assert params["after"] == "2024-01-01"
        assert params["before"] == "2024-12-31"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_search_vector_envelope_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "items": [
                {
                    "identity_name": "Sarah",
                    "match_confidence": 0.92,
                    "city": "Seattle",
                }
            ],
            "applied_face_weight": 0.7,
            "weight_source": "explicit",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        results = client.search_vector([0.1] * 128, semantic_query="park", limit=5)

        _args, kwargs = mock_request.call_args
        payload = kwargs["json"]
        assert _args[0] == "POST"
        assert _args[1].endswith("/search/vector")
        assert len(payload["face_vector"]) == 128
        assert payload["semantic_query"] == "park"
        assert payload["limit"] == 5
        assert isinstance(results["items"], list)
        assert results["items"][0]["identity_name"] == "Sarah"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_parser_health_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "fast_path": {"status": "ok"},
            "llm": {"status": "disabled"},
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.parser_health()

        _args, _kwargs = mock_request.call_args
        assert _args[0] == "GET"
        assert _args[1].endswith("/parser/health")
        assert result["fast_path"]["status"] == "ok"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_propagate_all_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "identities_processed": 2,
            "total_updated": 4,
            "total_conflicts": 0,
            "results": {},
            "dry_run": False,
            "threshold_used": 0.4,
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.propagate_all(threshold=0.4, limit=500, dry_run=False)

        _args, kwargs = mock_request.call_args
        assert _args[0] == "POST"
        assert _args[1].endswith("/propagate/all")
        assert kwargs["json"]["threshold"] == 0.4
        assert result["identities_processed"] == 2

    @patch("geoidenti_sdk.requests.Session.request")
    def test_search_cohort_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "items": [],
            "cohort": ["Alice", "Bob"],
            "match": "all",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.search_cohort(identity_name=["Alice", "Bob"], match="all")

        _args, kwargs = mock_request.call_args
        assert _args[0] == "GET"
        assert _args[1].endswith("/search/cohort")
        assert kwargs["params"]["identity_name"] == ["Alice", "Bob"]
        assert result["match"] == "all"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_define_cohort_alias_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b""
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.define_cohort_alias("parents", ["Alice", "Bob"])

        _args, kwargs = mock_request.call_args
        assert _args[0] == "POST"
        assert _args[1].endswith("/cohort/alias")
        assert kwargs["json"]["alias_name"] == "parents"
        assert result["status"] == "created"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_consent_and_privacy_methods(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True}
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")

        client.record_consent("alice", "consent", "verification", "EU")
        client.withdraw_consent("alice")
        client.export_subject("alice", include_vectors=True)
        client.rectify_subject("alice", city="Seattle")
        client.erase_subject("alice")
        client.retention_preview()

        calls = mock_request.call_args_list
        assert calls[0].args[0] == "POST"
        assert calls[0].args[1].endswith("/consent")
        assert calls[1].args[0] == "DELETE"
        assert calls[1].args[1].endswith("/consent/alice")
        assert calls[2].args[0] == "GET"
        assert calls[2].args[1].endswith("/privacy/subject/alice/export")
        assert calls[3].args[0] == "PATCH"
        assert calls[3].args[1].endswith("/privacy/subject/alice")
        assert calls[4].args[0] == "DELETE"
        assert calls[4].args[1].endswith("/privacy/subject/alice")
        assert calls[5].args[0] == "GET"
        assert calls[5].args[1].endswith("/privacy/retention/preview")

    @patch("geoidenti_sdk.requests.Session.request")
    def test_label_identity_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "vector_id": "vec-123",
            "name": "John Doe",
            "status": "updated",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.label_identity("vec-123", "John Doe")

        assert result["status"] == "updated"
        assert result["name"] == "John Doe"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_update_metadata_success(self, mock_request):
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
        result = client.update_metadata("vec-123", "Sarah", relationship="spouse")

        _args, kwargs = mock_request.call_args
        assert _args[0] == "PATCH"
        assert _args[1].endswith("/metadata")
        assert kwargs["json"]["vector_id"] == "vec-123"
        assert result["status"] == "updated"

    @patch("geoidenti_sdk.requests.Session.request")
    def test_propagate_label_success(self, mock_request):
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
        assert kwargs["json"]["vector_id"] == "vec-123"
        assert result["updated_count"] == 3

    @patch("geoidenti_sdk.requests.Session.request")
    def test_propagate_from_image_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "updated_count": 5,
            "vector_ids_updated": ["vec-1", "vec-2"],
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
        assert kwargs["json"]["image_url"] == "https://example.com/photo.jpg"
        assert result["updated_count"] == 5

    @patch("geoidenti_sdk.requests.Session.request")
    def test_status_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "healthy",
            "user": "test-user",
            "role": "analyst",
        }
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.status()

        assert result["status"] == "healthy"
        assert result["role"] == "analyst"

    @patch("geoidenti_sdk.requests.get")
    def test_health_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2026-04-09T12:00:00Z",
        }
        mock_get.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        result = client.health()

        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"

    @patch("geoidenti_sdk.requests.get")
    def test_health_with_custom_base_url(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "2.0.0",
        }
        mock_get.return_value = mock_response

        client = GeoIdenti(api_key="test-key", base_url="https://custom.api.com/v1")
        result = client.health()

        assert result["version"] == "2.0.0"
        mock_get.assert_called_once_with(
            "https://custom.api.com/health",
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )

    @patch("geoidenti_sdk.requests.Session.request")
    def test_analyze_http_error_raises(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_request.return_value = mock_response

        client = GeoIdenti(api_key="test-key")
        with pytest.raises(requests.HTTPError):
            client.analyze("https://example.com/image.jpg")

    @patch("geoidenti_sdk.requests.Session.request")
    def test_retry_logic(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "success"}
        mock_request.side_effect = [
            requests.RequestException("Network error"),
            requests.RequestException("Timeout"),
            mock_response,
        ]

        client = GeoIdenti(api_key="test-key", retries=3)
        result = client.status()

        assert result["status"] == "success"
        assert mock_request.call_count == 3

    @patch("geoidenti_sdk.requests.Session.request")
    def test_retry_logic_fails_after_max_retries(self, mock_request):
        mock_request.side_effect = requests.RequestException("Network down")

        client = GeoIdenti(api_key="test-key", retries=2)
        with pytest.raises(requests.RequestException):
            client.analyze("https://example.com/image.jpg")

        assert mock_request.call_count == 2
