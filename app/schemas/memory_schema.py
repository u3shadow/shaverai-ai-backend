from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    memory_id: str = Field(default_factory=lambda: f"mem_{uuid4().hex}")
    user_id: str
    type: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class MemorySearchRequest(BaseModel):
    user_id: str
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class MemorySearchResult(MemoryItem):
    score: float


class MemorySearchResponse(BaseModel):
    memories: list[MemorySearchResult] = Field(default_factory=list)


class MemoryDeleteResponse(BaseModel):
    deleted: bool
    memory_id: str