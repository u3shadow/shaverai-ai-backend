from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.prompt_builder import PromptBuilder
from app.services.reranker import Reranker
from app.services.retriever import Retriever
from app.vector_store.chroma_store import ChromaStore

class RagService:
    def __init__(self)-> None:
        self.min_rerank_score = 0.3977
        self.store = ChromaStore()
        self.retriever =  Retriever(self.store)
        self.reranker = Reranker()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", "，", " ", ""],
        )

    def ingest_markdown(self,file_path:str)->dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("文件不存在:{file_path}")

        raw_text = path.read_text(encoding="utf-8")
        cleaned_text =self._clean_text(raw_text) 

        chunks = self.text_splitter.split_text(cleaned_text)

        documents: list[Document] = []

        for index, chunk in enumerate(chunks):
            chunk_id = f"{path.stem}_{index+1:04d}"

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "doc_name": path.name,
                        "chunk_id": chunk_id,
                        "source_path": str(path),
                    },
                )
            )

        ids = self.store.add_documents(documents)
        
        return {
            "doc_name": path.name,
            "chunk_count": len(ids),
            "ids": ids,
        }

    def query(self, query: str, top_k: int = 5) -> dict:
        retrieved_chunks = self.retriever.retrieve(query=query, top_k=20)
        rerank_chunks = self.reranker.rerank(query=query, chunks=retrieved_chunks)
        if (
            not rerank_chunks
            or rerank_chunks[0].rerank_score < self.min_rerank_score
            ):
            return {
                "answer": "当前知识库中没有足够依据回答这个问题。",
                "sources": [],
                "retrieved_count": len(retrieved_chunks),
            }
        selected_chunks = rerank_chunks[:min(top_k, 5)]
        results = [
            {
                "doc_name": chunk.doc_name,
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,

                # 下面两个字段供现有 Sources 代码和 mock answer 使用
                "score": chunk.rerank_score,
                "content_preview": chunk.content[:120],
            }
             for chunk in selected_chunks
        ]
        if not results:
            return {
                "answer": "当前知识库中没有足够依据回答这个问题。",
                "sources": [],
                "retrieved_count": 0,
            }

        prompt = PromptBuilder.build_rag_prompt(query=query, retrieved_docs=results)

        # Day 3 先用 mock answer，先跑通 RAG 链路。
        # 后面再替换成 llm_client.generate(prompt)。
        answer = self._mock_answer(query=query, results=results, prompt=prompt)

        sources = [
            {
                "doc_name": item["doc_name"],
                "chunk_id": item["chunk_id"],
                "score": item["score"],
                "content_preview": item["content_preview"],
            }
            for item in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(retrieved_chunks),
        }

    def list_documents(self) -> list[str]:
        return self.store.list_documents()

    def _clean_text(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)

    def _mock_answer(self, query: str, results: list[dict], prompt: str) -> str:
        if "Tool Calling" in query or "ToolCall" in query or "安全" in query:
            return (
                "根据知识库资料，ShaverAI 中模型不能直接执行系统能力，"
                "而是只能输出结构化 ToolCall。系统会对 ToolCall 做 action 白名单校验、"
                "参数完整性和参数范围校验，最终由 Android 本地 ActionExecutor 执行真实设备能力。"
            )

        first = results[0]["content"] if results else ""
        return f"根据知识库检索结果，相关资料主要说明：{first[:200]}..."
