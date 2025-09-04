from langchain.prompts import PromptTemplate
from typing import Dict, Any

# Base template for all test case types
BASE_TEMPLATE = """You are a test automation expert. Your task is to generate comprehensive test cases for an API endpoint.

API Definition:
{api_definition}

Similar Test Cases for Reference:
{similar_cases}

Generate a {test_type} test case that follows these guidelines:
{guidelines}

IMPORTANT: This is part of a comprehensive test suite where we need:
- Functional tests: 5 different scenarios covering various business logic paths
- Performance tests: 5 different load/stress scenarios  
- Boundary tests: 5 different edge cases and limit validations
- Exception tests: At least 5 different error handling scenarios

The test case should be detailed and include ALL of the following required fields:
1. name: A clear and descriptive name that indicates the specific scenario being tested
2. description: Detailed description of what the test verifies and why it's important
3. type: The test type (must be one of: "functional", "performance", "boundary", "exception")
4. input_data: Dictionary containing the input parameters for this specific scenario
5. expected_output: Dictionary containing the expected response for this scenario
6. preconditions: List of required preconditions (can be empty list)
7. postconditions: List of expected postconditions (can be empty list)
8. tags: List of relevant tags for categorization (can be empty list)

For performance tests, also include:
- performance_metrics: Dictionary with expected metrics (example: response_time_ms: 500, throughput_rps: 100)

For exception tests, also include:
- expected_exception: String describing the expected exception type

Make sure each test case covers a DIFFERENT scenario or aspect to ensure comprehensive coverage.
Format the response as a JSON object with these exact field names. Do not wrap in any additional structure.
IMPORTANT: Return only ONE test case as a single JSON object, NOT an array of test cases."""

# Guidelines for different test types
GUIDELINES = {
    "functional": """
- Verify the core functionality of the API across different business scenarios
- Cover main success scenarios with various valid input combinations
- Validate response format and content for different data types
- Check business logic implementation with different user roles/permissions
- Ensure data persistence and retrieval work correctly
- Test different workflow states and transitions
- Validate integration with dependent services
- Cover different authentication and authorization scenarios""",

    "performance": """
- Test response times under different load conditions (light, medium, heavy)
- Verify throughput capabilities with concurrent users
- Check resource utilization under stress conditions
- Test performance with large datasets and complex queries
- Measure performance degradation patterns
- Test memory usage and garbage collection impact
- Validate performance with different network conditions
- Include relevant performance metrics and acceptable thresholds""",

    "boundary": """
- Test edge cases for all input parameters (min/max values)
- Include minimum and maximum string lengths
- Test numerical boundaries (zero, negative, overflow)
- Verify handling of empty, null, and undefined values
- Check array/list size limits (empty, single item, maximum)
- Test special characters and encoding edge cases
- Validate date/time boundary conditions
- Test resource limits and capacity constraints""",

    "exception": """
- Test comprehensive error handling scenarios
- Include invalid input format and type mismatches
- Verify authentication and authorization failures
- Test network timeout and connection errors
- Check resource not found and access denied scenarios
- Validate input validation errors with detailed messages
- Test system unavailability and service degradation
- Include security validation failures and injection attempts
- Verify proper error response format and HTTP status codes"""
}

class TestCasePrompts:
    """Collection of prompts for generating different types of test cases"""

    @staticmethod
    def get_prompt(test_type: str) -> PromptTemplate:
        """Get the prompt template for a specific test case type"""
        if test_type not in GUIDELINES:
            raise ValueError(f"Unknown test type: {test_type}")

        # Create the template with placeholders for all variables
        template = BASE_TEMPLATE.replace("{test_type}", test_type).replace("{guidelines}", GUIDELINES[test_type])
        
        return PromptTemplate(
            input_variables=["api_definition", "similar_cases"],
            template=template
        )

    @staticmethod
    def format_api_definition(api_def: Dict[str, Any]) -> str:
        """Format API definition for prompt input"""
        return f"""
Name: {api_def['name']}
Description: {api_def.get('description', 'N/A')}
Method: {api_def['method']}
Path: {api_def.get('path', 'N/A')}

Input Parameters:
{TestCasePrompts._format_parameters(api_def['input_params'])}

Output Parameters:
{TestCasePrompts._format_parameters(api_def['output_params'])}
"""

    @staticmethod
    def format_similar_cases(cases: list) -> str:
        """Format similar test cases for prompt input"""
        if not cases:
            return "No similar test cases available."

        formatted_cases = []
        for case in cases:
            formatted_case = f"""
Test Case: {case['name']}
Type: {case['type']}
Description: {case['description']}
Input: {case['input_data']}
Expected Output: {case['expected_output']}
"""
            formatted_cases.append(formatted_case)

        return "\n".join(formatted_cases)

    @staticmethod
    def _format_parameters(params: Dict[str, Any]) -> str:
        """Helper method to format parameters"""
        if not params:
            return "None"

        formatted = []
        for name, param in params.items():
            constraints = param.get('constraints', {})
            constraints_str = ", ".join(f"{k}={v}" for k, v in constraints.items()) if constraints else "None"
            
            formatted.append(f"""- {name}:
  Type: {param['type']}
  Required: {param.get('required', True)}
  Description: {param.get('description', 'N/A')}
  Constraints: {constraints_str}""")

        return "\n".join(formatted) 