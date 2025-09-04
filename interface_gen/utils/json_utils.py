"""JSON processing utilities."""

import re
import json
from typing import Dict, Any

class JSONProcessor:
    """JSON processing and cleaning utilities."""

    @staticmethod
    def clean_json_string(json_str: str) -> str:
        """Clean and normalize JSON string."""
        # Clean up the string
        json_str = json_str.strip()
        
        # Remove any trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Remove any newlines and extra spaces in property names
        json_str = re.sub(r'"\s*\n\s*([^"]+)\s*":', r'"\1":', json_str)
        
        # Remove any newlines between values
        json_str = re.sub(r'\s*\n\s*', ' ', json_str)
        
        # Fix any missing quotes around property names
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        return json_str

    @staticmethod
    def extract_json_from_markdown(text: str) -> str:
        """Extract JSON from markdown code blocks."""
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # If no code block found, try to find JSON directly
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text

    @staticmethod
    def parse_json(json_str: str, debug: bool = False) -> Dict[str, Any]:
        """Parse and validate JSON string."""
        try:
            # Clean the JSON string
            json_str = JSONProcessor.clean_json_string(json_str)
            
            if debug:
                print(f"Cleaned JSON string: {json_str}")
            
            # Parse JSON
            parsed_json = json.loads(json_str)
            
            # Handle case where LLM returns an array instead of single object
            if isinstance(parsed_json, list):
                if len(parsed_json) > 0:
                    parsed_json = parsed_json[0]  # Take the first item
                else:
                    raise ValueError("Empty JSON array returned")
            
            # Handle nested TestCase structure
            if "TestCase" in parsed_json:
                return parsed_json["TestCase"]
            elif "testCase" in parsed_json:
                return parsed_json["testCase"]
            else:
                return parsed_json
                
        except json.JSONDecodeError as e:
            if debug:
                print(f"JSON parsing error: {e}")
                print(f"Error position: {e.pos}")
                print(f"Error line: {e.lineno}")
                print(f"Error column: {e.colno}")
                print(f"Problematic JSON string: {json_str}")
            raise

    @classmethod
    def extract_and_parse_json(cls, text: str, debug: bool = False) -> Dict[str, Any]:
        """Extract JSON from text and parse it."""
        json_str = cls.extract_json_from_markdown(text)
        return cls.parse_json(json_str, debug) 