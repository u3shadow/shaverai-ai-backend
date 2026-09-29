from typing import Any

from app.a2a.a2a_schema import A2ATaskRequest, A2ATaskResult
from app.services.tool_dispatcher import tool_dispatcher


class KnowledgeAgent:
    """Handle knowledge-base query tasks."""

    agent_name = "knowledge_agent"
    task_type = "knowledge.query"

    def __init__(self, dispatcher: Any | None = None) -> None:
        self._dispatcher = (
            dispatcher if dispatcher is not None else tool_dispatcher
        )

    def handle(self, request: A2ATaskRequest) -> A2ATaskResult:
        if request.target_agent != self.agent_name:
            return self._failure(
                request,
                "WRONG_TARGET",
                f"任务目标不是 {self.agent_name}",
            )

        if request.task_type != self.task_type:
            return self._failure(
                request,
                "UNSUPPORTED_TASK",
                f"不支持的任务类型：{request.task_type}",
            )

        query = request.payload.get("query")
        if not isinstance(query, str) or not query.strip():
            return self._failure(
                request,
                "INVALID_QUERY",
                "payload.query 必须是非空字符串",
            )

        user_id = request.context.get("user_id")
        if not isinstance(user_id, str) or not user_id.strip():
            return self._failure(
                request,
                "MISSING_USER_CONTEXT",
                "请求缺少由后端提供的 user_id",
            )

        arguments: dict[str, Any] = {"query": query.strip()}
        if "top_k" in request.payload:
            arguments["top_k"] = request.payload["top_k"]

        try:
            result = self._dispatcher.dispatch(
                "search_knowledge",
                arguments,
                user_id=user_id,
            )
        except ValueError as exc:
            return self._failure(
                request,
                "INVALID_ARGUMENT",
                str(exc),
            )
        except Exception:
            # Do not expose internal service exception details to callers.
            return self._failure(
                request,
                "KNOWLEDGE_QUERY_FAILED",
                "知识库查询失败",
            )

        return A2ATaskResult(
            task_id=request.task_id,
            agent_name=self.agent_name,
            status="completed",
            data=result,
            message="知识库查询完成",
        )

    def _failure(
        self,
        request: A2ATaskRequest,
        error_code: str,
        message: str,
    ) -> A2ATaskResult:
        return A2ATaskResult(
            task_id=request.task_id,
            agent_name=self.agent_name,
            status="failed",
            error_code=error_code,
            errors=[message],
            message=message,
        )
