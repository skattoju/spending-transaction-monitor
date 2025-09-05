# E2E Tests for Ingestion Service

This directory contains end-to-end tests that verify the complete transaction flow from API through Kafka to message consumption.

## Requirements and Assumptions

### Prerequisites
- **Kubernetes cluster** with `kubectl` configured
- **Kafka deployed** in the cluster (accessible at `kafka-kafka-kafka-bootstrap:9092`)
- **Ingestion service deployed** in the cluster (accessible at `ingestion-py-ingestion-service-py:80`)

### Test Environment Setup

The E2E tests are designed to run **inside a Kubernetes cluster** using a test runner pod. They cannot run directly on localhost because they require:

1. **Network access** to cluster services (`kafka-kafka-kafka-bootstrap`, `ingestion-py-ingestion-service-py`)
2. **Kafka consumer** that can connect to the cluster's Kafka instance
3. **Service discovery** that works within the cluster network

## Running E2E Tests

### Option 1: Using Makefile (Recommended)
```bash
make test-e2e
```

This will:
1. Create a test runner pod in the cluster
2. Install required dependencies (`requests`, `kafka-python`)
3. Copy the E2E test script to the pod
4. Run the test with proper environment variables
5. Stream the logs to your terminal
6. Clean up the test runner pod

### Option 2: Manual Setup
If you need to run the tests manually or debug issues:

```bash
# 1. Create test runner pod
kubectl run e2e-test-runner --image=python:3.12-slim -- sleep 3600

# 2. Wait for pod to be ready
kubectl wait --for=condition=ready pod e2e-test-runner --timeout=60s

# 3. Install dependencies
kubectl exec e2e-test-runner -- pip install requests kafka-python

# 4. Copy test script
kubectl cp tests/e2e/test_e2e.py e2e-test-runner:/test_e2e.py

# 5. Run the test
kubectl exec e2e-test-runner -- \
  env INGESTION_SERVICE_HOST=ingestion-py-ingestion-service-py \
      INGESTION_SERVICE_PORT=80 \
      KAFKA_HOST=kafka-kafka-kafka-bootstrap \
      KAFKA_PORT=9092 \
  python /test_e2e.py

# 6. Clean up
kubectl delete pod e2e-test-runner
```

## Test Files

- **`test_e2e.py`**: Unified E2E test script that works both with pytest and standalone (no pytest dependency required)

## Environment Variables

The tests use these environment variables to connect to services:

| Variable | Default | Description |
|----------|---------|-------------|
| `INGESTION_SERVICE_HOST` | `localhost` | Hostname of ingestion service |
| `INGESTION_SERVICE_PORT` | `8000` | Port of ingestion service |
| `KAFKA_HOST` | `localhost` | Hostname of Kafka bootstrap server |
| `KAFKA_PORT` | `9092` | Port of Kafka bootstrap server |

## Expected Test Flow

1. **Health Check**: Verify ingestion service `/healthz` and `/health` endpoints
2. **Transaction Submit**: POST a test transaction to `/transactions/`
3. **Kafka Consumption**: Consume the message from the `transactions` topic
4. **Validation**: Verify the consumed message matches expected format

## Troubleshooting

### Common Issues

**"Connection refused" errors**: 
- Ensure you're running the test inside the cluster (not on localhost)
- Verify the ingestion service and Kafka are deployed and running

**"No brokers available" errors**:
- Check that Kafka is running: `kubectl get pods -l strimzi.io/cluster=kafka-kafka`
- Verify Kafka service: `kubectl get svc kafka-kafka-kafka-bootstrap`

**Pod creation failures**:
- Ensure you have permissions to create pods in the cluster
- Check cluster resources: `kubectl get nodes`

### Debugging

To debug test issues, you can:

1. **Check service status**:
   ```bash
   kubectl get pods -l app.kubernetes.io/name=ingestion-service-py
   kubectl get pods -l strimzi.io/cluster=kafka-kafka
   ```

2. **Check service logs**:
   ```bash
   kubectl logs -l app.kubernetes.io/name=ingestion-service-py
   kubectl logs kafka-kafka-dual-role-0
   ```

3. **Test connectivity manually**:
   ```bash
   kubectl exec e2e-test-runner -- curl http://ingestion-py-ingestion-service-py/healthz
   ```

## Local Development

For local development, use unit and integration tests instead:
```bash
make test-unit        # Unit tests (no external dependencies)
make test-integration # Integration tests (uses TestClient)
make test            # All local tests (unit + integration)
```

E2E tests are primarily intended for CI/CD pipelines and deployed environments.
