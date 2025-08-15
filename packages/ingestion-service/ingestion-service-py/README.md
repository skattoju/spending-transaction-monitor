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

To run the tests, you will need to have `pytest` installed.

```bash
python -m pytest
```

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
