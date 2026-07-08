from fastapi import FastAPI

from app.api.agent_api import router as agent_router
from app.api.health_api import router as health_router
from app.api.rag_api import router as rag_router

app = FastAPI(title="ShaverAI AI Backend")

app.include_router(health_router)
app.include_router(agent_router)
app.include_router(rag_router)