"""Custom exceptions for the interface test case generator."""

class InterfaceGenError(Exception):
    """Base exception for all interface generator errors."""
    pass

class ConfigurationError(InterfaceGenError):
    """Raised when there is a configuration error."""
    pass

class APIDefinitionError(InterfaceGenError):
    """Raised when there is an error in the API definition."""
    pass

class TestGenerationError(InterfaceGenError):
    """Raised when there is an error generating test cases."""
    pass

class RAGError(InterfaceGenError):
    """Raised when there is an error in the RAG system."""
    pass

class JSONProcessingError(InterfaceGenError):
    """Raised when there is an error processing JSON data."""
    pass

class LLMError(InterfaceGenError):
    """Raised when there is an error with the LLM service."""
    pass

class ValidationError(InterfaceGenError):
    """Raised when there is a validation error."""
    pass 