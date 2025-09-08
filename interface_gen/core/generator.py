import json
import uuid
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI

from ..models.api import APIDefinition
from ..models.test_case import TestCase
from .prompts import test_case_prompt, SYSTEM_MESSAGE, GUIDELINES
from .rag import TestCaseRAG
from ..config import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class TestCaseGenerator:
    """Core class for generating test cases"""

    def __init__(self):
        """Initialize the test case generator"""
        logger.info("Initializing TestCaseGenerator")
        # Configure ChatOpenAI
        openai_config = config.openai.get_llm_config()
        logger.debug(f"OpenAI config: {openai_config}")
        self.llm = ChatOpenAI(**openai_config)
        
        # Initialize RAG system
        logger.info("Initializing RAG system")
        self.rag = TestCaseRAG()

    def _get_similar_cases(self, api_name: str, test_type: str) -> List[Dict[str, Any]]:
        """Get similar test cases using RAG"""
        logger.info(f"Searching for similar {test_type} test cases for API {api_name}")
        try:
            similar_cases = self.rag.get_test_cases_by_type(
                test_type=test_type,
                api_name=api_name,
                k=3  # Get top 3 similar cases
            )
            logger.debug(f"Found {len(similar_cases)} similar cases")
            return similar_cases
        except Exception as e:
            logger.warning(f"Failed to get similar cases: {str(e)}")
            return []

    def _sanitize_json_string(self, s: str) -> str:
        """Sanitize a JSON string to ensure it's valid"""
        # Remove any invalid escape sequences
        s = s.replace("\\'", "'")  # Replace escaped single quotes
        s = s.replace('\\"', '"')  # Replace escaped double quotes
        s = s.replace('\\\\', '\\')  # Replace double backslashes
        
        # Handle any remaining backslashes
        chars = []
        i = 0
        while i < len(s):
            if s[i] == '\\':
                if i + 1 < len(s) and s[i + 1] in 'bfnrt/':
                    # Valid escape sequence
                    chars.append(s[i:i + 2])
                    i += 2
                else:
                    # Invalid escape sequence, skip the backslash
                    i += 1
            else:
                chars.append(s[i])
                i += 1
        
        return ''.join(chars)

    def _sanitize_test_case(self, test_case: Dict[str, Any], api_name: str, test_type: str) -> Dict[str, Any]:
        """Sanitize test case data to ensure proper format"""
        logger.debug(f"Sanitizing test case: {json.dumps(test_case, indent=2)}")
        
        # Ensure required fields exist
        required_fields = ["id", "name", "param", "headers", "rule"]
        for field in required_fields:
            if field not in test_case:
                logger.error(f"Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")

        # Add metadata
        test_case["api_name"] = api_name
        test_case["type"] = test_type

        # Ensure param is a JSON string
        if not isinstance(test_case["param"], str):
            logger.debug(f"Converting param to JSON string: {test_case['param']}")
            test_case["param"] = json.dumps(test_case["param"], ensure_ascii=False)
        else:
            test_case["param"] = self._sanitize_json_string(test_case["param"])

        # Ensure rule is a JSON string
        if not isinstance(test_case["rule"], str):
            logger.debug(f"Converting rule to JSON string: {test_case['rule']}")
            test_case["rule"] = json.dumps(test_case["rule"], ensure_ascii=False)
        else:
            test_case["rule"] = self._sanitize_json_string(test_case["rule"])

        # Force headers to be the correct format
        test_case["headers"] = {"Content-Type": "application/json"}
        logger.debug(f"After sanitization: {json.dumps(test_case, indent=2)}")
        return test_case

    def _fix_json_string(self, json_str: str) -> str:
        """Fix common JSON formatting issues in LLM responses"""
        import re
        
        # Remove any markdown code blocks
        json_str = re.sub(r'```json\s*', '', json_str)
        json_str = re.sub(r'```\s*$', '', json_str)
        
        # Remove any leading/trailing whitespace and newlines
        json_str = json_str.strip()
        
        # Find the actual JSON object
        start = json_str.find('{')
        end = json_str.rfind('}')
        if start != -1 and end != -1:
            json_str = json_str[start:end + 1]
        
        # Replace single quotes with double quotes (but be careful with nested quotes)
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)  # Keys
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)  # String values
        
        # Fix common formatting issues
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas before }
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas before ]
        
        # Fix missing commas between objects/arrays
        json_str = re.sub(r'}\s*{', '}, {', json_str)
        json_str = re.sub(r']\s*{', '], {', json_str)
        json_str = re.sub(r'}\s*"', '}, "', json_str)
        json_str = re.sub(r']\s*"', '], "', json_str)
        
        # Fix unescaped quotes in string values
        # This is tricky - we need to escape quotes that are inside string values
        # but not the quotes that delimit the strings themselves
        
        return json_str

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from text that might contain other content"""
        logger.debug(f"Extracting JSON from text: {text}")
        
        try:
            # First, try to fix the JSON string
            json_str = self._fix_json_string(text)
            logger.debug(f"Fixed JSON string: {json_str}")
            
            # Try to parse the JSON
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            
            # If parsing fails, try to create a minimal valid test case
            logger.warning("Creating fallback test case due to JSON parsing error")
            
            # Extract basic information if possible
            import re
            
            # Try to extract name
            name_match = re.search(r'"name"\s*:\s*"([^"]*)"', text)
            name = name_match.group(1) if name_match else "Generated Test Case"
            
            # Try to extract id
            id_match = re.search(r'"id"\s*:\s*"([^"]*)"', text)
            test_id = id_match.group(1) if id_match else str(uuid.uuid4())
            
            # Create a basic fallback test case
            fallback_case = {
                "id": test_id,
                "name": name,
                "param": "{}",
                "headers": {"Content-Type": "application/json"},
                "rule": json.dumps({
                    "rules": [
                        {
                            "matchType": "equal",
                            "dataPath": "result",
                            "columns": {
                                "result": 0
                            }
                        }
                    ]
                })
            }
            
            logger.debug(f"Created fallback test case: {json.dumps(fallback_case, indent=2)}")
            return fallback_case
            
        except Exception as e:
            logger.error(f"Failed to extract JSON: {str(e)}")
            raise ValueError(f"Could not extract valid JSON from response: {str(e)}")

    def _generate_test_case(self, api_definition: dict, test_type: str, similar_cases: List[dict] = None) -> TestCase:
        """Generate a single test case using the prompt template"""
        logger.info(f"Generating {test_type} test case")
        
        # Get similar cases from RAG if not provided
        if similar_cases is None:
            similar_cases = self._get_similar_cases(api_definition["name"], test_type)
        
        # Format similar cases
        formatted_cases = json.dumps(similar_cases, indent=2) if similar_cases else "[]"
        logger.debug(f"Using {len(similar_cases) if similar_cases else 0} similar cases for reference")
        
        # Format the prompt
        formatted_prompt = test_case_prompt.format(
            api_definition=json.dumps(api_definition, indent=2, ensure_ascii=False),
            similar_cases=formatted_cases,
            test_type=test_type,
            guidelines=GUIDELINES[test_type]
        )
        logger.debug(f"Formatted prompt: {formatted_prompt}")
        
        # Generate response
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": formatted_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            logger.debug(f"Raw LLM Response: {response.content}")
            
            # Extract and parse JSON from response
            test_case = self._extract_json_from_text(response.content)
            logger.debug(f"Parsed test case: {json.dumps(test_case, indent=2)}")
            
            # Sanitize and validate the test case
            test_case = self._sanitize_test_case(test_case, api_definition["name"], test_type)
            
            # Validate rule format
            try:
                rules = json.loads(test_case["rule"]) if isinstance(test_case["rule"], str) else test_case["rule"]
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse rule JSON: {str(e)}")
                logger.debug(f"Rule content: {test_case['rule']}")
                # Create a default rule if parsing fails
                rules = {
                    "rules": [
                        {
                            "matchType": "equal",
                            "dataPath": "result",
                            "columns": {
                                "result": 0
                            }
                        }
                    ]
                }
                test_case["rule"] = json.dumps(rules)
                
            if "rules" not in rules or not isinstance(rules["rules"], list):
                logger.error("Invalid rule format: missing or invalid 'rules' array")
                # Create a default rule
                rules = {
                    "rules": [
                        {
                            "matchType": "equal",
                            "dataPath": "result",
                            "columns": {
                                "result": 0
                            }
                        }
                    ]
                }
                test_case["rule"] = json.dumps(rules)
            
            # Validate each rule
            for i, rule in enumerate(rules["rules"]):
                try:
                    if "matchType" not in rule or rule["matchType"] not in ["top", "equal", "min", "max", "pos", "not_in"]:
                        logger.warning(f"Invalid matchType in rule {i}: {rule.get('matchType')}")
                        # Fix the rule
                        rule["matchType"] = "equal"
                    if rule["matchType"] in ["top", "pos", "not_in"] and "index" not in rule:
                        logger.warning(f"Missing index for matchType {rule['matchType']} in rule {i}")
                        rule["index"] = "1"
                    if "dataPath" not in rule:
                        logger.warning(f"Missing dataPath in rule {i}")
                        rule["dataPath"] = "result"
                    if "columns" not in rule:
                        logger.warning(f"Missing columns in rule {i}")
                        rule["columns"] = {"result": 0}
                except Exception as e:
                    logger.warning(f"Error validating rule {i}: {str(e)}")
                    # Replace with a default rule
                    rules["rules"][i] = {
                        "matchType": "equal",
                        "dataPath": "result",
                        "columns": {"result": 0}
                    }
            
            # Update the rule in test_case
            test_case["rule"] = json.dumps(rules)
            
            # Create test case object
            test_case_obj = TestCase(**test_case)
            logger.debug(f"Created TestCase object: {test_case_obj}")
            
            # Add to RAG system
            try:
                self.rag.add_test_cases([test_case])
                logger.debug("Added test case to RAG system")
            except Exception as e:
                logger.warning(f"Failed to add test case to RAG: {str(e)}")
            
            return test_case_obj
            
        except Exception as e:
            logger.error(f"Error in _generate_test_case: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to generate test case: {str(e)}")

    def generate_test_cases(self, api_definition: APIDefinition, test_types: List[str], num_cases: int = 5) -> List[TestCase]:
        """Generate multiple test cases for the given API definition"""
        logger.info(f"Generating {num_cases} test cases for each type in {test_types}")
        test_cases = []
        
        for test_type in test_types:
            if test_type not in GUIDELINES:
                logger.error(f"Unknown test type: {test_type}")
                raise ValueError(f"Unknown test type: {test_type}")
            
            for i in range(num_cases):
                logger.info(f"Generating test case {i+1} of {num_cases} for type {test_type}")
                test_case = self._generate_test_case(
                    api_definition.dict(),
                    test_type=test_type,
                    similar_cases=[tc.dict() for tc in test_cases]  # Pass previously generated cases as reference
                )
                test_cases.append(test_case)
        
        logger.info(f"Generated {len(test_cases)} test cases in total")
        return test_cases 