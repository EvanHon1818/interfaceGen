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

The test case should be detailed and include ALL of the following required fields:
1. name: A clear and descriptive name
2. description: Detailed description of what the test verifies
3. type: The test type (must be one of: "functional", "performance", "boundary", "exception")
4. input_data: Dictionary containing the input parameters
5. expected_output: Dictionary containing the expected response
6. preconditions: List of required preconditions (can be empty list)
7. postconditions: List of expected postconditions (can be empty list)
8. tags: List of relevant tags (can be empty list)

For performance tests, also include:
- performance_metrics: Dictionary with expected metrics (example: response_time_ms: 500, throughput_rps: 100)

For exception tests, also include:
- expected_exception: String describing the expected exception type

Format the response as a JSON object with these exact field names. Do not wrap in any additional structure."""

# Guidelines for different test types
GUIDELINES = {
    "functional": """
- Verify the core functionality of the API
- Cover main success scenarios
- Validate response format and content
- Check business logic implementation
- Ensure data persistence where applicable""",

    "performance": """
- Test response times under different loads
- Verify throughput capabilities
- Check resource utilization
- Test concurrent request handling
- Include relevant performance metrics
- Define acceptable performance thresholds""",

    "boundary": """
- Test edge cases for all parameters
- Include minimum and maximum values
- Test data type limits
- Verify handling of empty/null values
- Check string length boundaries
- Test numerical boundaries""",

    "exception": """
- Test error handling scenarios
- Include invalid input combinations
- Verify error response format
- Check security validation
- Test system unavailability scenarios
- Validate error messages"""
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