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
	@echo ""
	@echo "  run-service   - Start the ingestion service locally"
	@echo "  clean         - Clean up temporary files"
	@echo "  help          - Show this help message"
	@echo ""

.PHONY: test test-unit test-integration run-service clean help
