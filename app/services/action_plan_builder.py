from typing import Any

from app.schemas.tool_schema import ActionItem, ActionPlan
from app.services.tool_call_validator import tool_call_validator


class ActionPlanBuilder:
    android_actions = {
        "set_volume",
        "set_brightness",
        "set_bluetooth",
    }

    def build(self, tool_call: ActionItem | dict[str, Any]) -> ActionPlan:
        item = tool_call_validator.validate(tool_call)

        if item.action in self.android_actions:
            return self._build_android_action_plan(item)

        if item.action == "create_rule":
            return self._build_create_rule_plan(item)

        raise ValueError(f"Unsupported action: {item.action}")

    def _build_android_action_plan(self, item: ActionItem) -> ActionPlan:
        return ActionPlan(
            intent="device_control",
            need_android_execute=True,
            actions=[item],
            message="请在 Android 端执行设备控制动作",
        )

    def _build_create_rule_plan(self, item: ActionItem) -> ActionPlan:
        return ActionPlan(
            intent="rule_create",
            need_android_execute=False,
            actions=[item],
            message="规则已通过校验，后续由 RuleEngine 保存",
        )


action_plan_builder = ActionPlanBuilder()
