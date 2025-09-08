"""Configuration management for the interface test case generator."""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    api_base: str = os.getenv("OPENAI_API_BASE", "")
    api_version: str = os.getenv("OPENAI_API_VERSION", "")
    api_type: str = os.getenv("OPENAI_API_TYPE", "open_ai")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    azure_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        if self.api_type.lower() == "azure":
            config = {
                "model_name": self.azure_deployment or self.model_name,
                "openai_api_base": self.api_base,
                "openai_api_version": self.api_version,
                "temperature": 0.7,
                "openai_api_key": self.api_key
            }
        else:
            config = {
                "model_name": self.model_name,
                "temperature": 0.7,
                "openai_api_key": self.api_key
            }
            if self.api_base:
                config["openai_api_base"] = self.api_base
            if self.api_version:
                config["openai_api_version"] = self.api_version
        
        return {k: v for k, v in config.items() if v is not None and v != ""}

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        if self.api_type.lower() == "azure":
            config = {
                "azure_deployment": self.azure_deployment or self.embedding_model,
                "azure_endpoint": self.api_base,
                "api_version": self.api_version or "2024-02-15-preview",
                "openai_api_key": self.api_key
            }
        else:
            config = {
                "model": self.embedding_model,
                "openai_api_key": self.api_key
            }
            if self.api_base:
                config["openai_api_base"] = self.api_base
            if self.api_version:
                config["openai_api_version"] = self.api_version
        
        return {k: v for k, v in config.items() if v is not None and v != ""}

@dataclass
class RAGConfig:
    """RAG system configuration."""
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    chunk_size: int = 1000
    chunk_overlap: int = 200

@dataclass
class TestConfig:
    """Test generation configuration."""
    temperature_functional: float = float(os.getenv("TEMPERATURE_FUNCTIONAL", "0.7"))
    temperature_performance: float = float(os.getenv("TEMPERATURE_PERFORMANCE", "0.7"))
    temperature_boundary: float = float(os.getenv("TEMPERATURE_BOUNDARY", "0.7"))
    temperature_exception: float = float(os.getenv("TEMPERATURE_EXCEPTION", "0.7"))

    def get_temperature(self, test_type: str) -> float:
        """Get temperature for a specific test type."""
        return getattr(self, f"temperature_{test_type.lower()}", 0.7)

class Config:
    """Global configuration singleton."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.openai = OpenAIConfig()
            cls._instance.rag = RAGConfig()
            cls._instance.test = TestConfig()
        return cls._instance

config = Config() 