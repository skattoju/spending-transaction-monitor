# Python Ingestion Service

This service is a Python-based implementation of the transaction ingestion service. It uses FastAPI to create a REST API and `kafka-python` to produce messages to a Kafka topic.

The service uses a common data model defined in the `common` directory. See the main `README.md` for more details on the data model.

## Running the service

To run the service locally, you will need to have Python and Podman installed.

1. Install the dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Running the tests

We provide multiple ways to run tests for maximum reliability:

### Recommended: Use the test runner
```bash
# Run all tests (unit + integration + service validation)
make test

# Or use the test runner directly
python run_tests.py
```

### Run specific test types
```bash
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-e2e        # E2E tests (requires running service + Kafka)
```

### Traditional pytest (if needed)
```bash
python -m pytest tests/unit/ -v           # Unit tests
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/e2e/ -v -s        # E2E tests
```

### Test Organization
- **`tests/unit/`** - Unit tests with mocked dependencies
- **`tests/integration/`** - Integration tests using FastAPI TestClient
- **`tests/e2e/`** - End-to-end tests requiring real Kafka

The test runner (`run_tests.py`) provides the most comprehensive testing including:
- Service validation (imports, basic functionality)
- Unit tests (mocked Kafka, isolated component testing) 
- Integration tests (FastAPI TestClient, end-to-end flow)

Unit and integration tests are designed to work without requiring Kafka to be running, using graceful degradation.

## Kubernetes Deployment

This service is designed to run in Kubernetes with Kafka. The Helm charts include development defaults that work out-of-the-box:

```bash
# Quick local deployment (from project root)
make -C packages/ingestion-service/deploy install-kafka
make -C packages/ingestion-service/deploy install-ingestion-py
```

For detailed deployment scenarios including production configurations, see:
- [`../README.md`](../README.md) - Overview and quick start
- [`../deploy/INSTALL.md`](../deploy/INSTALL.md) - Comprehensive deployment guide
