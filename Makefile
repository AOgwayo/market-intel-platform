.PHONY: help api frontend tests format lint migrate generate-types up down logs clean install

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Development
install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && poetry install
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

api: ## Run the API server
	cd backend && poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

frontend: ## Run the frontend development server
	cd frontend && npm run dev

up: ## Start all services with Docker Compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

# Testing
tests: ## Run all tests
	cd backend && poetry run pytest

test-api: ## Run API tests only
	cd backend && poetry run pytest tests/api/

test-strategies: ## Run strategy tests only
	cd backend && poetry run pytest tests/strategies/

# Code Quality
format: ## Format code with black and isort
	cd backend && poetry run black .
	cd backend && poetry run isort .

lint: ## Run linting with ruff and mypy
	cd backend && poetry run ruff check .
	cd backend && poetry run mypy .

lint-fix: ## Fix linting issues automatically
	cd backend && poetry run ruff check --fix .

# Database
migrate: ## Run database migrations
	cd backend && poetry run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	cd backend && poetry run alembic revision --autogenerate -m "$(MESSAGE)"

migrate-down: ## Rollback one migration
	cd backend && poetry run alembic downgrade -1

db-reset: ## Reset database (WARNING: destroys all data)
	docker-compose down -v
	docker-compose up -d postgres redis
	sleep 5
	$(MAKE) migrate

# Code Generation
generate-types: ## Generate TypeScript types from OpenAPI spec
	./scripts/generate_openapi_types.sh

openapi-spec: ## Generate OpenAPI specification
	cd backend && poetry run python -c "from app.main import app; import json; print(json.dumps(app.openapi()))" > openapi.json

# Development Environment
bootstrap: ## Bootstrap development environment
	./scripts/dev_bootstrap.sh

setup-pre-commit: ## Setup pre-commit hooks
	cd backend && poetry run pre-commit install

# Utilities
clean: ## Clean up temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	cd frontend && rm -rf .next node_modules/.cache
	docker system prune -f

backup-db: ## Backup database
	docker-compose exec postgres pg_dump -U postgres market_intel > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database (usage: make restore-db FILE=backup_file.sql)
	docker-compose exec -T postgres psql -U postgres market_intel < $(FILE)

# Production
build: ## Build all Docker images
	docker-compose build

deploy: ## Deploy to production (placeholder)
	@echo "Production deployment not yet configured"

# Monitoring
health-check: ## Check health of all services
	@echo "Checking API health..."
	curl -f http://localhost:8000/health || echo "API is down"
	@echo "Checking Frontend..."
	curl -f http://localhost:3000 || echo "Frontend is down"
	@echo "Checking Airflow..."
	curl -f http://localhost:8080/health || echo "Airflow is down"

status: ## Show status of all services
	docker-compose ps