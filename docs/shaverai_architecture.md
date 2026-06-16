# ShaverAI 架构说明

ShaverAI 是一个 Android 端云协同 Agent 项目。

Android 端负责真实设备能力执行，例如音量、亮度、蓝牙、WiFi 状态监听和 ActionExecutor。

Python 后端负责 RAG 知识库、Memory、SkillRegistry、RuleEngine、ToolCall 校验和 Agent 编排。

用户输入后，系统会先判断是普通聊天、设备控制还是规则创建。如果是设备控制，模型会生成 ToolCall，后端校验后返回 ActionPlan，由 Android 本地执行。