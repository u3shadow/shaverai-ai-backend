from typing import Any

from app.schemas.tool_schema import ActionItem, ActionPlan
from app.services.tool_call_validator import tool_call_validator
from app.services.skill_registry import skill_registry

class ActionPlanBuilder:
    def build(self, tool_call: ActionItem | dict[str, Any]) -> ActionPlan:
        # 先做已有的动作和参数安全校验
        item = tool_call_validator.validate(tool_call)

        # 再从注册表读取这个动作属于哪个 Skill、交给谁处理
        registered = skill_registry.find_action(item.action)
        if registered is None:
            raise ValueError(f"No Skill registered for action: {item.action}")

        skill, action_definition = registered

        # 保留项目目前已有的 intent 命名
        intent = {
            "device_control": "device_control",
            "rule_management": "rule_create",
        }.get(skill.skill_id, skill.skill_id)

        if action_definition.execution_target == "android":
            message = "动作已通过校验，请由 Android 客户端执行。"
        else:
            message = "动作已通过校验；此接口只生成计划，不会执行或保存。"

        return ActionPlan(
            intent=intent,
            need_android_execute=(
                action_definition.execution_target == "android"
            ),
            actions=[item],
            message=message,
            skill_id=skill.skill_id,
            execution_target=action_definition.execution_target,
            requires_confirmation=skill.requires_confirmation,
        )

action_plan_builder = ActionPlanBuilder()
