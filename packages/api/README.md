# spending-monitor API

FastAPI backend application with Kafka consumer for real-time transaction processing.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Kafka Consumer** - Real-time transaction message processing from ingestion service
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
- Docker and Docker Compose
- Git

### Complete Setup (All Services)

1. **Clone the repository and navigate to API directory**:
```bash
git clone <your-repo-url>
cd spending-transaction-monitor/packages/api
```

2. **Install Python dependencies**:
```bash
uv sync
```

3. **Start required services**:

   **PostgreSQL Database**:
   ```bash
   cd ../db
   docker-compose up -d
   cd ../api
   ```

   **Kafka & Zookeeper**:
   ```bash
   cd ../ingestion-service/deploy/kafka
   docker-compose up -d
   cd ../../../api
   ```

4. **Run database migrations**:
```bash
cd ../db
uv run alembic upgrade head
cd ../api
```

5. **Seed the database with test data**:
```bash
cd ../db
uv run python src/db/scripts/seed.py
cd ../api
```

6. **Start the API server with Kafka consumer**:
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The services will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Kafka Health**: http://localhost:8000/kafka/health
- **PostgreSQL**: localhost:5432
- **Kafka**: localhost:9092

### Quick Test

Test the Kafka consumer by sending a transaction:
```bash
curl -X POST http://localhost:8000/kafka/send-test-transaction \
  -H "Content-Type: application/json" \
  -d '{"userId": "582ae68d-59ce-4185-a2e8-868b561d363e", "creditCardId": "a6e4a5de-d1a7-4c16-a37c-3d0d7f669abf"}'
```

Or run the automated test script:
```bash
python tests/test_kafka_setup.py
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
├── main.py              # FastAPI application entry point with Kafka consumer lifecycle
├── core/
│   └── config.py        # Application configuration including Kafka settings
├── routes/
│   ├── health.py        # Health check endpoints
│   ├── kafka.py         # Kafka testing and monitoring endpoints
│   ├── transactions.py  # Transaction management endpoints
│   ├── users.py         # User management endpoints
│   └── alerts.py        # Alert rule endpoints
├── services/
│   ├── __init__.py      # Service exports
│   └── kafka_consumer.py # Kafka consumer implementation
├── models/              # Database models (SQLAlchemy)
├── schemas/             # Pydantic schemas for request/response
└── __init__.py

tests/
├── test_health.py       # Health endpoint tests
├── test_kafka_setup.py  # Kafka connectivity and consumer tests
├── test_transactions.py # Transaction endpoint tests
├── test_users.py        # User endpoint tests
├── test_alerts.py       # Alert endpoint tests
└── __init__.py
```

## API Endpoints

### Health Check
- **GET** `/health` - Basic health check
- **GET** `/` - Root endpoint with welcome message

### Kafka
- **GET** `/kafka/health` - Kafka consumer and connection health status
- **POST** `/kafka/send-test-transaction` - Send test transaction message to Kafka

### Users, Transactions, Alerts
- **GET** `/users` - User management endpoints
- **GET** `/transactions` - Transaction endpoints  
- **GET** `/alerts` - Alert rule endpoints

### Database
All endpoints support async database operations with connection pooling.

## Configuration

Environment variables:
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts (default: "localhost,127.0.0.1")
- `DATABASE_URL` - PostgreSQL connection string
- `DB_ECHO` - Enable SQL query logging (default: false)

### Kafka Configuration
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses (default: "localhost:9092")
- `KAFKA_TRANSACTIONS_TOPIC` - Topic for transaction messages (default: "transactions")
- `KAFKA_GROUP_ID` - Consumer group ID (default: "transaction-processor")
- `KAFKA_AUTO_OFFSET_RESET` - Offset reset strategy (default: "earliest")

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

## Kafka Consumer Details

### Message Processing Flow
1. **Message Reception**: Consumer subscribes to `transactions` topic
2. **Format Transformation**: Converts ingestion service format to internal database format
3. **Validation**: Validates user and credit card existence
4. **Duplicate Check**: Prevents processing duplicate transactions
5. **Database Storage**: Stores transaction with proper relationships
6. **Offset Commit**: Commits Kafka offset only after successful database commit

### Supported Message Format (Ingestion Service)
```json
{
  "user": "user-uuid-string",
  "card": "card-uuid-string", 
  "year": 2025,
  "month": 8,
  "day": 27,
  "time": "16:24:00",
  "amount": 150.0,
  "use_chip": "Chip Transaction",
  "merchant_id": 12345,
  "merchant_city": "Test City",
  "merchant_state": "CA",
  "zip": "12345",
  "mcc": 5411,
  "errors": null,
  "is_fraud": false
}
```

## Troubleshooting

### Common Issues

**1. Kafka Consumer Not Connected**
- Check Kafka is running: `docker ps | grep kafka`
- Verify Kafka port: `telnet localhost 9092`
- Check consumer logs in API output
- Restart Kafka: `cd ../ingestion-service/deploy/kafka && docker-compose restart`

**2. Database Connection Issues**
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify database port: `telnet localhost 5432`
- Check connection string in config
- Restart database: `cd ../db && docker-compose restart`

**3. Transaction Processing Failures**
- Verify user and credit card IDs exist in database
- Check API logs for detailed error messages
- Use real UUIDs from seeded data for testing
- Check `/kafka/health` endpoint for consumer status

**4. Port Conflicts**
- API (8000): Change in uvicorn command
- PostgreSQL (5432): Modify docker-compose.yml port mapping
- Kafka (9092): Modify kafka docker-compose.yml

### Getting User/Card IDs for Testing
```bash
cd ../db
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import SessionLocal
from db.models import User, CreditCard

async def get_ids():
    async with SessionLocal() as session:
        user = (await session.execute(select(User).limit(1))).scalar_one_or_none()
        if user:
            print(f'User ID: {user.id}')
            card = (await session.execute(select(CreditCard).where(CreditCard.userId == user.id))).scalar_one_or_none()
            if card:
                print(f'Card ID: {card.id}')

asyncio.run(get_ids())
"
```

### Logs and Monitoring
- **API Logs**: Console output from uvicorn command
- **Kafka Consumer Logs**: Look for `INFO:src.services.kafka_consumer` messages
- **Database Logs**: SQLAlchemy query logs (set `DB_ECHO=true`)
- **Health Check**: `curl http://localhost:8000/kafka/health`

---

Generated with [AI Kickstart CLI](https://github.com/your-org/ai-kickstart)
