.PHONY: install dev services stop migrate test

# Install all dependencies
install:
	pip install uv && uv sync

# Start the dev server (auto-reload)
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Postgres + Qdrant + Redis
services:
	docker compose up -d
	@echo "Waiting for Postgres..."
	@sleep 3
	@echo "Services ready:"
	@echo "  Postgres  → localhost:5432"
	@echo "  Qdrant    → localhost:6333  (dashboard: http://localhost:6333/dashboard)"
	@echo "  Redis     → localhost:6379"

# Stop all services
stop:
	docker compose down

# Run DB migrations
migrate:
	alembic upgrade head

# Run tests
test:
	pytest tests/ -v

# Open the API docs
docs:
	open http://localhost:8000/docs

# Check health
health:
	curl -s http://localhost:8000/health | python3 -m json.tool
