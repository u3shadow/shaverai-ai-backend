from pathlib import Path
import sys

from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.vector_store.chroma_store import ChromaStore

def main()->None:
    store = ChromaStore()

    store.clear()

    docs = [
        Document(
            page_content=(
                "ShaverAI 中模型不能直接执行系统能力。"
                "模型只能输出结构化 ToolCall，后端或 Android 本地需要做白名单校验、参数校验，"
                "最终由 ActionExecutor 执行真实设备能力。"
            ),
            metadata={
                "doc_name": "shaverai_tool_call.md",
                "chunk_id": "shaverai_tool_call_001",
                "source_path": "docs/shaverai_tool_call.md",
            },
        ),
        Document(
            page_content=(
                "RAG 是检索增强生成。它会先加载文档，切分 chunk，生成 embedding，"
                "再通过向量数据库检索 TopK 内容，最后拼接 Prompt 生成回答。"
            ),
            metadata={
                "doc_name": "rag_notes.md",
                "chunk_id": "rag_notes_001",
                "source_path": "docs/rag_notes.md",
            },
        ),
    ]

    ids = store.add_documents(docs)
    print("写入 ids:", ids)
    print("当前 chunk 数:", store.count())
    print("当前文档:", store.list_documents())

    results = store.similarity_search("ShaverAI 里 Tool Calling 怎么保证安全？", top_k=3)

    print("\n检索结果:")
    for item in results:
        print("-" * 80)
        print("doc_name:", item["doc_name"])
        print("chunk_id:", item["chunk_id"])
        print("score:", item["score"])
        print("preview:", item["content_preview"])


if __name__ == "__main__":
    main()
