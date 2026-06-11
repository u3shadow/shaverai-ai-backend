from typing import Any

from app.schemas.tool_schema import ActionItem


class ToolCallValidator:
    supported_actions = {
        "set_volume",
        "set_brightness",
        "set_bluetooth",
        "create_rule",
    }

    def validate(self, action_item: ActionItem | dict[str, Any]) -> ActionItem:
        item = self._to_action_item(action_item)

        if item.action not in self.supported_actions:
            raise ValueError(f"Unsupported action: {item.action}")

        if item.action == "set_volume":
            self._validate_set_volume(item.params)
        elif item.action == "set_brightness":
            self._validate_set_brightness(item.params)
        elif item.action == "set_bluetooth":
            self._validate_set_bluetooth(item.params)
        elif item.action == "create_rule":
            self._validate_create_rule(item.params)

        return item

    def validate_many(self, action_items: list[ActionItem | dict[str, Any]]) -> list[ActionItem]:
        return [self.validate(item) for item in action_items]

    def _to_action_item(self, action_item: ActionItem | dict[str, Any]) -> ActionItem:
        if isinstance(action_item, ActionItem):
            return action_item

        return ActionItem(**action_item)

    def _validate_set_volume(self, params: dict[str, Any]) -> None:
        if "level" not in params:
            raise ValueError("set_volume requires params.level")

        level = params["level"]
        if not isinstance(level, int):
            raise ValueError("set_volume params.level must be int")

        if level < 0 or level > 15:
            raise ValueError("set_volume.level must be between 0 and 15")

    def _validate_set_brightness(self, params: dict[str, Any]) -> None:
        if "value" not in params:
            raise ValueError("set_brightness requires params.value")

        value = params["value"]
        if not isinstance(value, int):
            raise ValueError("set_brightness params.value must be int")

        if value < 0 or value > 100:
            raise ValueError("set_brightness params.value must be between 0 and 100")

    def _validate_set_bluetooth(self, params: dict[str, Any]) -> None:
        if "enabled" not in params:
            raise ValueError("set_bluetooth requires params.enabled")

        enabled = params["enabled"]
        if not isinstance(enabled, bool):
            raise ValueError("set_bluetooth params.enabled must be bool")

    def _validate_create_rule(self, params: dict[str, Any]) -> None:
        if "trigger" not in params:
            raise ValueError("create_rule requires params.trigger")

        if "action" not in params:
            raise ValueError("create_rule requires params.action")

        trigger = params["trigger"]
        action = params["action"]

        if not isinstance(trigger, dict):
            raise ValueError("create_rule params.trigger must be object")

        if not isinstance(action, dict):
            raise ValueError("create_rule params.action must be object")

        if "type" not in trigger:
            raise ValueError("create_rule params.trigger.type is required")

        if "type" not in action:
            raise ValueError("create_rule params.action.type is required")

        nested_action = {
            "action": action["type"],
            "params": action.get("params", {}),
        }
        self.validate(nested_action)


tool_call_validator = ToolCallValidator()
