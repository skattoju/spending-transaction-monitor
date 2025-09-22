# OpenShift Deployment Makefile for Spending Transaction Monitor

# Configuration
PROJECT_NAME = spending-monitor
REGISTRY_URL ?= quay.io
REPOSITORY ?= rh-ai-quickstart
NAMESPACE ?= spending-transaction-monitor
IMAGE_TAG ?= latest

# Component image names
UI_IMAGE = $(REGISTRY_URL)/$(REPOSITORY)/$(PROJECT_NAME)-ui:$(IMAGE_TAG)
API_IMAGE = $(REGISTRY_URL)/$(REPOSITORY)/$(PROJECT_NAME)-api:$(IMAGE_TAG)
DB_IMAGE = $(REGISTRY_URL)/$(REPOSITORY)/$(PROJECT_NAME)-db:$(IMAGE_TAG)

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  Building:"
	@echo "    build-all          Build all Podman images"
	@echo "    build-ui           Build UI image"
	@echo "    build-api          Build API image"
	@echo "    build-db           Build database image"
	@echo ""
	@echo "  Pushing:"
	@echo "    push-all           Push all images to registry"
	@echo "    push-ui            Push UI image to registry"
	@echo "    push-api           Push API image to registry"
	@echo "    push-db            Push database image to registry"
	@echo ""
	@echo "  Deploying:"
	@echo "    deploy             Deploy application using Helm"
	@echo "    deploy-dev         Deploy in development mode"
	@echo "    deploy-all         Build, push and deploy all components"
	@echo "    full-deploy        Complete pipeline: login, build, push, deploy"
	@echo ""
	@echo "  Undeploying:"
	@echo "    undeploy           Remove application deployment"
	@echo "    undeploy-all       Remove deployment and namespace"
	@echo ""
	@echo "  Development:"
	@echo "    port-forward-api   Forward API service to localhost:8000"
	@echo "    port-forward-ui    Forward UI service to localhost:8080"
	@echo "    port-forward-db    Forward database to localhost:5432"
	@echo ""
	@echo   "  Local Development:"
	@echo "    run-local          Start all services, run migrations, and seed database"
	@echo "    build-local        Build local Podman images"
	@echo "    build-run-local    Build and run all services with database setup"
	@echo "    stop-local         Stop local Podman Compose services"
	@echo "    logs-local         Show logs from local services"
	@echo "    reset-local        Reset local environment (restart with fresh data)"
	@echo "    pull-local         Pull latest images from registry"
	@echo "    setup-local        Complete local setup (pull, run, migrate, seed)"
	@echo ""
	@echo "  Helm:"
	@echo "    helm-lint          Lint Helm chart"
	@echo "    helm-template      Render Helm templates"
	@echo "    helm-debug         Debug Helm deployment"
	@echo ""
	@echo "  Utilities:"
	@echo "    login              Login to OpenShift registry"
	@echo "    create-project     Create OpenShift project"
	@echo "    status             Show deployment status"
	@echo "    clean-all          Clean up all resources"
	@echo "    clean-images       Remove local Podman images"

# Login to OpenShift registry
.PHONY: login
login:
	@echo "Logging into OpenShift registry..."
	@oc whoami --show-token | podman login --username=$(shell oc whoami) --password-stdin $(REGISTRY_URL)

# Create OpenShift project
.PHONY: create-project
create-project:
	@echo "Creating OpenShift project: $(NAMESPACE)"
	@oc new-project $(NAMESPACE) || echo "Project $(NAMESPACE) already exists"

# Build targets
.PHONY: build-ui
build-ui:
	@echo "Building UI image..."
	podman build --platform=linux/amd64 -t $(UI_IMAGE) -f ./packages/ui/Containerfile .

.PHONY: build-api
build-api:
	@echo "Building API image..."
	podman build --platform=linux/amd64 -t $(API_IMAGE) -f ./packages/api/Containerfile .

.PHONY: build-db
build-db:
	@echo "Building database image..."
	podman build --platform=linux/amd64 -t $(DB_IMAGE) -f ./packages/db/Containerfile .

.PHONY: build-all
build-all: build-ui build-api build-db
	@echo "All images built successfully"

# Push targets
.PHONY: push-ui
push-ui: build-ui
	@echo "Pushing UI image..."
	podman push $(UI_IMAGE)

.PHONY: push-api
push-api: build-api
	@echo "Pushing API image..."
	podman push $(API_IMAGE)

.PHONY: push-db
push-db: build-db
	@echo "Pushing database image..."
	podman push $(DB_IMAGE)

