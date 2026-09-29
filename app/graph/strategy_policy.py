from app.graph.agent_state import AgentMode
from app.schemas.agent_strategy_schema import StrategyDecision


def resolve_strategy(
    decision: StrategyDecision,
) -> tuple[AgentMode, str]:
    """检查模型建议与任务复杂度是否一致，并返回后端最终采用的模式。"""

    # 无法识别的请求留给 UNKNOWN 澄清分支，不需要进入工具循环。
    if decision.intent == "UNKNOWN":
        return "DIRECT", "未知意图使用 Direct，后续由未知意图分支澄清"

    # 简单任务不需要多步规划或 ReAct 循环。
    if decision.complexity == "SIMPLE":
        if decision.suggested_mode != "DIRECT":
            return "DIRECT", "简单任务不进入 ReAct 或 PlanAct，已调整为 Direct"
        return "DIRECT", "简单任务采用 Direct"

    # 多步骤任务不能采用 Direct；交给模型建议的 ReAct 或 PlanAct。
    if decision.suggested_mode == "DIRECT":
        return "REACT", "多步骤任务不采用 Direct，已调整为 ReAct"

    return decision.suggested_mode, "多步骤任务采用模型建议的策略"