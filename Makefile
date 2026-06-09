.PHONY: setup up down logs test lint clean

setup:
	@echo "🚀 Setting up RapiDrop development environment..."
	docker compose up -d postgres redis rabbitmq
	@sleep 3
	cd apps/api && poetry install
	cd apps/api && alembic upgrade head
	@echo "✅ Setup complete! Run 'make up' to start all services."

up:
	docker compose up -d
	@echo "✅ Services running. API: http://localhost:8000, Web: http://localhost:3000"

down:
	docker compose down

logs:
	docker compose logs -f

test:
	cd apps/api && pytest
	cd apps/web && pnpm test

lint:
	cd apps/api && ruff check .
	cd apps/web && pnpm lint

clean:
	docker compose down -v
	rm -rf apps/api/__pycache__ apps/api/.pytest_cache
	rm -rf apps/web/.next apps/web/node_modules
	rm -rf node_modules
