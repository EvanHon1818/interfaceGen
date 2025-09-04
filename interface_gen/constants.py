"""Constants used throughout the interface test case generator."""

from enum import Enum

class TestCaseType(str, Enum):
    """Test case types."""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    BOUNDARY = "boundary"
    EXCEPTION = "exception"

class TestCaseStatus(str, Enum):
    """Test case statuses."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"

# Default configuration values
DEFAULT_VECTOR_STORE_PATH = "./data/vector_store"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TEMPERATURE = 0.7

# LLM configuration
DEFAULT_MODEL_NAME = "gpt-4-turbo-preview"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_API_VERSION = "2024-02-15-preview"

# File patterns
JSON_FILE_PATTERN = "*.json"
MARKDOWN_FILE_PATTERN = "*.md"

# System messages
SYSTEM_MESSAGE = """You are a test case generator that ALWAYS responds with valid JSON objects.
Your responses should NEVER include markdown formatting or explanatory text.
Always use double quotes for strings and property names."""

# Error messages
ERR_INVALID_TEST_TYPE = "Invalid test type: {}"
ERR_INVALID_JSON = "Invalid JSON format: {}"
ERR_MISSING_FIELD = "Missing required field: {}"
ERR_INVALID_CONFIG = "Invalid configuration: {}"
ERR_LLM_ERROR = "LLM service error: {}"
ERR_RAG_ERROR = "RAG system error: {}" 