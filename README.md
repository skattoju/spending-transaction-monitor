# spending-monitor

AI-powered alerts for credit card transactions

## Architecture

This project is built with:

- **Turborepo** - High-performance build system for the monorepo
- **React + Vite** - Modern frontend with TanStack Router
- **FastAPI** - Python backend with async support
- **PostgreSQL** - Database with Alembic migrations

## Project Structure

```
spending-monitor/
├── packages/
│   ├── ui/           # React frontend application
│   ├── api/          # FastAPI backend service
│   └── db/           # Database and migrations
├── turbo.json        # Turborepo configuration
└── package.json      # Root package configuration
```

## Quick Start

### Prerequisites
- Node.js 18+
- pnpm 9+
- Python 3.11+
- uv (Python package manager)
- Docker (for database)

### Development

1. **Install all dependencies** (Node.js + Python):
```bash
pnpm setup
```

   Or install them separately:
```bash
pnpm install          # Install Node.js dependencies
pnpm install:deps     # Install Python dependencies in API package
```

2. **Start the database**:
```bash
pnpm db:start
```

3. **Run database migrations**:
```bash
pnpm db:upgrade
```

4. **Start development servers**:
```bash
pnpm dev
```

### Available Commands

```bash
# Development
pnpm dev              # Start all development servers
pnpm build            # Build all packages
pnpm test             # Run tests across all packages
pnpm lint             # Check code formatting
pnpm format           # Format code

# Database
pnpm db:start         # Start database containers
pnpm db:stop          # Stop database containers  
pnpm db:upgrade       # Run database migrations
pnpm db:revision      # Create new migration
# Utilities
pnpm clean            # Clean build artifacts (turbo prune)
```

## Development URLs

- **Frontend App**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: postgresql://localhost:5432

## Learn More

- [Turborepo](https://turbo.build/) - Monorepo build system
- [TanStack Router](https://tanstack.com/router) - Type-safe routing
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations

---

Generated with [AI Kickstart CLI](https://github.com/your-org/ai-kickstart)
