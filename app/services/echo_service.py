from app.schemas.agent_schema import ChatRequest, ChatResponse


class EchoService:
    def chat(self, request: ChatRequest) -> ChatResponse:
        wifi = request.device_context.wifi if request.device_context else None

        if wifi:
            answer = f"收到你的输入：{request.message}，当前 WiFi 是：{wifi}"
        else:
            answer = f"收到你的输入：{request.message}"

        return ChatResponse(answer=answer, intent="demo_chat", need_android_execute=False)


echo_service = EchoService()
