from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


IntentType = Literal[
    "KNOWLEDGE_QUERY",
    "DEVICE_CONTROL",
    "RULE_CREATE",
    "UNKNOWN",
]

AgentMode = Literal["DIRECT", "REACT", "PLAN_ACT"]
TaskComplexity = Literal["SIMPLE", "MULTI_STEP"]
ExecutionTarget = Literal["backend", "android"]
PlanStatus = Literal[
    "draft",
    "validated",
    "awaiting_confirmation",
    "approved",
    "completed",
    "failed",
]


def _validate_step_dependencies(steps: list[Any]) -> None:
    """检查步骤 ID、依赖是否有效，以及依赖关系中是否有环。"""
    steps_by_id = {step.step_id: step for step in steps}
    if len(steps_by_id) != len(steps):
        raise ValueError("plan 中的 step_id 不能重复")

    for step in steps:
        if len(step.depends_on) != len(set(step.depends_on)):
            raise ValueError(f"{step.step_id} 中存在重复依赖")
        if step.step_id in step.depends_on:
            raise ValueError(f"{step.step_id} 不能依赖自己")
        for dependency_id in step.depends_on:
            if dependency_id not in steps_by_id:
                raise ValueError(
                    f"{step.step_id} 依赖了不存在的步骤：{dependency_id}"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> None:
        if step_id in visiting:
            raise ValueError("plan 步骤之间存在循环依赖")
        if step_id in visited:
            return

        visiting.add(step_id)
        for dependency_id in steps_by_id[step_id].depends_on:
            visit(dependency_id)
        visiting.remove(step_id)
        visited.add(step_id)

    for step_id in steps_by_id:
        visit(step_id)


class StrategyDecision(BaseModel):
    """模型给出的意图和策略建议；最终策略仍需由后端校验。"""

    model_config = ConfigDict(extra="forbid")

    intent: IntentType
    complexity: TaskComplexity
    suggested_mode: AgentMode
    reason: str = Field(min_length=1, max_length=200)


class PlanStepDraft(BaseModel):
    """模型提出的步骤草案，不包含执行目标或确认权限。"""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    tool_name: str = Field(pattern=r"^[a-zA-Z0-9_.-]+$")
    arguments: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class AgentPlanDraft(BaseModel):
    """模型生成的多步骤草案，校验通过前不得执行。"""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    steps: list[PlanStepDraft] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def validate_dependencies(self) -> "AgentPlanDraft":
        _validate_step_dependencies(self.steps)
        return self


class PlanStep(BaseModel):
    """后端校验后的步骤；权限相关字段由 SkillRegistry 决定。"""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    tool_name: str = Field(pattern=r"^[a-zA-Z0-9_.-]+$")
    arguments: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    execution_target: ExecutionTarget
    requires_confirmation: bool = False


class AgentPlan(BaseModel):
    """经过工具白名单、参数和依赖检查后的计划。"""

    model_config = ConfigDict(extra="forbid")

    plan_id: str | None = None
    title: str = Field(min_length=1, max_length=120)
    steps: list[PlanStep] = Field(min_length=1, max_length=8)
    status: PlanStatus = "draft"

    @model_validator(mode="after")
    def validate_dependencies(self) -> "AgentPlan":
        _validate_step_dependencies(self.steps)
        return self

    @computed_field
    @property
    def requires_confirmation(self) -> bool:
        """计划中任一步骤需要确认，则整个计划都需要确认。"""
        return any(step.requires_confirmation for step in self.steps)
