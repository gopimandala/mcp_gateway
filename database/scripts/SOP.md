# Database Setup SOP

## Step 1: Start PostgreSQL
```bash
cd database
docker compose up -d
```

## Step 2: Install Dependencies
```bash
cd /home/ubuntu/mcp_gateway
uv add psycopg2-binary pydantic sqlparse sqlvalidator
```

## Step 3: Populate Database
```bash
cd database/scripts
uv run python setup_database.py
```

## Step 4: Verify Database
```bash
cd database/scripts
uv run python test_database.py
```

## Step 5: Test Metrics Module
```bash
cd src/metrics
uv run python test_step2.py
```

## Reset Everything
```bash
cd database
docker compose down -v
docker compose up -d
```

## Expected Results
- Jira Issues: 1000
- ServiceNow Incidents: 1000
- Total Tables: 6
- Metrics Module: All tests pass
