from langchain.prompts import PromptTemplate
from typing import Dict, Any
import uuid

# Base template for all test case types
BASE_TEMPLATE = """You are a test automation expert. Generate a {test_type} test case for this API:

API Definition:
{api_definition}

Similar Test Cases for Reference:
{similar_cases}

Guidelines:
{guidelines}

Required fields in the output JSON:
- id: A unique test case ID (UUID format)
- name: Clear and descriptive test case name
- param: JSON string containing input parameters
- headers: Always use the default Content-Type header for JSON
- rule: JSON string containing assertion rules, following this structure:
    {{
        "rules": [
            {{
                "matchType": one of ["top", "equal", "min", "max", "pos", "not_in"],
                "index": required for "top", "pos", "not_in" types, represents N,
                "dataPath": path to the field in response to match against,
                "columns": key-value pairs to match in the response
            }}
        ]
    }}

matchType explanation:
- top: Match in Top N results
- equal: Exact match
- min: Minimum value
- max: Maximum value
- pos: Match at position N
- not_in: Must not appear in first N positions

Example assertion rule:
{{
    "rules": [
        {{
            "matchType": "top",
            "index": "10",
            "dataPath": "data",
            "columns": {{
                "name": "example",
                "id": 123
            }}
        }}
    ]
}}

IMPORTANT: 
1. Return ONLY a JSON object with the required fields
2. For regex patterns in columns, use proper regex syntax (e.g., "^pattern$")
3. All string values in param and rule must be properly escaped
4. Headers must be {{"Content-Type": "application/json"}}"""

# Guidelines for different test types
GUIDELINES = {
    "functional": """
Focus on:
- Basic API functionality verification
- Common use cases
- Valid input combinations
- Expected response structure
Use assertion rules to verify:
- Exact matches for deterministic responses
- Position-based checks for ordered results
- Pattern matching for dynamic content""",

    "performance": """
Focus on:
- Response time verification
- Result quality under load
- Data volume handling
Use assertion rules to verify:
- Top N results quality
- Minimum/maximum value constraints
- Response structure under load""",

    "boundary": """
Focus on:
- Edge cases and limit values
- Minimum/maximum parameter values
- Special characters and formats
Use assertion rules to verify:
- Exact matches for edge cases
- Pattern matching for format validation
- Position checks for sorted results""",

    "exception": """
Focus on:
- Invalid input handling
- Error response verification
- Security boundaries
Use assertion rules to verify:
- Error code matches
- Error message patterns
- Response structure for errors"""
}

# Create prompt templates for each test type
test_case_prompt = PromptTemplate(
    input_variables=["api_definition", "similar_cases", "test_type", "guidelines"],
    template=BASE_TEMPLATE
)

# System message for chat models
SYSTEM_MESSAGE = """You are an expert test automation engineer. Your task is to generate high-quality test cases that:
1. Follow the exact output format specified
2. Use meaningful assertions based on API behavior
3. Cover important test scenarios
4. Use appropriate regex patterns where needed
5. Generate unique UUIDs for each test case""" 