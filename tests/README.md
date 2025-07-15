# Agent Caddie Test Suite

This directory contains comprehensive tests for the Agent Caddie golf caddie CLI application.

## Test Structure

### Test Files

- `test_analytics.py` - Tests for distance calculations and shot result recording
- `test_prompts.py` - Tests for shot details collection and prompt building
- `test_embeddings.py` - Tests for OpenAI embedding generation
- `test_db.py` - Tests for database operations (Supabase)
- `test_cli.py` - Tests for CLI commands and user interactions

### Test Categories

#### Unit Tests
- **Analytics**: Wind adjustments, effective distance calculations, shot result analysis
- **Prompts**: Shot details collection, prompt building for AI recommendations
- **Embeddings**: OpenAI embedding generation for similarity matching
- **Database**: CRUD operations for club distances and shot records

#### Integration Tests
- **CLI**: End-to-end command testing with mocked dependencies
- **Database**: Full database operation flows
- **AI Integration**: OpenAI API interaction testing

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_analytics.py

# Run specific test class
pytest tests/test_analytics.py::TestWindAdjustment

# Run specific test method
pytest tests/test_analytics.py::TestWindAdjustment::test_headwind_adjustment
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests excluding slow tests
pytest -m "not slow"

# Run tests with coverage
pytest --cov=agent_caddie --cov-report=html
```

### Test Configuration

The test suite uses `pytest.ini` for configuration:
- Test discovery patterns
- Output formatting
- Warning filters
- Custom markers

## Test Coverage

### Analytics Module
- ✅ Wind adjustment calculations
- ✅ Effective distance computations
- ✅ Shot result recording and analysis
- ✅ Edge cases and error handling

### Prompts Module
- ✅ Shot details collection
- ✅ Prompt building for AI recommendations
- ✅ Various scenario types (fairway, rough, sand)
- ✅ User input validation

### Embeddings Module
- ✅ OpenAI embedding generation
- ✅ Different text inputs and edge cases
- ✅ Error handling for API calls

### Database Module
- ✅ Club distance saving and updating
- ✅ Shot record saving (with mis-hit filtering)
- ✅ Similar shots retrieval
- ✅ Database connection mocking

### CLI Module
- ✅ Update command functionality
- ✅ Shot command workflow
- ✅ User input handling
- ✅ Error scenarios
- ✅ Help command testing

## Mocking Strategy

### External Dependencies
- **OpenAI API**: Mocked responses for embeddings and chat completions
- **Supabase**: Mocked database operations and RPC calls
- **User Input**: Mocked questionary prompts for CLI testing

### Test Fixtures
- `sample_scenario`: Standard golf scenario for testing
- `sample_past_shots`: Historical shot data
- `sample_club_distances`: Club distance data
- `mock_openai_response`: OpenAI API response mock
- `mock_embedding`: Embedding vector mock
- `mock_supabase`: Supabase client mock

## Best Practices

### Test Organization
- Tests are organized by module functionality
- Each test class focuses on a specific component
- Test methods have descriptive names and docstrings
- Edge cases and error conditions are covered

### Mocking Guidelines
- External APIs are always mocked
- Database operations use mocked responses
- User interactions are simulated
- Real network calls are avoided

### Assertion Strategy
- Verify function calls with correct parameters
- Check return values and side effects
- Validate data transformations
- Ensure error conditions are handled

## Adding New Tests

### For New Features
1. Create test file following naming convention: `test_<module>.py`
2. Add test classes with descriptive names
3. Include both positive and negative test cases
4. Mock external dependencies appropriately
5. Add fixtures to `conftest.py` if reusable

### Test Naming Convention
- Test classes: `Test<ComponentName>`
- Test methods: `test_<functionality>_<scenario>`
- Use descriptive names that explain the test purpose

### Example Test Structure
```python
class TestNewFeature:
    """Test new feature functionality."""
    
    def test_new_feature_success(self):
        """Test successful new feature execution."""
        # Arrange
        # Act
        # Assert
    
    def test_new_feature_error_handling(self):
        """Test new feature error handling."""
        # Arrange
        # Act
        # Assert
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:
- Fast execution (under 30 seconds)
- No external dependencies
- Comprehensive coverage
- Clear pass/fail indicators

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure `agent_caddie` package is installed in development mode
2. **Mock Issues**: Check that external dependencies are properly mocked
3. **Test Failures**: Verify that test data matches expected formats

### Debug Mode
```bash
# Run tests with debug output
pytest -v -s

# Run single test with debug
pytest tests/test_analytics.py::TestWindAdjustment::test_headwind_adjustment -v -s
``` 