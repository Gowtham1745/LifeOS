from typing import Any
from pydantic import BaseModel, Field


class StatePayload(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


class StateResponse(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)
