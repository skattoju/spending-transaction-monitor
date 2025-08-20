# Authentication Service

Keycloak-based authentication for the Spending Monitor application.

## Quick Start

```bash
# Start Keycloak
pnpm auth:start

# Check logs
pnpm auth:logs

# Stop Keycloak  
pnpm auth:stop
```

## Access

- **Keycloak Admin Console**: http://localhost:8080
- **Admin Credentials**: admin / admin

## Client Setup

After starting Keycloak, create a client in the master realm:

1. Go to http://localhost:8080 → Administration Console
2. Login with admin/admin
3. Go to Clients → Create Client
4. **Client ID**: `spending-monitor`
5. **Client type**: OpenID Connect
6. **Client authentication**: Off (public client)
7. **Valid redirect URIs**: `http://localhost:5173/*`
8. **Web origins**: `http://localhost:5173`

## Test Users

Create test users in Users section:
- Username: `testuser` / Password: `password` / Role: `user`
- Username: `admin` / Password: `password` / Role: `admin`

## Roles

Create realm roles:
- `user` - Standard user access
- `admin` - Administrative access