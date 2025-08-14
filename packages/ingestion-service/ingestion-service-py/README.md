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
