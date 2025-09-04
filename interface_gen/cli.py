import argparse
import json
import sys
from typing import Dict, Any
from pathlib import Path

from .models.api import APIDefinition
from .core.generator import TestCaseGenerator

def load_api_definition(file_path: str) -> APIDefinition:
    """Load API definition from a JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return APIDefinition(**data)

def save_test_cases(test_cases: list, output_file: str):
    """Save generated test cases to a file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(
            [tc.model_dump() for tc in test_cases],
            f,
            indent=2
        )

def main():
    parser = argparse.ArgumentParser(
        description="Generate test cases for API endpoints"
    )
    parser.add_argument(
        "api_definition",
        help="Path to JSON file containing API definition"
    )
    parser.add_argument(
        "-o", "--output",
        default="test_cases.json",
        help="Output file for generated test cases"
    )
    parser.add_argument(
        "-t", "--test-types",
        nargs="+",
        choices=["functional", "performance", "boundary", "exception"],
        help="Types of test cases to generate"
    )
    parser.add_argument(
        "-n", "--num-cases",
        type=int,
        default=5,
        help="Number of test cases to generate per type (default: 5)"
    )
    parser.add_argument(
        "--scenario",
        help="Generate a specific test case for this scenario"
    )
    parser.add_argument(
        "--scenario-type",
        choices=["functional", "performance", "boundary", "exception"],
        help="Test type for the specific scenario"
    )

    args = parser.parse_args()

    try:
        # Load API definition
        api_def = load_api_definition(args.api_definition)
        
        # Initialize generator
        generator = TestCaseGenerator()

        if args.scenario:
            if not args.scenario_type:
                print("Error: --scenario-type is required when using --scenario")
                sys.exit(1)
            
            # Generate specific test case
            test_case = generator.generate_specific_test_case(
                api_definition=api_def,
                test_type=args.scenario_type,
                specific_scenario=args.scenario
            )
            
            if test_case:
                save_test_cases([test_case], args.output)
                print(f"Generated specific test case and saved to {args.output}")
            else:
                print("Failed to generate specific test case")
                sys.exit(1)
        
        else:
            # Generate multiple test cases
            test_cases = generator.generate(
                api_definition=api_def,
                test_types=args.test_types,
                num_cases_per_type=args.num_cases
            )
            
            save_test_cases(test_cases, args.output)
            print(f"Generated {len(test_cases)} test cases and saved to {args.output}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 