.PHONY: push-all
push-all: push-ui push-api push-db
	@echo "All images pushed successfully"

# Deploy targets
.PHONY: deploy
deploy: create-project
	@echo "Deploying application using Helm..."
	helm upgrade --install $(PROJECT_NAME) ./deploy/helm/spending-monitor \
		--namespace $(NAMESPACE) \
		--set global.imageRegistry=$(REGISTRY_URL) \
		--set global.imageRepository=$(REPOSITORY) \
		--set global.imageTag=$(IMAGE_TAG) \

.PHONY: deploy-dev
deploy-dev: create-project
	@echo "Deploying application in development mode..."
	helm upgrade --install $(PROJECT_NAME) ./deploy/helm/spending-monitor \
		--namespace $(NAMESPACE) \
		--set global.imageRegistry=$(REGISTRY_URL) \
		--set global.imageRepository=$(REPOSITORY) \
		--set global.imageTag=$(IMAGE_TAG) \
		--set database.persistence.enabled=false \
		--set api.replicas=1 \
		--set ui.replicas=1 \

.PHONY: deploy-all
deploy-all: build-all push-all deploy
	@echo "Complete deployment finished successfully"

# Undeploy targets
.PHONY: undeploy
undeploy:
	@echo "Undeploying application..."
	helm uninstall $(PROJECT_NAME) --namespace $(NAMESPACE) || echo "Release $(PROJECT_NAME) not found"

.PHONY: undeploy-all
undeploy-all: undeploy
	@echo "Cleaning up namespace..."
	oc delete project $(NAMESPACE) || echo "Project $(NAMESPACE) not found or cannot be deleted"

# Full deployment pipeline
.PHONY: full-deploy
full-deploy: login create-project build-all push-all deploy
	@echo "Full deployment completed!"

# Development helpers
.PHONY: port-forward-api
port-forward-api:
	@echo "Port forwarding API service to localhost:8000..."
	oc port-forward service/spending-monitor-api 8000:8000 --namespace $(NAMESPACE)

.PHONY: port-forward-ui
port-forward-ui:
	@echo "Port forwarding UI service to localhost:8080..."
	oc port-forward service/spending-monitor-ui 8080:8080 --namespace $(NAMESPACE)

.PHONY: port-forward-db
port-forward-db:
	@echo "Port forwarding database service to localhost:5432..."
	oc port-forward service/spending-monitor-db 5432:5432 --namespace $(NAMESPACE)

# Helm helpers
.PHONY: helm-lint
helm-lint:
	@echo "Linting Helm chart..."
	helm lint ./deploy/helm/spending-monitor

.PHONY: helm-template
helm-template:
	@echo "Rendering Helm templates..."
	helm template $(PROJECT_NAME) ./deploy/helm/spending-monitor \
		--set global.imageRegistry=$(REGISTRY_URL) \
		--set global.imageRepository=$(REPOSITORY) \
		--set global.imageTag=$(IMAGE_TAG)

.PHONY: helm-debug
helm-debug:
	@echo "Debugging Helm deployment..."
	helm upgrade --install $(PROJECT_NAME) ./deploy/helm/spending-monitor \
		--namespace $(NAMESPACE) \
		--set global.imageRegistry=$(REGISTRY_URL) \
		--set global.imageRepository=$(REPOSITORY) \
		--set global.imageTag=$(IMAGE_TAG) \
		--dry-run --debug

# Clean up targets
.PHONY: clean-images
clean-images:
	@echo "Cleaning up local images..."
	@podman rmi $(UI_IMAGE) $(API_IMAGE) $(DB_IMAGE) || true

.PHONY: clean-all
clean-all: undeploy-all clean-images
	@echo "Complete cleanup finished"

# Status and logs
.PHONY: status
status:
	@echo "Checking application status..."
	@helm status $(PROJECT_NAME) --namespace $(NAMESPACE) || echo "Release not found"
	@echo "\nPod status:"
	@oc get pods --namespace $(NAMESPACE) || echo "No pods found"
	@echo "\nServices:"
	@oc get svc --namespace $(NAMESPACE) || echo "No services found"
	@echo "\nIngress:"
	@oc get ingress --namespace $(NAMESPACE) || echo "No ingress found"

.PHONY: logs
logs:
	@echo "Getting application logs..."
	@echo "=== API Logs ==="
	@oc logs -l app.kubernetes.io/component=api --namespace $(NAMESPACE) --tail=20 || echo "No API logs found"
	@echo "\n=== UI Logs ==="
	@oc logs -l app.kubernetes.io/component=ui --namespace $(NAMESPACE) --tail=20 || echo "No UI logs found"
	@echo "\n=== Database Logs ==="
	@oc logs -l app.kubernetes.io/component=database --namespace $(NAMESPACE) --tail=20 || echo "No database logs found"

