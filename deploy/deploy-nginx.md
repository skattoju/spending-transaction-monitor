# Nginx Reverse Proxy Deployment Guide

This guide explains how to deploy nginx as a reverse proxy for the Spending Transaction Monitor application.

## What was implemented

### 1. Nginx Configuration
- **nginx-configmap.yaml**: Contains nginx configuration that:
  - Routes `/api/*` requests to the API service (spending-monitor-api:8000)
  - Routes all other requests to the UI service (spending-monitor-ui:8080)
  - Handles CORS for API requests
  - Includes security headers
  - Provides health check endpoint

### 2. Nginx Deployment Files
- **nginx-deployment.yaml**: Deploys nginx with the custom configuration
- **nginx-service.yaml**: Creates a ClusterIP service for nginx
- **Updated routes.yaml**: Routes external traffic through nginx instead of directly to services

### 3. Updated Values
- Added nginx configuration section to values.yaml
- Routes now point to nginx service when nginx is enabled
- Fallback to original routing when nginx is disabled

## Deployment Options

### Option 1: Deploy with Nginx (Recommended)
```bash
# Deploy with nginx enabled and auto-generated hostname
helm upgrade --install spending-monitor deploy/helm/spending-monitor/ \
  --set nginx.enabled=true \
  --namespace your-namespace

# Deploy with nginx enabled and custom hostname
helm upgrade --install spending-monitor deploy/helm/spending-monitor/ \
  --set nginx.enabled=true \
  --set routes.nginx.host=my-custom-domain.example.com \
  --namespace your-namespace
```

### Option 2: Deploy without Nginx (Fallback)
```bash
# Deploy without nginx (uses original OpenShift Routes)
helm upgrade --install spending-monitor deploy/helm/spending-monitor/ \
  --set nginx.enabled=false \
  --namespace your-namespace
```

## Architecture

### With Nginx Enabled:
```
External Request → OpenShift Route → Nginx Service → nginx Pod
                                                   ├─ /api/* → API Service → API Pods
                                                   └─ /* → UI Service → UI Pods
```

### Without Nginx (Fallback):
```
External Request → OpenShift Route UI → UI Service → UI Pods
External Request → OpenShift Route API (/api) → API Service → API Pods
```

## Benefits of Nginx Reverse Proxy

1. **Single Entry Point**: All traffic goes through one route
2. **Simplified Routing**: No need for path-based OpenShift routes
3. **Better Control**: Custom nginx configuration for routing logic
4. **Performance**: Nginx handles static content and request routing efficiently
5. **Security**: Centralized security headers and CORS handling
6. **Flexibility**: Easy to modify routing rules without changing OpenShift routes

## Configuration Details

### Nginx Routes:
- `/api/*` → Proxied to API service with `/` rewrite
- `/health` → Proxied to API health endpoint
- `/*` → Proxied to UI service (SPA fallback to index.html)

### Security Features:
- CORS headers for API requests
- Security headers (X-Frame-Options, X-XSS-Protection, etc.)
- Content Security Policy

### Health Checks:
- Nginx health check on `/health` endpoint
- Liveness and readiness probes configured

## Monitoring

You can monitor nginx logs and metrics:
```bash
# View nginx logs
kubectl logs -l app.kubernetes.io/component=nginx -n your-namespace

# Check nginx service status
kubectl get svc spending-monitor-nginx -n your-namespace
```