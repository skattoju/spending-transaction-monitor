# 🔐 Auth Development Guide

Quick reference for authentication development commands and workflows.

## 🚀 Quick Start

### Option 1: Use Development Helper Script
```bash
# Show all available auth commands
./scripts/auth-dev.sh help

# Start all services + setup Keycloak
./scripts/auth-dev.sh dev-full

# Check service status
./scripts/auth-dev.sh status
```

### Option 2: Manual Setup
```bash
# 1. Start database
pnpm db:start

# 2. Setup Keycloak
python scripts/setup_keycloak.py

# 3. Start development environment  
pnpm dev
```

## 🔧 Available Commands

| Command | Description |
|---------|-------------|
| `./scripts/auth-dev.sh services-up` | Start DB + prepare for Keycloak |
| `./scripts/auth-dev.sh setup` | Automated Keycloak configuration |
| `./scripts/auth-dev.sh test` | Run auth tests + verify endpoints |
| `./scripts/auth-dev.sh status` | Check all service health |
| `./scripts/auth-dev.sh demo` | Auth demo instructions |

## 🧪 Testing Auth

```bash
# Run all auth tests
./scripts/auth-dev.sh test

# Or directly:
cd packages/api
uv run pytest tests/test_auth* -v
```

## 📋 Service URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **Keycloak**: http://localhost:8080
- **UI**: http://localhost:3000

## 🔍 Verification Endpoints

- OIDC Config: http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration
- JWKS: http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs
- API Health: http://localhost:8000/health

## 📚 Related Documentation

- [Auth Architecture](README.md) - Complete auth system overview
- [Auth Testing](TESTING.md) - Detailed testing guide
- [Developer Guide](../DEVELOPER_GUIDE.md) - Full development guide
