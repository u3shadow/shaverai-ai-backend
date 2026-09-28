from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class SmokeState(TypedDict, total=False):
    message: str
    result: str
    trace: list[str]


def test_node(state: SmokeState) -> dict:
    """演示节点：读取输入，并返回 State 的部分更新。"""
    message = state.get("message", "")

    # 创建新列表再追加，避免直接修改传入的 State。
    trace = [*state.get("trace", []), "test_node"]

    return {
        "result": f"节点已处理：{message}",
        "trace": trace,
    }


def build_graph():
    # 用 SmokeState 告诉 LangGraph：这张图的 State 有哪些字段。
    builder = StateGraph(SmokeState)

    # 注册节点：节点名称是 "test_node"，执行函数是 test_node。
    builder.add_node("test_node", test_node)

    # 设置固定流程：开始 → test_node → 结束。
    builder.add_edge(START, "test_node")
    builder.add_edge("test_node", END)

    # 编译后得到可以执行的图。
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    # 输入初始 State；LangGraph 会把它传给 test_node。
    initial_state: SmokeState = {
        "message": "你好，LangGraph",
        "trace": [],
    }

    result = graph.invoke(initial_state)
    print(result)