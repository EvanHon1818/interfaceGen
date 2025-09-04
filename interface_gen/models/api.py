from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class APIParameter(BaseModel):
    """Model for API parameter definition"""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    constraints: Optional[Dict[str, Any]] = None

class APIDefinition(BaseModel):
    """Model for complete API definition"""
    name: str = Field(..., description="Name of the API endpoint")
    description: Optional[str] = Field(None, description="Description of the API's functionality")
    method: str = Field("POST", description="HTTP method (GET, POST, PUT, DELETE, etc.)")
    path: Optional[str] = Field(None, description="API endpoint path")
    input_params: Dict[str, APIParameter] = Field(
        default_factory=dict,
        description="Input parameters definition"
    )
    output_params: Dict[str, APIParameter] = Field(
        default_factory=dict,
        description="Output parameters definition"
    )
    example_cases: Optional[Dict[str, Any]] = Field(
        None,
        description="Example test cases for RAG context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "user_registration",
                "description": "Register a new user in the system",
                "method": "POST",
                "path": "/api/v1/users",
                "input_params": {
                    "username": {
                        "name": "username",
                        "type": "string",
                        "description": "User's username",
                        "required": True,
                        "constraints": {
                            "min_length": 3,
                            "max_length": 50
                        }
                    }
                },
                "output_params": {
                    "user_id": {
                        "name": "user_id",
                        "type": "string",
                        "description": "Unique identifier for the created user"
                    }
                }
            }
        } 