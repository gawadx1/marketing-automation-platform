.PHONY: help install dev build up down logs test lint clean migrate

help:
	@echo "Marketing Automation Platform - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install      Install Python dependencies"
	@echo "  make dev          Run development server"
	@echo "  make build        Build Docker images"
	@echo "  make up           Start all services with Docker"
	@echo "  make down         Stop all services"
	@echo "  make logs         View Docker logs"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linting"
	@echo "  make migrate      Run database migrations"
	@echo "  make shell        Open Python shell"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker compose build

up:
	docker compose up -d

up-prod:
	docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/
	ruff format --check app/ tests/

format:
	ruff format app/ tests/

migrate:
	alembic upgrade head

migrate-new:
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

shell:
	python -c "import asyncio; from app.core.database import get_session_factory; from app.core.config import get_settings; print('Ready')"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache logs/ *.log

docker-clean:
	docker compose down -v
	docker system prune -f

.PHONY: help install dev build up up-prod down logs test lint format migrate migrate-new shell clean docker-clean
