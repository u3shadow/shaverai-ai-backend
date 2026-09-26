from typing import Any, Literal

from pydantic import BaseModel, Field


class SkillAction(BaseModel):
    name: str
    description: str
    execution_target: Literal["android", "backend"]
    parameters: dict[str, Any] = Field(default_factory=dict)


class SkillDefinition(BaseModel):
    skill_id: str
    name: str
    description: str
    requires_confirmation: bool = False
    actions: list[SkillAction] = Field(default_factory=list)