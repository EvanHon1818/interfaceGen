from pydantic import BaseModel, Field
from typing import Dict, Any
import json
import uuid

class TestCaseJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for test cases"""
    def default(self, obj):
        if isinstance(obj, TestCase):
            return {
                "id": obj.id,
                "name": obj.name,
                "param": obj.param,
                "headers": {"Content-Type": "application/json"},
                "rule": obj.rule
            }
        return super().default(obj)

class TestCase(BaseModel):
    """Model for a test case"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    param: str  # JSON string of input parameters
    headers: Dict[str, str] = Field(default_factory=lambda: {"Content-Type": "application/json"})
    rule: str  # JSON string of assertion rules

    def json(self, **kwargs):
        """Custom JSON serialization"""
        return json.dumps(self, cls=TestCaseJSONEncoder, **kwargs)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Search for Disney in top 10 results",
                "param": "{\"keyword\": \"disney\", \"limit\": 10}",
                "headers": {"Content-Type": "application/json"},
                "rule": """{
                    "rules": [
                        {
                            "matchType": "top",
                            "index": "10",
                            "dataPath": "data",
                            "columns": {
                                "name": "迪士尼",
                                "id": 123
                            }
                        }
                    ]
                }"""
            }
        } 