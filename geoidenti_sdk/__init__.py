"""
GeoIdenti Python SDK

A client library for interacting with the GeoIdenti API for biometric
identity and geospatial metadata indexing.

Open Source Version - Excludes NDA-protected server components.
"""

import time
from typing import Any, Dict, List, Optional, TypedDict
from urllib.parse import urljoin

import requests


class SearchResponseItem(TypedDict, total=False):
    """One item in the search response envelope."""

    object_id: str
    image_url: str
    identity_name: str
    relationship: str
    optional_search_field_1: str
    city: str
    region: str
    country: str
    display_name: str
    latitude: float
    longitude: float
    match_confidence: float
    timestamp: str


class SearchResponse(TypedDict, total=False):
    """Search envelope returned by engine /v1/search* endpoints."""

    items: List[SearchResponseItem]
    applied_face_weight: Optional[float]
    weight_source: Optional[str]


class GeoIdenti:
    """
    GeoIdenti API Client for high-speed biometric and geospatial indexing.

    Provides methods for image analysis, identity labeling, vector and photo
    search, metadata management, label propagation, status checking, and
    health monitoring.

    Example:
        client = GeoIdenti(api_key="your-jwt-token")
        result = client.analyze("https://example.com/photo.jpg")
        print(f"Found face at {result['location']['city']}")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.geoidenti.com/v1",
        timeout: float = 30.0,
        retries: int = 3,
    ):
        """
        Initialize the GeoIdenti Client.

        Args:
            api_key: Your JWT access token or bearer token for API authentication.
            base_url: The API endpoint (default is production).
            timeout: Request timeout in seconds (default: 30.0).
            retries: Number of retries for failed requests (default: 3).
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.retries = retries
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.health_base_url = self.base_url
        if self.health_base_url.endswith("v1/"):
            self.health_base_url = self.health_base_url[:-3]
        self.health_base_url = self.health_base_url.rstrip("/") + "/"
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _build_url(self, path: str, base_url: Optional[str] = None) -> str:
        """
        Build a full request URL from the base URL and endpoint path.
        """
        base = self.base_url if base_url is None else base_url
        return urljoin(base, path.lstrip("/"))

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic and timeout.

        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            requests.HTTPError: If all retries fail
        """
        kwargs.setdefault("timeout", self.timeout)

        last_exception = None
        for attempt in range(self.retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as err:
                last_exception = err
                if attempt < self.retries - 1:
                    time.sleep(2**attempt)
                continue

        raise last_exception

    def analyze(
        self,
        image_url: str,
        *,
        identity_name: Optional[str] = None,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        purpose: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scan an image for facial vectors and location data.

        Args:
            image_url: URL of the image to analyze.
            identity_name: Optional identity name hint to associate with the image.
            relationship: Optional relationship label.
            optional_search_field_1: Optional custom metadata field.
            city: Optional city override for geospatial metadata.
            country: Optional country override for geospatial metadata.
            jurisdiction: Optional jurisdiction code for privacy gating.
            purpose: Optional processing purpose string.

        Returns:
            Dictionary containing analysis results.
        """
        endpoint = self._build_url("analyze")
        payload: Dict[str, Any] = {"image_url": image_url}
        if identity_name is not None:
            payload["identity_name"] = identity_name
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1
        if city is not None:
            payload["city"] = city
        if country is not None:
            payload["country"] = country
        if jurisdiction is not None:
            payload["jurisdiction"] = jurisdiction
        if purpose is not None:
            payload["purpose"] = purpose

        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def analyze_multi(
        self,
        image_url: str,
        *,
        identity_name: Optional[str] = None,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        purpose: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze an image and return one record per detected face."""
        endpoint = self._build_url("analyze/multi")
        payload: Dict[str, Any] = {"image_url": image_url}
        if identity_name is not None:
            payload["identity_name"] = identity_name
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1
        if city is not None:
            payload["city"] = city
        if country is not None:
            payload["country"] = country
        if jurisdiction is not None:
            payload["jurisdiction"] = jurisdiction
        if purpose is not None:
            payload["purpose"] = purpose

        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def label_identity(self, vector_id: str, name: str) -> Dict[str, Any]:
        """Map a specific Face Vector to a human name."""
        endpoint = self._build_url("label")
        payload = {"vector_id": vector_id, "name": name}

        response = self._make_request("PATCH", endpoint, json=payload)
        return response.json()

    def search(
        self,
        identity_name: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 10,
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        country: Optional[str] = None,
        semantic_query: Optional[str] = None,
        face_weight: Optional[float] = None,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        radius_km: Optional[float] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> SearchResponse:
        """
        Search the index for matching photos.

        Returns the engine envelope: {items, applied_face_weight, weight_source}.
        """
        endpoint = self._build_url("search")
        params: Dict[str, Any] = {"limit": limit}
        if identity_name is not None:
            params["identity_name"] = identity_name
        if city is not None:
            params["city"] = city
        if relationship is not None:
            params["relationship"] = relationship
        if optional_search_field_1 is not None:
            params["optional_search_field_1"] = optional_search_field_1
        if country is not None:
            params["country"] = country
        if semantic_query is not None:
            params["semantic_query"] = semantic_query
        if face_weight is not None:
            params["face_weight"] = face_weight
        if near_lat is not None:
            params["near_lat"] = near_lat
        if near_lon is not None:
            params["near_lon"] = near_lon
        if radius_km is not None:
            params["radius_km"] = radius_km
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        response = self._make_request("GET", endpoint, params=params)
        return response.json()

    def search_vector(
        self,
        face_vector: List[float],
        *,
        semantic_query: Optional[str] = None,
        identity_name: Optional[str] = None,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        face_weight: Optional[float] = None,
        limit: int = 10,
    ) -> SearchResponse:
        """
        Hybrid face+metadata search using a raw face vector.

        Returns the engine envelope: {items, applied_face_weight, weight_source}.
        """
        endpoint = self._build_url("search/vector")
        payload: Dict[str, Any] = {"face_vector": face_vector, "limit": limit}
        if semantic_query is not None:
            payload["semantic_query"] = semantic_query
        if identity_name is not None:
            payload["identity_name"] = identity_name
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1
        if city is not None:
            payload["city"] = city
        if country is not None:
            payload["country"] = country
        if face_weight is not None:
            payload["face_weight"] = face_weight

        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def search_cohort(
        self,
        identity_name: Optional[List[str]] = None,
        *,
        match: str = "all",
        cohort_alias: Optional[str] = None,
        semantic_query: Optional[str] = None,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        radius_km: Optional[float] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Search photos containing a cohort of identities."""
        endpoint = self._build_url("search/cohort")
        params: Dict[str, Any] = {"match": match, "limit": limit}
        if identity_name:
            params["identity_name"] = identity_name
        if cohort_alias is not None:
            params["cohort_alias"] = cohort_alias
        if semantic_query is not None:
            params["semantic_query"] = semantic_query
        if near_lat is not None:
            params["near_lat"] = near_lat
        if near_lon is not None:
            params["near_lon"] = near_lon
        if radius_km is not None:
            params["radius_km"] = radius_km
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        response = self._make_request("GET", endpoint, params=params)
        return response.json()

    def define_cohort_alias(
        self, alias_name: str, identity_names: List[str]
    ) -> Dict[str, Any]:
        """Create or update a cohort alias (admin role)."""
        endpoint = self._build_url("cohort/alias")
        payload = {"alias_name": alias_name, "identity_names": identity_names}
        response = self._make_request("POST", endpoint, json=payload)
        if response.content:
            return response.json()
        return {"status": "created"}

    def update_metadata(
        self,
        vector_id: str,
        name: str,
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update relationship and optional metadata for a face vector."""
        endpoint = self._build_url("metadata")
        payload: Dict[str, Any] = {"vector_id": vector_id, "name": name}
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1

        response = self._make_request("PATCH", endpoint, json=payload)
        return response.json()

    def propagate_label(
        self,
        vector_id: str,
        identity_name: Optional[str],
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        limit: Optional[int] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Spread metadata to similar face vectors identified by vector ID."""
        endpoint = self._build_url("label/propagate")
        payload: Dict[str, Any] = {
            "vector_id": vector_id,
            "identity_name": identity_name,
        }
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1
        if similarity_threshold is not None:
            payload["similarity_threshold"] = similarity_threshold
        if limit is not None:
            payload["limit"] = limit
        if dry_run is not None:
            payload["dry_run"] = dry_run

        response = self._make_request("PATCH", endpoint, json=payload)
        return response.json()

    def propagate_from_image(
        self,
        image_url: str,
        identity_name: Optional[str],
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        limit: Optional[int] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Spread metadata to similar face vectors identified by source image."""
        endpoint = self._build_url("analyze/propagate")
        payload: Dict[str, Any] = {
            "image_url": image_url,
            "identity_name": identity_name,
        }
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1
        if similarity_threshold is not None:
            payload["similarity_threshold"] = similarity_threshold
        if limit is not None:
            payload["limit"] = limit
        if dry_run is not None:
            payload["dry_run"] = dry_run

        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def propagate_all(
        self,
        *,
        threshold: Optional[float] = None,
        limit: Optional[int] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Re-propagate identity metadata across all labeled identities (admin)."""
        endpoint = self._build_url("propagate/all")
        payload: Dict[str, Any] = {}
        if threshold is not None:
            payload["threshold"] = threshold
        if limit is not None:
            payload["limit"] = limit
        if dry_run is not None:
            payload["dry_run"] = dry_run

        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def parser_health(self) -> Dict[str, Any]:
        """Check parser subsystem health and backend status."""
        endpoint = self._build_url("parser/health")
        response = self._make_request("GET", endpoint)
        return response.json()

    def record_consent(
        self,
        subject_id: str,
        lawful_basis: str,
        purpose: str,
        jurisdiction: str,
    ) -> Dict[str, Any]:
        """Record subject consent (admin)."""
        endpoint = self._build_url("consent")
        payload = {
            "subject_id": subject_id,
            "lawful_basis": lawful_basis,
            "purpose": purpose,
            "jurisdiction": jurisdiction,
        }
        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def withdraw_consent(self, subject_id: str) -> Dict[str, Any]:
        """Withdraw subject consent and queue erasure (admin)."""
        endpoint = self._build_url(f"consent/{subject_id}")
        response = self._make_request("DELETE", endpoint)
        return response.json()

    def export_subject(
        self, subject_id: str, *, include_vectors: bool = False
    ) -> Dict[str, Any]:
        """Export all data held for a subject (admin)."""
        endpoint = self._build_url(f"privacy/subject/{subject_id}/export")
        params = {"include_vectors": str(include_vectors).lower()}
        response = self._make_request("GET", endpoint, params=params)
        return response.json()

    def rectify_subject(
        self,
        subject_id: str,
        *,
        identity_name: Optional[str] = None,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        city: Optional[str] = None,
        region: Optional[str] = None,
        country: Optional[str] = None,
        display_name: Optional[str] = None,
        purpose: Optional[str] = None,
        jurisdiction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rectify subject metadata across stored points (admin)."""
        endpoint = self._build_url(f"privacy/subject/{subject_id}")
        payload: Dict[str, Any] = {}
        if identity_name is not None:
            payload["identity_name"] = identity_name
        if relationship is not None:
            payload["relationship"] = relationship
        if optional_search_field_1 is not None:
            payload["optional_search_field_1"] = optional_search_field_1
        if city is not None:
            payload["city"] = city
        if region is not None:
            payload["region"] = region
        if country is not None:
            payload["country"] = country
        if display_name is not None:
            payload["display_name"] = display_name
        if purpose is not None:
            payload["purpose"] = purpose
        if jurisdiction is not None:
            payload["jurisdiction"] = jurisdiction

        response = self._make_request("PATCH", endpoint, json=payload)
        return response.json()

    def erase_subject(self, subject_id: str) -> Dict[str, Any]:
        """Erase all data for a subject (admin)."""
        endpoint = self._build_url(f"privacy/subject/{subject_id}")
        response = self._make_request("DELETE", endpoint)
        return response.json()

    def retention_preview(self) -> Dict[str, Any]:
        """Preview records that would be purged by retention policy (admin)."""
        endpoint = self._build_url("privacy/retention/preview")
        response = self._make_request("GET", endpoint)
        return response.json()

    def status(self) -> Dict[str, Any]:
        """Get API status information."""
        endpoint = self._build_url("status")
        response = self._make_request("GET", endpoint)
        return response.json()

    def health(self) -> Dict[str, Any]:
        """Get health check information (no authentication required)."""
        endpoint = self._build_url("health", base_url=self.health_base_url)
        response = requests.get(
            endpoint,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()


__version__ = "2.0.0"
