#!/bin/bash

# Service Status Check Script
# Checks health of all running services

echo "📊 Service Status:"
echo "==================="

# Check API
if curl -sf http://localhost:8000/health 2>/dev/null; then
    echo "✅ API (port 8000)"
else
    echo "❌ API (port 8000) - Not running"
fi

# Check UI (try both default ports)
if curl -sf http://localhost:3000 2>/dev/null; then
    echo "✅ UI (port 3000)"
elif curl -sf http://localhost:5173 2>/dev/null; then
    echo "✅ UI (port 5173 - Vite dev)"
else
    echo "ℹ️  UI - Not running (try 'pnpm dev')"
fi

# Check Keycloak (optional - only needed for full auth testing)
if curl -sf http://localhost:8080/health/ready 2>/dev/null; then
    echo "✅ Keycloak (port 8080) - Optional"
else
    echo "ℹ️  Keycloak (port 8080) - Not running (optional - auth bypass enabled)"
fi

echo ""
echo "💡 To start services:"
echo "   pnpm dev          # Start all core services (API + UI + DB)"
echo "   pnpm db:start     # Start just the database"
echo "   ./scripts/auth-dev.sh help  # Full auth testing with Keycloak"
