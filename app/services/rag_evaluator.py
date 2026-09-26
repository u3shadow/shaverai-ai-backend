class RagEvaluator:
    @staticmethod
    def recall_at_k(chunks, expected_docs: list[str], k: int = 5) -> float:
        if not expected_docs:
            return 0.0

        actual_docs = {
            chunk.doc_name
            for chunk in chunks[:k]
        }
        expected = set(expected_docs)

        return len(actual_docs & expected) / len(expected)

    @staticmethod
    def find_first_rank(chunks, expected_docs: list[str]) -> int | None:
        expected = set(expected_docs)

        for rank, chunk in enumerate(chunks, start=1):
            if chunk.doc_name in expected:
                return rank

        return None