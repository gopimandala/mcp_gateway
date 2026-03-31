# Test Suite (`tests/`)

Comprehensive test suite for the MCP Gateway project, covering unit tests, integration tests, and end-to-end workflows.

## Purpose

The test suite ensures:
- Code quality and reliability
- Integration compatibility
- API contract compliance
- Security and PII protection
- Performance benchmarks

## Directory Structure

```
tests/
├── test_jira.py           # Jira integration tests
├── jiratest.py            # Jira connection validation
├── test1.py               # Additional test file
└── README.md              # This documentation
```

## Test Categories

### 1. Unit Tests
**Purpose**: Test individual components in isolation

**Coverage Areas**:
- PII scrubbing functions
- Business field extraction
- Configuration validation
- Data model validation
- Error handling logic

### 2. Integration Tests
**Purpose**: Test component interactions and workflows

**Coverage Areas**:
- Service layer integration
- Client-server communication
- MCP tool registration
- HTTP wrapper functionality
- Database interactions (if applicable)

### 3. End-to-End Tests
**Purpose**: Test complete user workflows

**Coverage Areas**:
- Full request-response cycles
- Brain server orchestration
- Multi-tool execution plans
- Error recovery scenarios
- Performance validation

## Test Files

### `test_jira.py` - Jira Integration Tests
**Purpose**: Comprehensive testing of Jira integration

**Test Categories**:

**Connection Tests**:
```python
def test_jira_connection():
    """Verify Jira API connectivity and authentication"""
    
def test_invalid_credentials():
    """Test behavior with invalid Jira credentials"""
```

**Operation Tests**:
```python
def test_get_issue_success():
    """Test successful issue retrieval"""
    
def test_get_issue_not_found():
    """Test handling of non-existent issues"""
    
def test_add_comment_success():
    """Test successful comment addition"""
    
def test_add_comment_invalid_issue():
    """Test comment addition to invalid issue"""
```

**Data Validation Tests**:
```python
def test_issue_response_schema():
    """Validate issue response matches expected schema"""
    
def test_comment_response_schema():
    """Validate comment response matches expected schema"""
```

**Error Handling Tests**:
```python
def test_network_error_handling():
    """Test graceful handling of network failures"""
    
def test_api_rate_limiting():
    """Test behavior under rate limiting"""
```

### `jiratest.py` - Connection Validation
**Purpose**: Quick validation of Jira connection and configuration

**Usage**:
```bash
python tests/jiratest.py
```

**Features**:
- Configuration validation
- Authentication testing
- Basic API connectivity check
- Permission verification

## Test Configuration

### Environment Setup

Create test environment file:
```bash
# tests/.env.test
JIRA_URL=https://your-test-domain.atlassian.net
JIRA_EMAIL=test@company.com
JIRA_API_KEY=test-api-key
LANGCHAIN_PROJECT=test-mcp-gateway
```

### Pytest Configuration

**pytest.ini** (recommended):
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

### Test Markers

```python
@pytest.mark.unit        # Unit tests
@pytest.mark.integration # Integration tests
@pytest.mark.e2e        # End-to-end tests
@pytest.mark.slow       # Slow-running tests
@pytest.mark.external   # Tests requiring external services
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_jira.py

# Run specific test
pytest tests/test_jira.py::test_get_issue_success

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v
```

### Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run tests requiring external services
pytest -m external
```

### Test Environments

```bash
# Run against test environment
TEST_ENV=test pytest

# Run against staging environment
TEST_ENV=staging pytest

# Run with mocked external services
MOCK_EXTERNAL=true pytest
```

## Test Data Management

### Fixtures and Sample Data

**Sample Jira Issue** (`fixtures/jira_issue.json`):
```json
{
  "id": "12345",
  "key": "PROJ-123",
  "fields": {
    "summary": "Test Issue",
    "description": "This is a test issue",
    "status": {"name": "Open"},
    "priority": {"name": "Medium"},
    "assignee": {"displayName": "John Doe"},
    "reporter": {"displayName": "Jane Smith"},
    "created": "2024-01-01T00:00:00.000Z"
  }
}
```

**Mock Responses**:
```python
@pytest.fixture
def mock_jira_issue_response():
    return {
        "id": "12345",
        "key": "PROJ-123",
        "fields": {
            "summary": "Test Issue",
            "status": {"name": "Open"}
        }
    }
```

### Test Data Generation

```python
def generate_test_issue(issue_key: str) -> dict:
    """Generate test issue data"""
    return {
        "key": issue_key,
        "fields": {
            "summary": f"Test Issue {issue_key}",
            "description": "Generated test issue",
            "status": {"name": "Open"}
        }
    }
