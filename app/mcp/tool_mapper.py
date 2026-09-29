import json
from copy import deepcopy
from typing import Any

from app.services.skill_registry import skill_registry
from app.services.tool_dispatcher import tool_dispatcher


class MCPToolMapper:
    """Map ShaverAI's allowlisted tools to MCP-compatible definitions.

    This is a mapping/dispatch adapter, not a complete MCP server. It does
    not implement MCP transport, initialization, or session handling.
    """

    def __init__(self) -> None:
        self._dispatcher = tool_dispatcher
        self._skill_registry = skill_registry

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the tool definitions an MCP ``tools/list`` can expose."""
        specs = {
            item["name"]: item
            for item in self._dispatcher.tool_specs()
        }

        tools: list[dict[str, Any]] = []
        for name in ("search_knowledge", "search_memory"):
            spec = specs.get(name)
            if spec is None:
                raise ValueError(f"ToolDispatcher has no registered tool: {name}")
            tools.append(
                {
                    "name": name,
                    "description": spec["description"],
                    "inputSchema": self._query_input_schema(),
                }
            )

        device_spec = specs.get("prepare_device_action")
        if device_spec is None:
            raise ValueError(
                "ToolDispatcher has no registered tool: prepare_device_action"
            )
        tools.append(
            {
                "name": "prepare_device_action",
                "description": device_spec["description"],
                "inputSchema": self._device_action_input_schema(),
            }
        )
        return tools

    def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        user_id: str,
    ) -> dict[str, Any]:
        """Validate the exposed tool name, then delegate to ToolDispatcher.

        ``user_id`` is injected by the backend and is never a model argument.
        """
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be provided by the backend")

        allowed_names = {tool["name"] for tool in self.list_tools()}
        if name not in allowed_names:
            raise ValueError(f"Tool is not allowed: {name}")
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")

        result = self._dispatcher.dispatch(
            name,
            arguments,
            user_id=user_id,
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False),
                }
            ],
            "structuredContent": result,
        }

    @staticmethod
    def _query_input_schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question or content to search for.",
                    "minLength": 1,
                    "maxLength": 500,
                },
                "top_k": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5).",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 5,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        }

    def _device_action_input_schema(self) -> dict[str, Any]:
        """Build action-specific schemas from the registered device Skill."""
        skill = self._skill_registry.get_skill("device_control")
        if skill is None:
            raise ValueError("SkillRegistry has no device_control skill")

        variants: list[dict[str, Any]] = []
        for action in skill.actions:
            parameters = deepcopy(action.parameters)
            variants.append(
                {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "const": action.name,
                            "description": action.description,
                        },
                        "params": {
                            "type": "object",
                            "properties": parameters,
                            "required": list(parameters),
                            "additionalProperties": False,
                        },
                    },
                    "required": ["action", "params"],
                    "additionalProperties": False,
                }
            )

        if not variants:
            raise ValueError("device_control has no registered actions")

        return {
            "type": "object",
            "description": (
                "Creates and validates an Android action plan; "
                "it does not execute the device action."
            ),
            "oneOf": variants,
        }


mcp_tool_mapper = MCPToolMapper()
