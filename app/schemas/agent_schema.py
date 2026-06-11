from typing import Any

from pydantic import BaseModel, Field


class DeviceContext(BaseModel):
    wifi: str | None = None
    battery: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    user_id: str
    message: str
    device_context: DeviceContext | None = None


class ChatResponse(BaseModel):
    answer: str
    intent: str = "unknown"
    need_android_execute: bool = False
