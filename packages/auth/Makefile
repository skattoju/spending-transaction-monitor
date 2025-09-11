.PHONY: help install dev build test lint format clean
.PHONY: auth-up auth-down db-up db-down services-up services-down
.PHONY: test-unit test-e2e test-all test-watch
.PHONY: api-dev ui-dev deps-install

# Default target
help: ## Show this help message
	@echo "🔐 Authentication Development Commands"
	@echo "====================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 🚀 Quick Start
install: ## Install all dependencies (Node + Python)
	cd ../.. && pnpm setup

dev: services-up ## Start full development environment
	@echo "🚀 Starting development environment..."
	@echo "📊 UI: http://localhost:5173"
	@echo "🔌 API: http://localhost:8000"
	@echo "🔐 Keycloak: http://localhost:8080"
	cd ../.. && pnpm dev

##@ 🔧 Services Management  
auth-up: ## Start Keycloak authentication service
	@echo "🔐 Starting Keycloak..."
	podman compose up -d
	@echo "⏳ Waiting for Keycloak to be ready..."
	@timeout 60 bash -c 'until curl -f http://localhost:8080/health/ready >/dev/null 2>&1; do sleep 2; done' || true
	@echo "✅ Keycloak is ready at http://localhost:8080"

auth-down: ## Stop Keycloak authentication service
	podman compose down

auth-logs: ## Show Keycloak logs
	podman compose logs -f keycloak

auth-restart: ## Restart Keycloak
	podman compose restart keycloak

db-up: ## Start PostgreSQL database
	@echo "🗄️  Starting database..."
	cd ../.. && pnpm db:start
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	cd ../.. && pnpm db:upgrade
	@echo "✅ Database is ready"

db-down: ## Stop PostgreSQL database  
	cd ../.. && pnpm db:stop

services-up: auth-up db-up ## Start all services (Keycloak + Database)
	@echo "🎉 All services are running!"

services-down: auth-down db-down ## Stop all services
	@echo "🛑 All services stopped"

##@ 🧪 Testing
test-deps: ## Install test dependencies
	uv pip install -r requirements.txt

test-unit: ## Run unit tests only
	@echo "🧪 Running auth unit tests..."
	source .venv/bin/activate && python -m pytest tests/ -v

test-e2e: services-up ## Run end-to-end tests (requires services)
	@echo "🎭 Running E2E tests..."
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	source .venv/bin/activate && python scripts/test_e2e.py
	
test-all: test-unit ## Run all tests
	@echo "✅ All tests completed"

test-watch: ## Run tests in watch mode
	source .venv/bin/activate && python -m pytest tests/ -v --tb=short -f

test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	source .venv/bin/activate && python -m pytest tests/ --cov-report=html:htmlcov --cov-report=term-missing
	@echo "📋 Coverage report: htmlcov/index.html"

##@ 🎯 Development
api-dev: ## Start API development server only
	cd ../.. && pnpm --filter @spending-monitor/api dev

ui-dev: ## Start UI development server only  
	cd ../.. && pnpm --filter @spending-monitor/ui dev

##@ 🔍 Code Quality
lint: ## Run linting on auth code
	cd ../.. && pnpm lint

lint-fix: ## Fix linting issues automatically
	cd ../.. && pnpm lint:fix

format: ## Format all code
	cd ../.. && pnpm format

format-check: ## Check code formatting
	cd ../.. && pnpm format:check

##@ 🔐 Authentication Setup
auth-setup: auth-up ## Setup Keycloak with automated configuration
	@echo "🔧 Setting up Keycloak configuration..."
	@echo "⏳ Waiting for Keycloak to be fully ready..."
	@sleep 10
	@echo "🤖 Running automated setup script..."
	source .venv/bin/activate && python scripts/setup_keycloak.py
	@echo "✅ Keycloak setup completed!"
	@echo "📋 Created:"
	@echo "   • Realm: spending-monitor"
	@echo "   • Client: spending-monitor (OIDC, PKCE enabled)"
	@echo "   • Test user: testuser@example.com / password123"
	@echo "   • Roles: user, admin"

auth-test: auth-up ## Test authentication with real endpoints
	@echo "🔐 Testing authentication endpoints..."
	@sleep 5
	@echo "🔍 For comprehensive auth testing, use: make test-e2e"
	@echo "📋 Manual verification:"
	@echo "   • OIDC config: http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration"
	@echo "   • JWKS: http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs"

##@ 📊 Monitoring & Logs
status: ## Show status of all services
	@echo "📊 Service Status:"
	@echo "==================="
	@curl -sf http://localhost:8000/health 2>/dev/null && echo "✅ API (8000)" || echo "❌ API (8000)"
	@curl -sf http://localhost:8080/health/ready 2>/dev/null && echo "✅ Keycloak (8080)" || echo "❌ Keycloak (8080)"  
	@curl -sf http://localhost:5173 2>/dev/null && echo "✅ UI (5173)" || echo "ℹ️  UI (5173) - start with: pnpm dev:vite"

##@ 🎭 Demo & Examples  
demo: services-up ## Start demo environment with sample data
	@echo "🎭 Starting demo environment..."
	cd ../.. && pnpm db:seed
	$(MAKE) dev

demo-auth: auth-up api-dev ## Demo authentication flow only
	@echo "🔐 Authentication demo ready!"
	@echo "📋 Test endpoints:"
	@echo "   GET http://localhost:8000/auth-demo/public"
	@echo "   GET http://localhost:8000/auth-demo/protected (requires auth)"
	@echo "📖 See README.md for Keycloak setup"
	@echo ""
	@echo "💡 To start the UI separately:"
	@echo "   cd ../ui && pnpm dev:vite    # UI only at http://localhost:5173"
	@echo "   cd ../.. && pnpm dev         # Full dev environment (UI + API + services)"

##@ 🏗️  Build & Deploy
clean: ## Clean build artifacts and caches
	rm -rf htmlcov .coverage .pytest_cache
	rm -rf __pycache__ tests/__pycache__

##@ 🚀 CI/CD Simulation
ci-test: ## Run tests as they would in CI
	$(MAKE) clean
	$(MAKE) install  
	$(MAKE) test-all

ci-e2e: ## Run E2E tests as they would in CI
	$(MAKE) services-up
	$(MAKE) test-e2e
	$(MAKE) services-down