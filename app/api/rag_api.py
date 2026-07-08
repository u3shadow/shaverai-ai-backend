from fastapi import APIRouter, HTTPException

from app.schemas.rag_schema import (
    RagDocumentListResponse,
    RagQueryRequest,
    RagQueryResponse,
    RagUploadResponse,
    UploadLocalRequest,
)
from app.services.rag_service import RagService


router = APIRouter(prefix="/rag", tags=["RAG"])

rag_service = RagService()


@router.post("/upload-local", response_model=RagUploadResponse)
def upload_local(req: UploadLocalRequest):
    try:
        return rag_service.ingest_markdown(req.path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入文档失败: {e}")


@router.post("/query", response_model=RagQueryResponse)
def query(req: RagQueryRequest):
    try:
        return rag_service.query(query=req.query, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 查询失败: {e}")


@router.get("/documents", response_model=RagDocumentListResponse)
def documents():
    return {
        "documents": rag_service.list_documents()
    }