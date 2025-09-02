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

### 3. Development Bypass ✅ IMPLEMENTED

For development purposes, a bypass mechanism has been implemented:

**Backend Configuration** (`packages/api/src/core/config.py`):
```python
# Environment and auth bypass settings
ENVIRONMENT: Literal["development", "production", "staging", "test"] = "development"
BYPASS_AUTH: bool = False  # Auto-enabled in development mode

# Auto-configuration in __post_init__
if self.ENVIRONMENT == "development" and 'BYPASS_AUTH' not in os.environ:
    self.BYPASS_AUTH = True
```

**Backend Middleware** (`packages/api/src/auth/middleware.py`):
```python
# Both get_current_user and require_authentication check for bypass
if settings.BYPASS_AUTH:
    logger.info("🔓 Authentication bypassed - development mode enabled")
    return {
        'id': 'dev-user-123',
        'email': 'developer@example.com',
        'username': 'developer',
        'roles': ['user', 'admin'],
        'is_dev_mode': True
    }
```

**Frontend Configuration** (`packages/ui/src/contexts/AuthContext.tsx`):
```typescript
// Automatic bypass detection
const bypassAuth = 
  import.meta.env.VITE_BYPASS_AUTH === 'true' || 
  (environment === 'development' && import.meta.env.VITE_BYPASS_AUTH !== 'false');

// Development auth provider returns mock user immediately
const DEV_USER: User = {
  id: 'dev-user-123',
  email: 'developer@example.com',
  username: 'developer',
  name: 'Development User',
  roles: ['user', 'admin'],
  isDevMode: true
};
```

### 4. Frontend Integration ✅ IMPLEMENTED

The frontend authentication has been implemented with both development bypass and production OIDC:

1. **Auth Context Provider** (`packages/ui/src/contexts/AuthContext.tsx`):
```tsx
// Automatically chooses dev or production mode
export function AuthProvider({ children }: { children: React.ReactNode }) {
  if (authConfig.bypassAuth) {
    return <DevAuthProvider>{children}</DevAuthProvider>;
  }
  return <ProductionAuthProvider>{children}</ProductionAuthProvider>;
}

// Usage in app
import { AuthProvider } from './contexts/AuthContext';

<AuthProvider>
  <App />
</AuthProvider>
```

2. **Protected Routes**:
```tsx
import { useAuth } from '../contexts/AuthContext';

function ProtectedComponent() {
  const auth = useAuth();
  
  if (auth.isLoading) return <div>Loading...</div>;
  if (!auth.isAuthenticated) return <div>Please log in</div>;
  
  // Show dev mode indicator
  if (auth.user?.isDevMode) {
    console.log('🔓 Running in development mode');
  }
  
  return <div>Protected content</div>;
}
```

3. **API Calls with Auth** (Development mode automatically bypassed):
```tsx
// In development: no token needed, backend bypasses auth
// In production: token automatically included
const { user } = useAuth();
fetch('/api/users', {
  headers: user?.isDevMode ? {} : {
    'Authorization': `Bearer ${user?.token}`,
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

### Complete Configuration
Create a `.env` file in the project root:

```bash
# Environment
ENVIRONMENT=development  # development | production | staging | test

# Backend Authentication
BYPASS_AUTH=true         # Explicit bypass control (auto-enabled in development)
DEBUG=true              # Auto-enabled in development

# Keycloak Configuration (for production)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=spending-monitor
KEYCLOAK_CLIENT_ID=spending-monitor-api
KEYCLOAK_CLIENT_SECRET=

# Frontend Authentication
VITE_ENVIRONMENT=development
VITE_BYPASS_AUTH=true    # Auto-enabled if VITE_ENVIRONMENT=development
VITE_KEYCLOAK_URL=http://localhost:8080/realms/spending-monitor
VITE_KEYCLOAK_CLIENT_ID=spending-monitor

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/spending-monitor

# CORS
ALLOWED_HOSTS=http://localhost:5173,http://localhost:3000
```

### Controlling Authentication Bypass

**Development Mode (Default):**
```bash
# Authentication automatically bypassed
ENVIRONMENT=development
# BYPASS_AUTH automatically set to true
# VITE_BYPASS_AUTH automatically set to true
```

**Disable Bypass in Development:**
```bash
# Force production auth even in development
ENVIRONMENT=development
BYPASS_AUTH=false
VITE_BYPASS_AUTH=false
```

**Production Mode:**
```bash
# Full authentication required
ENVIRONMENT=production
BYPASS_AUTH=false
VITE_BYPASS_AUTH=false
# Keycloak configuration required
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

1. ✅ ~~Implement development bypass mechanism~~ **COMPLETED**
2. **Integrate authentication into main API routes** (add `Depends(require_authentication)` to routes)
3. ✅ ~~Set up frontend OIDC provider~~ **COMPLETED**
4. **Add role-based access control** (use `Depends(require_role('admin'))`)
5. **Configure for production deployment**

### Quick Integration Example

To protect existing API routes, simply add the dependency:

```python
# packages/api/src/routes/users.py
from ..auth.middleware import require_authentication

@router.get('/')
async def get_users(
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(require_authentication)  # Add this line
):
    # In development: user = mock dev user
    # In production: user = validated JWT claims
    logger.info(f"User {user['username']} accessed users endpoint")
    # ... rest of route logic
```
