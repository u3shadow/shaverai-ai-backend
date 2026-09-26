from fastapi import FastAPI

from app.api.agent_api import router as agent_router
from app.api.health_api import router as health_router
from app.api.rag_api import router as rag_router
from app.api.rule_api import router as rule_router
from app.api.memory_api import router as memory_router
from app.api.skill_api import router as skill_router

app = FastAPI(title="ShaverAI AI Backend")

app.include_router(health_router)
app.include_router(agent_router)
app.include_router(rag_router)
app.include_router(rule_router)
app.include_router(memory_router)
app.include_router(skill_router)