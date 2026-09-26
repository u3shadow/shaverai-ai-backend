from fastapi import APIRouter, HTTPException

from app.schemas.rag_schema import (
    RagDocumentListResponse,
    RagQueryRequest,
    RagQueryResponse,
    RagUploadResponse,
    UploadLocalRequest,
)
from app.services.rag_service import RagService
from app.services.retriever import Retriever


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

@router.post("/debug")
def debug_rag(req:RagQueryRequest):
    retriever = Retriever(rag_service.store)
    chunks = retriever.retrieve(req.query,top_k=20)

    return {
        "query":req.query,
        "retrieved":[
            {
               "rank": rank,
                "doc_name": chunk.doc_name,
                "chunk_id": chunk.chunk_id,
                "vector_distance": chunk.vector_distance,
                "vector_score": chunk.vector_score,
                "content_preview": chunk.content[:150],
            }
            for rank, chunk in enumerate(chunks, start=1)
        ]
    }
