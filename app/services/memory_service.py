from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory_schema import MemoryItem


class MemoryService:
    def __init__(
        self,
        repository: MemoryRepository | None = None,
    ) -> None:
        self.repository = repository or MemoryRepository()

    def save_memory(self, item: MemoryItem) -> MemoryItem:
        return self.repository.save(item)

    def search_memory(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        return self.repository.search(
            user_id=user_id,
            query=query,
            top_k=top_k,
        )

    def list_memories(self, user_id: str) -> list[MemoryItem]:
        return self.repository.list_by_user(user_id)

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        return self.repository.delete(
            user_id=user_id,
            memory_id=memory_id,
        )