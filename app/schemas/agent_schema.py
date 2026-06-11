from pydantic import BaseModel


class DeviceContext(BaseModel):
    wifi: str | None = None
    battery: int | None = None
    bluetooth_enabled: bool | None = None
    screen_brightness: int | None = None
    volume: int | None = None


class ChatRequest(BaseModel):
    user_id: str
    message: str
    device_context: DeviceContext | None = None


class ChatResponse(BaseModel):
    answer: str
    intent: str = "unknown"
    need_android_execute: bool = False
