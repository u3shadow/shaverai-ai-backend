from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReactDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["tool_call", "final"]
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    answer: str | None = None

    @model_validator(mode="after")
    def validate_decision(self) -> "ReactDecision":
        if self.status == "tool_call":
            if not self.tool_name:
                raise ValueError("tool_call 必须提供 tool_name")
            if self.answer is not None:
                raise ValueError("tool_call 不能同时提供 answer")

        if self.status == "final":
            if not self.answer or not self.answer.strip():
                raise ValueError("final 必须提供非空 answer")
            if self.tool_name is not None:
                raise ValueError("final 不能同时提供 tool_name")

        return self