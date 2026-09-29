import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.a2a.a2a_schema import A2ATaskRequest
from app.a2a.coordinator import A2ACoordinator
from app.a2a.device_agent import DeviceAgent
from app.a2a.knowledge_agent import KnowledgeAgent


class FakeKnowledgeDispatcher:
    """Replace only knowledge search to avoid calling real RAG."""

    def dispatch(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        user_id: str,
    ) -> dict[str, Any]:
        assert tool_name == "search_knowledge"
        assert user_id == "u3"
        assert arguments["query"]

        return {
            "answer": "设备动作由 Android 本地执行。",
            "sources": [{"doc_name": "shaverai_tool_call.md"}],
        }


def main() -> None:
    coordinator = A2ACoordinator(
        agents={
            # Keep knowledge search deterministic and avoid a live RAG call.
            "knowledge_agent": KnowledgeAgent(FakeKnowledgeDispatcher()),
            # No dispatcher injection: use the real ToolDispatcher.
            "device_agent": DeviceAgent(),
        }
    )

    knowledge_request = A2ATaskRequest(
        source_agent="orchestrator",
        target_agent="knowledge_agent",
        task_type="knowledge.query",
        payload={"query": "Android 动作由哪一端执行？"},
        context={"user_id": "u3"},
    )
    knowledge_result = coordinator.dispatch(knowledge_request)

    assert knowledge_result.status == "completed"
    assert knowledge_result.task_id == knowledge_request.task_id
    assert (
        knowledge_result.data["sources"][0]["doc_name"]
        == "shaverai_tool_call.md"
    )
    print("PASS: Coordinator -> Knowledge Agent -> result")

    # Pass the previous Agent's result as context for the next task.
    device_request = A2ATaskRequest(
        source_agent="orchestrator",
        target_agent="device_agent",
        task_type="device.plan_action",
        payload={
            "action": "set_volume",
            "params": {"level": 3},
        },
        context={
            "user_id": "u3",
            "previous_agent_result": knowledge_result.data,
        },
    )
    device_result = coordinator.dispatch(device_request)

    assert device_result.status == "completed"
    assert device_result.task_id == device_request.task_id

    action_plan = device_result.data["action_plan"]
    assert action_plan["need_android_execute"] is True
    assert action_plan["execution_target"] == "android"
    assert action_plan["actions"][0]["action"] == "set_volume"
    assert action_plan["actions"][0]["params"] == {"level": 3}
    print("PASS: Device Agent used real ToolDispatcher and validated the plan")

    # An out-of-range volume must be rejected by the real validator.
    invalid_request = A2ATaskRequest(
        source_agent="orchestrator",
        target_agent="device_agent",
        task_type="device.plan_action",
        payload={
            "action": "set_volume",
            "params": {"level": 999},
        },
        context={"user_id": "u3"},
    )
    invalid_result = coordinator.dispatch(invalid_request)

    assert invalid_result.status == "failed"
    assert invalid_result.error_code == "INVALID_DEVICE_ACTION"
    print("PASS: Invalid device parameter was rejected")
    print("PASS: No Android action was executed")


if __name__ == "__main__":
    main()
