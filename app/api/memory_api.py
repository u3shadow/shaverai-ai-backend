from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.memory_schema import (
    MemoryDeleteResponse,
    MemoryItem,
    MemorySearchRequest,
    MemorySearchResponse,
)
from app.core.service_container import memory_service


router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post(
    "",
    response_model=MemoryItem,
    status_code=status.HTTP_201_CREATED,
)
def save_memory(item: MemoryItem):
    try:
        return memory_service.save_memory(item)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("", response_model=list[MemoryItem])
def list_memories(user_id: str = Query(...)):
    try:
        return memory_service.list_memories(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/search", response_model=MemorySearchResponse)
def search_memory(request: MemorySearchRequest):
    try:
        memories = memory_service.search_memory(
            user_id=request.user_id,
            query=request.query,
            top_k=request.top_k,
        )
        return {"memories": memories}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete(
    "/{memory_id}",
    response_model=MemoryDeleteResponse,
)
def delete_memory(
    memory_id: str,
    user_id: str = Query(...),
):
    deleted = memory_service.delete_memory(
        user_id=user_id,
        memory_id=memory_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory 不存在，或不属于该用户",
        )

    return {
        "deleted": True,
        "memory_id": memory_id,
    }
