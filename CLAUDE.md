# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Setup
```bash
pnpm setup                    # Install all dependencies (Node + Python)
pnpm dev                      # Start full stack (DB, API, UI)
```

### Common Tasks
```bash
pnpm build                    # Build all packages
pnpm test                     # Run all tests
pnpm lint                     # Lint all packages
pnpm format                   # Format all code
pnpm format:check             # Check formatting without changes
pnpm type-check               # TypeScript type checking
```

### Database Management
```bash
pnpm db:start                 # Start PostgreSQL via Podman/Docker
pnpm db:stop                  # Stop database
pnpm db:upgrade               # Apply migrations
pnpm db:revision -m "msg"     # Create new migration
pnpm db:seed                  # Seed with test data
pnpm db:verify                # Verify database state
```

### Individual Package Development
```bash
pnpm --filter @spending-monitor/api dev          # API only
pnpm --filter @spending-monitor/ui dev           # UI only  
pnpm --filter @spending-monitor/ui dev:storybook # Storybook only
```

### Authentication Development (from packages/auth/)
```bash
make services-up              # Start Keycloak + Database
make auth-up                  # Start Keycloak only
make db-up                    # Start PostgreSQL only
make test-unit               # Run auth middleware unit tests
make test-e2e                 # Run end-to-end auth tests
make auth-setup               # Show Keycloak setup instructions
make test-e2e                # Test authentication end-to-end
make demo-auth                # Demo auth flow with API
make status                   # Check all service status
```

### Testing
```bash
pnpm --filter @spending-monitor/api test         # API tests
pnpm --filter @spending-monitor/ui test          # UI tests
```

## Architecture Overview

This is a **Turborepo monorepo** for a credit card transaction monitoring system with rule-based alerts.

### Core Components

- **API** (`packages/api`): FastAPI with async SQLAlchemy, routes for users/transactions/alerts/health
- **Database** (`packages/db`): PostgreSQL with SQLAlchemy models, Alembic migrations
- **UI** (`packages/ui`): React + Vite app with TanStack Router, Storybook components
- **Auth** (`packages/auth`): OAuth 2.0/OIDC authentication with Keycloak, JWT middleware, role-based authorization
- **Evaluation** (`packages/evaluation`): Rule evaluation service (scaffold)
- **Alerts** (`packages/alerts`): Alert delivery service (scaffold)
- **Ingestion Service** (`packages/ingestion-service`): Kafka-based transaction ingestion with Helm charts

### Data Flow
1. **Transaction Ingestion**: External sources → Ingestion Service → API → Database
2. **Rule Evaluation**: API triggers evaluation service against stored rules
3. **Alert Generation**: Triggered rules create notifications
4. **Alert Delivery**: Notifications sent via email/SMS/push/webhook

### Key Models
- **Users**: Core user info, location tracking, financial data
- **CreditCards**: Card details linked to users
- **Transactions**: Transaction records with merchant/location data
- **AlertRules**: Rule definitions (amount, merchant, category, timeframe, location)
- **AlertNotifications**: Generated alerts with delivery status

## Development URLs
- Web UI: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Storybook: http://localhost:6006
- Keycloak: http://localhost:8080 (admin/admin)

### Authentication Demo Endpoints
- `GET /auth-demo/public` - No auth required
- `GET /auth-demo/profile` - Optional auth (personalized if logged in)
- `GET /auth-demo/protected` - Authentication required
- `GET /auth-demo/user-only` - Requires `user` role or higher
- `GET /auth-demo/admin-only` - Requires `admin` role
- `GET /auth-demo/token-info` - Shows JWT token details

## Code Standards

### Branch Naming
Must use prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`, `ci/`, `build/`, `perf/`

### Commit Messages
Follow Conventional Commits with 100 character max:
- `feat(api): add transactions POST`
- `fix(db): correct Alembic URL driver`
- `chore(ui): update deps`

### Pre-commit Hooks
- **UI**: Prettier format + ESLint on staged files
- **API**: Ruff format + check on staged Python files

### Pre-push Hooks
- Branch name validation
- Commitlint on commit range
- `pnpm format:check`, `pnpm lint`, `pnpm test`

## Authentication Architecture

The system uses **OAuth 2.0 / OpenID Connect** with Keycloak for authentication:

### Components
- **Frontend**: React with `react-oidc-context` library for OAuth flow
- **Backend**: FastAPI JWT validation middleware using `python-jose`
- **Identity Provider**: Keycloak (using master realm for simplicity)
- **Security**: PKCE flow, RS256 JWT signatures, role-based authorization

### Auth Package Structure (`packages/auth/`)
- `compose.yml` - Keycloak service definition
- `requirements.txt` - Testing dependencies (pytest, fastapi, python-jose, etc.)
- `tests/test_auth_middleware.py` - 18 comprehensive unit tests
- `scripts/test_e2e.py` - End-to-end authentication testing
- `Makefile` - Development commands for auth workflows

### Authentication Flow
1. User clicks login → redirected to Keycloak with PKCE
2. User authenticates → auth code returned to UI
3. UI exchanges code for JWT tokens
4. API validates JWT on protected endpoints using cached OIDC config/JWKS
5. User roles extracted from JWT for authorization

### Testing
```bash
cd packages/auth
make test-unit    # Unit tests for JWT middleware
make test-e2e     # E2E tests against running services
```

## Python Environment
Each Python package uses **uv-managed virtual environments**:
```bash
pnpm --filter @spending-monitor/api install:deps   # API venv
pnpm --filter @spending-monitor/db install:deps    # DB venv
cd packages/auth && uv venv && uv pip install -r requirements.txt  # Auth testing venv
```

## UI Technology Stack
- **React 18** with TypeScript
- **TanStack Router** for routing
- **TanStack Query** for data fetching
- **Tailwind CSS** with Radix UI components
- **Storybook** for component development
- **Vitest** for testing

## API Technology Stack
- **FastAPI** with async/await
- **SQLAlchemy 2.0** with mapped_column syntax
- **Alembic** for migrations
- **Pydantic v2** for schemas
- **Ruff** for linting/formatting

## Release Process
Automated via **semantic-release** using commit messages:
- `main` branch: stable releases
- `next` branch: pre-releases

## Troubleshooting

### Database Issues
If database connection fails, ensure:
1. `pnpm db:start` has been run
2. PostgreSQL is accessible on localhost:5432
3. Run `pnpm db:upgrade` to apply migrations

### Python Dependencies
Use `uv` for Python dependency management, not pip. Each package has its own virtual environment.

### Monorepo Commands
Always use `pnpm` (not npm/yarn) and leverage Turborepo's caching with `turbo` commands where available.