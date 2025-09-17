# API Services Test Suite

This directory contains comprehensive test suites for the API services, focusing on business logic and data access operations.

## 📁 Test Files

| File | Description | Coverage |
|------|-------------|----------|
| `test_transaction_service.py` | Tests for `TransactionService` | Data access, filtering, pagination |
| `test_alert_rule_service.py` | Tests for `AlertRuleService` | Rule validation, alert triggering, LLM integration |
| `conftest.py` | Shared test fixtures | Mock objects, sample data |
| `run_tests.py` | Test runner script | Easy test execution with options |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd packages/api/src/tests
python run_tests.py --install-deps
```

### 2. Run All Tests
```bash
python run_tests.py
```

### 3. Run Specific Service Tests
```bash
# Transaction Service only
python run_tests.py --transaction

# Alert Rule Service only  
python run_tests.py --alert-rule
```

### 4. Run with Coverage Report
```bash
python run_tests.py --coverage
```

## 🧪 Test Coverage

### TransactionService Tests (25 test cases)
- ✅ **Data Retrieval**: `get_latest_transaction()`, `get_transaction_by_id()`
- ✅ **Pagination**: `get_user_transactions()` with limit/offset
- ✅ **Filtering**: `get_transactions_with_filters()` with multiple criteria
- ✅ **Validation**: `user_has_transactions()`
- ✅ **Fallback Data**: `get_dummy_transaction()`
- ✅ **Error Handling**: Database connection errors
- ✅ **Edge Cases**: Empty results, invalid parameters

### AlertRuleService Tests (20 test cases)
- ✅ **Rule Validation**: `validate_alert_rule()` with real/dummy transactions
- ✅ **Alert Triggering**: `trigger_alert_rule()` success/failure scenarios  
- ✅ **LLM Integration**: `parse_nl_rule_with_llm()`, `generate_alert_with_llm()`
- ✅ **Notification Creation**: Proper `AlertNotification` object creation
- ✅ **Database Updates**: Trigger count and timestamp updates
- ✅ **Business Logic**: Inactive rules, missing transactions
- ✅ **Error Handling**: LLM failures, database errors

## 🛠️ Test Architecture

### Mocking Strategy
- **Database Sessions**: `AsyncMock` for SQLAlchemy sessions
- **LLM Services**: `patch` for external graph applications
- **Service Dependencies**: Dependency injection mocking

### Fixtures
- **Shared Data**: Common user IDs, transaction objects, alert rules
- **Mock Objects**: Pre-configured database mocks
- **Response Templates**: Standard LLM response formats

### Async Testing  
- Uses `pytest-asyncio` for proper async/await testing
- Event loop management for database operations
- Proper cleanup of async resources

## 📊 Running Different Test Types

### Unit Tests Only
```bash
pytest -m "not integration"
```

### With Verbose Output
```bash
python run_tests.py --verbose
```

### Specific Test Methods
```bash
pytest test_transaction_service.py::TestTransactionService::test_get_latest_transaction_success -v
```

### Failed Tests Only
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## 📈 Coverage Reports

After running with `--coverage`, view the HTML report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

## 🔧 Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers
asyncio_mode = auto
```

### Required Dependencies
- `pytest>=7.0.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-mock>=3.10.0` - Advanced mocking
- `pytest-cov>=4.0.0` - Coverage reporting

## 🎯 Best Practices

### 1. Test Organization
- **One test class per service**
- **Descriptive test method names**
- **Setup with fixtures, cleanup automatic**

### 2. Mocking Approach
- **Mock external dependencies** (database, LLM services)
- **Keep business logic real** (test actual service methods)
- **Use shared fixtures** for common objects

### 3. Assertion Strategy
- **Verify return values** and data structures
- **Check method calls** on mocked dependencies  
- **Assert side effects** (database operations, state changes)

### 4. Error Testing
- **Test exception scenarios** (invalid input, service failures)
- **Verify error messages** and error types
- **Test graceful degradation** (fallback behaviors)

## 🚨 Troubleshooting

### Import Errors
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../.."
```

### Async Test Issues
```bash
# Install specific asyncio plugin version
pip install pytest-asyncio==0.21.0
```

### Database Mock Problems
```bash
# Verify SQLAlchemy mock setup
pytest -v -s test_transaction_service.py::TestTransactionService::test_get_latest_transaction_success
```

## 📝 Adding New Tests

### 1. Create Test Method
```python
@pytest.mark.asyncio
async def test_new_feature(self, service, mock_session):
    # Arrange
    # Act  
    # Assert
```

### 2. Add Fixtures if Needed
```python
@pytest.fixture
def custom_test_data():
    return {"key": "value"}
```

### 3. Update Documentation
- Add test description to this README
- Document new fixtures in `conftest.py`
- Update coverage statistics

---

## 🎉 Ready to Test!

Your services now have comprehensive test coverage with easy-to-use runners and detailed reporting. Happy testing! 🧪✨
