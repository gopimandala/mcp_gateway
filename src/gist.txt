uv run -m src.main
uv run -m src.main_http_wrapper
uv run uvicorn brain_server:app --host 0.0.0.0 --port 9000 --reload

curl -X POST http://localhost:9000/run_brain -H "Content-Type: application/json" -d '{"user_request":"are you stupid"}'