# Contributing to GeoIdenti SDK

Thank you for your interest in contributing to the GeoIdenti Python SDK! This document provides guidelines and information for contributors.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eddeuser-tech/geoidenti-sdk.git
   cd geoidenti-sdk
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to ensure everything works:**
   ```bash
   pytest
   ```

## Development Workflow

This repository follows a simple GitHub Flow:
- `main` is the stable production branch.
- Branch from `main` for any change.
- Open a pull request back into `main`.
- Require reviews, testing, and CI before merging.

### 1. Choose an Issue
- Check the [issue tracker](https://github.com/eddeuser-tech/geoidenti-sdk/issues) for open issues
- Comment on the issue to indicate you're working on it
- Create a new branch for your work

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Write clear, concise commit messages
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Code Quality
Run the quality checks before submitting:

```bash
# Format code
black geoidenti_sdk/
isort geoidenti_sdk/

# Lint code
flake8 geoidenti_sdk/

# Run tests with coverage
pytest --cov=geoidenti_sdk --cov-report=html
```

### 5. Submit a Pull Request
- Push your branch to GitHub
- Create a pull request with a clear description
- Reference any related issues
- Ensure all CI checks pass

## Code Style

This project follows these style guidelines:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **Google-style docstrings**: Documentation

### Example Code Style

```python
def analyze_image(self, image_url: str) -> Dict[str, Any]:
    """
    Analyze an image for facial features and geospatial metadata.

    Args:
        image_url: URL of the image to analyze.

    Returns:
        Dictionary containing analysis results.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    # Implementation here
    pass
```

## Testing

### Writing Tests
- Use `pytest` for testing
- Place test files in the `tests/` directory
- Use descriptive test names: `test_function_name_behavior`
- Mock external dependencies (API calls, etc.)

### Example Test

```python
import pytest
from unittest.mock import Mock, patch
from geoidenti_sdk import GeoIdenti

@patch('requests.request')
def test_analyze_success(mock_request):
    """Test successful image analysis."""
    # Arrange
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    client = GeoIdenti(api_key="test-key")

    # Act
    result = client.analyze("https://example.com/image.jpg")

    # Assert
    assert result["status"] == "success"
    mock_request.assert_called_once()
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=geoidenti_sdk

# Run specific test
pytest tests/test_sdk.py::TestGeoIdenti::test_analyze_success

# Run tests matching pattern
pytest -k "analyze"
```

## Documentation

### Updating Documentation
- Update docstrings for any changed functionality
- Update the README.md for new features
- Add examples for new methods
- Update type hints

### Building Documentation
```bash
# Generate API documentation (if using sphinx)
make docs
```

## Release Process

1. **Version Bump**: Update version in `setup.py` and `__init__.py`
2. **Changelog**: Update CHANGELOG.md with new features/fixes
3. **Tests**: Ensure all tests pass and coverage is adequate
4. **Documentation**: Update README and any other docs
5. **Tag Release**: Create a git tag for the release
6. **Publish**: Publish to PyPI

## Security Considerations

- Never commit API keys or sensitive credentials
- Use environment variables for configuration
- Follow secure coding practices
- Report security vulnerabilities privately

## Getting Help

- 📖 [Documentation](https://geoidenti-sdk.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/eddeuser-tech/geoidenti-sdk/issues)
- 💬 [Discussions](https://github.com/eddeuser-tech/geoidenti-sdk/discussions)
- 📧 [Email Support](mailto:support@geoidenti.com)

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.</content>
<parameter name="filePath">/Users/kristideuser/geoidenti-engine/geoidenti-sdk/CONTRIBUTING.md