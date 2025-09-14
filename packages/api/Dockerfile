FROM registry.access.redhat.com/ubi9/python-312:latest

USER root

# Set working directory
WORKDIR /app

# Install system dependencies for PostgreSQL
RUN dnf install -y gcc gcc-c++ postgresql-devel && dnf clean all

# Copy workspace configuration and packages
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY packages/ ./packages/

# Install Python dependencies from pyproject.toml
RUN pip install --no-cache-dir -e ./packages/db
RUN pip install --no-cache-dir -e ./packages/api[dev]
# Install psycopg2 for PostgreSQL sync operations (migrations)
RUN pip install --no-cache-dir psycopg2

# Set environment variables
ENV PYTHONPATH=/app/packages/api/src

USER 1001

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]