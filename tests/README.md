# ResoftAI Test Suite

Comprehensive test suite for the ResoftAI multi-agent software development platform.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_llm_factory.py      # LLM factory and provider tests
├── test_crud_project.py     # Project CRUD operation tests
├── test_workflow.py         # Workflow orchestration tests
├── test_api_execution.py    # Execution API endpoint tests
├── test_agents.py           # Agent implementation tests
├── test_integration.py      # Integration and E2E tests
└── README.md               # This file
```

## Test Categories

### Unit Tests
- **test_llm_factory.py**: Tests for LLM factory and configuration
- **test_crud_project.py**: Database CRUD operations
- **test_agents.py**: Individual agent implementations
- **test_workflow.py**: Workflow orchestration logic

### API Tests
- **test_api_execution.py**: Execution API endpoints
- Additional API test files can be added for other endpoints

### Integration Tests
- **test_integration.py**: Complete workflow integration tests
  - Project lifecycle tests
  - API integration scenarios
  - WebSocket integration
  - Database integration
  - End-to-end user scenarios

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only workflow tests
pytest -m workflow
```

### Run Specific Test Files
```bash
# Run LLM factory tests
pytest tests/test_llm_factory.py

# Run workflow tests
pytest tests/test_workflow.py

# Run integration tests
pytest tests/test_integration.py
```

### Run Specific Test Classes or Functions
```bash
# Run specific test class
pytest tests/test_workflow.py::TestWorkflowOrchestrator

# Run specific test function
pytest tests/test_llm_factory.py::TestLLMFactory::test_create_deepseek_provider
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=src/resoftai --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Fast Tests (Skip Slow Tests)
```bash
pytest -m "not slow"
```

## Test Markers

Tests are marked with the following markers for easy filtering:

- `unit`: Unit tests for individual components
- `integration`: Integration tests for multiple components
- `api`: API endpoint tests
- `workflow`: Workflow orchestration tests
- `crud`: Database CRUD operation tests
- `slow`: Slow-running tests (e.g., full E2E scenarios)

## Test Configuration

### pytest.ini
Test configuration is defined in `pytest.ini` at the project root:
- Test discovery patterns
- Coverage settings
- Async test mode
- Output options

### conftest.py
Shared fixtures and test utilities:
- Database session fixtures
- Test user/project fixtures
- Mock LLM responses
- Authentication fixtures

## Writing Tests

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Using Fixtures
```python
def test_with_fixtures(db, test_user, test_project):
    # Use provided fixtures
    assert test_user.id is not None
    assert test_project.user_id == test_user.id
```

### Mocking LLM Calls
```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_mocked_llm(sample_llm_config):
    from resoftai.agents.requirement_analyst import RequirementAnalyst

    analyst = RequirementAnalyst(sample_llm_config)

    mock_response = {
        "content": "Mocked response",
        "usage": {"total_tokens": 100}
    }

    with patch.object(analyst.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
        result = await analyst.analyze("Test input")
        assert result is not None
```

## Test Database

Tests use an in-memory SQLite database by default:
- Fast execution
- No external dependencies
- Clean state for each test
- Defined in `conftest.py`

## Continuous Integration

Tests are designed to run in CI environments:
- No external service dependencies (when using mocks)
- Fast execution (unit tests)
- Comprehensive coverage (integration tests)
- Clear failure messages

## Coverage Goals

- **Overall**: >80% code coverage
- **Critical paths**: >90% coverage
  - Authentication
  - Workflow execution
  - Database operations
  - API endpoints

## Best Practices

1. **Write tests first**: TDD approach when possible
2. **Mock external services**: Use mocks for LLM calls, external APIs
3. **Use fixtures**: Reuse common test data and setup
4. **Test edge cases**: Include error handling tests
5. **Keep tests focused**: One concept per test
6. **Use descriptive names**: Test names should describe what they test
7. **Mark appropriately**: Use markers for slow/integration tests
8. **Clean up**: Use fixtures for setup/teardown

## Dependencies

Testing dependencies are defined in `requirements.txt`:
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `pytest-mock`: Mocking utilities
- `faker`: Test data generation
- `aiosqlite`: Async SQLite for test database

## Troubleshooting

### Tests Fail with Database Errors
- Ensure `aiosqlite` is installed
- Check database connection string in `conftest.py`

### Async Tests Don't Run
- Verify `pytest-asyncio` is installed
- Check `asyncio_mode = auto` in `pytest.ini`

### Coverage Report Not Generated
- Install `pytest-cov`
- Run with `--cov` flag

### Import Errors
- Ensure you're running from project root
- Check PYTHONPATH includes `src/`

## Contributing

When adding new features:
1. Write tests for new code
2. Update existing tests if behavior changes
3. Ensure all tests pass before committing
4. Maintain coverage above 80%

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
