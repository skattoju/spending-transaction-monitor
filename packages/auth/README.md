# Authentication Service

OAuth2/OIDC authentication infrastructure using Keycloak for the Spending Monitor application.

## Components

- **Keycloak**: Identity provider and authorization server
- **JWT Middleware**: FastAPI middleware for token validation  
- **Setup Scripts**: Automated Keycloak configuration
- **Tests**: Comprehensive auth middleware test suite

## Quick Start

### 1. Start Services
```bash
./scripts/auth-dev.sh services-up
```

### 2. Configure Realm
```bash
cd scripts
python3 setup_keycloak.py
```

### 3. Access
- **Keycloak Admin Console**: http://localhost:8080
- **Admin Credentials**: admin / admin

## Client Configuration

The setup script automatically creates:
- **Realm**: `spending-monitor`
- **Client ID**: `spending-monitor`  
- **Client Type**: Public (PKCE flow)
- **Valid Redirect URIs**: `http://localhost:5173/*`
- **Web Origins**: `http://localhost:5173`

## Test Users

Created automatically by setup script:
- **Username**: `testuser@example.com`
- **Password**: `password123`
- **Roles**: `user`

## Development

### Manual Setup

If automated setup fails:

1. Go to http://localhost:8080 → Administration Console
2. Login with admin/admin
3. Create realm: `spending-monitor`
4. Create client: `spending-monitor`
5. Configure client settings:
   - Client type: OpenID Connect
   - Client authentication: Off (public client)
   - Valid redirect URIs: `http://localhost:5173/*`
   - Web origins: `http://localhost:5173`

### Testing

Test the auth infrastructure:
```bash
cd ../api
uv run uvicorn src.main:app --reload

# Test endpoints
curl http://localhost:8000/health                           # ✅ Works (no auth)
curl -H "Authorization: Bearer <token>" http://localhost:8000/users/profile  # ⚠️  Will work when auth is enabled
```

## Integration

See [`docs/auth/INTEGRATION.md`](../../docs/auth/INTEGRATION.md) for detailed integration instructions.

## Commands

```bash
./scripts/auth-dev.sh services-up    # Start DB + prepare for Keycloak
./scripts/auth-dev.sh services-down  # Stop services
./scripts/auth-dev.sh setup          # Setup Keycloak configuration
./scripts/auth-dev.sh status         # Check service status
./scripts/auth-dev.sh help           # Show all available commands
```

Or use the consolidated pnpm commands:
```bash
pnpm dev           # Start all services (API + UI + DB)
pnpm status        # Check all service health  
pnpm db:start      # Start just database
pnpm db:stop       # Stop database
```
