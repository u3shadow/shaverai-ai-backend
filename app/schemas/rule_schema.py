from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

class RuleCreateRequest(BaseModel):
    user_id: str
    name: str
    trigger: dict[str, Any]
    action: dict[str, Any]

class Rule(RuleCreateRequest):
    rule_id: str
    enabled: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class DeviceEvent(BaseModel):
    user_id: str
    event_type: Literal["wifi_connected"]
    params: dict[str, Any]

class RuleEnableRequest(BaseModel):
    user_id: str
    enabled: bool