```

## Mocking and External Services

### HTTP Client Mocking

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def mock_http_client():
    """Mock HTTP client for API calls"""
    client = AsyncMock()
    
    # Mock successful response
    client.get.return_value.json.return_value = generate_test_issue("PROJ-123")
    client.get.return_value.raise_for_status.return_value = None
    
    return client

@patch('httpx.AsyncClient')
def test_with_mocked_client(mock_async_client, mock_http_client):
    mock_async_client.return_value = mock_http_client
    # Test implementation
```

### External Service Mocking

```python
@pytest.fixture
def mock_jira_service():
    """Mock Jira service for integration tests"""
    service = AsyncMock()
    service.get_issue.return_value = generate_test_issue("PROJ-123")
    service.add_comment.return_value = {"id": "67890", "self": "http://example.com"}
    return service
```

## Performance Testing

### Load Testing

```python
import time
import asyncio

@pytest.mark.performance
async def test_concurrent_requests():
    """Test performance under concurrent load"""
    start_time = time.time()
    
    tasks = [get_issue(f"PROJ-{i}") for i in range(100)]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    assert duration < 10.0  # Should complete within 10 seconds
    assert len(results) == 100
```

### Memory Testing

```python
@pytest.mark.performance
def test_memory_usage():
    """Test memory usage doesn't grow excessively"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Execute many operations
    for i in range(1000):
        scrub_pii(generate_large_test_data())
    
    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory
    
    assert memory_growth < 100 * 1024 * 1024  # Less than 100MB growth
```

## Security Testing

### PII Scrubbing Tests

```python
def test_pii_scrubbing_comprehensive():
    """Test comprehensive PII scrubbing"""
    test_data = {
        "email": "user@example.com",
        "phone": "+1-555-123-4567",
        "token": "sk-1234567890abcdef1234567890abcdef",
        "nested": {
            "contact": "admin@company.com",
            "secret": "verylongsecretkey1234567890"
        }
    }
    
    result = scrub_pii(test_data)
    
    assert "[REDACTED_EMAIL]" in str(result)
    assert "[REDACTED_PHONE]" in str(result)
    assert "[REDACTED_SENSITIVE]" in str(result)
    assert "user@example.com" not in str(result)
    assert "sk-1234567890abcdef" not in str(result)
```

### Authentication Tests

```python
def test_header_masking():
    """Test authentication headers are properly masked"""
    headers = {
        "Authorization": "Bearer secret-token",
        "X-API-Key": "api-key-123",
        "Content-Type": "application/json"
    }
    
    result = mask_sensitive_data({"headers": headers})
    
    assert result["headers"]["Authorization"] == "[MASKED]"
    assert result["headers"]["X-API-Key"] == "[MASKED]"
    assert result["headers"]["Content-Type"] == "application/json"
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Best Practices

### Test Organization

1. **Descriptive Names**: Use clear, descriptive test names
2. **Single Responsibility**: Each test should verify one thing
3. **Independent Tests**: Tests should not depend on each other
4. **Repeatable**: Tests should produce same results every time
5. **Fast Execution**: Prefer fast unit tests over slow integration tests

### Test Data

1. **Realistic Data**: Use data that matches production
2. **Edge Cases**: Test boundary conditions and error cases
3. **Privacy**: Never use real user data in tests
4. **Cleanup**: Clean up test data after tests complete

### Assertions

1. **Specific Assertions**: Use specific assertions for clarity
2. **Error Messages**: Provide helpful assertion messages
3. **Multiple Assertions**: Group related assertions
4. **Soft Assertions**: Use for non-critical validations

## Dependencies

### Test Dependencies

```bash
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
httpx-mock>=0.10.0
psutil>=5.9.0  # For performance testing
```

### Development Dependencies

```bash
black          # Code formatting
flake8         # Linting
mypy           # Type checking
pre-commit     # Git hooks
```

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure src directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Async Test Failures**:
```python
# Use pytest-asyncio for async tests
@pytest.mark.asyncio
async def test_async_function():
    await some_async_function()
```

**Mock Not Working**:
```python
# Ensure correct patch path
@patch('src.integrations.jira.client.httpx.AsyncClient')
# Not:
@patch('httpx.AsyncClient')
```

**External Service Failures**:
```bash
# Use mock mode for CI/CD
MOCK_EXTERNAL=true pytest
```

## Coverage Goals

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: 80%+ coverage of critical paths
- **End-to-End Tests**: Cover all user workflows
- **Security Tests**: 100% coverage of PII handling
