import sys
from pathlib import Path


# Support launching this script directly from VS Code or another directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.agent_graph import agent_graph


def main() -> None:
    result = agent_graph.invoke(
        {
            "user_id": "u3",
            "message": "请为我生成音量设置为 3 的动作计划。",
            "test_strategy_decision": {
                "intent": "DEVICE_CONTROL",
                "complexity": "MULTI_STEP",
                "suggested_mode": "REACT",
                "reason": "使用 ReAct 测试工具调用循环",
            },
            "test_react_decisions": [
                {
                    "status": "tool_call",
                    "tool_name": "prepare_device_action",
                    "arguments": {
                        "action": "set_volume",
                        "params": {"level": 3},
                    },
                },
                {
                    "status": "final",
                    "answer": "已生成通过校验的设备动作计划，等待 Android 客户端执行。",
                },
            ],
        }
    )

    trace_nodes = [entry["node"] for entry in result.get("trace", [])]
    observations = result.get("observations", [])

    assert result.get("mode") == "REACT"
    assert result.get("iteration_count") == 1
    assert len(observations) == 1
    assert observations[0].get("ok") is True
    assert (
        observations[0]
        .get("result", {})
        .get("action_plan", {})
        .get("need_android_execute")
        is True
    )
    assert "react_tool_node" in trace_nodes
    assert result.get("final_answer", "").startswith("已生成")

    print("PASS: ReAct 调用白名单工具、保存 observation 并返回最终答案")
    print("PASS: Android 动作只生成计划，没有由后端执行")


if __name__ == "__main__":
    main()
