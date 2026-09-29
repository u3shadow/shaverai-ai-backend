from typing import Any

from app.core.service_container import memory_service, rag_service
from app.services.action_plan_builder import action_plan_builder
from app.services.skill_registry import skill_registry


class ToolDispatcher:
    MAX_TOP_K = 5
    MAX_QUERY_LENGTH = 500
    MAX_MEMORY_CONTENT_LENGTH = 500

    def tool_specs(self) -> list[dict[str, Any]]:
        """给模型看的工具描述。这里只描述允许调用的工具。"""
        return [
            {
                "name": "search_knowledge",
                "description": "查询 ShaverAI 项目知识库。",
                "arguments": {
                    "query": "必填，知识库查询问题",
                    "top_k": "可选，1 到 5，默认 5",
                },
            },
            {
                "name": "search_memory",
                "description": "查询当前用户自己的记忆。",
                "arguments": {
                    "query": "必填，记忆查询内容",
                    "top_k": "可选，1 到 5，默认 5",
                },
            },
            {
                "name": "prepare_device_action",
                "description": "生成并校验 Android 动作计划，不执行设备操作。",
                "arguments": {
                    "action": "必填，已注册的设备动作名",
                    "params": "必填，动作参数对象",
                },
            },
        ]

    def dispatch(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        user_id: str,
    ) -> dict[str, Any]:
        if not isinstance(arguments, dict):
            raise ValueError("工具 arguments 必须是对象")

        if tool_name == "search_knowledge":
            self._check_keys(arguments, {"query"}, {"top_k"})
            query = self._validate_query(arguments["query"])
            top_k = self._validate_top_k(arguments.get("top_k", 5))

            result = rag_service.query(query=query, top_k=top_k)
            return {
                "answer": result.get("answer", ""),
                "sources": result.get("sources", [])[:top_k],
                "retrieved_count": result.get("retrieved_count", 0),
            }

        if tool_name == "search_memory":
            self._check_keys(arguments, {"query"}, {"top_k"})
            query = self._validate_query(arguments["query"])
            top_k = self._validate_top_k(arguments.get("top_k", 5))

            # user_id 由后端传入，模型不能指定或覆盖用户范围。
            memories = memory_service.search_memory(
                user_id=user_id,
                query=query,
                top_k=top_k,
            )
            return {
                "memories": [
                    {
                        "memory_id": item.get("memory_id"),
                        "type": item.get("type"),
                        "content": str(item.get("content", ""))[
                            : self.MAX_MEMORY_CONTENT_LENGTH
                        ],
                        "metadata": item.get("metadata", {}),
                    }
                    for item in memories[:top_k]
                ]
            }

        if tool_name == "prepare_device_action":
            self._check_keys(arguments, {"action", "params"}, set())
            action = arguments["action"]
            params = arguments["params"]

            if not isinstance(action, str) or not action:
                raise ValueError("action 必须是非空字符串")
            if not isinstance(params, dict):
                raise ValueError("params 必须是对象")

            registered = skill_registry.find_action(action)
            if registered is None or registered[0].skill_id != "device_control":
                raise ValueError("只允许生成已注册的设备控制动作计划")

            # ActionPlanBuilder 会再次执行已有的 action 和参数校验。
            plan = action_plan_builder.build(
                {"action": action, "params": params}
            )
            return {"action_plan": plan.model_dump(mode="json")}

        raise ValueError(f"不允许调用此工具：{tool_name}")

    @staticmethod
    def _check_keys(
        arguments: dict[str, Any],
        required: set[str],
        optional: set[str],
    ) -> None:
        keys = set(arguments)
        missing = required - keys
        unexpected = keys - required - optional

        if missing:
            raise ValueError(f"缺少工具参数：{', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(f"不支持的工具参数：{', '.join(sorted(unexpected))}")

    def _validate_query(self, query: Any) -> str:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query 必须是非空字符串")
        if len(query) > self.MAX_QUERY_LENGTH:
            raise ValueError("query 过长")
        return query.strip()

    def _validate_top_k(self, top_k: Any) -> int:
        # bool 是 int 的子类，所以单独排除。
        if isinstance(top_k, bool) or not isinstance(top_k, int):
            raise ValueError("top_k 必须是整数")
        if not 1 <= top_k <= self.MAX_TOP_K:
            raise ValueError(f"top_k 必须在 1 到 {self.MAX_TOP_K} 之间")
        return top_k


tool_dispatcher = ToolDispatcher()