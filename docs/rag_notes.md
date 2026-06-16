# RAG 基础说明

RAG 是 Retrieval-Augmented Generation，即检索增强生成。

它的核心流程是：

文档加载
→ 文本清洗
→ Chunk 切分
→ Embedding
→ 向量数据库
→ 相似度检索
→ TopK
→ Prompt 拼接
→ 回答生成
→ 引用来源
→ 幻觉控制

RAG 和微调不同。微调是改变模型参数，让模型学会某种风格或任务；RAG 不改变模型参数，而是在回答前检索外部知识，把相关内容放进 Prompt。