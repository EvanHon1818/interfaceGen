import json
import sys
import logging
from pathlib import Path
import typer
from typing import List, Any, Dict

from .models.api import APIDefinition
from .core.generator import TestCaseGenerator
from .core.rag import TestCaseRAG
from .utils.logger import setup_logger

app = typer.Typer()
logger = setup_logger(__name__)

def load_api_definition(file_path: str) -> APIDefinition:
    """Load API definition from a JSON file"""
    logger.info(f"Loading API definition from {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
    logger.debug(f"Loaded API definition: {json.dumps(data, indent=2)}")
    return APIDefinition(**data)

def load_example_test_cases(file_path: str) -> List[Dict[str, Any]]:
    """Load example test cases from an API definition file"""
    logger.info(f"Loading example test cases from {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    test_cases = []
    if "example_cases" in data:
        for case_name, case_data in data["example_cases"].items():
            # Create test case with metadata
            test_case = {
                "id": f"example_{case_name}",
                "name": case_name,
                "api_name": data["name"],
                "type": case_name.split("_")[0],  # Extract type from case name
                "param": json.dumps(case_data["input"]),
                "headers": {"Content-Type": "application/json"},
                "rule": json.dumps({
                    "rules": [
                        {
                            "matchType": "equal",
                            "dataPath": "result",
                            "columns": {
                                "result": case_data["output"]["result"]
                            }
                        }
                    ]
                })
            }
            test_cases.append(test_case)
            logger.debug(f"Added example test case: {json.dumps(test_case, indent=2)}")
    
    return test_cases

def initialize_rag_with_examples():
    """Initialize RAG system with example test cases"""
    logger.info("Initializing RAG system with example test cases")
    rag = TestCaseRAG()
    
    # Load example test cases from all API definition files in examples directory
    examples_dir = Path("examples")
    if examples_dir.exists():
        for file_path in examples_dir.glob("*.json"):
            try:
                test_cases = load_example_test_cases(str(file_path))
                if test_cases:
                    logger.info(f"Adding {len(test_cases)} test cases from {file_path}")
                    rag.add_test_cases(test_cases)
            except Exception as e:
                logger.warning(f"Failed to load examples from {file_path}: {str(e)}")
    
    return rag

def save_test_cases(test_cases: list, output_file: str):
    """Save generated test cases to a file"""
    logger.info(f"Saving {len(test_cases)} test cases to {output_file}")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert test cases to dictionaries
    test_cases_data = []
    for i, tc in enumerate(test_cases):
        logger.debug(f"Processing test case {i+1}:")
        logger.debug(f"  Original test case: {tc}")
        logger.debug(f"  Headers type: {type(tc.headers)}")
        logger.debug(f"  Headers value: {tc.headers}")
        
        try:
            data = tc.dict()
            logger.debug(f"  Converted to dict: {json.dumps(data, indent=2)}")
            test_cases_data.append(data)
        except Exception as e:
            logger.error(f"  Error converting test case to dict: {str(e)}")
            raise
    
    try:
        logger.debug(f"Final data to save: {json.dumps(test_cases_data, indent=2)}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_cases_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved test cases to {output_file}")
    except Exception as e:
        logger.error(f"Error saving test cases: {str(e)}")
        raise

@app.command()
def main(
    api_definition: str = typer.Argument(..., help="Path to JSON file containing API definition"),
    output: str = typer.Option("test_cases.json", "-o", help="Output file for generated test cases"),
    num_cases: int = typer.Option(5, "-n", help="Number of test cases to generate per type"),
    test_types: List[str] = typer.Option(
        ["functional", "performance", "boundary", "exception"],
        "--test-types",
        "-t",
        help="Types of test cases to generate"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Generate test cases for API endpoints with custom assertion rules"""
    try:
        # Set log level
        if debug:
            logger.setLevel(logging.DEBUG)
        
        logger.info("Starting test case generation")
        logger.debug(f"Parameters: api_definition={api_definition}, output={output}, "
                    f"num_cases={num_cases}, test_types={test_types}")
        
        # Initialize RAG with examples
        initialize_rag_with_examples()
        
        # Load API definition
        api_def = load_api_definition(api_definition)
        
        # Initialize generator
        logger.info("Initializing test case generator")
        generator = TestCaseGenerator()
        
        # Generate test cases
        logger.info("Generating test cases")
        test_cases = generator.generate_test_cases(
            api_definition=api_def,
            test_types=test_types,
            num_cases=num_cases
        )
        
        # Save test cases
        save_test_cases(test_cases, output)
        logger.info(f"Generated {len(test_cases)} test cases and saved to {output}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 