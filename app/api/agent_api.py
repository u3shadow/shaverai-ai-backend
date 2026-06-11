from fastapi import APIRouter

from app.schemas.agent_schema import ChatRequest, ChatResponse
from app.schemas.tool_schema import ToolCall
from app.services.action_plan_builder import action_plan_builder
from app.services.echo_service import echo_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return echo_service.chat(request)


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
