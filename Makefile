.PHONY: help build up down logs shell migrate makemigrations createsuperuser populate test clean

help:
	@echo "K-Auto Parts Management System - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View all logs"
	@echo "  make logs-web       - View web service logs"
	@echo "  make logs-db        - View database logs"
	@echo "  make logs-redis     - View Redis logs"
	@echo "  make shell          - Access Django shell"
	@echo "  make bash           - Access container bash"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make populate       - Populate sample data"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make restart        - Restart all services"
	@echo "  make ps             - List running containers"

build:
	docker-compose build

up:
	docker-compose up

up-d:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

logs-redis:
	docker-compose logs -f redis

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

populate:
	docker-compose exec web python manage.py populate_data

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	docker system prune -f

restart:
	docker-compose restart

ps:
	docker-compose ps

# Database commands
db-shell:
	docker-compose exec db psql -U postgres -d kauto_db

db-backup:
	docker-compose exec db pg_dump -U postgres kauto_db > backup_$$(date +%Y%m%d_%H%M%S).sql

# Redis commands
redis-cli:
	docker-compose exec redis redis-cli

redis-flush:
	docker-compose exec redis redis-cli FLUSHALL

# Development helpers
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

check:
	docker-compose exec web python manage.py check

requirements:
	docker-compose exec web pip freeze > requirements.txt
