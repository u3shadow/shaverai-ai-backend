from fastapi import FastAPI
from app.core.config import settings
from app.api.health_api import router as health_router
from app.api.agent_api import router as agent_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(health_router)
app.include_router(agent_router)

@app.get("/") 
def root():
    return {"message": "ShaverAI AI Backend is running"}