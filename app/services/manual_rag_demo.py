from pathlib import Path
KEYWORDS = [
    "ToolCall",
    "白名单",
    "参数",
    "校验",
    "ActionExecutor",
    "安全",
]
def load_markdown(path) -> str:
    project_root = Path(__file__).resolve().parents[2]
    markdown_path = project_root / path
    return markdown_path.read_text(encoding="utf-8")
def clean_text(text) -> str:
    lines = text.splitlines()
    cleaned_lines = []
    previous_blank = False
    for line in lines:
        stripped_line = line.strip()
        if stripped_line == "":
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
            continue
        cleaned_lines.append(stripped_line)
        previous_blank = False
    return "\n".join(cleaned_lines)
def split_intochunks(text, doc_name) -> list[dict]:
    paragraphs = text.split("\n\n")
    chunks = []
    for index,paragraph in enumerate(paragraphs):
        content = paragraph.strip()
        if  content == "":
            continue
        chunks.append({
            "chunk_id": f"{doc_name}#chunk_{index}",
            "content": content,
            "doc_name": doc_name,
        })
    return chunks 

def search_chunks(query, chunks, top_k=3) -> list[dict]:
    scored_chunks = []
    for chunk in chunks:
        content = chunk["content"]
        content_lower = content.lower()

        score = 0
        matched_keywords = []
        for keyword in KEYWORDS:
            if keyword.lower() in content_lower:
                score += 1
                matched_keywords.append(keyword)

        if score > 0:
            scored_chunks.append({**chunk, "score": score, "matched_keywords": matched_keywords})
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]

def build_prompt(query, retrieved_chunks) -> str:
    context_parts = []

    for chunk in retrieved_chunks:
        chunk_id = chunk["chunk_id"]
        content = chunk["content"]
        context_parts.append(f"{chunk_id} {content}")
        
    context = "\n\n".join(context_parts)

    prompt = f"""请基于以下资料回答问题。
            如果资料中没有答案，请回答“不确定”。
            资料：
            {context}

            问题：
            {query}
            """
    return prompt

def run_manual_rag(query: str) -> str:
    doc_name = "shaverai_tool_call.md"
    raw_text = load_markdown(f"docs/{doc_name}")
    clean = clean_text(raw_text)
    chunks = split_intochunks(clean, doc_name)
    retrieved_chunks = search_chunks(query, chunks, top_k=3)
    prompt = build_prompt(query, retrieved_chunks)

    return prompt

if __name__ == "__main__":
    query = "ShaverAI 里 Tool Calling 怎么保证安全？"
    prompt = run_manual_rag(query)
    print(prompt)