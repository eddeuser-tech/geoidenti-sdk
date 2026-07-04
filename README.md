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
response = client.search(identity_name="Sarah", city="Seattle", limit=20)
for photo in response["items"]:
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

#### Demo coverage

- `demo.py` is a quick walkthrough for `health`, `status`, `analyze`, `label_identity`, `search`, and `search_vector`.
- `integration/image_url_demo.py` is an admin pipeline demo for analyze/label/
  propagate/search workflows.
- Cohort and privacy methods are available in the SDK and documented below, but
  not exercised end-to-end in the quick demo.
- If your engine enforces strict roles, use an admin token for methods in the **Admin methods** section.

## Breaking Change (v2.0.0)

- `search()` and `search_vector()` return the engine response envelope instead
  of plain lists.

```python
# v1.x
results = client.search(identity_name="Sarah")
first = results[0]

# v2.x
response = client.search(identity_name="Sarah")
first = response["items"][0]
```

### Analyst / standard methods

#### `analyze(image_url, *, identity_name=None, relationship=None, optional_search_field_1=None, city=None, country=None, jurisdiction=None, purpose=None) -> Dict[str, Any]`

Analyze an image for biometric and geospatial metadata.

**Parameters:**
- `image_url` (str): URL of the image to analyze
- `identity_name` (str, optional): Identity hint to associate with the image
- `relationship` (str, optional): Relationship label
- `optional_search_field_1` (str, optional): Custom metadata field
- `city`, `country` (str, optional): Geospatial overrides
- `jurisdiction` (str, optional): Privacy jurisdiction code
- `purpose` (str, optional): Processing purpose label

**Returns:** Analysis envelope that may include `object_id`, `vector_id`,
`face_vector`, `location`, `timestamp`, and `inferred_identity`.

#### `analyze_multi(image_url, *, identity_name=None, relationship=None, optional_search_field_1=None, city=None, country=None, jurisdiction=None, purpose=None) -> Dict[str, Any]`

Analyze an image and return one record per detected face.

#### `search(identity_name=None, city=None, limit=10, *, relationship=None, optional_search_field_1=None, country=None, semantic_query=None, face_weight=None, near_lat=None, near_lon=None, radius_km=None, after=None, before=None) -> Dict[str, Any]`

Search photos by identity, location, metadata, semantic query, and geo/time
filters.

**Returns:** Search response envelope:
- `items`: List of matches
- `applied_face_weight`: Effective face weight used by engine
- `weight_source`: `explicit`, `adaptive`, or `default`

Each item may include fields like `image_url`, `identity_name`, `city`,
`match_confidence`, `region`, `display_name`, `latitude`, and `longitude`.

#### `search_vector(face_vector, *, semantic_query=None, identity_name=None, relationship=None, optional_search_field_1=None, city=None, country=None, face_weight=None, limit=10) -> Dict[str, Any]`

Hybrid face+semantic+metadata search using a raw 128-d face vector.

**Returns:** Same envelope as `search()`.

#### `search_cohort(identity_name=None, *, match="all", cohort_alias=None, semantic_query=None, near_lat=None, near_lon=None, radius_km=None, after=None, before=None, limit=20) -> Dict[str, Any]`

Search photos containing groups of identities, with optional alias and
geo/time/semantic filters.

Example full cohort alias flow:

```python
# 1) define the cohort alias (admin-capable token required)
client.define_cohort_alias("incident_team_alpha", ["Alex Rivera", "Jordan Lee"])

# 2) search by alias
response = client.search_cohort(
    cohort_alias="incident_team_alpha",
    match="all",
    semantic_query="parking garage",
    limit=20,
)

for item in response.get("items", []):
    print(item.get("identity_name"), item.get("image_url"))
```

#### `parser_health() -> Dict[str, Any]`

Get parser subsystem health and backend status.

```python
health = client.parser_health()
print(health.get("fast_path", {}).get("status"))
print(health.get("llm", {}).get("status"))
```

#### `status() -> Dict[str, Any]`

Get authenticated API status.

#### `health() -> Dict[str, Any]`

Health check endpoint (no authentication required).

### Admin methods

All methods in this section require an admin-capable token.

#### `label_identity(vector_id, name) -> Dict[str, Any]`

Map a face vector to a human-readable identity name.

#### `update_metadata(vector_id, name, *, relationship=None, optional_search_field_1=None) -> Dict[str, Any]`

Update relationship and optional metadata for a face vector.

#### `propagate_label(vector_id, identity_name, *, relationship=None, optional_search_field_1=None, similarity_threshold=None, limit=None, dry_run=None) -> Dict[str, Any]`

Propagate metadata to similar vectors from a source vector.

#### `propagate_from_image(image_url, identity_name, *, relationship=None, optional_search_field_1=None, similarity_threshold=None, limit=None, dry_run=None) -> Dict[str, Any]`

Propagate metadata to similar vectors from a source image.

#### `propagate_all(*, threshold=None, limit=None, dry_run=None) -> Dict[str, Any]`

Re-propagate identity metadata across all labeled identities.

```python
result = client.propagate_all(threshold=0.4, limit=500, dry_run=True)
print(result.get("identities_processed"), result.get("total_updated"))
```

#### `define_cohort_alias(alias_name, identity_names) -> Dict[str, Any]`

Create or update a named cohort alias.

#### `record_consent(subject_id, lawful_basis, purpose, jurisdiction) -> Dict[str, Any]`

Record consent and lawful basis for a subject.

```python
result = client.record_consent(
    subject_id="subject-123",
    lawful_basis="consent",
    purpose="verification",
    jurisdiction="EU",
)
print(result)
```

#### `withdraw_consent(subject_id) -> Dict[str, Any]`

Withdraw consent and queue erasure workflow.

#### `export_subject(subject_id, *, include_vectors=False) -> Dict[str, Any]`

Export subject data.

#### `rectify_subject(subject_id, *, identity_name=None, relationship=None, optional_search_field_1=None, city=None, region=None, country=None, display_name=None, purpose=None, jurisdiction=None) -> Dict[str, Any]`

Rectify subject metadata fields across stored records.

#### `erase_subject(subject_id) -> Dict[str, Any]`

Erase all retained data for a subject.

#### `retention_preview() -> Dict[str, Any]`

Preview retention-policy purge candidates.

### Engine baseline

This v2 parity update is aligned to engine commit
`a86595c69035018f2fef3b9d91f42002cb26ad82`.

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
python3 -m pytest tests/
```

### Code Quality

```bash
python3 -m black geoidenti_sdk/ tests demo.py integration/image_url_demo.py
python3 -m isort geoidenti_sdk/ tests
python3 -m flake8 geoidenti_sdk/
python3 -m pytest --cov=geoidenti_sdk --cov-report=html
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

See [CHANGELOG.md](CHANGELOG.md) for complete release history.