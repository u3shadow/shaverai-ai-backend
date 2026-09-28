from app.services.rag_service import RagService
from app.services.memory_service import MemoryService
from app.services.rule_engine import RuleEngine

# 模块只加载一次，避免 API 和 Agent Graph 各自重复初始化 RAG 模型。
rag_service = RagService()

# API 和 Agent Graph 共用同一个 MemoryService 实例。
memory_service = MemoryService()

# API 和 Agent Graph 共用同一个 RuleEngine。
rule_engine = RuleEngine()
