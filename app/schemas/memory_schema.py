from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    memory_id: str = Field(default_factory=lambda: f"mem_{uuid4().hex}")
    user_id: str
    type: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
