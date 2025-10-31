# Helm Deployment Guide

## Overview

This directory contains Helm charts and deployment configurations for the Spending Monitor application.

## Prerequisites

1. OpenShift cluster access
2. Helm 3.x installed
3. Images pushed to container registry (Quay.io)
4. Keycloak Operator installed (for auth-enabled deployments)

## Image Building

**Important**: Images must be built for AMD64 architecture for OpenShift deployment.

### Building with Rosetta (macOS ARM64)

On macOS with Apple Silicon, ensure Rosetta is enabled in your podman machine:

```bash
# Check if Rosetta is enabled
podman machine inspect | grep Rosetta

# Build images for AMD64
podman build --platform linux/amd64 -t quay.io/YOUR_USERNAME/spending-monitor-api:latest -f packages/api/Containerfile .
podman build --platform linux/amd64 -t quay.io/YOUR_USERNAME/spending-monitor-ui:latest -f packages/ui/Containerfile .
podman build --platform linux/amd64 -t quay.io/YOUR_USERNAME/spending-monitor-db:latest -f packages/db/Containerfile .

# Push to registry
podman push quay.io/YOUR_USERNAME/spending-monitor-api:latest
podman push quay.io/YOUR_USERNAME/spending-monitor-ui:latest
podman push quay.io/YOUR_USERNAME/spending-monitor-db:latest
```

## Deployment Configurations

### sid-test-1: With Keycloak Authentication

Deploy with full authentication using Keycloak:

```bash
# Create namespace
oc new-project sid-test-1

# Install Keycloak (using Keycloak Operator)
# Ensure Keycloak Operator is installed cluster-wide first

# Deploy application
helm upgrade --install spending-monitor ./deploy/helm/spending-monitor \
  -n sid-test-1 \
  -f deploy/helm/keycloak-auth-values.yaml

# Users are automatically synced to Keycloak via a Helm post-install hook
# Check sync job status: oc get jobs -n sid-test-1 | grep user-sync
```

**Test URL**: https://spending-monitor-nginx-route-sid-test-1.apps.ai-dev02.kni.syseng.devcluster.openshift.com/

**Test Credentials**: Any database user email with password: `password123` (default)

### sid-test-2: No Authentication (Bypass Mode)

Deploy without authentication for testing:

```bash
# Create namespace
oc new-project sid-test-2

# Deploy application
helm upgrade --install spending-monitor ./deploy/helm/spending-monitor \
  -n sid-test-2 \
  -f deploy/helm/no-auth-values.yaml
```

**Test URL**: https://spending-monitor-nginx-route-sid-test-2.apps.ai-dev02.kni.syseng.devcluster.openshift.com/

## Configuration Files

- `values.yaml` - Default values with placeholders
- `keycloak-auth-values.yaml` - Override for auth-enabled deployment
- `no-auth-values.yaml` - Override for no-auth deployment

### Key Configuration Parameters

| Parameter | Description | sid-test-1 | sid-test-2 |
|-----------|-------------|------------|------------|
| `BYPASS_AUTH` | Disable authentication | `false` | `true` |
| `POSTGRES_PASSWORD` | Database password | Strong password | `devpassword` |
| `KEYCLOAK_URL` | Keycloak base URL (API) | External route | N/A |
| `KEYCLOAK_REALM` | Keycloak realm name | `spending-monitor` | N/A |

## Post-Deployment Steps

### For Auth-Enabled (sid-test-1)

1. **Verify Keycloak is accessible**:
   ```bash
   curl https://keycloak-route-sid-test-1.apps.ai-dev02.kni.syseng.devcluster.openshift.com/realms/spending-monitor
   ```

2. **User sync to Keycloak**:
   
   **Automated (Recommended)**: Users are automatically synced from the database to Keycloak via a Helm post-install/post-upgrade hook. Check the job status:
   ```bash
   oc get jobs -n sid-test-1 | grep user-sync
   oc logs job/spending-monitor-keycloak-user-sync -n sid-test-1
   ```
   
   **Manual (if needed)**: If the automatic sync fails or you need to re-sync:
   ```bash
   # Port forward services
   oc port-forward -n sid-test-1 svc/spending-monitor-keycloak-service 8080:8080 &
   oc port-forward -n sid-test-1 svc/spending-monitor-db 5432:5432 &
   
   # Set environment variables
   export KEYCLOAK_URL="http://localhost:8080"
   export KEYCLOAK_ADMIN_USER=temp-admin
   export KEYCLOAK_ADMIN_PASSWORD=$(oc get secret spending-monitor-keycloak-initial-admin -n sid-test-1 -o jsonpath='{.data.password}' | base64 -d)
   export DATABASE_URL="postgresql://user:<password>@localhost:5432/spending-monitor"
   
   # Run sync using pnpm
   pnpm --filter @*/auth sync-users
   ```

3. **Test login**: Use any synced email with password `password123`

### For No-Auth (sid-test-2)

1. **Verify API is accessible**:
   ```bash
   curl https://spending-monitor-nginx-route-sid-test-2.apps.ai-dev02.kni.syseng.devcluster.openshift.com/api/transactions/?limit=5
   ```

2. **Load sample data** (if needed):
   - Data is automatically loaded during migration if CSV files are present

## Troubleshooting

### Image Pull Errors

If you see `Exec format error`, the image was built for the wrong architecture:
- Rebuild with `--platform linux/amd64`
- Verify with: `podman inspect IMAGE_NAME --format '{{.Architecture}}'`

### Database Password Mismatch

If API can't connect to database:
1. Check `DATABASE_URL` password matches `POSTGRES_PASSWORD`
2. Update database password:
   ```bash
   oc exec DB_POD -- psql -U user -d spending-monitor -c "ALTER USER \"user\" WITH PASSWORD 'NEW_PASSWORD';"
   ```

### Keycloak Configuration Issues

If authentication fails:
1. Verify `KEYCLOAK_URL` is correct (base URL for API, full URL with realm for UI)
2. Check JWKS endpoint: `KEYCLOAK_URL/realms/REALM/protocol/openid-connect/certs`
3. Ensure Keycloak route is accessible externally

## Updating Configuration

To update runtime configuration without redeploying:

```bash
# Update secret
oc patch secret spending-monitor-secret -n NAMESPACE --type='json' \
  -p='[{"op": "replace", "path": "/data/KEY", "value": "BASE64_VALUE"}]'

# Restart pods to pick up changes
oc rollout restart deployment/spending-monitor-api -n NAMESPACE
oc rollout restart deployment/spending-monitor-ui -n NAMESPACE
```

## Clean Up

```bash
# Delete deployment
helm uninstall spending-monitor -n NAMESPACE

# Delete namespace
oc delete project NAMESPACE
```

