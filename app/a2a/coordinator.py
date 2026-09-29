from typing import Protocol

from app.a2a.a2a_schema import A2ATaskRequest, A2ATaskResult
from app.a2a.device_agent import DeviceAgent
from app.a2a.knowledge_agent import KnowledgeAgent


class AgentHandler(Protocol):
    """Interface required by an Agent registered with the coordinator."""

    agent_name: str

    def handle(self, request: A2ATaskRequest) -> A2ATaskResult:
        ...


class A2ACoordinator:
    """Route tasks to local Agents running in the same Python process."""

    def __init__(
        self,
        agents: dict[str, AgentHandler] | None = None,
    ) -> None:
        if agents is None:
            knowledge_agent = KnowledgeAgent()
            device_agent = DeviceAgent()
            agents = {
                knowledge_agent.agent_name: knowledge_agent,
                device_agent.agent_name: device_agent,
            }

        self._agents = agents

    def dispatch(self, request: A2ATaskRequest) -> A2ATaskResult:
        agent = self._agents.get(request.target_agent)
        if agent is None:
            return A2ATaskResult(
                task_id=request.task_id,
                agent_name="coordinator",
                status="failed",
                error_code="UNKNOWN_AGENT",
                errors=[f"未注册目标 Agent：{request.target_agent}"],
                message="任务无法路由",
            )

        try:
            result = agent.handle(request)
        except Exception:
            # Keep internal exceptions out of the inter-Agent response.
            return A2ATaskResult(
                task_id=request.task_id,
                agent_name="coordinator",
                status="failed",
                error_code="AGENT_CALL_FAILED",
                errors=["目标 Agent 调用失败"],
                message="任务处理失败",
            )

        if result.task_id != request.task_id:
            return A2ATaskResult(
                task_id=request.task_id,
                agent_name="coordinator",
                status="failed",
                error_code="TASK_ID_MISMATCH",
                errors=["Agent 返回的 task_id 与请求不一致"],
                message="Agent 响应关联校验失败",
            )

        if result.agent_name != request.target_agent:
            return A2ATaskResult(
                task_id=request.task_id,
                agent_name="coordinator",
                status="failed",
                error_code="AGENT_NAME_MISMATCH",
                errors=["响应 Agent 与请求目标不一致"],
                message="Agent 身份校验失败",
            )

        return result


a2a_coordinator = A2ACoordinator()
