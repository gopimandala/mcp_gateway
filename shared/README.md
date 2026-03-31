# Shared Utilities (`shared/`)

Common utilities, tracing infrastructure, and shared components used across the MCP Gateway project.

## Purpose

The `shared/` directory provides reusable components that maintain consistency and reduce code duplication across different modules of the MCP Gateway.

## Directory Structure

```
shared/
├── tracing_utils.py       # Centralized tracing and PII protection
└── tool_registry.py       # Tool registry service base class
```

## Core Components

### `tracing_utils.py` - Tracing & Security Infrastructure
**Purpose**: Centralized tracing, PII scrubbing, and data sanitization

#### Key Features

**PII Patterns & Scrubbing**:
- **Email Detection**: Regex pattern for email addresses
- **Token/Key Detection**: Long alphanumeric strings (16+ chars)
- **Phone Detection**: Flexible phone number patterns
- **Recursive Scrubbing**: Handles nested dicts, lists, and strings

**Data Processing Functions**:

```python
scrub_pii(data)          # Remove PII from any data structure
mask_sensitive_data()    # Mask authentication headers
extract_business_fields() # Extract relevant business data
redact_output()         # Prepare data for tracing
```

**Tracing Decorators**:

```python
@secure_trace(name="operation_name")  # Client-level tracing
@secure_mcp_tool(name="tool_name")    # MCP tool tracing
```

#### PII Detection Patterns

```python
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}'
TOKEN_REGEX = r'[a-zA-Z0-9]{16,}'  # API keys, tokens
PHONE_REGEX = r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{3,4}'
```

#### Business Field Extraction

For Jira responses, extracts only relevant fields:
- Basic info: `key`, `id`
- Business fields: `summary`, `description`, `status`, `priority`
- People fields: `assignee`, `reporter` (display names only)
- Timestamps: `created` date

#### Security Features

**Header Masking**:
- Authorization headers masked as `[MASKED]`
- API keys, cookies, and sensitive headers protected
- Preserves header structure while hiding credentials

**Output Redaction**:
- Automatic PII scrubbing before tracing
- Business field extraction to reduce noise
- Maintains data structure for usability

### `tool_registry.py` - Tool Registry Base Class
**Purpose**: Base class for service implementations that expose tools dynamically

#### Features

**Dynamic Tool Discovery**:
- Automatic tool listing capabilities
- Standardized tool metadata format
- Integration with MCP tool registration

**Service Interface**:
```python
class ToolRegistryService:
    def get_tools_list() -> List[Dict]
    # Returns: [{"name": "...", "description": "...", "method": "...", "path": "..."}]
```

## Usage Patterns

### Client-Level Tracing

```python
from shared.tracing_utils import secure_trace

@secure_trace(name="jira_client_execute")
async def execute(self, operation: str, **params):
    # Implementation
    # - Inputs automatically masked
    # - Outputs automatically scrubbed
    # - Traced in LangSmith with business data only
```

### PII Scrubbing

```python
from shared.tracing_utils import scrub_pii

# Scrub any data structure
clean_data = scrub_pii(user_input)

# Handles nested structures automatically
data = {
    "user": {"email": "user@example.com", "name": "John"},
    "tokens": ["abc123def456", "valid_data"]
}
clean = scrub_pii(data)
# Result: {"user": {"email": "[REDACTED_EMAIL]", "name": "John"}, "tokens": ["[REDACTED_SENSITIVE]", "valid_data"]}
```

### Business Field Extraction

```python
from shared.tracing_utils import extract_business_fields

# Extract only relevant Jira fields
jira_response = {...}  # Full Jira API response
business_data = extract_business_fields(jira_response)
# Result: {"key": "PROJ-123", "fields": {"summary": "...", "status": "Open"}}
```

## Architecture Integration

### Tracing Flow

```
Client Request → @secure_trace → PII Masking → Business Logic → PII Scrubbing → LangSmith Trace
```

### Data Processing Pipeline

1. **Input Processing**:
   - Mask sensitive headers
   - Preserve data structure
   - Prepare for tracing

2. **Business Logic**:
   - Execute core functionality
   - Return full data internally

3. **Output Processing**:
   - Extract business fields
   - Scrub remaining PII
   - Send to tracing system

## Configuration

### LangSmith Integration

Tracing automatically integrates with LangSmith:
- Project name from environment variables
- Automatic run type classification
- Structured metadata attachment
- Secure data transmission

### Environment Variables

```bash
# LangSmith Configuration
LANGCHAIN_PROJECT=mcp-multi-gateway
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your-langsmith-key
```

## Security Considerations

### Data Protection

**PII Detection**:
- Comprehensive pattern matching
- Multi-language support (primarily English)
- Configurable sensitivity levels

**Data Minimization**:
- Only business-relevant data traced
- Automatic field extraction
- Structured data preservation

**Credential Protection**:
- Header masking for authentication
- Token pattern detection
- Secure logging practices

### Compliance Features

**Audit Trail**:
- Complete operation tracing
- User action logging
- Error tracking and reporting

**Data Retention**:
- Configurable trace retention
- Automatic data cleanup
- Privacy by design

## Performance Considerations

### Efficient Processing

**Regex Optimization**:
- Compiled regex patterns
- Efficient string processing
- Minimal memory overhead

**Recursive Handling**:
- Depth-limited recursion
- Circular reference protection
- Memory-efficient processing

### Caching Strategies

**Pattern Compilation**:
- Pre-compiled regex patterns
- Reusable across calls
- Reduced initialization overhead

## Testing

### Unit Tests

```python
# Test PII scrubbing
def test_scrub_pii():
    data = {"email": "test@example.com", "name": "John"}
    result = scrub_pii(data)
    assert result["email"] == "[REDACTED_EMAIL]"

# Test business field extraction
def test_extract_business_fields():
    jira_data = {"key": "PROJ-123", "fields": {"summary": "Test"}}
    result = extract_business_fields(jira_data)
    assert "summary" in result["fields"]
```

### Integration Tests

- End-to-end tracing workflows
- PII detection accuracy
- Performance benchmarking
- Memory usage validation

## Extensibility

### Adding New PII Patterns

```python
# Add new pattern to tracing_utils.py
CREDIT_CARD_REGEX = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

def scrub_pii(data: Any) -> Any:
    # ... existing logic ...
    elif isinstance(data, str):
        s = EMAIL_REGEX.sub('[REDACTED_EMAIL]', data)
        s = TOKEN_REGEX.sub('[REDACTED_SENSITIVE]', s)
        s = PHONE_REGEX.sub('[REDACTED_PHONE]', s)
        s = CREDIT_CARD_REGEX.sub('[REDACTED_CREDIT_CARD]', s)  # New pattern
        return s
```

### Custom Business Field Extractors

```python
def extract_gitlab_fields(data: dict) -> dict:
    """Custom extractor for GitLab responses."""
    # Implementation similar to extract_business_fields
    pass
```

## Dependencies

- `langsmith` - Tracing and monitoring
- `httpx` - HTTP response handling
- `pydantic` - Data validation (optional)
- `re` - Regex pattern matching (built-in)

## Best Practices

1. **Always use tracing decorators** for external API calls
2. **Validate PII scrubbing** with realistic test data
3. **Monitor trace quality** in LangSmith dashboard
4. **Update patterns** as new PII types are identified
5. **Test business field extraction** with actual API responses
