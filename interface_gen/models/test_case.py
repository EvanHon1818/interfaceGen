from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class TestCaseType(str, Enum):
    """Enumeration of test case types"""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    BOUNDARY = "boundary"
    EXCEPTION = "exception"

class TestCaseStatus(str, Enum):
    """Enumeration of test case statuses"""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"

class TestCase(BaseModel):
    """Model for a single test case"""
    id: str = Field(..., description="Unique identifier for the test case")
    name: str = Field(..., description="Name of the test case")
    description: str = Field(..., description="Description of what the test case verifies")
    type: TestCaseType = Field(..., description="Type of test case")
    input_data: Dict[str, Any] = Field(..., description="Input data for the test case")
    expected_output: Dict[str, Any] = Field(..., description="Expected output data")
    preconditions: Optional[List[str]] = Field(default_factory=list, description="Required preconditions")
    postconditions: Optional[List[str]] = Field(default_factory=list, description="Expected postconditions")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the test case")
    
    # Performance specific fields
    performance_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Performance metrics to measure (e.g., response_time, throughput)"
    )
    
    # Exception specific fields
    expected_exception: Optional[str] = Field(None, description="Expected exception type if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "test_001",
                "name": "Valid user registration",
                "description": "Test user registration with valid input data",
                "type": "functional",
                "input_data": {
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "SecurePass123!"
                },
                "expected_output": {
                    "status": "success",
                    "user_id": "uuid-example"
                },
                "preconditions": ["Database is accessible", "Email is not already registered"],
                "postconditions": ["User is created in database", "Welcome email is sent"],
                "tags": ["registration", "happy-path", "user-management"]
            }
        }

class TestSuite(BaseModel):
    """Model for a collection of test cases"""
    api_definition: str = Field(..., description="Reference to the API definition")
    test_cases: List[TestCase] = Field(default_factory=list, description="List of test cases")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata") 