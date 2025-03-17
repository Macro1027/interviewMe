# Testing Documentation for AI Interview Simulation Platform

## Testing Structure

The testing framework for the AI Interview Simulation Platform is organized into three main categories:

```
src/tests/
    ├── unit/             # Unit tests for individual components
    ├── integration/      # Integration tests for component interactions 
    ├── benchmarks/       # Performance benchmark tests
    └── __init__.py       # Package initialization
```

## Test Categories

### Unit Tests

Unit tests verify the functionality of individual components in isolation. These tests should be fast, independent, and not rely on external services.

Examples:
- Testing utility functions
- Testing model validation
- Testing business logic
- Testing configuration loading

### Integration Tests

Integration tests verify how different components interact with each other and external systems. These tests may require external services like databases.

Examples:
- Database connection tests
- API endpoint tests
- Service interaction tests
- External API integration tests

### Benchmark Tests

Benchmark tests measure and track the performance of critical operations over time. These tests ensure that code changes don't introduce performance regressions.

Examples:
- Data processing performance
- Algorithm scaling tests
- API response time benchmarks

## Running Tests

### Running All Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=html
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest src/tests/unit/

# Run only integration tests
pytest src/tests/integration/

# Run only benchmark tests
pytest src/tests/benchmarks/
```

### Running Tests with Specific Markers

```bash
# Run tests marked as "slow"
pytest -m slow

# Run tests marked as "asyncio"
pytest -m asyncio

# Run tests that don't use external APIs
pytest -m "not api"
```

## Test Configuration

Test configuration is managed through the `pytest.ini` file in the project root. This file defines:

- Test discovery paths
- Custom markers
- Benchmark settings
- Timeout settings
- Warning filters

## CI/CD Integration

Tests are automatically run in the CI/CD pipeline through GitHub Actions. The workflow is defined in `.github/workflows/testing.yml`.

The CI pipeline:
1. Runs linting checks (flake8, black, isort)
2. Runs unit tests
3. Runs integration tests with test databases (MongoDB, PostgreSQL)
4. Generates and uploads coverage reports
5. Runs security scans (bandit, safety)

## Writing Tests

### Test Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test functions should be named `test_*`

### Test Organization

- Group related tests in classes
- Use descriptive names for test functions
- Use docstrings to describe test purpose
- Use fixtures for shared setup code

### Fixtures

Fixtures provide a consistent way to set up test environments. Common fixtures are available in the `conftest.py` files.

Example:
```python
@pytest.fixture
def test_settings():
    """Create test settings for database testing."""
    with mock.patch.dict(os.environ, {...}):
        return get_settings()
```

### Mocking

Use mocking to isolate the component under test:

```python
with mock.patch('module.function') as mock_function:
    mock_function.return_value = 'expected'
    result = function_under_test()
    assert result == 'expected'
```

## Environment Variables for Testing

Tests use environment variables defined in `.env.test`. The CI pipeline sets up the required environment variables automatically.

Key test environment variables:
- `APP_ENV=test`
- `DEBUG=true`
- `MOCK_AI_SERVICES=true`
- `MONGODB_URI=mongodb://localhost:27017/test_db`
- `POSTGRES_URI=postgresql://postgres:postgres@localhost:5432/test_db`

## Best Practices

1. **Isolate tests**: Tests should not depend on each other or order of execution
2. **Clean up resources**: Tests should clean up any resources they create
3. **Use appropriate mocking**: Mock external services when appropriate
4. **Keep tests fast**: Slow tests should be marked with `@pytest.mark.slow`
5. **Test edge cases**: Include tests for error conditions and edge cases
6. **Maintain coverage**: Aim for at least 80% code coverage
7. **Use assertions effectively**: Use specific assertions that provide clear error messages 