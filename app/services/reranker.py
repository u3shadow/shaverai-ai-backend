import re

from app.schemas.rag_schema import RetrievedChunk, RerankedChunk

class Reranker:
    def rerank(
        self, query: str, chunks: list[RetrievedChunk]
    ) -> list[RerankedChunk]:
        query_terms = self._terms(query)
        results = []

        for chunk in chunks:
            content_terms = self._terms(chunk.content)
            title_terms = self._terms(chunk.doc_name)

            keyword_score = self._overlap(query_terms, content_terms)
            title_score = self._overlap(query_terms, title_terms)
            metadata_text = " ".join(str(v) for v in chunk.metadata.values())
            metadata_score = self._overlap(query_terms, self._terms(metadata_text))

            score = (
                0.6 * chunk.vector_score
                + 0.2 * keyword_score
                + 0.1 * title_score
                + 0.1 * metadata_score
            )

            results.append(
                RerankedChunk(
                    **chunk.model_dump(),
                    keyword_score=keyword_score,
                    title_score=title_score,
                    metadata_score=metadata_score,
                    rerank_score=score,
                )
            )

        return sorted(results, key=lambda item: item.rerank_score, reverse=True)

    @staticmethod
    def _terms(text: str) -> set[str]:
        text = text.lower()
        terms = set(re.findall(r"[a-z0-9_]+", text))

        for segment in re.findall(r"[\u4e00-\u9fff]+", text):
            if len(segment) == 1:
                terms.add(segment)
            else:
                terms.update(
                    segment[i:i + 2]
                    for i in range(len(segment) - 1)
                )

        return terms

    @staticmethod
    def _overlap(query_terms: set[str], target_terms: set[str]) -> float:
        if not query_terms:
            return 0.0
        return len(query_terms & target_terms) / len(query_terms)
