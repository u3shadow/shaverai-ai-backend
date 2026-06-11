from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    action: str
    params: dict[str, Any] = Field(default_factory=dict)


class ActionItem(BaseModel):
    action: str
    params: dict[str, Any] = Field(default_factory=dict)


class ActionPlan(BaseModel):
    intent: str
    need_android_execute: bool
    actions: list[ActionItem] = Field(default_factory=list)
    message: str
