# Makefile for Django Project - إدريسي مارت
# Usage: make <command>

.PHONY: help install setup test lint format clean run migrate shell

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)Available commands:$(NC)'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================
# Setup & Installation
# ============================================

install: ## Install all dependencies
	@echo '$(BLUE)📦 Installing dependencies...$(NC)'
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo '$(GREEN)✅ Dependencies installed$(NC)'

setup: install ## Complete project setup
	@echo '$(BLUE)🔧 Setting up project...$(NC)'
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo '$(YELLOW)⚠️  Created .env file. Please update with your values!$(NC)'; \
	fi
	python manage.py migrate
	@echo '$(GREEN)✅ Project setup complete$(NC)'

env: ## Generate new SECRET_KEY and create .env
	@echo '$(BLUE)🔑 Generating new SECRET_KEY...$(NC)'
	@python -c "from django.core.management.utils import get_random_secret_key; print(f'DJANGO_SECRET_KEY={get_random_secret_key()}')" > .env
	@echo 'DJANGO_DEBUG=True' >> .env
	@echo 'DB_PASSWORD=your-password-here' >> .env
	@echo '$(GREEN)✅ .env file created. Update DB_PASSWORD!$(NC)'

# ============================================
# Code Quality
# ============================================

lint: ## Run all linters (Ruff + Bandit + DjLint)
	@echo '$(BLUE)🔍 Running linters...$(NC)'
	@echo '$(YELLOW)Running Ruff...$(NC)'
	ruff check .
	@echo '$(YELLOW)Running Bandit...$(NC)'
	bandit -r . -c pyproject.toml
	@echo '$(YELLOW)Running DjLint...$(NC)'
	djlint templates/ --check || true
	@echo '$(GREEN)✅ Linting complete$(NC)'

lint-fix: ## Auto-fix linting issues
	@echo '$(BLUE)🔧 Fixing linting issues...$(NC)'
	ruff check . --fix
	ruff format .
	djlint templates/ --reformat || true
	@echo '$(GREEN)✅ Auto-fix complete$(NC)'

format: ## Format code with Ruff
	@echo '$(BLUE)🎨 Formatting code...$(NC)'
	ruff format .
	@echo '$(GREEN)✅ Code formatted$(NC)'

check: ## Run Django system checks
	@echo '$(BLUE)🔍 Running Django checks...$(NC)'
	python manage.py check
	python manage.py check --deploy
	@echo '$(GREEN)✅ Django checks passed$(NC)'

security: ## Run security checks
	@echo '$(BLUE)🔒 Running security checks...$(NC)'
	bandit -r . -c pyproject.toml
	safety check || true
	@echo '$(GREEN)✅ Security scan complete$(NC)'

# ============================================
# Testing
# ============================================

test: ## Run Django tests
	@echo '$(BLUE)🧪 Running tests...$(NC)'
	python manage.py test
	@echo '$(GREEN)✅ Tests complete$(NC)'

test-all: ## Run comprehensive test suite
	@echo '$(BLUE)🧪 Running comprehensive tests...$(NC)'
	./test_all.sh
	@echo '$(GREEN)✅ All tests complete$(NC)'

coverage: ## Run tests with coverage report
	@echo '$(BLUE)📊 Running tests with coverage...$(NC)'
	coverage run --source='.' manage.py test
	coverage report
	coverage html
	@echo '$(GREEN)✅ Coverage report generated in htmlcov/$(NC)'

# ============================================
# Database
# ============================================

migrate: ## Run database migrations
	@echo '$(BLUE)🗄️  Running migrations...$(NC)'
	python manage.py migrate
	@echo '$(GREEN)✅ Migrations complete$(NC)'

makemigrations: ## Create new migrations
	@echo '$(BLUE)📝 Creating migrations...$(NC)'
	python manage.py makemigrations
	@echo '$(GREEN)✅ Migrations created$(NC)'

db-reset: ## Reset database (WARNING: Deletes all data!)
	@echo '$(RED)⚠️  WARNING: This will delete all data!$(NC)'
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f db.sqlite3; \
		python manage.py migrate; \
		echo '$(GREEN)✅ Database reset complete$(NC)'; \
	else \
		echo '$(YELLOW)Cancelled$(NC)'; \
	fi

# ============================================
# Development
# ============================================

