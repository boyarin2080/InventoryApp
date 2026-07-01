# Makefile for Inventory Management System

.PHONY: help install setup dev test migrate makemigrations shell clean docker-up docker-down docker-build

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

setup: ## Set up development environment
	cp .env.example .env
	pip install -r requirements.txt
	python manage.py migrate
	@echo "Development environment setup complete!"
	@echo "Edit .env file with your settings"
	@echo "Run 'make dev' to start development server"

dev: ## Run development server
	python manage.py runserver

test: ## Run tests
	python manage.py test

migrate: ## Apply database migrations
	python manage.py migrate

makemigrations: ## Create new migrations
	python manage.py makemigrations

shell: ## Open Django shell
	python manage.py shell

clean: ## Clean up Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".coverage" -delete

docker-up: ## Start Docker containers
	docker-compose up

docker-down: ## Stop Docker containers
	docker-compose down

docker-build: ## Build Docker images
	docker-compose build

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-shell: ## Open shell in web container
	docker-compose exec web bash

docker-migrate: ## Run migrations in Docker
	docker-compose exec web python manage.py migrate

docker-createsuperuser: ## Create superuser in Docker
	docker-compose exec web python manage.py createsuperuser

docker-test: ## Run tests in Docker
	docker-compose exec web python manage.py test