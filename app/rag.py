import requests
import jieba
from pathlib import Path

from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = str(BASE_DIR / "data" / "vector_db")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL
)

db = Chroma(
    persist_directory=VECTOR_DB_DIR,
    embedding_function=embeddings
)




def get_all_docs():
    
    return db.get()["documents"], db.get()["metadatas"]


def dense_retrieve(query, k=2):
    
    docs = db.similarity_search(query, k=k)
    return docs


def bm25_retrieve(query, k=2):
    
    data = db.get()

    texts = data["documents"]
    metadatas = data["metadatas"]

    tokenized_corpus = [list(jieba.cut(text)) for text in texts]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = list(jieba.cut(query))
    scores = bm25.get_scores(tokenized_query)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    results = []
    for idx in ranked_indices:
        doc = {
            "page_content": texts[idx],
            "metadata": metadatas[idx]
        }
        results.append(doc)

    return results


def hybrid_retrieve(query, dense_k=2, bm25_k=2):
    dense_docs = dense_retrieve(query, k=dense_k)
    bm25_docs = bm25_retrieve(query, k=bm25_k)

    merged = []
    seen = set()

    for doc in dense_docs:
        key = doc.page_content[:100]
        if key not in seen:
            merged.append(doc)
            seen.add(key)

    for doc in bm25_docs:
        key = doc["page_content"][:100]
        if key not in seen:
            merged.append(doc)
            seen.add(key)

    return merged


def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]


def build_prompt(query, docs):
    context_parts = []

    for i, doc in enumerate(docs, 1):
        if hasattr(doc, "page_content"):
            text = doc.page_content
            source = doc.metadata.get("source_file", "Unknown")
            page = doc.metadata.get("page", "N/A")
        else:
            text = doc["page_content"]
            source = doc["metadata"].get("source_file", "Unknown")
            page = doc["metadata"].get("page", "N/A")

        context_parts.append(f"[{i}] 来源: {source} | Page: {page}\n{text}")

    context = "\n\n".join(context_parts)

    prompt = f"""
你是企业知识库问答助手。

请严格依据提供的上下文回答问题。
不要补充上下文中没有明确出现的信息。
如果资料不足，请回答：无法在提供的文档中找到足够信息。

上下文：
{context}

问题：
{query}

回答要求：
1. 使用简洁、准确的中文回答。
2. 仅基于上下文内容作答。
3. 不要编造额外技术细节。
4. 回答结尾附上引用来源编号，例如：[1]

最终回答：
"""
    return prompt


if __name__ == "__main__":
    question = input("请输入问题：")

    docs = hybrid_retrieve(question, dense_k=2, bm25_k=2)

    print("\n参考来源：")
    for i, doc in enumerate(docs, 1):
        if hasattr(doc, "page_content"):
            source = doc.metadata.get("source_file", "Unknown")
            page = doc.metadata.get("page", "N/A")
            text = doc.page_content
        else:
            source = doc["metadata"].get("source_file", "Unknown")
            page = doc["metadata"].get("page", "N/A")
            text = doc["page_content"]

        print(f"\n--- Chunk {i} ---")
        print(f"Source: [{i}] {source} | Page: {page}")
        print(text[:300])

    prompt = build_prompt(question, docs)
    answer = ask_ollama(prompt)

    print("\n最终回答：")
    print(answer)