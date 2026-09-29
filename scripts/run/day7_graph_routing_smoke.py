import sys
from pathlib import Path


# Support direct execution from VS Code or any working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.agent_graph import agent_graph


def trace_nodes(result: dict) -> list[str]:
    return [entry["node"] for entry in result.get("trace", [])]


def main() -> None:
    direct_result = agent_graph.invoke(
        {
            "user_id": "u3",
            "message": "把音量调到 3",
            "test_strategy_decision": {
                "intent": "DEVICE_CONTROL",
                "complexity": "SIMPLE",
                "suggested_mode": "DIRECT",
                "reason": "单个设备动作",
            },
            "test_tool_call": {
                "action": "set_volume",
                "params": {"level": 3},
            },
        }
    )
    direct_trace = trace_nodes(direct_result)
    assert direct_result.get("mode") == "DIRECT"
    assert "direct_dispatch_node" in direct_trace
    assert "device_plan_node" in direct_trace
    assert direct_result.get("action_plan") is not None
    print("PASS: DIRECT -> existing device plan branch")

    react_result = agent_graph.invoke(
        {
            "user_id": "u3",
            "message": "先查询资料，再根据结果决定下一步",
            "test_strategy_decision": {
                "intent": "KNOWLEDGE_QUERY",
                "complexity": "MULTI_STEP",
                "suggested_mode": "REACT",
                "reason": "需要根据观察结果继续决策",
            },
            "test_react_decisions": [
                {
                    "status": "final",
                    "answer": "ReAct 路由测试完成。",
                }
            ],
        }
    )
    react_trace = trace_nodes(react_result)
    assert react_result.get("mode") == "REACT"
    assert "react_agent_node" in react_trace
    assert "knowledge_node" not in react_trace
    print("PASS: REACT -> ReAct agent branch")

    plan_result = agent_graph.invoke(
        {
            "user_id": "u3",
            "message": "把音量设置为 3",
            "test_strategy_decision": {
                "intent": "DEVICE_CONTROL",
                "complexity": "MULTI_STEP",
                "suggested_mode": "PLAN_ACT",
                "reason": "测试 PlanAct 路由",
            },
            # 注入固定草案，避免冒烟测试调用真实 DeepSeek。
            "test_plan_draft": {
                "title": "测试计划",
                "steps": [
                    {
                        "step_id": "set_volume",
                        "tool_name": "prepare_device_action",
                        "arguments": {
                            "action": "set_volume",
                            "params": {"level": 3},
                        },
                        "depends_on": [],
                    }
                ],
            },
        }
    )
    plan_trace = trace_nodes(plan_result)
    assert plan_result.get("mode") == "PLAN_ACT"
    assert "plan_act_node" in plan_trace
    assert plan_result.get("plan") is not None
    assert "rule_plan_node" not in plan_trace
    assert plan_result["plan"]["status"] == "validated"
    print("PASS: PLAN_ACT -> PlanAct branch (deterministic draft; no execution)")


if __name__ == "__main__":
    main()
