from fastapi import APIRouter

from app.schemas.agent_schema import ChatRequest, ChatResponse
from app.schemas.tool_schema import ToolCall
from app.services.action_plan_builder import action_plan_builder
from app.services.echo_service import echo_service
from app.graph.agent_graph import agent_graph

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    graph_input = {
        "user_id": request.user_id,
        "message": request.message,
        "device_context": (
            request.device_context.model_dump()
            if request.device_context
            else None
        ),
    }

    result = agent_graph.invoke(graph_input)
    return graph_result_to_response(result)


@router.post("/echo")
def echo(request: ChatRequest):
    return {
        "user_id": request.user_id,
        "message": request.message,
        "device_context": request.device_context,
    }


@router.post("/validate-tool-call")
def validate_tool_call(request: ToolCall):
    try:
        action_plan = action_plan_builder.build(request.model_dump())
        action_plan.message = "ToolCall 校验通过"
        return {
            "valid": True,
            "error": None,
            "action_plan": action_plan,
        }
    except ValueError as exc:
        return {
            "valid": False,
            "error": str(exc),
            "action_plan": None,
        }

def graph_result_to_response(result: dict) -> ChatResponse:
    intent = result.get("intent", "UNKNOWN")
    action_plan = result.get("action_plan")
    rule_result = result.get("rule_result")
    errors = result.get("errors", [])

    if errors:
        response_type = "error"
    elif rule_result:
        response_type = "rule_result"
    elif result.get("needs_clarification", False):
        response_type = "clarification"
    elif (
        intent == "RULE_CREATE"
        and action_plan
        and action_plan.get("requires_confirmation", False)
    ):
        response_type = "confirmation_required"
    elif action_plan:
        response_type = "action_plan"
    elif intent == "UNKNOWN":
        response_type = "clarification"
    else:
        response_type = "answer"

    return ChatResponse(
        answer=result.get("final_answer", ""),
        intent=intent,
        need_android_execute=(
            action_plan.get("need_android_execute", False)
            if action_plan
            else False
        ),
        type=response_type,
        sources=result.get("sources", []),
        action_plan=action_plan,
        rule_result=rule_result,
        errors=errors,
        trace=result.get("trace", []),
    )
