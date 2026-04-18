# Changelog

All notable changes to the GeoIdenti SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-18

### Added
- `search_vector()` — POST /v1/search/vector: hybrid face+metadata search using a raw 128-dimensional face embedding
- `update_metadata()` — PATCH /v1/metadata: update identity name, relationship, and optional metadata for a vector (admin)
- `propagate_label()` — PATCH /v1/label/propagate: spread metadata to similar vectors by source vector ID (admin)
- `propagate_from_image()` — POST /v1/analyze/propagate: spread metadata to similar vectors by source image (admin)
- `analyze()` now accepts optional `identity_name`, `relationship`, `optional_search_field_1`, `city`, `country` parameters
- `analyze()` response documents `inferred_identity` (bool) field returned by the engine
- `search()` now accepts optional `relationship`, `optional_search_field_1`, `country`, `semantic_query`, `face_weight` parameters
- `search()` response documents `region`, `display_name`, `latitude`, `longitude` fields returned by the engine
- Admin role requirement documented for `label_identity`, `update_metadata`, `propagate_label`, `propagate_from_image`

### Fixed
- `test_label_identity_success`: corrected expected status from `"labeled"` to `"updated"` to match engine response
- `None`-valued optional parameters are now omitted from request payloads and query strings (not sent as `null`)

### Breaking Changes
- None

## [1.0.0] - 2026-04-09

### Added
- Initial open source release of GeoIdenti Python SDK
- Complete API client implementation with all endpoints:
  - `analyze()` - Image analysis for faces and geospatial metadata
  - `search()` - Search photos by identity, location, or filters
  - `label_identity()` - Assign human names to face vectors
  - `status()` - API status and authentication information
  - `health()` - Service health checks (no auth required)
- Comprehensive error handling with retry logic and exponential backoff
- JWT authentication with automatic token management
- Configurable timeouts and retry policies
- Production-ready request handling with proper headers
- Type hints and comprehensive docstrings
- Full test suite with mocking and coverage reporting
- MIT license for open source distribution
- Complete documentation with examples and API reference

### Technical Details
- **Dependencies**: Only `requests>=2.25.0` for minimal footprint
- **Python Support**: 3.8, 3.9, 3.10, 3.11
- **Architecture**: Clean client library with no server dependencies
- **Security**: Input validation, timeout handling, secure defaults
- **Testing**: 100% test coverage for public API methods
- **Packaging**: Modern setuptools with pyproject.toml support

### Breaking Changes
- None (initial release)

### Deprecated
- None

### Fixed
- None

### Security
- No known security issues in initial release
- Follows secure coding practices for API clients
- No sensitive data storage or transmission</content>
<parameter name="filePath">/Users/kristideuser/geoidenti-engine/geoidenti-sdk/CHANGELOG.md