.PHONY: logs-ui
logs-ui:
	@oc logs -f -l app.kubernetes.io/component=ui --namespace $(NAMESPACE)

.PHONY: logs-api
logs-api:
	@oc logs -f -l app.kubernetes.io/component=api --namespace $(NAMESPACE)

.PHONY: logs-db
logs-db:
	@oc logs -f -l app.kubernetes.io/component=database --namespace $(NAMESPACE)

# Local development targets using Podman Compose
.PHONY: run-local
run-local:
	@echo "Starting all services locally with Podman Compose..."
	@echo "This will start: PostgreSQL, API, UI, nginx proxy, and SMTP server"
	@echo "Services will be available at:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - API (proxied): http://localhost:3000/api/*"
	@echo "  - API (direct): http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - SMTP Web UI: http://localhost:3002"
	@echo "  - Database: localhost:5432"
	@echo ""
	podman-compose -f podman-compose.yml up -d
	@echo ""
	@echo "Waiting for database to be ready..."
	@sleep 15
	@echo "Running database migrations..."
	@pnpm db:upgrade || (echo "❌ Database upgrade failed. Check if database is running." && exit 1)
	@echo "Seeding database with test data..."
	@pnpm db:seed || (echo "❌ Database seeding failed. Check migration status." && exit 1)
	@echo ""
	@echo "✅ All services started and database is ready!"
	@echo ""
	@echo "To also start pgAdmin for database management, run:"
	@echo "  podman-compose -f podman-compose.yml --profile tools up -d pgadmin"
	@echo "  Then access pgAdmin at: http://localhost:8080"
	@echo ""
	@echo "To view logs: make logs-local"
	@echo "To stop services: make stop-local"

.PHONY: stop-local
stop-local:
	@echo "Stopping local Podman Compose services..."
	podman-compose -f podman-compose.yml down

.PHONY: build-local
build-local:
	@echo "Building local Podman images..."
	podman-compose -f podman-compose.yml build

.PHONY: pull-local
pull-local:
	@echo "Pulling latest images from registry..."
	podman-compose -f podman-compose.yml pull

.PHONY: logs-local
logs-local:
	@echo "Showing logs from local services..."
	podman-compose -f podman-compose.yml logs -f

.PHONY: reset-local
reset-local:
	@echo "Resetting local environment..."
	@echo "This will stop services, remove containers and volumes, pull latest images, and restart"
	podman-compose -f podman-compose.yml down -v
	podman-compose -f podman-compose.yml pull
	podman-compose -f podman-compose.yml up -d
	@echo ""
	@echo "Waiting for database to be ready..."
	@sleep 15
	@echo "Running database migrations..."
	@pnpm db:upgrade || (echo "❌ Database upgrade failed. Check if database is running." && exit 1)
	@echo "Seeding database with test data..."
	@pnpm db:seed || (echo "❌ Database seeding failed. Check migration status." && exit 1)
	@echo ""
	@echo "✅ Local environment has been reset and database is ready!"

.PHONY: build-run-local
build-run-local: build-local
	@echo "Starting all services locally with freshly built images..."
	@echo "This will start: PostgreSQL, API, UI, nginx proxy, and SMTP server"
	@echo "Services will be available at:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - API (proxied): http://localhost:3000/api/*"
	@echo "  - API (direct): http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - SMTP Web UI: http://localhost:3002"
	@echo "  - Database: localhost:5432"
	@echo ""
	podman-compose -f podman-compose.yml up -d
	@echo ""
	@echo "Waiting for database to be ready..."
	@sleep 15
	@echo "Running database migrations..."
	@pnpm db:upgrade || (echo "❌ Database upgrade failed. Check if database is running." && exit 1)
	@echo "Seeding database with test data..."
	@pnpm db:seed || (echo "❌ Database seeding failed. Check migration status." && exit 1)
	@echo ""
	@echo "✅ All services started and database is ready!"
	@echo ""
	@echo "To also start pgAdmin for database management, run:"
	@echo "  podman-compose -f podman-compose.yml --profile tools up -d pgadmin"
	@echo "  Then access pgAdmin at: http://localhost:8080"
	@echo ""
	@echo "To view logs: make logs-local"
	@echo "To stop services: make stop-local"

.PHONY: setup-local
setup-local: pull-local run-local
	@echo "✅ Local development environment is fully set up and ready!"
	@echo "Database has been migrated and seeded with test data."