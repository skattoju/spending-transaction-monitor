# spending-monitor API

FastAPI backend application with modern Python development practices.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Async/Await** - Fully asynchronous request handling
- **Pydantic** - Data validation using Python type annotations
- **CORS** - Cross-Origin Resource Sharing support
- **Database** - PostgreSQL with async SQLAlchemy
- **Migrations** - Database migrations with Alembic
- **Testing** - Comprehensive test suite with pytest
- **Code Quality** - Linting with ruff, type checking with mypy
- **Development** - Hot reload with uvicorn

## Quick Start

### Prerequisites
- Python 3.11+
- uv (Python package manager)

### Development

1. **Install dependencies**:
```bash
uv sync
```

2. **Start development server**:
```bash
uv run uvicorn src.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Database Setup

1. **Start database** (from project root):
```bash
pnpm db:start
```

2. **Run migrations**:
```bash
uv run alembic upgrade head
```

3. **Create new migration**:
```bash
uv run alembic revision --autogenerate -m "description"
```

## Available Scripts

```bash
# Development
uv run uvicorn src.main:app --reload  # Start dev server with hot reload
uv run uvicorn src.main:app           # Start production server

# Testing
uv run pytest                        # Run all tests
uv run pytest tests/test_health.py   # Run specific test file
uv run pytest -v                     # Run tests with verbose output
uv run pytest --cov=src             # Run tests with coverage

# Code Quality
uv run ruff check .                  # Lint code
uv run ruff check . --fix           # Fix linting issues
uv run ruff format .                # Format code
uv run mypy src/                     # Type checking

# Database
uv run alembic upgrade head          # Apply migrations
uv run alembic downgrade -1          # Rollback one migration
uv run alembic revision --autogenerate -m "message"  # Create migration
uv run alembic history               # Show migration history
```

## Project Structure

```
src/
├── main.py              # FastAPI application entry point
├── core/
│   └── config.py        # Application configuration
├── routes/
│   └── health.py        # Health check endpoints
├── models/              # Database models (SQLAlchemy)
├── schemas/             # Pydantic schemas for request/response
└── __init__.py

tests/
├── test_health.py       # Health endpoint tests
└── __init__.py
```

## API Endpoints

### Health Check
- **GET** `/health` - Basic health check
- **GET** `/` - Root endpoint with welcome message

### Database
All endpoints support async database operations with connection pooling.

## Configuration

Environment variables:
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts (default: "localhost,127.0.0.1")
- `DATABASE_URL` - PostgreSQL connection string
- `DB_ECHO` - Enable SQL query logging (default: false)

## Development Tips

1. **API Documentation**: Visit `/docs` for interactive Swagger UI
2. **Schema Validation**: Pydantic automatically validates request/response data
3. **Async Operations**: Use `async def` for all route handlers
4. **Type Hints**: Add type annotations for better IDE support and mypy validation
5. **Database Sessions**: Use dependency injection for database sessions

## Testing

The test suite includes:
- Unit tests for individual functions
- Integration tests for API endpoints
- Database transaction rollback for test isolation
- Async test support with pytest-asyncio

Run specific test categories:
```bash
uv run pytest tests/ -k "health"     # Run health-related tests
uv run pytest tests/ -k "integration" # Run integration tests
```

---

Generated with [AI Kickstart CLI](https://github.com/your-org/ai-kickstart)
