import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import ValidationError

from app.a2a import A2ATaskRequest, A2ATaskResult


def main() -> None:
    request = A2ATaskRequest(
        source_agent="orchestrator",
        target_agent="knowledge_agent",
        task_type="knowledge.query",
        payload={
            "query": "ShaverAI 中模型如何控制 Android 设备？",
        },
        context={
            "user_id": "u3",
            "trace_id": "trace_day7_demo",
        },
    )

    assert request.task_id.startswith("task_")
    assert request.source_agent == "orchestrator"
    assert request.target_agent == "knowledge_agent"
    print("PASS: A2ATaskRequest construction and validation")

    result = A2ATaskResult(
        task_id=request.task_id,
        agent_name="knowledge_agent",
        status="completed",
        data={
            "answer": (
                "The model emits a structured ToolCall; the backend and "
                "Android validate and execute it."
            ),
            "sources": [
                {
                    "doc_name": "shaverai_tool_call.md",
                    "chunk_id": "shaverai_tool_call_0001",
                }
            ],
        },
        message="Knowledge query completed",
    )

    assert result.task_id == request.task_id
    assert result.data["sources"][0]["doc_name"] == "shaverai_tool_call.md"

    serialized = result.model_dump_json()
    restored = A2ATaskResult.model_validate_json(serialized)
    assert restored.task_id == request.task_id
    assert restored.status == "completed"
    print("PASS: A2ATaskResult serialization and parsing")

    try:
        A2ATaskResult(
            task_id=request.task_id,
            agent_name="device_agent",
            status="needs_clarification",
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Clarification status must include a message")

    try:
        A2ATaskResult(
            task_id=request.task_id,
            agent_name="knowledge_agent",
            status="failed",
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Failed status must include error details")

    print("PASS: clarification and failure status validation")


if __name__ == "__main__":
    main()
