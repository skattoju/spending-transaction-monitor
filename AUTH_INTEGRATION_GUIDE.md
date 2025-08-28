# Authentication Integration Guide

This guide explains how to integrate OAuth2/OIDC authentication into the spending-monitor application.

## Current State

The authentication infrastructure has been set up with the following components:

### Backend Components
- **JWT Middleware** (`packages/api/src/auth/middleware.py`)
- **Keycloak Setup** (`packages/auth/`)
- **Test Endpoints** (`packages/api/src/routes/auth_test.py`)
- **Dependencies** (`python-jose`, `requests`)

### Test Endpoints
- `GET /auth-test/public` - No authentication required
- `GET /auth-test/protected` - Requires valid JWT token  
- `GET /auth-test/optional-auth` - Optional authentication

## Integration Steps

### 1. Backend Route Integration

To protect existing routes, update route files to use the auth middleware:

```python
# Before
from fastapi import APIRouter, Depends
from db import get_db

@router.get('/')
async def get_users(session: AsyncSession = Depends(get_db)):
    # route logic
```

```python
# After  
from fastapi import APIRouter, Depends
from db import get_db
from ..auth.middleware import require_authentication, get_current_user

@router.get('/')
async def get_users(
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(require_authentication)  # Add this
):
    # route logic - can now access user['id'], user['username'], etc.
```

### 2. Optional vs Required Authentication

Choose the appropriate dependency:

- **Required**: `Depends(require_authentication)` - Returns 401 if no valid token
- **Optional**: `Depends(get_current_user)` - Returns `None` if no token, user dict if valid
- **Role-based**: `Depends(require_role('admin'))` - Requires specific role

### 3. Development Bypass (TODO)

For development purposes, implement a bypass mechanism:

```python
# In config.py
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
BYPASS_AUTH = os.getenv('BYPASS_AUTH', 'false').lower() == 'true'

# In auth middleware  
if settings.BYPASS_AUTH:
    return {
        'id': 'dev-user',
        'username': 'developer', 
        'email': 'dev@example.com',
        'roles': ['user', 'admin']
    }
```

### 4. Frontend Integration (TODO)

The frontend needs:

1. **OIDC Provider Setup**:
```tsx
import { AuthProvider } from 'react-oidc-context';

const oidcConfig = {
  authority: 'http://localhost:8080/realms/spending-monitor',
  client_id: 'spending-monitor',
  redirect_uri: window.location.origin,
  response_type: 'code',
  scope: 'openid profile email',
  automaticSilentRenew: true,
  loadUserInfo: true,
};

// Wrap app with AuthProvider
<AuthProvider {...oidcConfig}>
  <App />
</AuthProvider>
```

2. **Protected Routes**:
```tsx
import { useAuth } from 'react-oidc-context';

function ProtectedComponent() {
  const auth = useAuth();
  
  if (auth.isLoading) return <div>Loading...</div>;
  if (auth.error) return <div>Error: {auth.error.message}</div>;
  if (!auth.isAuthenticated) return <div>Please log in</div>;
  
  return <div>Protected content</div>;
}
```

3. **API Calls with Auth**:
```tsx
const token = auth.user?.access_token;
fetch('/api/users', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## Setup Instructions

### 1. Start Keycloak
```bash
cd packages/auth
make services-up
```

### 2. Configure Keycloak Realm
```bash
cd packages/auth/scripts  
python3 setup_keycloak.py
```

### 3. Test Authentication
```bash
# Start API
cd packages/api
uv run uvicorn src.main:app --reload

# Test endpoints
curl http://localhost:8000/auth-test/public
curl -H "Authorization: Bearer <token>" http://localhost:8000/auth-test/protected
```

## Environment Variables

```bash
# API (.env)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=spending-monitor
KEYCLOAK_CLIENT_ID=spending-monitor

# Development mode (optional)
DEVELOPMENT_MODE=true
BYPASS_AUTH=true  # For development only
```

## Migration Strategy

1. **Phase 1**: Core infrastructure (current)
2. **Phase 2**: Integrate auth into main routes  
3. **Phase 3**: Frontend integration
4. **Phase 4**: Role-based permissions
5. **Phase 5**: Production deployment

## Testing

Run the auth middleware tests:
```bash
cd packages/auth
python -m pytest tests/test_auth_middleware.py -v
```

## Security Considerations

- JWT tokens are validated against Keycloak's public keys
- Tokens are cached for performance (1-hour expiry)
- CORS is configured for the frontend domain
- HTTPS should be used in production
- Sensitive endpoints should require authentication

## Troubleshooting

### Common Issues

1. **Token validation fails**: Check Keycloak is running and realm is configured
2. **CORS errors**: Verify ALLOWED_HOSTS includes frontend URL
3. **Connection refused**: Ensure Keycloak is accessible at configured URL

### Debug Mode

Enable debug logging in the auth middleware:
```python
import logging
logging.getLogger('packages.api.src.middleware.auth').setLevel(logging.DEBUG)
```

## Next Steps

1. Implement development bypass mechanism
2. Integrate authentication into main API routes
3. Set up frontend OIDC provider
4. Add role-based access control
5. Configure for production deployment
