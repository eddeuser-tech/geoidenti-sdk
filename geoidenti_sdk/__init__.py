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

    Provides methods for image analysis, identity labeling, photo search,
    status checking, and health monitoring.

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

    def analyze(self, image_url: str) -> Dict[str, Any]:
        """
        Scan an image for facial vectors and location data.

        Args:
            image_url: URL of the image to analyze.

        Returns:
            Dictionary containing analysis results with object_id, vector_id,
            face_vector, location, and timestamp.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            result = client.analyze("https://example.com/photo.jpg")
            print(f"Face vector: {result['face_vector'][:5]}...")
            print(f"Location: {result['location']['city']}")
        """
        endpoint = self._build_url("analyze")
        payload = {"image_url": image_url}

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
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the index for matching photos.

        Args:
            identity_name: Filter by labeled person name (optional).
            city: Filter by city name (optional).
            limit: Maximum number of results to return (default: 10).

        Returns:
            List of search results containing image URLs, confidence scores,
            and timestamps.

        Raises:
            requests.HTTPError: If the API request fails.

        Example:
            results = client.search(identity_name="Sarah", city="Seattle")
            for result in results:
                print(f"Found {result['identity_name']} in {result['city']}")
        """
        endpoint = self._build_url("search")
        params = {
            "identity_name": identity_name,
            "city": city,
            "limit": limit
        }

        response = self._make_request("GET", endpoint, params=params)
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

__version__ = "1.0.0"
