from pydantic import BaseModel, Field


class UploadLocalRequest(BaseModel):
    path: str = Field(..., description="本地md文件路径")

class RagQueryRequest(BaseModel):
    user_id: str = Field(..., description="userid")
    query: str = Field(..., description="用户问题")
    top_k: int = Field(default=5,ge=1,le=20, description="检索数量")


class RagSource(BaseModel):
    doc_name: str
    chunk_id: str
    score: float
    content_preview: str


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[RagSource] = Field(default_factory=list)
    retrieved_count: int

class RagUploadResponse(BaseModel):
    doc_name: str
    chunk_count: int
    ids:list[str]

class RagDocumentListResponse(BaseModel):
    documents:list[str]