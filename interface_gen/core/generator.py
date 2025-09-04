import os
import uuid
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.chains import LLMChain
from langchain_community.callbacks.manager import get_openai_callback
from langchain.prompts import PromptTemplate

from ..models.api import APIDefinition
from ..models.test_case import TestCase, TestCaseType
from .rag import TestCaseRAG
from .prompts import TestCasePrompts

class TestCaseGenerator:
    """Core class for generating test cases"""

    def __init__(self):
        """Initialize the test case generator"""
        self.rag = TestCaseRAG()
        # Get OpenAI API configuration
        openai_api_base = os.getenv("OPENAI_API_BASE")
        openai_api_version = os.getenv("OPENAI_API_VERSION")
        openai_api_type = os.getenv("OPENAI_API_TYPE", "open_ai")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        # Configure ChatOpenAI based on API type
        if openai_api_type.lower() == "azure":
            # Use Azure ChatOpenAI
            config = {
                "deployment_name": azure_deployment or os.getenv("MODEL_NAME", "gpt-4"),
                "azure_endpoint": openai_api_base,
                "api_version": openai_api_version or "2024-02-15-preview",
                "temperature": 0.7
            }
            self.llm = AzureChatOpenAI(**config)
        else:
            # Use standard ChatOpenAI
            config = {
                "model_name": os.getenv("MODEL_NAME", "gpt-4-turbo-preview"),
                "temperature": 0.7
            }
            
            # Add custom API configuration if provided
            if openai_api_base:
                config["openai_api_base"] = openai_api_base
            if openai_api_version:
                config["openai_api_version"] = openai_api_version

            self.llm = ChatOpenAI(**config)

    def generate(
        self,
        api_definition: APIDefinition,
        test_types: Optional[List[str]] = None,
        num_cases_per_type: int = 3
    ) -> List[TestCase]:
        """Generate test cases for the given API definition"""
        if test_types is None:
            test_types = [t.value for t in TestCaseType]

        all_test_cases = []
        
        for test_type in test_types:
            # Get temperature based on test type
            temperature = float(os.getenv(f"TEMPERATURE_{test_type.upper()}", 0.7))
            self.llm.temperature = temperature

            # Get similar cases from RAG
            similar_cases = self.rag.get_test_cases_by_type(
                test_type=test_type,
                api_name=api_definition.name,
                k=3
            )

            # Create prompt
            prompt = TestCasePrompts.get_prompt(test_type)
            
            # Format API definition and similar cases
            formatted_api = TestCasePrompts.format_api_definition(api_definition.dict())
            formatted_cases = TestCasePrompts.format_similar_cases(similar_cases)

            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)

            # Generate multiple test cases
            for _ in range(num_cases_per_type):
                with get_openai_callback() as cb:
                    # Generate test case
                    result = chain.run(
                        api_definition=formatted_api,
                        similar_cases=formatted_cases
                    )

                    try:
                        # Parse the result and create TestCase object
                        test_case_dict = eval(result)  # Safe since we control the input
                        test_case_dict["id"] = str(uuid.uuid4())
                        test_case = TestCase(**test_case_dict)
                        all_test_cases.append(test_case)

                        # Add to RAG for future reference
                        self.rag.add_test_cases([test_case_dict])

                    except Exception as e:
                        print(f"Error generating test case: {e}")
                        continue

        return all_test_cases

    def generate_specific_test_case(
        self,
        api_definition: APIDefinition,
        test_type: str,
        specific_scenario: str
    ) -> Optional[TestCase]:
        """Generate a specific test case based on a scenario"""
        # Adjust temperature based on test type
        temperature = float(os.getenv(f"TEMPERATURE_{test_type.upper()}", 0.7))
        self.llm.temperature = temperature

        # Get similar cases that might be relevant
        similar_cases = self.rag.search_similar_cases(
            query=specific_scenario,
            api_name=api_definition.name,
            test_type=test_type,
            k=3
        )

        # Create and format prompt
        prompt = TestCasePrompts.get_prompt(test_type)
        formatted_api = TestCasePrompts.format_api_definition(api_definition.dict())
        formatted_cases = TestCasePrompts.format_similar_cases(similar_cases)

        # Add specific scenario to prompt
        modified_prompt = PromptTemplate(
            input_variables=["api_definition", "similar_cases", "specific_scenario"],
            template=prompt.template + "\n\nSpecific Scenario to Test:\n{specific_scenario}"
        )

        # Create chain and generate test case
        chain = LLMChain(llm=self.llm, prompt=modified_prompt)

        try:
            with get_openai_callback() as cb:
                result = chain.run(
                    api_definition=formatted_api,
                    similar_cases=formatted_cases,
                    specific_scenario=specific_scenario
                )

                # Parse and create TestCase object
                test_case_dict = eval(result)
                test_case_dict["id"] = str(uuid.uuid4())
                test_case = TestCase(**test_case_dict)

                # Add to RAG for future reference
                self.rag.add_test_cases([test_case_dict])

                return test_case

        except Exception as e:
            print(f"Error generating specific test case: {e}")
            return None 