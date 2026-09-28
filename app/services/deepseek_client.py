from openai import OpenAI

from app.core.config import settings


class DeepSeekClient:
    """Thin client for DeepSeek's OpenAI-compatible chat API."""

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        response_format: dict[str, str] | None = None,
        max_tokens: int = 512,
    ):
        if not settings.deepseek_api_key:
            raise RuntimeError(
                "未配置 DEEPSEEK_API_KEY。请在项目根目录的 .env 文件中设置。"
            )

        if self._client is None:
            self._client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )

        request_args = {
            "model": settings.deepseek_model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": max_tokens,
            "extra_body": {
                "thinking": {"type": "disabled"},
            },
        }

        if response_format is not None:
            request_args["response_format"] = response_format

        return self._client.chat.completions.create(**request_args)


deepseek_client = DeepSeekClient()
