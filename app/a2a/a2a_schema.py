from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


A2ATaskStatus = Literal[
    "completed",
    "needs_clarification",
    "failed",
]


class A2ATaskRequest(BaseModel):
    """Task request sent by a coordinating Agent to a target Agent."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(
        default_factory=lambda: f"task_{uuid4().hex}",
        min_length=1,
        max_length=80,
    )
    source_agent: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    target_agent: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    task_type: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )
    payload: dict[str, Any] = Field(default_factory=dict)
    # Trusted context is supplied by the backend, not copied from model output.
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class A2ATaskResult(BaseModel):
    """Result returned by the target Agent to the coordinator."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1, max_length=80)
    agent_name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    status: A2ATaskStatus
    data: dict[str, Any] = Field(default_factory=dict)
    message: str = Field(default="", max_length=2000)
    error_code: str | None = Field(default=None, max_length=100)
    errors: list[str] = Field(default_factory=list)
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @model_validator(mode="after")
    def validate_status_fields(self) -> "A2ATaskResult":
        """Ensure the status has the corresponding clarification/error data."""
        if self.status == "needs_clarification" and not self.message.strip():
            raise ValueError(
                "needs_clarification status requires a clarification message"
            )

        if self.status == "failed" and not (self.error_code or self.errors):
            raise ValueError(
                "failed status requires error_code or errors"
            )

        if self.status != "failed" and (
            self.error_code is not None or self.errors
        ):
            raise ValueError(
                "error_code and errors are only allowed for failed status"
            )

        return self
