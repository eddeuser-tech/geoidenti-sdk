# GeoIdenti Python SDK

[![PyPI version](https://badge.fury.io/py/geoidenti-sdk.svg)](https://pypi.org/project/geoidenti-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/geoidenti-sdk.svg)](https://pypi.org/project/geoidenti-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for the GeoIdenti API - high-speed biometric identity and geospatial metadata synthesis.

## Features

- 🚀 **High-Performance**: Sync client with retry logic and timeouts
- 🔒 **Secure**: JWT authentication with automatic token handling
- 🗺️ **Geospatial**: Built-in support for location-based search and filtering
- 👤 **Biometric**: Face recognition and identity labeling capabilities
- 📊 **Monitoring**: Health checks and status monitoring
- 🛡️ **Production-Ready**: Comprehensive error handling and logging

## Installation

```bash
pip install geoidenti-sdk
```

Or install from source:

```bash
git clone https://github.com/eddeuser-tech/geoidenti-sdk.git
cd geoidenti-sdk
pip install -e .
```

## Quick Start

```python
from geoidenti_sdk import GeoIdenti

# Initialize the client
client = GeoIdenti(
    api_key="your-jwt-access-token",
    base_url="https://api.geoidenti.com/v1"  # Optional, defaults to production
)

# Analyze an image for faces and location
result = client.analyze(image_url="https://example.com/photo.jpg")
print(f"Found face at {result['location']['city']}, {result['location']['country']}")

# Label a face vector with a human name
client.label_identity(vector_id=result['vector_id'], name="Sarah Johnson")

# Search for photos by identity or location
results = client.search(identity_name="Sarah", city="Seattle", limit=20)
for photo in results:
    print(f"Found {photo['identity_name']} in {photo['city']}")

# Check API status
status = client.status()
print(f"API Status: {status['status']}")

# Health check (no auth required)
health = client.health()
print(f"Service health: {health['status']}")
```

## API Reference

### Initialization

```python
client = GeoIdenti(
    api_key="your-jwt-token",           # Required: JWT access token
    base_url="https://api.example.com/v1",  # Optional: API endpoint
    timeout=30.0,                       # Optional: Request timeout in seconds
    retries=3                           # Optional: Number of retries on failure
)
```

### Methods

#### `analyze(image_url, *, identity_name=None, relationship=None, optional_search_field_1=None, city=None, country=None) -> Dict[str, Any]`

Analyzes an image for facial features and geospatial metadata.

**Parameters:**
- `image_url` (str): URL of the image to analyze
- `identity_name` (str, optional): Identity name hint to associate with the image
- `relationship` (str, optional): Relationship label (e.g. `"spouse"`, `"sibling"`)
- `optional_search_field_1` (str, optional): Custom metadata field
- `city` (str, optional): City override for geospatial metadata
- `country` (str, optional): Country override for geospatial metadata

**Returns:** Dictionary containing:
- `object_id`: Unique object identifier
- `vector_id`: Face vector identifier
- `face_vector`: 128-dimensional face embedding
- `location`: Geospatial metadata (city, country, coordinates)
- `timestamp`: Analysis timestamp
- `inferred_identity` (bool): Whether the identity was inferred by the engine

**Example:**
```python
result = client.analyze(
    "https://example.com/vacation.jpg",
    identity_name="Sarah",
    city="Seattle",
    country="USA",
)
print(f"Face found in {result['location']['city']}")
print(f"Inferred identity: {result['inferred_identity']}")
```

#### `label_identity(vector_id, name) -> Dict[str, Any]`

Assigns a human-readable name to a face vector.

> **Requires admin role.**

**Parameters:**
- `vector_id` (str): Unique identifier of the face vector
- `name` (str): Human-readable name (e.g., "Sarah Johnson")

**Returns:** Confirmation of the labeling operation

**Example:**
```python
client.label_identity("vec-12345", "John Smith")
```

#### `search(identity_name=None, city=None, limit=10, *, relationship=None, optional_search_field_1=None, country=None, semantic_query=None, face_weight=None) -> List[Dict]`

Searches the biometric index for matching photos.

**Parameters:**
- `identity_name` (str, optional): Filter by person name
- `city` (str, optional): Filter by city name
- `limit` (int, optional): Maximum results (default: 10)
- `relationship` (str, optional): Filter by relationship label
- `optional_search_field_1` (str, optional): Filter by custom metadata field
- `country` (str, optional): Filter by country name
- `semantic_query` (str, optional): Free-text semantic search string
- `face_weight` (float, optional): Weight (0.0–1.0) given to face similarity vs. semantic match

**Returns:** List of matching photos. Each item contains:
- `image_url`, `identity_name`, `city`, `confidence`
- `region`, `display_name`, `latitude`, `longitude`

**Example:**
```python
photos = client.search(
    identity_name="Sarah",
    city="Seattle",
    semantic_query="park",
    face_weight=0.7,
)
for photo in photos:
    print(f"Found {photo['identity_name']} at {photo['image_url']}")
```

#### `search_vector(face_vector, *, semantic_query=None, identity_name=None, relationship=None, optional_search_field_1=None, city=None, country=None, face_weight=None, limit=10) -> List[Dict]`

Hybrid face+metadata search using a raw 128-dimensional face vector.

**Parameters:**
- `face_vector` (List[float]): 128-dimensional face embedding to search against
- `semantic_query` (str, optional): Free-text semantic search string
- `identity_name` (str, optional): Filter by person name
- `relationship` (str, optional): Filter by relationship label
- `optional_search_field_1` (str, optional): Filter by custom metadata field
- `city` (str, optional): Filter by city name
- `country` (str, optional): Filter by country name
- `face_weight` (float, optional): Weight (0.0–1.0) given to face similarity vs. semantic match
- `limit` (int, optional): Maximum results (default: 10)

**Returns:** List of matching results with identity and location metadata

**Example:**
```python
results = client.search_vector(
    face_vector=[0.1] * 128,
    semantic_query="park",
    city="Seattle",
    limit=5,
)
```

#### `update_metadata(vector_id, name, *, relationship=None, optional_search_field_1=None) -> Dict[str, Any]`

Updates relationship and optional metadata fields for a face vector.

> **Requires admin role.**

**Parameters:**
- `vector_id` (str): Unique identifier of the face vector to update
- `name` (str): Identity name to associate with the vector
- `relationship` (str, optional): Relationship label to assign
- `optional_search_field_1` (str, optional): Custom metadata field value

**Returns:** Dictionary confirming the metadata update

**Example:**
```python
client.update_metadata(
    "vec-12345",
    "Sarah Johnson",
    relationship="spouse",
    optional_search_field_1="badge-99",
)
```

#### `propagate_label(vector_id, identity_name, *, relationship=None, optional_search_field_1=None, similarity_threshold=None, limit=None, dry_run=None) -> Dict[str, Any]`

Spreads metadata to similar face vectors identified by a source vector ID.

> **Requires admin role.**

**Parameters:**
- `vector_id` (str): Source face vector whose neighbours will be updated
- `identity_name` (str): Identity name to propagate to similar vectors
- `relationship` (str, optional): Relationship label to propagate
- `optional_search_field_1` (str, optional): Custom metadata field to propagate
- `similarity_threshold` (float, optional): Minimum cosine similarity to qualify a neighbour
- `limit` (int, optional): Maximum number of vectors to update
- `dry_run` (bool, optional): If `True`, simulate without writing changes

**Returns:** Dictionary with propagation result summary

**Example:**
```python
result = client.propagate_label(
    "vec-12345",
    "Sarah Johnson",
    similarity_threshold=0.85,
    dry_run=True,
)
print(f"Would update {result['updated_count']} vectors")
```

#### `propagate_from_image(image_url, identity_name, *, relationship=None, optional_search_field_1=None, similarity_threshold=None, limit=None, dry_run=None) -> Dict[str, Any]`

Spreads metadata to similar face vectors identified by a source image.

> **Requires admin role.**

**Parameters:**
- `image_url` (str): URL of the source image whose face embedding is used
- `identity_name` (str): Identity name to propagate to similar vectors
- `relationship` (str, optional): Relationship label to propagate
- `optional_search_field_1` (str, optional): Custom metadata field to propagate
- `similarity_threshold` (float, optional): Minimum cosine similarity to qualify a neighbour
- `limit` (int, optional): Maximum number of vectors to update
- `dry_run` (bool, optional): If `True`, simulate without writing changes

**Returns:** Dictionary containing:
- `updated_count` (int): Number of vectors updated
- `vector_ids_updated` (List[str]): IDs of updated vectors
- `conflicts` (List): Conflicting existing labels encountered
- `dry_run` (bool): Whether this was a dry-run
- `threshold_used` (float): The similarity threshold applied

**Example:**
```python
result = client.propagate_from_image(
    "https://example.com/photo.jpg",
    "Sarah Johnson",
    similarity_threshold=0.85,
    dry_run=False,
)
print(f"Updated {result['updated_count']} vectors")
print(f"IDs: {result['vector_ids_updated']}")
```

#### `status() -> Dict[str, Any]`

Retrieves API status and authentication information.

**Returns:** API status, user role, and authentication details

#### `health() -> Dict[str, Any]`

Performs a health check (no authentication required).

**Returns:** Service health status and version information

## Error Handling

The SDK includes comprehensive error handling:

```python
from geoidenti_sdk import GeoIdenti
import requests

client = GeoIdenti(api_key="your-token")

try:
    result = client.analyze("https://example.com/image.jpg")
except requests.exceptions.HTTPError as e:
    print(f"API returned an error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## Configuration

### Environment Variables

- `GEOIDENTI_API_KEY`: Your JWT access token
- `GEOIDENTI_BASE_URL`: API endpoint (default: production)

### Configuration Example

```python
import os
from geoidenti_sdk import GeoIdenti

client = GeoIdenti(
    api_key=os.getenv("GEOIDENTI_API_KEY"),
    base_url=os.getenv("GEOIDENTI_BASE_URL", "https://api.geoidenti.com/v1"),
    timeout=60.0,
    retries=5
)
```

### Advanced Configuration

```python
# Custom timeout and retry settings
client = GeoIdenti(
    api_key="your-token",
    timeout=60.0,    # 60 second timeout
    retries=5        # Retry up to 5 times
)
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/eddeuser-tech/geoidenti-sdk.git
cd geoidenti-sdk
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
black geoidenti_sdk/
isort geoidenti_sdk/
flake8 geoidenti_sdk/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://geoidenti-sdk.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/eddeuser-tech/geoidenti-sdk/issues)
- 💬 [Discussions](https://github.com/eddeuser-tech/geoidenti-sdk/discussions)

## Security

If you discover a security vulnerability, please email security@geoidenti.com instead of creating a public issue.

## Changelog

### v1.1.0 (2026-04-18)
- Added `search_vector()` — hybrid face+metadata search via POST /v1/search/vector
- Added `update_metadata()` — update identity name, relationship, and optional metadata (admin)
- Added `propagate_label()` — spread metadata to similar vectors by source vector ID (admin)
- Added `propagate_from_image()` — spread metadata to similar vectors by source image (admin)
- Extended `analyze()` with optional `identity_name`, `relationship`, `optional_search_field_1`, `city`, `country` params
- Extended `search()` with optional `relationship`, `optional_search_field_1`, `country`, `semantic_query`, `face_weight` params
- Documented `inferred_identity` field in `analyze()` response
- Documented `region`, `display_name`, `latitude`, `longitude` fields in `search()` response
- Admin role requirement noted for `label_identity`, `update_metadata`, `propagate_label`, `propagate_from_image`

### v1.0.0 (2026-04-09)
- Initial open source release
- Complete API client implementation
- Comprehensive error handling and retry logic
- Production-ready authentication and timeout handling</content>
<parameter name="filePath">/Users/kristideuser/geoidenti-engine/geoidenti-sdk/README.md