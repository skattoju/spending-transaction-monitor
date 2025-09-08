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

**Backend Configuration** (`packages/api/src/core/config.py`):

```python
class Settings(BaseSettings):
    # Environment settings
    ENVIRONMENT: Literal['development', 'production', 'staging', 'test'] = 'development'
    
    # Authentication settings  
    BYPASS_AUTH: bool = False

    def __post_init__(self):
        """Auto-enable auth bypass in development if not explicitly set"""
        if (
            self.ENVIRONMENT == 'development'
            and not hasattr(self, '_bypass_auth_explicitly_set')
            and 'BYPASS_AUTH' not in os.environ
        ):
            self.BYPASS_AUTH = True
```

**Auth Middleware** (`packages/api/src/auth/middleware.py`):

```python
async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict | None:
    """Extract user info from JWT token (optional auth) with development bypass"""
    
    # Development bypass - return mock user
    if settings.BYPASS_AUTH:
        logger.info("🔓 Authentication bypassed - development mode enabled")
        return {
            'id': 'dev-user-123',
            'email': 'developer@example.com',
            'username': 'developer',
            'roles': ['user', 'admin'],
            'is_dev_mode': True,
            'token_claims': {
                'sub': 'dev-user-123',
                'preferred_username': 'developer',
                'email': 'developer@example.com',
                'realm_access': {'roles': ['user', 'admin']}
            }
        }
    # ... existing production auth logic ...
```

**Usage**:
```bash
# Automatic bypass in development
ENVIRONMENT=development  # Auto-enables BYPASS_AUTH=true

# Explicit control
BYPASS_AUTH=true   # Force enable bypass
BYPASS_AUTH=false  # Force disable bypass
```

### 4. Frontend Integration ✅ IMPLEMENTED

**Auth Configuration** (`packages/ui/src/config/auth.ts`):

```typescript
export interface AuthConfig {
  bypassAuth: boolean;
  keycloakUrl: string;
  clientId: string;
  redirectUri: string;
  postLogoutRedirectUri: string;
  environment: 'development' | 'production' | 'staging' | 'test';
}

const environment = (import.meta.env.VITE_ENVIRONMENT || 'development') as AuthConfig['environment'];

export const authConfig: AuthConfig = {
  environment,
  bypassAuth:
    import.meta.env.VITE_BYPASS_AUTH === 'true' ||
    (environment === 'development' && import.meta.env.VITE_BYPASS_AUTH !== 'false'),
  // ... Keycloak config
};
```

**Auth Context** (`packages/ui/src/contexts/AuthContext.tsx`):

```tsx
// Custom AuthProvider that switches between dev and production modes
export function AuthProvider({ children }: { children: React.ReactNode }) {
  if (authConfig.bypassAuth) {
    console.log('🔓 Running in development mode - authentication bypassed');
    return <DevAuthProvider>{children}</DevAuthProvider>;
  }
  return <ProductionAuthProvider>{children}</ProductionAuthProvider>;
}

// Development provider returns mock user immediately
function DevAuthProvider({ children }: { children: React.ReactNode }) {
  const [user] = useState<User>({
    id: 'dev-user-123',
    email: 'developer@example.com',
    username: 'developer',
    name: 'Development User',
    roles: ['user', 'admin'],
    isDevMode: true,
  });
  // ... context implementation
}
```

**Usage**:
```bash
# Development Mode (Default) - Auto-bypass
VITE_ENVIRONMENT=development
VITE_BYPASS_AUTH=true

# Production Mode
VITE_ENVIRONMENT=production  
VITE_BYPASS_AUTH=false

# Force Production Auth in Development
VITE_ENVIRONMENT=development
VITE_BYPASS_AUTH=false  # Explicit override
```

**Visual Indicators**: 
- 🔓 Dev mode badges in UI components
- 🎯 "Continue (Dev Mode)" login button
- 🟡 Yellow dot on user avatar when in dev mode

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
# Backend API (.env)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=spending-monitor
KEYCLOAK_CLIENT_ID=spending-monitor

# Backend Development Mode
ENVIRONMENT=development        # Auto-enables auth bypass
BYPASS_AUTH=true              # Explicit control

# Frontend UI (.env)
VITE_ENVIRONMENT=development  # Auto-enables auth bypass
VITE_BYPASS_AUTH=true        # Explicit control
VITE_KEYCLOAK_URL=http://localhost:8080/realms/spending-monitor
VITE_KEYCLOAK_CLIENT_ID=spending-monitor
```

## Migration Strategy

1. **Phase 1**: Core infrastructure ✅ COMPLETED
   - JWT middleware and Keycloak setup 
   - Development bypass for backend and frontend
   - Test endpoints and documentation

2. **Phase 2**: Integrate auth into main routes (TODO)
   - Apply `Depends(require_authentication)` to protected routes
   - Add user context to business logic
   
3. **Phase 3**: Role-based permissions (TODO)  
   - Implement role checking decorators
   - Add admin-only endpoints
   
4. **Phase 4**: Production deployment (TODO)
   - Configure production Keycloak instance
   - HTTPS and security hardening

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
