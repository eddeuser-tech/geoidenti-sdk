"""
GeoIdenti Python SDK

A client library for interacting with the GeoIdenti API for biometric
identity and geospatial metadata indexing.

Open Source Version - Excludes NDA-protected server components.
"""

import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import time


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
        retries: int = 3
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
        kwargs.setdefault('timeout', self.timeout)

        last_exception = None
        for attempt in range(self.retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
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
    ) -> Dict[str, Any]:
        """
        Scan an image for facial vectors and location data.

        Args:
            image_url: URL of the image to analyze.
            identity_name: Optional identity name hint to associate with the image.
            relationship: Optional relationship label (e.g. "spouse", "sibling").
            optional_search_field_1: Optional custom metadata field.
            city: Optional city override for geospatial metadata.
            country: Optional country override for geospatial metadata.

        Returns:
            Dictionary containing analysis results with object_id, vector_id,
            face_vector, location, timestamp, and inferred_identity (bool).

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            result = client.analyze(
                "https://example.com/photo.jpg",
                identity_name="Sarah",
                city="Seattle",
                country="USA",
            )
            print(f"Location: {result['location']['city']}")
            print(f"Inferred identity: {result['inferred_identity']}")
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

        response = self._make_request("POST", endpoint, json=payload)
        return response.json()

    def label_identity(self, vector_id: str, name: str) -> Dict[str, Any]:
        """
        Map a specific Face Vector to a human name.

        Args:
            vector_id: The unique identifier of the face vector.
            name: The human-readable name to assign (e.g., "Sarah").

        Returns:
            Dictionary confirming the label mapping.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            client.label_identity("vec-12345", "Sarah Johnson")
        """
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
    ) -> List[Dict[str, Any]]:
        """
        Search the index for matching photos.

        Args:
            identity_name: Filter by labeled person name (optional).
            city: Filter by city name (optional).
            limit: Maximum number of results to return (default: 10).
            relationship: Filter by relationship label (optional).
            optional_search_field_1: Filter by custom metadata field (optional).
            country: Filter by country name (optional).
            semantic_query: Free-text semantic search string (optional).
            face_weight: Weight (0.0–1.0) given to face similarity vs. semantic
                match when blending scores (optional).

        Returns:
            List of search results. Each item contains image_url, identity_name,
            city, confidence, region, display_name, latitude, and longitude.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            results = client.search(
                identity_name="Sarah",
                city="Seattle",
                semantic_query="park",
                face_weight=0.7,
            )
            for result in results:
                print(f"Found {result['identity_name']} in {result['city']}")
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
    ) -> List[Dict[str, Any]]:
        """
        Hybrid face+metadata search using a raw face vector.

        Args:
            face_vector: 128-dimensional face embedding to search against.
            semantic_query: Free-text semantic search string (optional).
            identity_name: Filter by labeled person name (optional).
            relationship: Filter by relationship label (optional).
            optional_search_field_1: Filter by custom metadata field (optional).
            city: Filter by city name (optional).
            country: Filter by country name (optional).
            face_weight: Weight (0.0–1.0) given to face similarity vs. semantic
                match when blending scores (optional).
            limit: Maximum number of results to return (default: 10).

        Returns:
            List of matching results, each as a dictionary with identity and
            location metadata.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            results = client.search_vector(
                face_vector=[0.1] * 128,
                semantic_query="park",
                limit=5,
            )
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

    def update_metadata(
        self,
        vector_id: str,
        name: str,
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update relationship and optional metadata for a face vector.

        Note:
            Requires admin role.

        Args:
            vector_id: Unique identifier of the face vector to update.
            name: Identity name to associate with the vector.
            relationship: Relationship label to assign (optional).
            optional_search_field_1: Custom metadata field value (optional).

        Returns:
            Dictionary confirming the metadata update.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            client.update_metadata(
                "vec-12345",
                "Sarah Johnson",
                relationship="spouse",
            )
        """
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
        identity_name: str,
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        limit: Optional[int] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Spread metadata to similar face vectors identified by vector ID.

        Note:
            Requires admin role.

        Args:
            vector_id: Source face vector whose neighbours will be updated.
            identity_name: Identity name to propagate to similar vectors.
            relationship: Relationship label to propagate (optional).
            optional_search_field_1: Custom metadata field to propagate (optional).
            similarity_threshold: Minimum cosine similarity to qualify a neighbour
                (optional, engine default used if omitted).
            limit: Maximum number of vectors to update (optional).
            dry_run: If True, simulate the operation without writing changes
                (optional).

        Returns:
            Dictionary with propagation result summary.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            result = client.propagate_label(
                "vec-12345",
                "Sarah Johnson",
                similarity_threshold=0.85,
                dry_run=True,
            )
        """
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
        identity_name: str,
        *,
        relationship: Optional[str] = None,
        optional_search_field_1: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        limit: Optional[int] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Spread metadata to similar face vectors identified by source image.

        Note:
            Requires admin role.

        Args:
            image_url: URL of the source image whose face embedding is used.
            identity_name: Identity name to propagate to similar vectors.
            relationship: Relationship label to propagate (optional).
            optional_search_field_1: Custom metadata field to propagate (optional).
            similarity_threshold: Minimum cosine similarity to qualify a neighbour
                (optional, engine default used if omitted).
            limit: Maximum number of vectors to update (optional).
            dry_run: If True, simulate the operation without writing changes
                (optional).

        Returns:
            Dictionary containing:
            - updated_count (int): Number of vectors updated.
            - vector_ids_updated (List[str]): IDs of updated vectors.
            - conflicts (List): Any conflicting existing labels encountered.
            - dry_run (bool): Whether this was a dry-run.
            - threshold_used (float): The similarity threshold applied.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            result = client.propagate_from_image(
                "https://example.com/photo.jpg",
                "Sarah Johnson",
                similarity_threshold=0.85,
                dry_run=True,
            )
            print(f"Would update {result['updated_count']} vectors")
        """
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

    def status(self) -> Dict[str, Any]:
        """
        Get API status information.

        Returns:
            Dictionary containing API status, authentication info, and role.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            status = client.status()
            print(f"API Status: {status['status']}")
        """
        endpoint = self._build_url("status")
        response = self._make_request("GET", endpoint)
        return response.json()

    def health(self) -> Dict[str, Any]:
        """
        Get health check information (no authentication required).

        Returns:
            Dictionary containing health status, version, and timestamp.

        Raises:
            requests.HTTPError: If the health check fails.

        Example:
            health = client.health()
            print(f"Service is {health['status']}")
        """
        endpoint = self._build_url("health", base_url=self.health_base_url)
        # Health endpoint doesn't require authentication
        response = requests.get(
            endpoint,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

__version__ = "1.1.0"
