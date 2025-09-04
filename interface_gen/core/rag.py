from typing import List, Dict, Any
import os
from pathlib import Path
import json

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class TestCaseRAG:
    """RAG implementation for test case storage and retrieval"""
    
    def __init__(self, vector_store_path: str = None):
        """Initialize the RAG system"""
        self.vector_store_path = vector_store_path or os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
        # Get OpenAI API configuration
        openai_api_base = os.getenv("OPENAI_API_BASE")
        openai_api_version = os.getenv("OPENAI_API_VERSION")
        openai_api_type = os.getenv("OPENAI_API_TYPE", "open_ai")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        # Configure embeddings based on API type
        if openai_api_type.lower() == "azure":
            # For Azure, use standard OpenAI with custom base URL
            config = {
                "model": azure_deployment or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
                "openai_api_base": openai_api_base,
                "openai_api_version": openai_api_version or "2024-02-15-preview",
            }
            # Remove None values to avoid parameter conflicts
            config = {k: v for k, v in config.items() if v is not None}
            self.embeddings = OpenAIEmbeddings(**config)
        else:
            # Use standard OpenAI Embeddings
            config = {
                "model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            }
            
            # Add custom API configuration if provided
            if openai_api_base:
                config["openai_api_base"] = openai_api_base
            if openai_api_version:
                config["openai_api_version"] = openai_api_version
                
            self.embeddings = OpenAIEmbeddings(**config)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._load_or_create_vector_store()

    def _load_or_create_vector_store(self):
        """Load existing vector store or create a new one"""
        if os.path.exists(self.vector_store_path):
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # Create empty vector store
            self.vector_store = FAISS.from_texts(
                ["placeholder"],
                self.embeddings
            )
            # Save it
            os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
            self.vector_store.save_local(self.vector_store_path)

    def add_test_cases(self, test_cases: List[Dict[str, Any]]):
        """Add test cases to the vector store"""
        documents = []
        for test_case in test_cases:
            # Convert test case to string representation
            test_case_str = json.dumps(test_case, indent=2)
            # Split into chunks if necessary
            chunks = self.text_splitter.split_text(test_case_str)
            # Create documents
            docs = [
                Document(
                    page_content=chunk,
                    metadata={
                        "test_case_id": test_case.get("id"),
                        "type": test_case.get("type"),
                        "api_name": test_case.get("api_name")
                    }
                )
                for chunk in chunks
            ]
            documents.extend(docs)

        # Add to vector store
        self.vector_store.add_documents(documents)
        # Save updated vector store
        self.vector_store.save_local(self.vector_store_path)

    def search_similar_cases(
        self,
        query: str,
        api_name: str = None,
        test_type: str = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar test cases"""
        # Prepare filter based on metadata
        filter_dict = {}
        if api_name:
            filter_dict["api_name"] = api_name
        if test_type:
            filter_dict["type"] = test_type

        # Search vector store
        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter=filter_dict if filter_dict else None
        )

        # Process and return results
        similar_cases = []
        for doc in results:
            try:
                case_data = json.loads(doc.page_content)
                similar_cases.append(case_data)
            except json.JSONDecodeError:
                continue

        return similar_cases

    def get_test_cases_by_type(
        self,
        test_type: str,
        api_name: str = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Get test cases of a specific type"""
        filter_dict = {"type": test_type}
        if api_name:
            filter_dict["api_name"] = api_name

        results = self.vector_store.similarity_search(
            f"Test cases of type {test_type}",
            k=k,
            filter=filter_dict
        )

        test_cases = []
        for doc in results:
            try:
                case_data = json.loads(doc.page_content)
                test_cases.append(case_data)
            except json.JSONDecodeError:
                continue

        return test_cases 