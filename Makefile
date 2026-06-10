.PHONY: setup up down logs test lint clean glitchtip-setup glitchtip-reset glitchtip-logs

setup:
	@echo "🚀 Setting up RapiDrop development environment..."
	docker compose up -d postgres redis rabbitmq
	@sleep 3
	cd apps/api && poetry install
	cd apps/api && alembic upgrade head
	@echo "✅ Setup complete! Run 'make up' to start all services."

up:
	docker compose up -d
	@echo "✅ Services running. API: http://localhost:8000, Web: http://localhost:3000, GlitchTip: http://localhost:8000"

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

# GlitchTip (Sentry-compatible error tracking)
glitchtip-setup:
	@echo "🔧 Setting up GlitchTip..."
	docker compose up -d postgres redis
	@sleep 3
	docker compose exec postgres psql -U rapidrop -c "CREATE DATABASE glitchtip OWNER rapidrop;" 2>/dev/null || true
	docker compose up -d glitchtip
	@echo "⏳ Waiting for GlitchTip to start..."
	@sleep 10
	docker compose exec glitchtip ./manage.py migrate --noinput
	docker compose exec glitchtip ./manage.py createsuperuser --email admin@rapidrop.local --noinput 2>/dev/null || true
	docker compose exec glitchtip ./manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(email='admin@rapidrop.local')
u.set_password('rapidrop123')
u.save()
print('Admin password set to: rapidrop123')
"
	@echo "✅ GlitchTip ready at http://localhost:8000"
	@echo "   Login: admin@rapidrop.local / rapidrop123"
	@echo "   Create a project to get your DSN"

glitchtip-reset:
	@echo "🔄 Resetting GlitchTip..."
	docker compose rm -sf glitchtip
	docker compose exec postgres psql -U rapidrop -c "DROP DATABASE IF EXISTS glitchtip;" 2>/dev/null || true
	docker volume rm rapidrop_glitchtip-data 2>/dev/null || true
	@make glitchtip-setup

glitchtip-logs:
	docker compose logs -f glitchtip
