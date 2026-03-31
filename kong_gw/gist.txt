docker compose up -d
docker exec -it kong-gateway kong reload

curl -X POST http://localhost:8000/api/jira/issue \
-H "Content-Type: application/json" \
-d '{"query":"delete kan-1"}'

