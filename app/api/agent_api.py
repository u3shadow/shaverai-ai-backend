from fastapi import APIRouter

from app.schemas.agent_schema import ChatRequest, ChatResponse
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
