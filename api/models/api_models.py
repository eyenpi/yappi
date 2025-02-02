from pydantic import BaseModel, Field
from typing import Dict


class APIRegistration(BaseModel):
    name: str = Field(..., description="Name of the API")
    openapi_spec: Dict = Field(..., description="OpenAPI specification")
