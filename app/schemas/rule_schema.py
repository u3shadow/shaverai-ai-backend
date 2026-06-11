from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Rule(BaseModel):
    rule_id: str
    user_id: str
    trigger: dict[str, Any]
    action: dict[str, Any]
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