run: ## Start development server
	@echo '$(BLUE)🚀 Starting development server...$(NC)'
	python manage.py runserver

shell: ## Open Django shell
	@echo '$(BLUE)🐚 Opening Django shell...$(NC)'
	python manage.py shell

superuser: ## Create superuser
	@echo '$(BLUE)👤 Creating superuser...$(NC)'
	python manage.py createsuperuser

collectstatic: ## Collect static files
	@echo '$(BLUE)📦 Collecting static files...$(NC)'
	python manage.py collectstatic --noinput
	@echo '$(GREEN)✅ Static files collected$(NC)'

# ============================================
# Git Hooks
# ============================================

pre-commit-install: ## Install pre-commit hooks
	@echo '$(BLUE)🪝 Installing pre-commit hooks...$(NC)'
	pip install pre-commit
	pre-commit install
	@echo '$(GREEN)✅ Pre-commit hooks installed$(NC)'

pre-commit-run: ## Run pre-commit on all files
	@echo '$(BLUE)🪝 Running pre-commit checks...$(NC)'
	pre-commit run --all-files
	@echo '$(GREEN)✅ Pre-commit checks complete$(NC)'

# ============================================
# Cleaning
# ============================================

clean: ## Clean up cache and temporary files
	@echo '$(BLUE)🧹 Cleaning up...$(NC)'
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	@echo '$(GREEN)✅ Cleanup complete$(NC)'

clean-all: clean ## Deep clean including database and static files
	@echo '$(RED)⚠️  Deep cleaning (removes db and static files)...$(NC)'
	rm -f db.sqlite3
	rm -rf staticfiles/
	rm -rf media/
	@echo '$(GREEN)✅ Deep clean complete$(NC)'

# ============================================
# Production
# ============================================

prod-check: ## Check if ready for production
	@echo '$(BLUE)🔍 Checking production readiness...$(NC)'
	@python manage.py check --deploy
	@echo '$(YELLOW)Checking for DEBUG=False...$(NC)'
	@grep -q "DEBUG = False" idrissimart/settings/docker.py && echo '$(GREEN)✅ DEBUG is False$(NC)' || echo '$(RED)❌ DEBUG is True$(NC)'
	@echo '$(YELLOW)Checking SECRET_KEY in environment...$(NC)'
	@grep -q "os.getenv" idrissimart/settings/common.py && echo '$(GREEN)✅ SECRET_KEY uses environment$(NC)' || echo '$(RED)❌ SECRET_KEY is hardcoded$(NC)'
	@echo '$(GREEN)✅ Production check complete$(NC)'

deploy-prep: lint test collectstatic ## Prepare for deployment
	@echo '$(BLUE)🚀 Preparing for deployment...$(NC)'
	@echo '$(GREEN)✅ Ready to deploy!$(NC)'

# ============================================
# Documentation
# ============================================

docs: ## Generate project documentation
	@echo '$(BLUE)📚 Generating documentation...$(NC)'
	@echo 'Documentation generation not configured yet'

# ============================================
# Quick Commands
# ============================================

quickstart: setup run ## Quick project start (setup + run)

quicktest: lint-fix test ## Quick test (fix lint + test)

daily: clean lint test ## Daily development workflow

# ============================================
# Information
# ============================================

info: ## Show project information
	@echo '$(BLUE)📊 Project Information:$(NC)'
	@echo '  Python version:  ' $$(python --version)
	@echo '  Django version:  ' $$(python -c "import django; print(django.VERSION)")
	@echo '  Project:         إدريسي مارت'
	@echo '  Files:           ' $$(find . -name '*.py' -not -path '*/migrations/*' -not -path '*/.venv/*' | wc -l) 'Python files'
	@echo ''
	@echo '$(BLUE)📦 Installed packages:$(NC)'
	@pip list --format=freeze | head -10
	@echo '  ... (showing first 10)'

status: ## Show git status and pending changes
	@echo '$(BLUE)📊 Git Status:$(NC)'
	@git status --short
	@echo ''
	@echo '$(BLUE)📝 Uncommitted changes:$(NC)'
	@git diff --stat

# ============================================
# Aliases
# ============================================

server: run ## Alias for 'run'
tests: test ## Alias for 'test'
fmt: format ## Alias for 'format'
install-hooks: pre-commit-install ## Alias for 'pre-commit-install'
