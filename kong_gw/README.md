# Kong Gateway Integration (`kong_gw/`)

Kong API Gateway configuration for the MCP Gateway, providing enterprise-grade API management, security, and traffic management.

## Purpose

The Kong Gateway integration provides:
- **API Gateway**: Single entry point for all MCP Gateway services
- **Load Balancing**: Distribute traffic across multiple instances
- **Security**: Authentication, rate limiting, and access control
- **Monitoring**: Request logging and metrics collection
- **High Availability**: Health checks and failover capabilities

## Directory Structure

```
kong_gw/
├── kong.yml              # Kong declarative configuration
├── kong.conf             # Kong runtime configuration
├── docker-compose.yml    # Kong + database deployment
└── README.md             # This documentation
```

## Architecture Overview

```
Internet → Kong Gateway → MCP Gateway Services
                        ├── Brain Server (8000)
                        ├── MCP Server (8020)
                        └── HTTP Wrapper (8021)
```

## Configuration Files

### `kong.yml` - Declarative Configuration
**Purpose**: Complete Kong configuration in declarative format

**Key Sections**:

```yaml
_format_version: "3.0"

# Services Configuration
services:
  - name: brain-server
    url: http://brain-server:8000
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
  
  - name: mcp-server
    url: http://mcp-server:8020
    plugins:
      - name: request-size-limiting
        config:
          allowed_payload_size: 10

# Routes Configuration
routes:
  - name: brain-api
    service: brain-server
    paths:
      - /api/brain
    methods:
      - POST
      - GET
  
  - name: mcp-api
    service: mcp-server
    paths:
      - /api/mcp
    methods:
      - POST
      - GET

# Consumers and Authentication
consumers:
  - username: api-client
    keyauth_credentials:
      - key: your-api-key-here

plugins:
  - name: key-auth
    service: mcp-server
    config:
      hide_credentials: true
```

### `kong.conf` - Runtime Configuration
**Purpose**: Kong daemon runtime settings

**Key Settings**:
```ini
# Database Configuration
database = postgres
pg_host = kong-database
pg_port = 5432
pg_user = kong
pg_password = kong_password
pg_database = kong

# Network Configuration
proxy_listen = 0.0.0.0:8000
admin_listen = 0.0.0.0:8001

# Performance Tuning
nginx_worker_processes = auto
nginx_worker_connections = 16384

# Logging
log_level = info
access_log = /dev/stdout
error_log = /dev/stderr

# Security
trusted_ips = 0.0.0.0/0,::/0
real_ip_header = X-Forwarded-For
```

### `docker-compose.yml` - Deployment Configuration
**Purpose**: Complete Kong ecosystem deployment

**Services**:
```yaml
version: '3.8'

services:
  # Kong Database
  kong-database:
    image: postgres:13
    environment:
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: kong_password
      POSTGRES_DB: kong
    volumes:
      - kong_data:/var/lib/postgresql/data
    networks:
      - kong-net

  # Kong Migration
  kong-migration:
    image: kong:3.4
    command: kong migrations bootstrap
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong_password
    depends_on:
      - kong-database
    networks:
      - kong-net

  # Kong Gateway
  kong:
    image: kong:3.4
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong_password
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    ports:
      - "8000:8000"  # Proxy port
      - "8001:8001"  # Admin API port
    depends_on:
      - kong-database
    networks:
      - kong-net
    volumes:
      - ./kong.yml:/kong/declarative/kong.yml:ro

volumes:
  kong_data:

networks:
  kong-net:
    driver: bridge
```

## Deployment

### Quick Start

```bash
# Start Kong ecosystem
cd kong_gw
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f kong

# Verify Kong is running
curl http://localhost:8000
```

### Configuration Deployment

```bash
# Apply declarative configuration
curl -X POST http://localhost:8001/config \
  -H "Content-Type: application/json" \
  -d @kong.yml

# Verify configuration
curl http://localhost:8001/services
curl http://localhost:8001/routes
```

## API Gateway Configuration

### Service Registration

**Brain Server Service**:
```bash
curl -X POST http://localhost:8001/services \
  --data name=brain-server \
  --data url='http://brain-server:8000'
```

**MCP Server Service**:
```bash
curl -X POST http://localhost:8001/services \
  --data name=mcp-server \
  --data url='http://mcp-server:8020'
```

