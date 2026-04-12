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

#### `analyze(image_url: str) -> Dict[str, Any]`

Analyzes an image for facial features and geospatial metadata.

**Parameters:**
- `image_url` (str): URL of the image to analyze

**Returns:** Dictionary containing:
- `object_id`: Unique object identifier
- `vector_id`: Face vector identifier
- `face_vector`: 128-dimensional face embedding
- `location`: Geospatial metadata (city, country, coordinates)
- `timestamp`: Analysis timestamp

**Example:**
```python
result = client.analyze("https://example.com/vacation.jpg")
print(f"Face found in {result['location']['city']}")
```

#### `label_identity(vector_id: str, name: str) -> Dict[str, Any]`

Assigns a human-readable name to a face vector.

**Parameters:**
- `vector_id` (str): Unique identifier of the face vector
- `name` (str): Human-readable name (e.g., "Sarah Johnson")

**Returns:** Confirmation of the labeling operation

**Example:**
```python
client.label_identity("vec-12345", "John Smith")
```

#### `search(identity_name=None, city=None, limit=10) -> List[Dict]`

Searches the biometric index for matching photos.

**Parameters:**
- `identity_name` (str, optional): Filter by person name
- `city` (str, optional): Filter by city name
- `limit` (int, optional): Maximum results (default: 10)

**Returns:** List of matching photos with metadata

**Example:**
```python
photos = client.search(identity_name="Sarah", city="Seattle")
for photo in photos:
    print(f"Found {photo['identity_name']} at {photo['image_url']}")
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

### v1.0.0 (2026-04-09)
- Initial open source release
- Complete API client implementation
- Comprehensive error handling and retry logic
- Production-ready authentication and timeout handling</content>
<parameter name="filePath">/Users/kristideuser/geoidenti-engine/geoidenti-sdk/README.md