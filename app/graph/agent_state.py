from typing import Any, Literal, NotRequired, TypedDict

from app.schemas.agent_strategy_schema import (
    AgentMode,
    TaskComplexity,
)


# Agent 当前处理的请求类型。
# UNKNOWN 用于无法识别或需要向用户澄清的请求。
IntentType = Literal[
    "KNOWLEDGE_QUERY",
    "DEVICE_CONTROL",
    "RULE_CREATE",
    "UNKNOWN",
]


class TraceEntry(TypedDict):
    """Graph 执行过程中的一条调试记录。"""

    node: str
    result: str


class AgentState(TypedDict):
    """
    LangGraph 节点之间共享的状态。

    user_id 和 message 是每次 Agent 请求必须提供的输入。
    其他字段由不同节点按需写入，因此标记为 NotRequired。
    """

    # 每个请求所属的用户；Memory 查询时会用它做用户范围过滤。
    user_id: str

    # 用户的原始输入，例如“帮我把音量调低”。
    message: str

    # Android 当前设备信息；ChatRequest 中对应的 DeviceContext。
    # 转成普通 dict 后放入 Graph State。
    device_context: NotRequired[dict[str, Any] | None]

    # IntentNode 判断出的请求类型。
    intent: NotRequired[IntentType]

    # Day 7：任务复杂度，以及后端校验后采用的处理模式。
    complexity: NotRequired[TaskComplexity]
    mode: NotRequired[AgentMode]
    suggested_mode: NotRequired[AgentMode]
    strategy_reason: NotRequired[str]

    # Day 7：结构化计划草案和校验后的计划，统一以 dict 放入 State。
    plan_draft: NotRequired[dict[str, Any] | None]
    plan: NotRequired[dict[str, Any] | None]

    # Day 7：ReAct 工具循环的观察结果和轮数控制字段。
    observations: NotRequired[list[dict[str, Any]]]
    iteration_count: NotRequired[int]
    max_iterations: NotRequired[int]
    react_status: NotRequired[
        Literal["tool_call", "observed", "final", "limit", "error"]
    ]
    react_tool_call: NotRequired[dict[str, Any] | None]

    # MemoryNode 搜索到的用户记忆。
    memories: NotRequired[list[dict[str, Any]]]

    # SkillNode 从 SkillRegistry 读取的能力定义。
    # 通常会把 Pydantic SkillDefinition 转成 dict 后放入这里。
    available_skills: NotRequired[list[dict[str, Any]]]

    # PlanNode 生成的结构化 ToolCall，例如：
    # {"action": "set_volume", "params": {"level": 3}}
    tool_call: NotRequired[dict[str, Any] | None]

    # ActionPlanBuilder 生成的执行计划。
    # 设备动作由 Android 执行；Python 不直接操作设备。
    action_plan: NotRequired[dict[str, Any] | None]

    # RagService.query() 的完整返回结果。
    # 当前包含 answer、sources、retrieved_count。
    rag_result: NotRequired[dict[str, Any] | None]

    # RAG 的引用来源，供最终 ChatResponse 使用。
    sources: NotRequired[list[dict[str, Any]]]

    # RuleEngine 创建规则或处理规则时的结果。
    rule_result: NotRequired[dict[str, Any] | None]

    # 最终回复给用户的文字。
    final_answer: NotRequired[str]

    # 设备规划节点发现请求信息不足时，提示 API 返回澄清类型。
    needs_clarification: NotRequired[bool]

    # 节点发现的错误或需要澄清的问题。
    errors: NotRequired[list[str]]

    # 节点执行轨迹，例如：
    # [{"node": "intent_node", "result": "KNOWLEDGE_QUERY"}]
    trace: NotRequired[list[TraceEntry]]

    test_intent: NotRequired[IntentType]
    # 仅供内部测试：注入结构化意图/策略结果，避免调用 DeepSeek。
    # API 不会从用户请求中接收或转发这个字段。
    test_strategy_decision: NotRequired[dict[str, Any]]
    # 仅供本地验收：按顺序模拟 ReAct 模型的工具选择和最终回答。
    test_react_decisions: NotRequired[list[dict[str, Any]]]
    test_react_decision_index: NotRequired[int]
    test_tool_call: NotRequired[dict[str, Any]]
    # 仅供本地验收：模拟用户已确认规则草案。
    test_confirmed: NotRequired[bool]
    # 仅供本地验收：注入 PlanAct 草案，避免调用 DeepSeek。
    test_plan_draft: NotRequired[dict[str, Any]]
