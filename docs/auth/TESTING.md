# Auth Infrastructure Testing Guide

## ✅ **Current Testing Status**

### **All Tests Passing:**
- ✅ **9/9** basic auth core tests (`test_auth_core.py`) 
- ✅ **18/18** comprehensive middleware tests (`test_auth_middleware.py`)
- ✅ **Integration** with project's pnpm/turbo workflow
- ✅ **E2E validation** script ready (`test_e2e.py`)

---

## **Testing Approaches**

### **1. Using Project Standards (Recommended)**

**Via pnpm (orchestrated by turbo):**
```bash
# Test all packages
pnpm test

# Test just API package (includes auth tests)  
pnpm --filter @spending-monitor/api test

# Development workflow
pnpm dev  # Starts all services
```

**Via uv directly:**
```bash
cd packages/api
uv run pytest  # Runs all API tests including auth
```

### **2. Auth-Specific Testing**

**Using API package venv (recommended for auth development):**
```bash
# Core auth tests (9 tests)
cd packages/auth
source ../api/.venv/bin/activate
python -m pytest tests/test_auth_core.py -v

# Comprehensive middleware tests (18 tests) 
source ../api/.venv/bin/activate
python -m pytest tests/test_auth_middleware.py -v

# E2E infrastructure validation
source ../api/.venv/bin/activate  
python scripts/test_e2e.py
```

### **3. E2E Testing with Services**

**Full authentication flow testing:**
```bash
# Start services + setup Keycloak
./scripts/auth-dev.sh dev-full

# Or step by step:
./scripts/auth-dev.sh services-up  # Start DB + prepare for Keycloak
./scripts/auth-dev.sh setup        # Setup Keycloak realm/client

# Run E2E validation
./scripts/auth-dev.sh test
```

---

## **Test Coverage Breakdown**

### **Basic Tests (`test_auth_core.py` - 9 tests):**
- KeycloakJWTBearer initialization
- OIDC configuration (success/failure scenarios)
- Token validation (valid/invalid tokens) 
- Auth dependencies (protected endpoints)

### **Comprehensive Tests (`test_auth_middleware.py` - 18 tests):**
- OIDC config caching and fallback
- JWKS retrieval and failure handling
- Token validation with various error scenarios
- Role-based access control (require_role, require_any_role)
- Complete integration flow testing

### **E2E Validation (`test_e2e.py`):**
- Service health checks (API, Keycloak)
- Auth endpoint validation
- JWT middleware behavior
- CORS configuration
- API documentation accessibility

---

## **Integration with Project Workflow**

### **✅ Works With:**
- **pnpm test** - Includes auth tests via API package
- **turbo test** - Orchestrates all package testing  
- **uv run pytest** - Direct Python testing
- **Pre-push hooks** - Auth tests run in CI checks

### **Dependencies Resolution:**
- All auth test dependencies added to `packages/api/pyproject.toml`
- Uses shared venv from API package (has all dependencies)
- No separate venv needed for auth package
