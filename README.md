# MCP Gateway

A comprehensive Model Context Protocol (MCP) gateway that provides secure, traced access to enterprise tools like Jira through both MCP and HTTP interfaces.

## Architecture Overview

```
mcp_gateway/
├── brain/           # AI orchestration and planning layer
├── chat/            # Chat interfaces for user interaction
├── kong_gw/         # Kong API gateway configuration
├── shared/          # Common utilities and tracing
├── src/             # Core gateway implementation
│   ├── api/         # HTTP wrapper endpoints
│   ├── core/        # Configuration and settings
│   └── integrations/ # Service integrations (Jira, etc.)
└── tests/           # Test suite
```

## Quick Start

### Prerequisites
- Python 3.9+
- Docker (optional, for Kong)

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd mcp_gateway
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials (see Environment Variables below)
```

### Running the Gateway

#### Option 1: MCP Server
```bash
python src/main.py
# Runs on port 8020
# For: MCP clients (Claude Desktop, MCP-compatible AI assistants)
```

#### Option 2: HTTP Wrapper
```bash
python src/main_http_wrapper.py
# Runs on port 8021
# For: HTTP clients (web apps, mobile apps, testing with curl/Postman)
```

#### Option 3: Brain Server (AI Orchestration)
```bash
cd brain
python brain_server.py
# Runs on port 8000
# For: AI-powered orchestration and natural language interfaces
```

## Environment Variables

Create a `.env` file in the root directory:

```bash
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_KEY=your-api-token-here

# GitLab Configuration (Optional)
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your-gitlab-token

# LangSmith/LangChain Configuration
LANGCHAIN_PROJECT=mcp-multi-gateway

# OpenAI Configuration (for Brain Server)
OPENAI_KEY=your-openai-api-key
```

**Security Note**: Never commit actual API keys to version control. Use environment variables or secure secret management.

## Core Components

### 1. MCP Server (`src/main.py`)
- **Purpose**: Primary MCP protocol server
- **Port**: 8020
- **Features**: Tool registration, service lifecycle management

### 2. HTTP Wrapper (`src/main_http_wrapper.py`)
- **Purpose**: REST API interface for MCP tools
- **Port**: 8021
- **Features**: HTTP endpoints mirroring MCP tools

### 3. Brain Server (`brain/brain_server.py`)
- **Purpose**: AI-powered orchestration and planning
- **Port**: 8000
- **Features**: LLM-based tool selection and execution planning

### 4. Integration Services (`src/integrations/`)
- **Purpose**: Enterprise system connectors
- **Current**: Jira integration with client/service architecture
- **Extensible**: Framework for adding new integrations

## Workflow

1. **User Request** → Brain Server (AI planning) or Direct API call
2. **Tool Selection** → LLM selects appropriate MCP tools
3. **Execution** → MCP Server or HTTP Wrapper executes tools
4. **Integration** → Service layer calls external APIs (Jira, etc.)
5. **Response** → Traced, cleaned response back to user

## Tracing & Security

- **Client-Level Tracing**: All operations traced at integration client level
- **PII Scrubbing**: Automatic removal of sensitive data from traces
- **Business Field Extraction**: Only relevant business data logged
- **Secure Headers**: Authentication headers masked in logs

## Development

### Adding New Integrations

1. Create new integration in `src/integrations/`
2. Follow client/service pattern
3. Add tracing decorators
4. Register tools in MCP server
5. Add HTTP wrapper endpoints if needed

### Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python tests/test_jira.py
```

## API Documentation

### MCP Endpoints (Port 8020)
- `POST /mcp/call` - Execute MCP tools
- `GET /mcp/tools` - List available tools

### HTTP Endpoints (Port 8021)
- `POST /api/jira/issue` - Get Jira issue
- `POST /api/jira/comment` - Add comment to Jira issue
- `GET /api/jira/tools` - List Jira tools

### Brain Server Endpoints (Port 8000)
- `POST /plan` - Generate execution plan
- `POST /execute` - Execute plan with tools

## Monitoring & Debugging

- **LangSmith Tracing**: Automatic tracing of all operations
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Health Checks**: Built-in health endpoints for monitoring

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Kong Gateway Integration
See `kong_gw/` directory for Kong API gateway configuration.

## Support

For issues and questions:
1. Check individual component READMEs in subdirectories
2. Review test files for usage examples
3. Check logs for tracing information

---

**Note**: This project follows the standard practice of having a high-level overview at the root and detailed documentation in each subdirectory for maintainable, scalable documentation.