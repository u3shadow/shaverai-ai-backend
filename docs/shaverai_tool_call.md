# ShaverAI Tool Calling 说明

ShaverAI 中，模型不能直接执行系统能力。

模型只能输出结构化 ToolCall，例如：

{
  "action": "set_volume",
  "params": {
    "level": 3
  }
}

后端或 Android 本地需要对 ToolCall 做校验：

1. action 必须在白名单中；
2. params 参数必须完整；
3. 参数范围必须合法；
4. 高风险操作需要二次确认；
5. 最终由 Android ActionExecutor 执行真实设备能力。

这种设计可以把不确定的模型输出变成可校验、可控制、可执行的系统行为。