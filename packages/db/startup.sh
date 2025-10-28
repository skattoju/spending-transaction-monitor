#!/bin/bash
set -e

echo "🚀 Starting database initialization process..."

# Wait for PostgreSQL to be ready with better error handling
echo "⏳ Waiting for PostgreSQL to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS: Checking PostgreSQL connection..."
    
    # Try pg_isready first
    if pg_isready -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-user} -d ${POSTGRES_DB:-spending-monitor} -q; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "❌ PostgreSQL not ready after $MAX_ATTEMPTS attempts"
        echo "Connection details:"
        echo "  Host: ${POSTGRES_HOST:-postgres}"
        echo "  User: ${POSTGRES_USER:-user}" 
        echo "  Database: ${POSTGRES_DB:-spending-monitor}"
        exit 1
    fi
    
    echo "   PostgreSQL not ready yet, waiting 5 seconds..."
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))
done

# Change to the db package directory and run migrations
cd /app/packages/db

# Run Alembic migrations
echo "📊 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Skip CSV data loading in migration container (sample data is optional)
echo "ℹ️  Skipping optional CSV sample data loading in migration job"
echo "   Sample data can be loaded separately if needed"

echo "🎉 Database initialization completed!"

# Keep the container running if this is being used as a migration container
# The container will exit after completion, which is the desired behavior for init containers
