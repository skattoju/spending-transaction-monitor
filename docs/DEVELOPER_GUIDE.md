# 🚀 Developer Guide

Complete development guide for the Spending Transaction Monitor - a real-time credit card transaction alerting system.

## 📋 Quick Navigation

- [🏗️ Architecture Overview](#️-architecture-overview)
- [🛠️ Development Setup](#️-development-setup)
- [📦 Service Documentation](#-service-documentation)
- [🔐 Authentication & Security](#-authentication--security)
- [🧪 Testing](#-testing)
- [📊 Data Flow](#-data-flow)
- [🚀 Deployment](#-deployment)

---

## 🏗️ Architecture Overview

The system consists of several microservices that work together to provide real-time transaction monitoring and alerting:

```mermaid
graph TD
    %% External Data Sources
    subgraph EXT["External Sources"]
        BANK["Credit Card Transactions"]
        USER["User Interface"]
    end

    %% Authentication Layer
    subgraph AUTH["🔐 Authentication"]
        KC["Keycloak Server"]
        JWT["JWT Middleware"]
    end

    %% Ingestion Layer  
    subgraph ING["📥 Ingestion Layer"]
        INGEST["Ingestion Service<br/>Port: 8001"]
        TRANSFORM["Data Transformation"]
    end

    %% Core API Layer
    subgraph API["🔧 API Layer"]
        FASTAPI["FastAPI Server<br/>Port: 8000"]
        MIDDLEWARE["Auth Middleware"]
        ROUTES["API Routes"]
    end

    %% Business Logic Layer
    subgraph BIZ["💼 Business Logic"]
        RULES["Alert Rules Engine"]
        EVAL["Rule Evaluation"]
        ALERTS["Alert Processing"]
        AI["AI/NLP Features"]
    end

    %% Data Layer
    subgraph DATA["💾 Data Layer"]
        POSTGRES["PostgreSQL Database<br/>Port: 5432"]
        MODELS["SQLAlchemy Models"]
        MIGRATIONS["Alembic Migrations"]
    end

    %% Frontend Layer
    subgraph UI["🖥️ Frontend"]
        REACT["React App<br/>Port: 3000"]
        COMP["Components"]
        CHARTS["Charts & Analytics"]
    end

    %% External Services
    subgraph NOTIFY["📧 Notifications"]
        EMAIL["Email"]
        SMS["SMS"] 
        PUSH["Push Notifications"]
        WEBHOOK["Webhooks"]
    end

    %% Data Flow
    BANK --> INGEST
    INGEST --> TRANSFORM
    TRANSFORM --> FASTAPI
    
    USER --> KC
    KC --> JWT
    JWT --> MIDDLEWARE
    MIDDLEWARE --> ROUTES
    
    FASTAPI --> RULES
    RULES --> EVAL
    EVAL --> ALERTS
    ALERTS --> NOTIFY
    
    FASTAPI <--> MODELS
    MODELS <--> POSTGRES
    
    REACT <--> FASTAPI
    
    %% AI Integration
    FASTAPI --> AI
    AI --> EVAL
```

### 🏛️ Service Architecture

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| **UI** | React + Vite | 3000 | Frontend web application |
| **API** | FastAPI + SQLAlchemy | 8000 | Core business logic & REST API |
| **Ingestion** | FastAPI | 8001 | Transaction data ingestion & transformation |
| **Database** | PostgreSQL | 5432 | Data persistence |
| **Auth** | Keycloak | 8080 | OAuth2/OIDC authentication |

---

## 🛠️ Development Setup

### Prerequisites

- **Node.js** 18+ & **pnpm** 9+
- **Python** 3.11+ & **uv** package manager
- **Podman** (preferred) or **Docker**
- **Git**

### Quick Start (All Services)

```bash
# 1. Clone and install dependencies
git clone <repo-url>
cd spending-transaction-monitor
pnpm setup

# 2. Start all services (DB + API + UI)
pnpm dev
```

### Individual Service Setup

#### 🗄️ Database
```bash
cd packages/db
pnpm db:start      # Start PostgreSQL
pnpm db:upgrade    # Run migrations  
pnpm db:seed       # Seed test data
```

#### 🔧 API Server  
```bash
cd packages/api
uv sync            # Install Python dependencies
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 📥 Ingestion Service
```bash
cd packages/ingestion-service
uv sync            # Install dependencies
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

#### 🖥️ Frontend
```bash
cd packages/ui
pnpm install       # Install dependencies
pnpm dev           # Start development server
```

#### 🔐 Authentication (Keycloak)
```bash
# Use our setup script
python scripts/setup_keycloak.py

# Or use auth development helper script
./scripts/auth-dev.sh setup            # Automated setup
./scripts/auth-dev.sh help              # See all auth commands
```

### 📍 Development URLs

- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs
- **Ingestion Service**: http://localhost:8001
- **Keycloak Admin**: http://localhost:8080
- **Storybook**: http://localhost:6006

---

## 📦 Service Documentation

### 🔧 API Service
**Location**: `packages/api/`  
**Documentation**: [API README](../packages/api/README.md)

**Key Features**:
- User management & authentication
- Transaction CRUD operations
- Alert rules management  
- Real-time rule evaluation
- Analytics & reporting endpoints
- AI-powered natural language processing

**Important Endpoints**:
- `GET /health` - Health check
- `POST /transactions` - Create transaction
- `GET /transactions` - List/filter transactions  
- `POST /users/{id}/alert-rules` - Create alert rule
- `GET /users/{id}/transactions` - User transactions

### 📥 Ingestion Service
**Location**: `packages/ingestion-service/`  
**Documentation**: [Ingestion README](../packages/ingestion-service/README.md)

**Key Features**:
- Raw transaction data ingestion
- Data validation & transformation
- Bulk processing capabilities
- API forwarding to main server

**Data Flow**: `Raw Data → Validation → Transformation → API Server`

### 🖥️ Frontend (UI)
**Location**: `packages/ui/`  
**Documentation**: [UI README](../packages/ui/README.md)

**Key Features**:
- React with TypeScript
- TanStack Router for routing
- Recharts for data visualization  
- Shadcn/ui component library
- Dark/light theme support

### 💾 Database
**Location**: `packages/db/`  
**Documentation**: [Database README](../packages/db/README.md)

**Key Features**:
- PostgreSQL with async SQLAlchemy
- Alembic migrations
- Database models & relationships
- Seed data for development

---

## 🔐 Authentication & Security

**Complete Documentation**: [Authentication Guide](auth/README.md)

### Overview
- **OAuth2/OIDC** with Keycloak
- **JWT tokens** for API authentication
- **Role-based access control**
- **Development bypass mode** for local development

### Setup Keycloak Locally
```bash
# Use our automated setup script
python scripts/setup_keycloak.py

# Or manually:
# 1. Start Keycloak container
# 2. Create realm: spending-monitor  
# 3. Create client: spending-monitor
# 4. Configure users and roles
```

### Development Mode
The API includes authentication bypass for local development:
- Set `BYPASS_AUTH=True` in environment
- Returns mock user data for testing
- Automatically enabled in development mode

### Testing Authentication
**Documentation**: [Auth Testing Guide](auth/TESTING.md)

```bash
# Run auth tests
cd packages/api
uv run pytest tests/test_auth* -v
```

---

## 🧪 Testing

### Run All Tests
```bash
pnpm test    # All packages
```

### Package-Specific Tests
```bash
# API tests
cd packages/api
uv run pytest -v

# Ingestion service tests  
cd packages/ingestion-service
uv run pytest -v

# Database tests
cd packages/db
uv run pytest -v

# Frontend tests (when available)
cd packages/ui
pnpm test
```

### Test Coverage
- **API**: 22 tests (auth, transactions, health)
- **Ingestion**: 5 tests (transformation, integration)
- **Database**: 1 test (connectivity)
- **Frontend**: Test framework configured with vitest

---

## 📊 Data Flow

### Transaction Processing Flow

```mermaid
sequenceDiagram
    participant Bank as Credit Card Provider
    participant Ingest as Ingestion Service  
    participant API as API Server
    participant DB as PostgreSQL
    participant Rules as Rules Engine
    participant Alerts as Alert Service
    participant User as Frontend

    Bank->>Ingest: Raw Transaction Data
    Ingest->>Ingest: Validate & Transform
    Ingest->>API: POST /transactions
    API->>DB: Store Transaction
    API->>Rules: Evaluate Against Rules
    Rules->>DB: Fetch User Alert Rules
    Rules->>Rules: Process Rules
    
    alt Alert Triggered
        Rules->>Alerts: Create Alert
        Alerts->>User: Send Notification
        Alerts->>DB: Store Alert Record
    end
    
    API-->>Ingest: 201 Created
    User->>API: GET /transactions
    API->>DB: Query Transactions  
    DB-->>API: Transaction Data
    API-->>User: Display Transactions
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant KC as Keycloak
    participant API as API Server
    participant JWT as JWT Middleware

    FE->>KC: 1. Redirect to login
    KC->>FE: 2. Authorization code
    FE->>KC: 3. Exchange for JWT
    KC->>FE: 4. JWT access token
    FE->>API: 5. API request with JWT
    API->>JWT: 6. Validate token
    JWT->>KC: 7. Verify signature
    KC-->>JWT: 8. Token valid
    JWT-->>API: 9. User context
    API-->>FE: 10. Protected resource
```

---

## 🚀 Deployment

### Local Development
```bash
pnpm dev          # All services
pnpm db:start     # Just database
pnpm build        # Build all packages
```

### Production Deployment
- **Kubernetes** manifests available
- **Helm** charts for ingestion service
- **Docker** containers for all services
- **Environment** configuration via env vars

### Environment Variables

#### Service Ports (for development conflicts)
```bash
# Service-specific ports - override defaults when needed
API_PORT=8000       # API service port (default: 8000)
UI_PORT=3000        # UI service port (default: 3000)  
DB_PORT=5432        # Database external port (default: 5432)
KEYCLOAK_PORT=8080  # Keycloak port (default: 8080)

# Example: Run API on different port
API_PORT=8002 pnpm --filter @spending-monitor/api dev
```

#### Core Configuration
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/spending_monitor

# Authentication  
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=spending-monitor
KEYCLOAK_CLIENT_ID=spending-monitor
BYPASS_AUTH=false  # Set to true for development

# API Configuration  
API_HOST=localhost
```

---

## 📋 Common Development Tasks

### Database Operations
```bash
pnpm db:revision   # Create new migration
pnpm db:upgrade    # Apply migrations  
pnpm db:seed       # Add sample data
pnpm db:verify     # Verify setup
```

### Code Quality
```bash
pnpm lint          # Lint all packages
pnpm format        # Format all code
pnpm type-check    # TypeScript checking
```

### Package Management
```bash
pnpm --filter @spending-monitor/api install:deps
pnpm --filter @spending-monitor/ui build
```

---

## 🔗 Additional Resources

- [Main README](../README.md) - Project overview
- [Contributing Guidelines](../CONTRIBUTING.md) - Development standards
- [Auth Integration Guide](auth/INTEGRATION.md) - Detailed auth setup
- [API Documentation](../packages/api/README.md) - API service details
- [Ingestion Service Docs](../packages/ingestion-service/README.md) - Data ingestion

---

## 🆘 Troubleshooting

### Common Issues

**Database Connection Errors**:
```bash
# Check if PostgreSQL is running
pnpm db:start
# Verify connection settings in DATABASE_URL
```

**Authentication Issues**:
```bash
# Enable development bypass
export BYPASS_AUTH=True
# Or restart Keycloak
python scripts/setup_keycloak.py
```

**Port Conflicts**:
- API: 8000
- Frontend: 3000  
- Ingestion: 8001
- Database: 5432
- Keycloak: 8080

**Python Environment Issues**:
```bash
# Recreate virtual environment
cd packages/api
rm -rf .venv
uv sync
```

---

## 🤝 Getting Help

1. Check this developer guide
2. Review service-specific READMEs
3. Check existing GitHub issues
4. Create new issue with detailed description

Happy developing! 🎉
