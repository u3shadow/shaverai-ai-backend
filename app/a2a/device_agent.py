from typing import Any

from app.a2a.a2a_schema import A2ATaskRequest, A2ATaskResult
from app.services.tool_dispatcher import tool_dispatcher


class DeviceAgent:
    """Create and validate device action plans; never execute Android actions."""

    agent_name = "device_agent"
    task_type = "device.plan_action"

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

        user_id = request.context.get("user_id")
        if not isinstance(user_id, str) or not user_id.strip():
            return self._failure(
                request,
                "MISSING_USER_CONTEXT",
                "请求缺少由后端提供的 user_id",
            )

        # Only pass the fields supported by prepare_device_action.
        arguments = {
            "action": request.payload.get("action"),
            "params": request.payload.get("params"),
        }

        try:
            result = self._dispatcher.dispatch(
                "prepare_device_action",
                arguments,
                user_id=user_id,
            )
        except ValueError as exc:
            return self._failure(
                request,
                "INVALID_DEVICE_ACTION",
                str(exc),
            )
        except Exception:
            return self._failure(
                request,
                "DEVICE_PLAN_FAILED",
                "设备动作计划生成失败",
            )

        return A2ATaskResult(
            task_id=request.task_id,
            agent_name=self.agent_name,
            status="completed",
            data=result,
            message="动作计划已通过校验；尚未执行设备操作",
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
