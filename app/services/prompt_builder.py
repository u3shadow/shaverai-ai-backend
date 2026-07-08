class PromptBuilder:
    @staticmethod
    def build_rag_prompt(query: str, retrieved_docs: list[dict]) -> str:
        context_parts: list[str] = []

        for index, item in enumerate(retrieved_docs, start=1):
            doc_name = item.get("doc_name", "")
            chunk_id = item.get("chunk_id", "")
            content = item.get("content", "")

            context_parts.append(
                f"[资料 {index}]\n"
                f"来源: {doc_name} / {chunk_id}\n"
                f"内容:\n{content}"
            )

        context = "\n\n".join(context_parts)

        return f"""
你是 ShaverAI 项目知识库助手。

请只基于下面给定资料回答问题。
如果资料中没有答案，请回答：当前知识库中没有足够依据回答这个问题。
回答要简洁、准确，并尽量指出依据来自哪些资料。

资料：
{context}

问题：
{query}
""".strip()