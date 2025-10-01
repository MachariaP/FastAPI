# Testing Documentation

## Overview

This document describes the comprehensive testing setup for the FastAPI application in `main.py`.

## Test Suite

The test suite is located in `test_main.py` and includes **59 comprehensive tests** covering:

### Coverage Areas

1. **Health Check Endpoints (3 tests)**
   - Root health check
   - Detailed health check
   - Configuration endpoint

2. **Authentication Help & Info (2 tests)**
   - Authentication help endpoint
   - API information endpoint

3. **User Registration (7 tests)**
   - Successful registration
   - Duplicate username handling
   - Duplicate email handling
   - Invalid email format validation
   - Short password validation
   - Short username validation
   - Registration information endpoint

4. **User Login (5 tests)**
   - Successful login
   - Wrong username handling
   - Wrong password handling
   - Missing credentials validation
   - Login information endpoint

5. **Authenticated User Operations (4 tests)**
   - Getting current user
   - No token handling
   - Invalid token handling
   - Expired token handling

6. **User Management (5 tests)**
   - Getting all users
   - Unauthenticated access handling
   - Pagination support
   - Get user by ID
   - User not found handling

7. **Item CRUD Operations (12 tests)**
   - Creating items (authenticated)
   - Creating items without auth
   - Invalid price validation
   - Getting item by ID
   - Item not found handling
   - Updating items
   - Update authorization checks
   - Deleting items
   - Delete authorization checks

8. **Item Filtering & Search (8 tests)**
   - Pagination
   - Category filtering
   - Search by name/description
   - Price range filtering
   - Advanced search with query
   - Advanced search with category
   - Advanced search with price range
   - Sorting options

9. **Item Categories (2 tests)**
   - Empty categories
   - Categories with items and statistics

10. **User Items (2 tests)**
    - Getting user's items
    - Authorization checks

11. **Statistics (2 tests)**
    - Getting application statistics
    - Unauthenticated access handling

12. **Error Handling (4 tests)**
    - Validation error handling
    - 404 errors
    - Token with non-existent user
    - Malformed token handling

13. **Middleware & Models (3 tests)**
    - Request logging
    - Item model validation
    - User model validation

## Running Tests

### Basic Test Run

```bash
pytest test_main.py
```

### Verbose Output

```bash
pytest test_main.py -v
```

### With Coverage Report

```bash
pytest test_main.py --cov=main --cov-report=html --cov-report=term
```

### Run Specific Test Class

```bash
pytest test_main.py::TestUserRegistration -v
```

### Run Specific Test

```bash
pytest test_main.py::TestUserRegistration::test_successful_registration -v
```

## Coverage

Current test coverage: **88%**

Coverage report is generated in:
- Terminal output (term-missing format)
- HTML report in `htmlcov/` directory

To view HTML coverage report:

```bash
python -m pytest test_main.py --cov=main --cov-report=html
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Test Configuration

### pytest.ini

The project includes a `pytest.ini` configuration file with:
- Test discovery patterns
- Coverage settings
- Output formatting options
- Custom markers

### .flake8

Code style is enforced using flake8 with:
- Max line length: 100 characters
- Ignored rules: E203, W503
- Excluded directories: `.git`, `__pycache__`, `.pytest_cache`, `htmlcov`

## Code Quality Checks

### Running Flake8

```bash
flake8 main.py
```

### Running Black (Auto-formatter)

```bash
black main.py --line-length 100
```

### Running Pylint

```bash
pylint main.py
```

### Running MyPy (Type Checking)

```bash
mypy main.py
```

## Best Practices

### The tests follow these best practices:

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Reset**: Database is reset before each test using fixtures
3. **Clear naming**: Test names clearly describe what they test
4. **Edge cases**: Tests cover both happy paths and error scenarios
5. **Assertions**: Multiple assertions verify different aspects
6. **Documentation**: Tests are well-documented with docstrings

### Test Structure

Tests are organized into classes by functionality:
- `TestHealthEndpoints`
- `TestAuthenticationHelp`
- `TestUserRegistration`
- `TestUserLogin`
- `TestAuthenticatedUser`
- `TestUserManagement`
- `TestItemManagement`
- `TestItemFiltering`
- `TestAdvancedItemSearch`
- `TestItemCategories`
- `TestUserItems`
- `TestStatistics`
- `TestErrorHandling`
- `TestMiddleware`
- `TestModels`

## Fixtures

### `reset_databases`
- **Scope**: Function (runs before each test)
- **Purpose**: Clears and reinitializes databases
- **Auto-use**: Yes

### `client`
- **Purpose**: Provides TestClient instance for making requests

### `admin_token`
- **Purpose**: Generates JWT token for admin user

### `test_user_token`
- **Purpose**: Creates a test user and returns their JWT token

## Continuous Integration

The test suite is designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov httpx
      - run: pytest test_main.py --cov=main
```

## Adding New Tests

When adding new endpoints or features:

1. Create a new test class if it's a new feature area
2. Add test methods for success cases
3. Add test methods for error/edge cases
4. Update this documentation
5. Ensure tests pass and coverage remains high

### Example Test Template

```python
class TestNewFeature:
    """Test new feature functionality."""

    def test_feature_success(self, client, admin_token):
        """Test successful feature operation."""
        response = client.get(
            "/new-endpoint",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data

    def test_feature_unauthorized(self, client):
        """Test feature without authentication."""
        response = client.get("/new-endpoint")
        assert response.status_code == 401
```

## Dependencies

Testing dependencies are listed in `requirements.txt`:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for TestClient
- `black` - Code formatting
- `flake8` - Style checking
- `pylint` - Code analysis
- `mypy` - Type checking

## Known Issues

None at this time.

## Contributing

When contributing tests:
1. Follow existing test patterns
2. Maintain or improve coverage
3. Run all tests before submitting
4. Update this documentation if needed
