import requests
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = str(BASE_DIR / "data" / "vector_db")


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
    )


def retrieve_docs(query, k=3):
    db = get_vectorstore()
    docs = db.similarity_search(query, k=k)
    return docs


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
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a helpful assistant.
Answer the question only based on the context below.

Context:
{context}

Question:
{query}

Answer:
"""
    return prompt


if __name__ == "__main__":
    question = input("请输入问题：")

    docs = retrieve_docs(question)
    print("\n召回内容：")
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Chunk {i} ---")
        print(doc.page_content[:300])

    prompt = build_prompt(question, docs)
    answer = ask_ollama(prompt)

    print("\n最终回答：")
    print(answer)