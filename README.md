# Interface Test Case Generator

This project uses LangChain and RAG (Retrieval Augmented Generation) to automatically generate comprehensive test cases for APIs. It generates test cases across multiple dimensions:
- Functional testing
- Performance testing
- Boundary testing
- Exception testing

## Features

- RAG-based test case generation using existing test cases as context
- Support for multiple test dimensions
- Structured output format for easy integration
- API parameter analysis and validation
- Customizable prompt templates
- Learning from previous test cases to improve future generations
- Support for specific scenario generation
- CLI interface for easy usage

## Core Components

1. **Models**:
   - API definition models for structured input
   - Test case models with comprehensive metadata
   - Support for various parameter types and constraints

2. **RAG System**:
   - Storage and retrieval of similar test cases
   - Learning from generated test cases
   - Context-aware test case generation

3. **Prompt Templates**:
   - Specialized templates for each test type
   - Customizable generation guidelines
   - Support for specific scenarios

4. **Test Case Generator**:
   - LangChain and OpenAI integration
   - Temperature control for different test types
   - Structured output generation

## Setup

1. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Required: OpenAI API Key
export OPENAI_API_KEY=your-api-key-here

# Optional: Custom OpenAI API configuration
export OPENAI_API_BASE=your-custom-api-base-url  # e.g., https://api.openai.com/v1
export OPENAI_API_VERSION=your-api-version       # e.g., 2024-02-15
export OPENAI_API_TYPE=your-api-type            # e.g., azure, open_ai, etc.

# For Azure OpenAI (when OPENAI_API_TYPE=azure):
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name  # Azure deployment name

# Optional: Model configuration
export MODEL_NAME=gpt-4-turbo-preview
export EMBEDDING_MODEL=text-embedding-3-small

# Optional: Vector store configuration
export VECTOR_STORE_PATH=./data/vector_store

# Optional: Temperature settings for different test types
export TEMPERATURE_FUNCTIONAL=0.3
export TEMPERATURE_PERFORMANCE=0.4
export TEMPERATURE_BOUNDARY=0.5
export TEMPERATURE_EXCEPTION=0.7
```

### Azure OpenAI Configuration Example

If you're using Azure OpenAI, set up your environment like this:

```bash
# Azure OpenAI configuration
export OPENAI_API_KEY=your-azure-api-key
export OPENAI_API_BASE=https://your-resource-name.openai.azure.com
export OPENAI_API_TYPE=azure
export OPENAI_API_VERSION=2024-02-15-preview
export AZURE_OPENAI_DEPLOYMENT=your-gpt-deployment-name
export EMBEDDING_MODEL=your-embedding-deployment-name
```

## Usage

### 1. Create API Definition

Create a JSON file describing your API (see `examples/user_api.json` for a complete example):

```python
{
    "name": "create_user",
    "description": "Create a new user account",
    "method": "POST",
    "path": "/api/v1/users",
    "input_params": {
        "username": {
            "type": "string",
            "description": "User's username",
            "required": true,
            "constraints": {
                "min_length": 3,
                "max_length": 50
            }
        }
    },
    "output_params": {
        "user_id": {
            "type": "string",
            "description": "Unique identifier"
        }
    }
}
```

### 2. Generate Test Cases

Use the CLI to generate test cases:

```bash
# Generate all types of test cases
python -m interface_gen.cli examples/user_api.json -o output/test_cases.json

# Generate specific types of test cases
python -m interface_gen.cli examples/user_api.json -t functional performance -n 5

# Generate a test case for a specific scenario
python -m interface_gen.cli examples/user_api.json \
    --scenario "Test password strength requirements" \
    --scenario-type functional
```

### 3. Test Case Output

Generated test cases include:
- Unique identifier
- Name and description
- Input data
- Expected output
- Pre and post conditions
- Relevant tags
- Type-specific metrics (e.g., performance thresholds)

Example test case output:
```json
{
    "id": "test_001",
    "name": "Valid user registration",
    "description": "Test user registration with valid input data",
    "type": "functional",
    "input_data": {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    },
    "expected_output": {
        "status": "success",
        "user_id": "usr_123456789"
    },
    "preconditions": ["Database is accessible"],
    "postconditions": ["User is created in database"],
    "tags": ["registration", "happy-path"]
}
```

## Test Case Types

1. **Functional Testing**:
   - Core functionality verification
   - Success scenarios
   - Response format validation
   - Business logic testing
   - Data persistence checks

2. **Performance Testing**:
   - Response time measurements
   - Throughput capabilities
   - Resource utilization
   - Concurrent request handling
   - Performance thresholds

3. **Boundary Testing**:
   - Edge cases for all parameters
   - Minimum/maximum values
   - Data type limits
   - Empty/null handling
   - String length boundaries

4. **Exception Testing**:
   - Error handling scenarios
   - Invalid input combinations
   - Error response format
   - Security validation
   - System unavailability scenarios

## RAG System

The RAG (Retrieval Augmented Generation) system:
- Stores generated test cases for future reference
- Learns from existing test cases to improve generation
- Provides context-aware suggestions
- Supports filtering by test type and API
- Enables similarity-based test case retrieval

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 