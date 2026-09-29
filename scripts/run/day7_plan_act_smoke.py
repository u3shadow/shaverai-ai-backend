import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.agent_graph import agent_graph


def main() -> None:
    result = agent_graph.invoke(
        {
            "user_id": "u3",
            "message": "把音量设为 3，然后打开蓝牙。",
            "test_strategy_decision": {
                "intent": "DEVICE_CONTROL",
                "complexity": "MULTI_STEP",
                "suggested_mode": "PLAN_ACT",
                "reason": "请求包含两个有顺序的设备操作",
            },
            "test_plan_draft": {
                "title": "调整音量并打开蓝牙",
                "steps": [
                    {
                        "step_id": "set_volume",
                        "tool_name": "prepare_device_action",
                        "arguments": {
                            "action": "set_volume",
                            "params": {"level": 3},
                        },
                        "depends_on": [],
                    },
                    {
                        "step_id": "enable_bluetooth",
                        "tool_name": "prepare_device_action",
                        "arguments": {
                            "action": "set_bluetooth",
                            "params": {"enabled": True},
                        },
                        "depends_on": ["set_volume"],
                    },
                ],
            },
        }
    )

    plan = result.get("plan")
    assert result.get("mode") == "PLAN_ACT"
    assert plan is not None
    assert len(plan["steps"]) == 2
    assert plan["steps"][1]["depends_on"] == ["set_volume"]
    assert plan["status"] == "validated"
    assert result.get("action_plan") is None
    assert "未执行工具" in result.get("final_answer", "")

    print("PASS: PlanAct 生成两步计划并验证步骤依赖")
    print("PASS: 计划已返回，但后端未执行设备操作")


if __name__ == "__main__":
    main()