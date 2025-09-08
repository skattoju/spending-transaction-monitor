# Makefile for Ingestion Service Testing and Development

# Default target (see detailed help at bottom of file)

# Run all tests
test:
	@echo "🚀 Running all tests..."
	uv run python run_tests.py

# Run only unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	uv run pytest tests/unit/ -v

# Run only integration tests (using our test runner)
test-integration:
	@echo "🔗 Running integration tests..."
	uv run python -c "from run_tests import run_integration_tests, run_service_validation; import sys; sys.exit(0 if run_service_validation() and run_integration_tests() else 1)"

# Run only E2E tests
test-e2e:
	@echo "🌐 Running E2E tests in Kubernetes cluster..."
	@echo "📋 Prerequisites: kubectl configured, Kafka + ingestion service deployed"
	@echo ""
	@echo "🚀 Creating E2E test runner pod..."
	@kubectl run e2e-test-runner --image=python:3.12-slim -- sleep 3600 || true
	@echo "⏳ Waiting for test runner pod to be ready..."
	@kubectl wait --for=condition=ready pod e2e-test-runner --timeout=60s
	@echo "📦 Installing test dependencies..."
	@kubectl exec e2e-test-runner -- pip install requests kafka-python > /dev/null 2>&1
	@echo "📁 Copying E2E test script..."
	@kubectl cp tests/e2e/test_e2e.py e2e-test-runner:/test_e2e.py
	@echo "🧪 Running E2E tests..."
	@echo "════════════════════════════════════════════════════════════════"
	@kubectl exec e2e-test-runner -- \
		env INGESTION_SERVICE_HOST=ingestion-py-ingestion-service-py \
		    INGESTION_SERVICE_PORT=80 \
		    KAFKA_HOST=kafka-kafka-kafka-bootstrap \
		    KAFKA_PORT=9092 \
		python /test_e2e.py || \
		(echo "❌ E2E tests failed. Cleaning up..." && kubectl delete pod e2e-test-runner --ignore-not-found && exit 1)
	@echo "════════════════════════════════════════════════════════════════"
	@echo "🧹 Cleaning up test runner pod..."
	@kubectl delete pod e2e-test-runner --ignore-not-found
	@echo "✅ E2E tests completed successfully!"

# Start the service locally
run-service:
	@echo "🚀 Starting ingestion service..."
	uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Show help
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests (unit + integration + service validation)"
	@echo "  test-unit     - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  test-e2e      - Run E2E tests in Kubernetes cluster (requires kubectl + deployed services)"
	@echo "  run-service   - Start the ingestion service locally"
	@echo "  clean         - Clean up temporary files"
	@echo "  help          - Show this help message"
	@echo ""
	@echo "Note: E2E tests require a Kubernetes cluster with Kafka and ingestion service deployed."
	@echo "      See tests/e2e/README.md for detailed setup instructions."

.PHONY: test test-unit test-integration test-e2e run-service clean help
