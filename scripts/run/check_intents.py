from app.graph.agent_graph import intent_node

cases = [
    ("RAG 和微调有什么区别？", "KNOWLEDGE_QUERY"),
    ("把音量调到 3", "DEVICE_CONTROL"),
    ("创建一个连接公司 WiFi 后静音的规则", "RULE_CREATE"),
    ("你好", "UNKNOWN"),
]

for message, expected in cases:
    result = intent_node({"user_id": "u3", "message": message})
    actual = result["intent"]
    status = "PASS" if actual == expected else "CHECK"
    print(f"{status}: expected={expected}, actual={actual}, message={message}")