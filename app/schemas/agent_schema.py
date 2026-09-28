from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.tool_schema import ActionPlan


class DeviceContext(BaseModel):
    wifi: str | None = None
    battery: int | None = None
    bluetooth_enabled: bool | None = None
    screen_brightness: int | None = None
    volume: int | None = None


class ChatRequest(BaseModel):
    user_id: str
    message: str
    device_context: DeviceContext | None = None


class ChatResponse(BaseModel):
    # 面向用户的文字回复
    answer: str
    intent: str = "unknown"
    need_android_execute: bool = False

    # 响应类型：普通回答、设备计划、规则结果、澄清或错误
    type: Literal[
        "answer",
        "action_plan",
        "rule_result",
        "clarification",
        "confirmation_required",
        "error",
    ] = "answer"

    # RAG 来源
    sources: list[dict[str, Any]] = Field(default_factory=list)

    # 设备控制等场景生成的结构化计划
    action_plan: ActionPlan | None = None

    # RuleEngine 创建规则后的结果
    rule_result: dict[str, Any] | None = None

    # 错误信息和 Graph 执行轨迹
    errors: list[str] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
