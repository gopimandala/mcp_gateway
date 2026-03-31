# Source Code (`src/`)

Core implementation of the MCP Gateway. This directory contains the main server logic, API endpoints, configuration, and service integrations.

## Directory Structure

```
src/
├── main.py                 # MCP Server entry point
├── main_http_wrapper.py    # HTTP API wrapper entry point
├── api/                    # HTTP endpoint definitions
│   └── jira/
│       └── jira_http_wrapper.py
├── core/                   # Configuration and settings
│   └── config.py
└── integrations/           # Service integrations
    └── jira/
        ├── client.py       # Jira API client with tracing
        ├── service.py      # Jira service layer
        ├── tools.py        # MCP tool registration
        ├── operations.py   # API operation definitions
        └── schemas.py      # Pydantic data models
```

## Core Files

### `main.py` - MCP Server
**Purpose**: Primary MCP protocol server implementation

**Key Responsibilities**:
- Initialize FastMCP server with lifecycle management
- Register integration services (Jira, etc.)
- Handle MCP protocol communication
- Manage service initialization and cleanup

**Startup Flow**:
1. Load environment variables
2. Initialize HTTP client for integrations
3. Create service instances (JiraService, etc.)
4. Register MCP tools
5. Start ASGI application

**Port**: 8020

### `main_http_wrapper.py` - HTTP API Server
**Purpose**: REST API interface for MCP tools

**Key Responsibilities**:
- Provide HTTP endpoints mirroring MCP tools
- Initialize and manage service instances
- Handle HTTP request/response lifecycle
- Maintain persistent HTTP connections

**Startup Flow**:
1. Load environment variables
2. Initialize persistent HTTP client
3. Create service instances
4. Register API routers
5. Start FastAPI application

**Port**: 8021

## Subdirectories

### `api/` - HTTP Endpoints
Contains HTTP endpoint definitions that wrap MCP tools for REST API access.

#### `api/jira/jira_http_wrapper.py`
**Purpose**: HTTP endpoints for Jira operations

**Endpoints**:
- `POST /api/jira/issue` - Get Jira issue details
- `POST /api/jira/comment` - Add comment to Jira issue
- `GET /api/jira/tools` - List available Jira tools

**Architecture**:
- Factory pattern for router creation
- Dependency injection for service access
- Clean separation from business logic

### `core/` - Configuration
Central configuration management using Pydantic settings.

#### `core/config.py`
**Purpose**: Environment-based configuration management

**Settings**:
- `jira_url`: Jira instance URL
- `jira_email`: Jira API email
- `jira_api_key`: Jira API token
- `gitlab_url`: GitLab instance URL (optional)
- `gitlab_token`: GitLab API token (optional)
- `langchain_project`: LangSmith project name

**Features**:
- Type validation with Pydantic
- Environment variable loading
- Default values for optional settings

### `integrations/` - Service Integrations
Modular integration framework for connecting to external services.

#### Integration Pattern
Each integration follows this structure:
1. **Client** - Low-level API communication with tracing
2. **Service** - Business logic layer
3. **Tools** - MCP tool registration
4. **Operations** - API endpoint definitions
5. **Schemas** - Data validation models

#### `integrations/jira/` - Jira Integration

**client.py**
- **Purpose**: Low-level Jira API client
- **Features**:
  - HTTP request execution
  - Authentication handling
  - Error handling and mapping
  - Client-level tracing with PII scrubbing
  - Schema validation

**service.py**
- **Purpose**: Jira business logic layer
- **Features**:
  - High-level operations (get_issue, add_comment)
  - Tool registry integration
  - Clean interface for HTTP wrapper

**tools.py**
- **Purpose**: MCP tool registration
- **Features**:
  - FastMCP tool decorators
  - Service integration
  - Tool metadata definition

**operations.py**
- **Purpose**: API operation definitions
- **Features**:
  - HTTP method and path definitions
  - Operation metadata
  - Centralized endpoint configuration

**schemas.py**
- **Purpose**: Data validation and transformation
- **Features**:
  - Pydantic models for API responses
  - Field extraction and cleaning
  - Data transformation helpers

## Data Flow

### MCP Server Flow
```
MCP Client → FastMCP → Tool Registration → Service Layer → Client → External API
```

### HTTP Wrapper Flow
```
HTTP Client → FastAPI → Router → Service Layer → Client → External API
```

## Tracing Architecture

- **Client-Level Tracing**: All external API calls traced at client level
- **PII Protection**: Automatic scrubbing of sensitive data
- **Business Field Extraction**: Only relevant data logged
- **Structured Metadata**: Consistent trace metadata across operations

## Error Handling

- **HTTP Status Mapping**: External API errors mapped to appropriate HTTP responses
- **Service Unavailable**: Graceful handling when services not initialized
- **Validation Errors**: Pydantic-based input validation
- **Timeout Handling**: Configurable timeouts for external API calls

## Development Guidelines

### Adding New Integrations

1. **Create Integration Directory**:
   ```bash
   mkdir src/integrations/newservice
   ```

2. **Implement Core Files**:
   - `client.py` - API client with tracing
   - `service.py` - Business logic
   - `tools.py` - MCP registration
   - `operations.py` - API definitions
   - `schemas.py` - Data models

3. **Update Configuration**:
   - Add settings to `core/config.py`

4. **Register Integration**:
   - Import and initialize in `main.py`
   - Add HTTP wrapper endpoints if needed

### Testing

Integration tests should be placed in `tests/` directory and follow the pattern:
- Unit tests for individual components
- Integration tests for full workflows
- Mock external API calls for reliable testing

## Configuration

All configuration is managed through environment variables. See the root README.md for the complete list of required variables.

## Dependencies

Key dependencies for this module:
- `fastapi` - HTTP server framework
- `fastmcp` - MCP protocol implementation
- `pydantic` - Data validation
- `httpx` - Async HTTP client
- `langsmith` - Tracing and monitoring
- `python-dotenv` - Environment variable loading
