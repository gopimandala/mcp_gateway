# Brain Module (`brain/`)

AI-powered orchestration layer that provides intelligent planning and execution of MCP Gateway operations using Large Language Models (LLMs).

## Purpose

The Brain module transforms natural language requests into structured execution plans by:
1. Analyzing user requests
2. Selecting appropriate MCP tools
3. Generating execution sequences
4. Coordinating tool execution

## Directory Structure

```
brain/
├── brain_server.py        # Main FastAPI server
├── brain.py               # Core LLM orchestration logic
├── guardrail_server.py    # Safety and validation layer
├── system_prompt.md       # LLM system instructions
├── user_prompt.md         # User request template
├── .env                   # Brain-specific environment variables
└── .gitignore             # Git ignore rules
```

## Core Components

### `brain_server.py` - FastAPI Server
**Purpose**: HTTP API server for AI orchestration

**Key Features**:
- **Port**: 8000
- **Endpoints**:
  - `POST /plan` - Generate execution plan from user request
  - `POST /execute` - Execute plan with MCP tools
- **Dynamic Tool Discovery**: Automatically fetches available tools from MCP Gateway
- **LLM Integration**: Uses OpenAI GPT-4o-mini for planning

**Architecture**:
```python
User Request → LLM Planning → Tool Selection → Execution → Results
```

### `brain.py` - Core Orchestration Logic
**Purpose**: Core LLM interaction and planning logic

**Key Functions**:
- `fetch_tools()` - Dynamic tool discovery from MCP Gateway
- `run_brain()` - LLM-based plan generation
- `execute_plan()` - Tool execution coordination
- `load_prompt()` - Prompt template management

**Workflow**:
1. **Tool Discovery**: Fetch available tools from MCP Gateway
2. **LLM Planning**: Generate structured execution plan
3. **Plan Validation**: Validate plan structure and tool availability
4. **Execution**: Coordinate tool execution with proper error handling

### `guardrail_server.py` - Safety Layer
**Purpose**: Input validation and safety checks

**Features**:
- Request validation
- Rate limiting preparation
- Safety rule enforcement
- Error boundary handling

## Prompt Engineering

### `system_prompt.md`
**Purpose**: Defines LLM behavior, capabilities, and constraints

**Key Sections**:
- Role definition and capabilities
- Tool selection guidelines
- Output format requirements
- Error handling instructions
- Safety and validation rules

### `user_prompt.md`
**Purpose**: Template for formatting user requests

**Template Variables**:
- `{user_request}` - Natural language user input
- `{tools_json}` - Available tools in JSON format

## API Specification

### Generate Plan
```http
POST /plan
Content-Type: application/json

{
  "user_request": "Get the details of Jira ticket PROJ-123 and add a comment saying 'Review completed'"
}
```

**Response**:
```json
{
  "plan": {
    "steps": [
      {
        "tool": "get_issue",
        "input": {"issue_key": "PROJ-123"},
        "description": "Fetch Jira issue details"
      },
      {
        "tool": "add_comment", 
        "input": {"issue_key": "PROJ-123", "comment": "Review completed"},
        "description": "Add comment to Jira issue"
      }
    ]
  }
}
```

### Execute Plan
```http
POST /execute
Content-Type: application/json

{
  "plan": {
    "steps": [
      {
        "tool": "get_issue",
        "input": {"issue_key": "PROJ-123"}
      }
    ]
  }
}
```

**Response**:
```json
{
  "plan": {...},
  "execution_results": [
    {
      "tool": "get_issue",
      "input": {"issue_key": "PROJ-123"},
      "output": {"key": "PROJ-123", "fields": {...}}
    }
  ]
}
```

## Environment Configuration

Create `.env` in brain directory:

```bash
# OpenAI Configuration
OPENAI_KEY=sk-your-openai-api-key-here

# MCP Gateway Configuration
MCP_GATEWAY_URL=http://localhost:8000
TOOLS_URL=http://localhost:8000/api/jira/tools
```

## Integration Architecture

### Tool Discovery
The Brain dynamically discovers available tools:
1. **HTTP Request**: `GET /api/jira/tools`
2. **Tool Registry**: MCP Gateway responds with available tools
3. **LLM Context**: Tools formatted into LLM prompt
4. **Dynamic Selection**: LLM selects appropriate tools

### Execution Flow
1. **Plan Generation**: LLM creates structured plan
2. **Tool Validation**: Verify tools exist and inputs are valid
3. **Sequential Execution**: Execute tools in planned order
4. **Result Aggregation**: Collect and format results
5. **Error Handling**: Graceful failure with detailed error messages

## LLM Integration

### Model Configuration
- **Model**: GPT-4o-mini
- **Provider**: OpenAI
- **Temperature**: 0 (deterministic output)
- **Max Tokens**: Configurable based on complexity

### Prompt Strategy
- **System Prompt**: Defines behavior, constraints, and output format
- **User Prompt**: Combines user request with tool context
- **Few-Shot Examples**: Embedded in system prompt for consistency
- **JSON Output**: Enforced structured output for reliable parsing

## Error Handling

### Plan Generation Errors
- **LLM Failures**: Retry with exponential backoff
- **Invalid JSON**: Fallback to simple text parsing
- **Tool Unavailable**: Graceful degradation with suggestions

### Execution Errors
- **Network Failures**: Retry with timeout
- **Invalid Inputs**: Detailed error messages
- **Tool Failures**: Continue with remaining tools
- **Partial Success**: Return completed steps with error details

## Monitoring & Debugging

### Logging
- **Request Logging**: Full request/response logging
- **LLM Calls**: Token usage and response times
- **Tool Execution**: Success/failure rates
- **Error Tracking**: Detailed error context

### Performance Metrics
- **Plan Generation Time**: LLM response latency
- **Execution Time**: Total workflow duration
- **Tool Performance**: Individual tool response times
- **Success Rate**: Overall workflow success percentage

## Development Guidelines

### Adding New Tool Types
1. Update tool discovery endpoint
2. Extend prompt templates with new tool examples
3. Add validation rules for new tool inputs
4. Update error handling for new tool types

### Prompt Optimization
1. Test with various user request patterns
2. Monitor LLM output consistency
3. Optimize token usage
4. Add edge case handling

### Safety Considerations
1. Input sanitization and validation
2. Rate limiting for API protection
3. Audit logging for compliance
4. Guardrails for harmful requests

## Dependencies

Key dependencies:
- `fastapi` - HTTP server framework
- `openai` - OpenAI API client
- `aiohttp` - Async HTTP client for tool execution
- `pydantic` - Data validation
- `python-dotenv` - Environment management

## Testing

### Unit Tests
- LLM prompt formatting
- Tool discovery logic
- Plan validation
- Error handling

### Integration Tests
- End-to-end workflow execution
- LLM integration
- MCP Gateway communication
- Error scenarios

### LLM Testing
- Prompt effectiveness
- Output consistency
- Edge case handling
- Performance benchmarking
