import sys
from pathlib import Path


# Make the project root importable even when this script is launched from
# VS Code's Run button or from a working directory outside the repository.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.agent_graph import intent_node, strategy_node


CASES = [
    (
        "单步设备操作",
        {
            "intent": "DEVICE_CONTROL",
            "complexity": "SIMPLE",
            "suggested_mode": "DIRECT",
            "reason": "单个设备动作",
        },
        "DIRECT",
    ),
    (
        "简单任务的冲突建议",
        {
            "intent": "KNOWLEDGE_QUERY",
            "complexity": "SIMPLE",
            "suggested_mode": "PLAN_ACT",
            "reason": "测试后端策略调整",
        },
        "DIRECT",
    ),
    (
        "多步边查边决策",
        {
            "intent": "KNOWLEDGE_QUERY",
            "complexity": "MULTI_STEP",
            "suggested_mode": "REACT",
            "reason": "需要根据查询结果继续决策",
        },
        "REACT",
    ),
    (
        "多步骤计划",
        {
            "intent": "RULE_CREATE",
            "complexity": "MULTI_STEP",
            "suggested_mode": "PLAN_ACT",
            "reason": "步骤之间存在依赖",
        },
        "PLAN_ACT",
    ),
    (
        "多步骤任务误建议 Direct",
        {
            "intent": "DEVICE_CONTROL",
            "complexity": "MULTI_STEP",
            "suggested_mode": "DIRECT",
            "reason": "测试后端策略调整",
        },
        "REACT",
    ),
    (
        "未知意图",
        {
            "intent": "UNKNOWN",
            "complexity": "MULTI_STEP",
            "suggested_mode": "PLAN_ACT",
            "reason": "意图无法识别",
        },
        "DIRECT",
    ),
]


def main() -> None:
    for name, decision, expected_mode in CASES:
        state = {
            "user_id": "u3",
            "message": name,
            "trace": [],
            "test_strategy_decision": decision,
        }

        state.update(intent_node(state))
        state.update(strategy_node(state))

        actual_mode = state.get("mode")
        if actual_mode != expected_mode:
            raise AssertionError(
                f"{name}: expected={expected_mode}, actual={actual_mode}"
            )

        print(f"PASS: {name} -> {actual_mode}")


if __name__ == "__main__":
    main()
