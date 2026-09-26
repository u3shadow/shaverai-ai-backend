from app.schemas.rag_schema import RetrievedChunk


class Retriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self,query:str,top_k:int = 20)->list[RetrievedChunk]:
        raw_results = self.vector_store.similarity_search(
            query = query,
            top_k = top_k,
        )

        chunks = []
        for item in raw_results:
            distance = float(item["score"])

            chunks.append(
                RetrievedChunk(
                     doc_name=item["doc_name"] or "unknown",
                    chunk_id=item["chunk_id"] or "unknown",
                    content=item["content"],
                    vector_distance=distance,
                    vector_score=1.0 / (1.0 + max(distance, 0.0)),
                    metadata=item.get("metadata") or {},
                )
            )

        return chunks