from uuid import uuid4

from app.repositories.rule_repository import RuleRepository
from app.schemas.rule_schema import DeviceEvent, Rule, RuleCreateRequest
from app.schemas.tool_schema import ActionItem, ActionPlan
from app.services.tool_call_validator import tool_call_validator


class RuleEngine:
    # 第一版规则只允许触发 Android 设备动作
    RULE_ACTIONS = {
        "set_volume",
        "set_brightness",
        "set_bluetooth",
    }

    def __init__(
        self,
        repository: RuleRepository | None = None,
    ) -> None:
        self.repository = repository or RuleRepository()

    def create_rule(self, request: RuleCreateRequest) -> Rule:
        """校验并保存规则。"""
        normalized = self.validate_rule(request)
        rule = Rule(
            rule_id=f"rule_{uuid4().hex}",
            user_id=normalized.user_id,
            name=normalized.name,
            trigger=normalized.trigger,
            action=normalized.action,
        )
        return self.repository.create(rule)

    def validate_rule(self, request: RuleCreateRequest) -> RuleCreateRequest:
        """Validate and normalize a rule draft without writing to storage."""
        if not request.user_id.strip():
            raise ValueError("user_id 不能为空")

        if not request.name.strip():
            raise ValueError("规则名称不能为空")

        # Day 5 先只实现 WiFi 连接触发
        trigger_type = request.trigger.get("type")
        if trigger_type != "wifi_connected":
            raise ValueError(
                f"暂不支持的触发类型: {trigger_type}"
            )

        trigger_params = request.trigger.get("params", {})
        if not isinstance(trigger_params, dict):
            raise ValueError("wifi_connected 触发器 params 必须是对象")
        ssid = trigger_params.get("ssid")

        if not isinstance(ssid, str) or not ssid.strip():
            raise ValueError(
                "wifi_connected 触发器必须提供非空 ssid"
            )

        # 规则动作采用 {type, params} 格式，
        # 转成 ToolCallValidator 使用的 {action, params} 格式校验。
        action_type = request.action.get("type")
        action_params = request.action.get("params", {})

        if not isinstance(action_type, str) or action_type not in self.RULE_ACTIONS:
            raise ValueError(
                f"规则暂不支持此动作: {action_type}"
            )
        if not isinstance(action_params, dict):
            raise ValueError("规则动作 params 必须是对象")

        validated_action = tool_call_validator.validate(
            {
                "action": action_type,
                "params": action_params,
            }
        )

        # 返回规范化草案，供确认前展示，也供最终保存时复用。
        normalized_action = {
            "type": validated_action.action,
            "params": validated_action.params,
        }

        return RuleCreateRequest(
            user_id=request.user_id,
            name=request.name,
            trigger={
                "type": trigger_type,
                "params": {"ssid": ssid},
            },
            action=normalized_action,
        )

    def list_rules(self, user_id: str) -> list[Rule]:
        """列出指定用户的规则。"""
        if not user_id.strip():
            raise ValueError("user_id 不能为空")

        return self.repository.list_by_user(user_id)

    def set_enabled(
        self,
        rule_id: str,
        user_id: str,
        enabled: bool,
    ) -> Rule | None:
        """启用或禁用指定用户的规则。"""
        return self.repository.update_enabled(
            rule_id=rule_id,
            user_id=user_id,
            enabled=enabled,
        )

    def delete_rule(self, rule_id: str, user_id: str) -> bool:
        """删除指定用户拥有的规则。"""
        return self.repository.delete(
            rule_id=rule_id,
            user_id=user_id,
        )

    def match_event(self, event: DeviceEvent) -> dict:
        """匹配设备事件，并为命中的规则构造 ActionPlan。"""

        if event.event_type == "wifi_connected":
            ssid = event.params.get("ssid")
            if not isinstance(ssid, str) or not ssid.strip():
                raise ValueError(
                    "wifi_connected 事件必须提供非空 ssid"
                )

        user_rules = self.repository.list_by_user(event.user_id)

        matched_rules: list[Rule] = []
        actions: list[ActionItem] = []

        for rule in user_rules:
            if not rule.enabled:
                continue

            rule_trigger = rule.trigger
            if rule_trigger.get("type") != event.event_type:
                continue

            rule_params = rule_trigger.get("params", {})

            if event.event_type == "wifi_connected":
                if rule_params.get("ssid") != event.params.get("ssid"):
                    continue

            # 匹配时再次校验动作，再把 type 转成 ActionItem 的 action 字段
            action = tool_call_validator.validate(
                {
                    "action": rule.action.get("type"),
                    "params": rule.action.get("params", {}),
                }
            )

            matched_rules.append(rule)
            actions.append(action)

        action_plan = None

        if actions:
            action_plan = ActionPlan(
                intent="rule_trigger",
                need_android_execute=True,
                actions=actions,
                message="规则已匹配，请由 Android 端执行动作",
                skill_id="device_control",
                execution_target="android",
                requires_confirmation=False,
            )

        return {
            "matched": bool(matched_rules),
            "matched_rules": [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                }
                for rule in matched_rules
            ],
            "action_plan": (
                action_plan.model_dump()
                if action_plan is not None
                else None
            ),
        }
