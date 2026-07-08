from __future__  import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class ChromaStore:
    def __init__(self,persist_dir:str = "data/chroma",
               collection_name:str = "shaverai_docs",
               embedding_model_name:str = "BAAI/bge-small-zh-v1.5",
               )->None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name

        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
            )

        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_dir),
        )

    def add_documents(self, documents: list[Document]) -> list[str]:
        if not documents:
            return []
        
        ids:list[str] = []

        for doc in documents:
            chunk_id = doc.metadata.get("chunk_id")
            if not chunk_id:
                chunk_id = f"chunk_{uuid4().hex}"
                doc.metadata["chunk_id"] = chunk_id

            ids.append(chunk_id)

        self.vector_store.add_documents(documents, ids=ids)

        return ids

    def similarity_search(self,query:str,top_k:int = 5) -> list[dict[str,Any]]:
        if not query.strip():
            return []
        
        results = self.vector_store.similarity_search_with_score(query, k=top_k)

        normalized_results:list[dict[str,Any]] = []

        for doc, score in results:
            normalized_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "doc_name": doc.metadata.get("doc_name", ""),
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "score": score,
                "source_path": doc.metadata.get("source_path", ""),
                "content_preview": doc.page_content[:120],
            })

        return normalized_results
    
    def list_documents(self)->list[str]:
        raw = self.vector_store.get()
        metadatas = raw.get("metadatas", []) or []

        doc_names ={
            metadata.get("doc_name")
            for metadata in metadatas
            if  metadata and metadata.get("doc_name")
        } 
        
        return sorted(doc_names)

    def count(self)->int:
        raw = self.vector_store.get()
        ids = raw.get("ids", []) or []
        return len(ids)

    def clear(self)->None:
        raw = self.vector_store.get()
        ids = raw.get("ids", []) or []
        
        if ids:
            self.vector_store.delete(ids=ids)
    

