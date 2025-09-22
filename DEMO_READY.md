# 🎬 Authentication Demo - READY TO RECORD!

## ✅ All Services Running & Configured

### **Infrastructure Services (Docker Compose)**
- **PostgreSQL Database**: `localhost:5432` ✅
  - Sample user: `john.doe@example.com` 
  - 3 transactions, 1 credit card, 3 alert rules
- **Keycloak Identity Provider**: `http://localhost:8080` ✅  
  - Admin: `admin` / `admin`
  - Realm: `spending-monitor` configured

### **Development Services (Local)**
- **FastAPI Backend**: `http://localhost:8000` ✅
  - Authentication middleware working
  - Database connected with sample data
- **React Frontend**: `http://localhost:3000` ✅
  - OIDC integration ready
  - Development auth bypass enabled

## 🧪 **Working Test Endpoints**

| Endpoint | Status | Response |
|----------|---------|----------|
| `GET /health/` | ✅ Public | API + Database healthy |
| `GET /users/profile` | ✅ Protected | User profile data |  
| `GET /transactions/` | ✅ Protected | User transactions |
| `GET /alerts/rules` | ✅ Protected | User alert rules |

## 👥 **Test Users Created**

### **Keycloak Users** (for production auth demo)
- **Regular User**: `testuser@example.com` / `password123`
- **Admin User**: `admin@example.com` / `admin123`

### **Database Users** (for development auth demo)  
- **Sample User**: `john.doe@example.com` (with transaction history)
- **Mock Dev User**: `developer@example.com` (auth middleware fallback)

## 🎯 **Demo Flow Options**

### **Option 1: Development Mode (Current Setup)**
- Auth bypass enabled for easy development
- Shows real user data from database
- All endpoints work without authentication
- Perfect for showing API functionality

### **Option 2: Production Mode**  
```bash
# Enable real Keycloak authentication
export BYPASS_AUTH=false
export VITE_BYPASS_AUTH=false

# Restart services to pick up changes
pkill -f uvicorn && cd packages/api && uv run uvicorn src.main:app --reload --port 8000 &
```
- Full OIDC login flow with Keycloak
- Role-based access control
- JWT token validation
- Perfect for showing security features

## 🛠 **Quick Commands for Demo**

### **Service Management**
```bash
# Stop all services
podman compose -f docker-compose.dev.yml down
pkill -f uvicorn
pkill -f vite

# Start all services  
podman compose -f docker-compose.dev.yml up -d
cd packages/api && uv run uvicorn src.main:app --reload --port 8000 &
cd packages/ui && npm run dev:vite &
```

### **Testing Commands**
```bash
# Test public endpoint
curl http://localhost:8000/health/

# Test protected endpoints (dev mode)
curl http://localhost:8000/users/profile
curl http://localhost:8000/transactions/

# Access UI
open http://localhost:3000

# Access Keycloak Admin  
open http://localhost:8080
```

## 🎥 **Recording Script**

1. **Show Services Running**
   - `podman compose -f docker-compose.dev.yml ps`
   - Access UI at `http://localhost:3000`

2. **Development Mode Demo**
   - Show auth bypass in action
   - Test API endpoints with curl
   - Show user profile and transactions

3. **Production Mode Switch**
   - Set `BYPASS_AUTH=false`
   - Show Keycloak login flow
   - Demonstrate role-based access

4. **Architecture Overview**
   - Show JWT middleware code
   - Explain OIDC integration  
   - Highlight security features

---

**🚀 Ready to record! All authentication functionality working perfectly.**

