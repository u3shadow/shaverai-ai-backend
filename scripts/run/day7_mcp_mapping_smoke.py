import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mcp.tool_mapper import mcp_tool_mapper


def main() -> None:
    tools = mcp_tool_mapper.list_tools()
    tools_by_name = {tool["name"]: tool for tool in tools}

    expected_names = {
        "search_knowledge",
        "search_memory",
        "prepare_device_action",
    }
    assert set(tools_by_name) == expected_names

    query_schema = tools_by_name["search_knowledge"]["inputSchema"]
    assert query_schema["required"] == ["query"]
    assert query_schema["properties"]["top_k"]["minimum"] == 1
    assert query_schema["properties"]["top_k"]["maximum"] == 5

    # user_id must come from backend context, not from model-controlled args.
    memory_schema = tools_by_name["search_memory"]["inputSchema"]
    assert "user_id" not in memory_schema["properties"]

    device_schema = tools_by_name["prepare_device_action"]["inputSchema"]
    volume_schema = next(
        variant
        for variant in device_schema["oneOf"]
        if variant["properties"]["action"]["const"] == "set_volume"
    )
    level_schema = volume_schema["properties"]["params"]["properties"]["level"]
    assert level_schema["minimum"] == 0
    assert level_schema["maximum"] == 15

    # Unknown tools are rejected before reaching the dispatcher.
    try:
        mcp_tool_mapper.call_tool(
            "delete_everything",
            {},
            user_id="u3",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown tool was not rejected")

    # Missing query is rejected before any search service is called.
    try:
        mcp_tool_mapper.call_tool(
            "search_memory",
            {},
            user_id="u3",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Missing query was not rejected")

    print("PASS: ShaverAI tools are mapped to MCP-style definitions")
    print("PASS: schemas constrain arguments and do not expose user_id")
    print("PASS: unknown tools and invalid arguments are rejected")


if __name__ == "__main__":
    main()
