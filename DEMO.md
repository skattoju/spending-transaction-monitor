# 🎬 Authentication Demo Setup Guide

## 🚀 Quick Start for Demo Recording

### Option 1: Infrastructure Only (Recommended for Development)
```bash
# Start database + keycloak only
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start (about 1-2 minutes)
docker-compose -f docker-compose.dev.yml logs -f

# Setup Keycloak realm and test users
cd packages/api && uv run python ../../scripts/auth/setup_keycloak.py

# Start API locally (for hot-reload)
cd packages/api && uv run uvicorn src.main:app --reload --port 8000

# Start UI locally (for hot-reload)
cd packages/ui && npm run dev:vite
```

### Option 2: Full Docker Stack
```bash
# Start all services in Docker
docker-compose up -d

# Setup Keycloak (run once)
docker-compose --profile setup run keycloak-setup

# Check all services are running
docker-compose ps
```

## 📋 Services & URLs

| Service | URL | Credentials |
|---------|-----|------------|
| **UI (Frontend)** | http://localhost:3000 | N/A (dev bypass) |
| **API (Backend)** | http://localhost:8000 | N/A (dev bypass) |
| **API Docs** | http://localhost:8000/docs | Interactive OpenAPI |
| **Keycloak Admin** | http://localhost:8080 | admin / admin |
| **Database** | localhost:5432 | user / password |

## 👥 Test Users (Created Automatically)

| Email | Password | Roles |
|-------|----------|-------|
| `testuser@example.com` | `password123` | user |
| `admin@example.com` | `admin123` | user, admin |

## 🎯 Demo Flow

### 1. Development Mode (Auth Bypassed) ✅
- Authentication is bypassed for easy development
- Shows existing user data from database
- All endpoints accessible

### 2. Production Mode (Real Keycloak Auth)
```bash
# Enable production auth
export BYPASS_AUTH=false
export VITE_BYPASS_AUTH=false

# Restart services
# Then test with real Keycloak login flow
```

## 🧪 API Testing Commands

```bash
# Public endpoint (always works)
curl http://localhost:8000/health/

# Protected endpoint (works in dev mode)
curl http://localhost:8000/users/profile

# All user transactions (filtered by auth)
curl http://localhost:8000/transactions/

# User's alert rules
curl http://localhost:8000/alerts/rules
```

## 🛠 Maintenance Commands

```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down

# Reset everything (including data)
docker-compose -f docker-compose.dev.yml down -v

# View logs
docker-compose -f docker-compose.dev.yml logs -f keycloak
docker-compose -f docker-compose.dev.yml logs -f postgres

# Restart just Keycloak
docker-compose -f docker-compose.dev.yml restart keycloak
```

## 🐛 Troubleshooting

### Keycloak not starting
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs keycloak

# Common issue: port 8080 in use
lsof -i :8080
```

### Database connection issues
```bash
# Check if database is ready
docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U user -d spending-monitor

# Reset database
docker-compose -f docker-compose.dev.yml restart postgres
```

### API not connecting to services
```bash
# Check if all services are healthy
docker-compose -f docker-compose.dev.yml ps

# Check API logs
tail -f packages/api/logs/app.log  # if logging to file
```

---

**Ready to record! 🎥** All services should be accessible and authentication flow demonstrable.