### Route Configuration

**Brain API Routes**:
```bash
curl -X POST http://localhost:8001/services/brain-server/routes \
  --data 'paths[]=/api/brain' \
  --data 'methods[]=POST,GET'
```

**MCP API Routes**:
```bash
curl -X POST http://localhost:8001/services/mcp-server/routes \
  --data 'paths[]=/api/mcp' \
  --data 'methods[]=POST,GET'
```

## Security Configuration

### API Key Authentication

```bash
# Enable key-auth plugin
curl -X POST http://localhost:8001/plugins \
  --data name=key-auth \
  --data service=mcp-server

# Create consumer
curl -X POST http://localhost:8001/consumers \
  --data username=api-client

# Generate API key
curl -X POST http://localhost:8001/consumers/api-client/keyauth \
  --data key=your-secure-api-key
```

### Rate Limiting

```bash
# Apply rate limiting to brain server
curl -X POST http://localhost:8001/plugins \
  --data name=rate-limiting \
  --data service=brain-server \
  --data config.minute=100 \
  --data config.hour=1000

# Apply stricter limits to MCP server
curl -X POST http://localhost:8001/plugins \
  --data name=rate-limiting \
  --data service=mcp-server \
  --data config.minute=50 \
  --data config.hour=500
```

### IP Whitelisting

```bash
# Restrict access to specific IPs
curl -X POST http://localhost:8001/plugins \
  --data name=ip-restriction \
  --data service=mcp-server \
  --data config.whitelist=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

## Monitoring and Logging

### Request Logging

```bash
# Enable detailed logging
curl -X POST http://localhost:8001/plugins \
  --data name=file-log \
  --data config.path=/var/log/kong/access.log \
  --data config.reopen=true
```

### Prometheus Metrics

```bash
# Enable Prometheus plugin
curl -X POST http://localhost:8001/plugins \
  --data name=prometheus

# Access metrics
curl http://localhost:8001/metrics
```

### Health Checks

```bash
# Configure active health checks
curl -X PATCH http://localhost:8001/services/brain-server \
  --data 'active_probes.enabled=true' \
  --data 'active_probes.http_path=/health' \
  --data 'active_probes.healthy.interval=10' \
  --data 'active_probes.healthy.successes=3'
```

## Performance Optimization

### Caching Configuration

```bash
# Enable response caching
curl -X POST http://localhost:8001/plugins \
  --data name=proxy-cache \
  --data config.cache_ttl=300 \
  --data config.cache_strategy=memory

# Cache specific endpoints
curl -X POST http://localhost:8001/services/mcp-server/routes \
  --data 'paths[]=/api/mcp/tools' \
  --data 'methods[]=GET'
```

### Connection Pooling

```yaml
# In kong.conf
upstream_keepalive_pool_size = 100
upstream_keepalive_max_requests = 1000
upstream_keepalive_timeout = 60
```

## High Availability

### Load Balancing

```yaml
# Multiple upstream instances
upstreams:
  - name: brain-server-upstream
    algorithm: round-robin
    healthchecks:
      active:
        http_path: /health
        interval: 10
        timeout: 5
        healthy:
          interval: 5
          successes: 3
        unhealthy:
          interval: 5
          http_failures: 3
    targets:
      - target: brain-server-1:8000
        weight: 100
      - target: brain-server-2:8000
        weight: 100
```

### Failover Configuration

```yaml
services:
  - name: brain-server-primary
    url: http://brain-server-primary:8000
    plugins:
      - name: canary-release
        config:
          percentage: 90
  
  - name: brain-server-canary
    url: http://brain-server-canary:8000
    plugins:
      - name: canary-release
        config:
          percentage: 10
```

## SSL/TLS Configuration

### Certificate Management

```bash
# Add SSL certificate
curl -X POST http://localhost:8001/certificates \
  --form "cert=@/path/to/cert.pem" \
  --form "key=@/path/to/key.pem" \
  --form "snis[]=api.yourdomain.com"
```

### HTTPS Enforcement

```bash
# Force HTTPS redirect
curl -X POST http://localhost:8001/plugins \
  --data name=redirect-https \
  --data config.https_port=8443
```

## API Usage Examples

### Through Kong Gateway

```bash
# Brain Server API (with API key)
curl -X POST http://localhost:8000/api/brain/plan \
  -H "Content-Type: application/json" \
  -H "apikey: your-api-key" \
  -d '{"user_request": "Get Jira ticket PROJ-123"}'

