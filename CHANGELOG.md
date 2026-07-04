# Changelog

All notable changes to the GeoIdenti SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-07-03

### Added
- Engine parity methods for latest API surface:
  - `analyze_multi()` — POST `/v1/analyze/multi`
  - `search_cohort()` — GET `/v1/search/cohort`
  - `define_cohort_alias()` — POST `/v1/cohort/alias` (admin)
  - `parser_health()` — GET `/v1/parser/health`
  - `propagate_all()` — POST `/v1/propagate/all` (admin)
  - Privacy/consent methods (admin): `record_consent()`, `withdraw_consent()`,
    `export_subject()`, `rectify_subject()`, `erase_subject()`, `retention_preview()`
- `analyze()` and `analyze_multi()` now accept `jurisdiction` and `purpose`.
- `search()` now accepts geo/time filters: `near_lat`, `near_lon`, `radius_km`, `after`, `before`.

### Changed
- Version metadata aligned to `2.0.0` across package and module.
- SDK demos updated to consume the engine search envelope.

### Breaking Changes
- `search()` now returns the engine envelope object (not a plain list):
  `{ "items": [...], "applied_face_weight": float|null, "weight_source": str|null }`
- `search_vector()` now returns the same envelope object (not a plain list).
- Search result confidence field consumed from engine as `match_confidence`.

### Migration
- Before:
  `results = client.search(...); first = results[0]`
- After:
  `response = client.search(...); first = response["items"][0]`

### Notes
- Engine baseline pinned for this parity update: `eddeuser-tech/geoidenti-engine` `main` snapshot on 2026-07-03.

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