import json

from langchain_core.documents import Document

from app.schemas.memory_schema import MemoryItem
from app.vector_store.chroma_store import ChromaStore


class MemoryRepository:
    MEMORY_TYPES = {
        "preference",
        "entity_mapping",
        "history",
        "conversation_summary",
    }

    def __init__(self, store: ChromaStore | None = None) -> None:
        # 和知识库共用持久化目录，但使用独立 collection
        self.store = store or ChromaStore(
            persist_dir="data/chroma",
            collection_name="shaverai_memory",
        )

    def save(self, item: MemoryItem) -> MemoryItem:
        """把一条 Memory 写入独立的向量集合。"""
        if not item.user_id.strip():
            raise ValueError("user_id 不能为空")

        if not item.content.strip():
            raise ValueError("Memory content 不能为空")

        if item.type not in self.MEMORY_TYPES:
            raise ValueError(f"不支持的 Memory 类型: {item.type}")

        document = Document(
            page_content=item.content,
            metadata={
                # ChromaStore.add_documents() 用 chunk_id 作为向量记录 ID
                "chunk_id": item.memory_id,
                "memory_id": item.memory_id,
                "user_id": item.user_id,
                "memory_type": item.type,

                # Chroma metadata 存简单值；复杂字典单独 JSON 编码
                "memory_metadata_json": json.dumps(
                    item.metadata,
                    ensure_ascii=False,
                ),
            },
        )

        self.store.add_documents([document])
        return item

    def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """只搜索指定用户的 Memory。"""
        if not user_id.strip():
            raise ValueError("user_id 不能为空")

        if not query.strip():
            return []

        results = self.store.similarity_search(
            query=query,
            top_k=top_k,
            where={"user_id": user_id},
        )

        memories = []

        for result in results:
            memory = self._to_memory_item(
                content=result["content"],
                metadata=result["metadata"],
            )

            distance = float(result["score"])

            memories.append(
                {
                    **memory.model_dump(),
                    # 这是排序用分数，不是概率
                    "score": 1.0 / (1.0 + max(distance, 0.0)),
                }
            )

        return memories

    def list_by_user(self, user_id: str) -> list[MemoryItem]:
        """列出指定用户保存的全部 Memory。"""
        if not user_id.strip():
            raise ValueError("user_id 不能为空")

        raw = self.store.get_by_metadata({"user_id": user_id})
        documents = raw.get("documents") or []
        metadatas = raw.get("metadatas") or []

        items = [
            self._to_memory_item(content, metadata)
            for content, metadata in zip(documents, metadatas)
        ]

        return sorted(items, key=lambda item: item.memory_id)

    def delete(self, user_id: str, memory_id: str) -> bool:
        """只删除指定用户自己的 Memory。"""
        if not user_id.strip():
            raise ValueError("user_id 不能为空")

        raw = self.store.get_by_metadata({"user_id": user_id})
        ids = raw.get("ids") or []
        metadatas = raw.get("metadatas") or []

        matching_ids = [
            ids[index]
            for index, metadata in enumerate(metadatas)
            if metadata.get("memory_id") == memory_id
        ]

        self.store.delete_by_ids(matching_ids)
        return bool(matching_ids)

    @staticmethod
    def _to_memory_item(
        content: str,
        metadata: dict,
    ) -> MemoryItem:
        extra_metadata = json.loads(
            metadata.get("memory_metadata_json", "{}")
        )

        return MemoryItem(
            memory_id=metadata["memory_id"],
            user_id=metadata["user_id"],
            type=metadata["memory_type"],
            content=content,
            metadata=extra_metadata,
        )