# MCP Server API (with API key)
curl -X POST http://localhost:8000/api/mcp/call \
  -H "Content-Type: application/json" \
  -H "apikey: your-api-key" \
  -d '{"tool": "get_issue", "parameters": {"issue_key": "PROJ-123"}}'
```

### Direct Service Access (Bypassing Kong)

```bash
# Direct Brain Server access
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"user_request": "Get Jira ticket PROJ-123"}'

# Direct MCP Server access
curl -X POST http://localhost:8020/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_issue", "parameters": {"issue_key": "PROJ-123"}}'
```

## Management API

### Service Management

```bash
# List all services
curl http://localhost:8001/services

# Get service details
curl http://localhost:8001/services/brain-server

# Update service
curl -X PATCH http://localhost:8001/services/brain-server \
  --data url='http://new-brain-server:8000'

# Delete service
curl -X DELETE http://localhost:8001/services/brain-server
```

### Plugin Management

```bash
# List all plugins
curl http://localhost:8001/plugins

# Get plugin details
curl http://localhost:8001/plugins/{plugin-id}

# Update plugin
curl -X PATCH http://localhost:8001/plugins/{plugin-id} \
  --data config.minute=200

# Delete plugin
curl -X DELETE http://localhost:8001/plugins/{plugin-id}
```

## Troubleshooting

### Common Issues

**Service Not Reachable**:
```bash
# Check service status
curl http://localhost:8001/services/brain-server

# Check upstream connectivity
curl http://localhost:8001/upstreams

# Check Kong logs
docker-compose logs kong
```

**Authentication Failures**:
```bash
# Verify consumer exists
curl http://localhost:8001/consumers

# Check API key validity
curl http://localhost:8001/consumers/api-client/keyauth

# Test with curl
curl -H "apikey: your-api-key" http://localhost:8000/api/brain/plan
```

**Rate Limiting Issues**:
```bash
# Check rate limiting configuration
curl http://localhost:8001/plugins?name=rate-limiting

# Monitor rate limit headers
curl -I http://localhost:8000/api/brain/plan
```

### Debug Mode

```bash
# Enable debug logging
docker-compose exec kong kong config dev /etc/kong/kong.conf

# View detailed logs
docker-compose logs -f kong
```

## Security Best Practices

### Network Security

1. **Network Segmentation**: Place Kong in DMZ
2. **Firewall Rules**: Restrict access to admin API
3. **VPN Access**: Use VPN for administrative access
4. **IP Whitelisting**: Restrict source IPs

### API Security

1. **API Key Rotation**: Regularly rotate API keys
2. **Rate Limiting**: Implement strict rate limits
3. **Input Validation**: Validate all inputs
4. **HTTPS Only**: Enforce TLS encryption

### Monitoring

1. **Access Logs**: Monitor all API access
2. **Anomaly Detection**: Alert on unusual patterns
3. **Performance Metrics**: Monitor response times
4. **Error Tracking**: Alert on high error rates

## Dependencies

- **Kong Gateway**: 3.4+ (recommended)
- **PostgreSQL**: 13+ (for Kong database)
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-container deployment)

## Integration with MCP Gateway

### Service Discovery

Kong automatically discovers MCP Gateway services:
- **Brain Server**: AI orchestration service
- **MCP Server**: Primary MCP protocol server
- **HTTP Wrapper**: REST API interface

### Traffic Routing

Kong routes requests based on path patterns:
- `/api/brain/*` → Brain Server
- `/api/mcp/*` → MCP Server
- `/api/jira/*` → HTTP Wrapper

### Health Monitoring

Kong monitors service health:
- **Active Health Checks**: Periodic health probes
- **Passive Health Checks**: Monitor response codes
- **Circuit Breaking**: Fail fast on unhealthy services

## Future Enhancements

### Planned Features

1. **Web Application Firewall (WAF)**: Advanced threat protection
2. **API Analytics**: Detailed usage analytics and insights
3. **GraphQL Gateway**: GraphQL API aggregation
4. **Service Mesh Integration**: Istio/Linkerd integration
5. **Multi-Region Deployment**: Global traffic management
6. **API Documentation**: OpenAPI/Swagger integration
7. **Developer Portal**: Self-service API management
