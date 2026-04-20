from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.rag import hybrid_retrieve, rerank_docs, build_prompt, ask_ollama

app = FastAPI(title="Enterprise RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "Enterprise RAG API is running."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "enterprise-rag-backend"
    }


@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        return {
            "Success":False,
            "question": question,
            "answer": "问题不能为空。",
            "sources": []
        }

    candidates = hybrid_retrieve(question, dense_k=2, bm25_k=2)

    if not candidates:
        return {
            "Success":False,
            "question": question,
            "answer": "未检索到相关文档，请先检查知识库是否已构建。",
            "sources": []
        }

    docs = rerank_docs(question, candidates, top_n=2)
    prompt = build_prompt(question, docs)
    answer = ask_ollama(prompt)

    sources = []
    for doc in docs:
        sources.append({
            "source_file": doc["metadata"].get("source_file", "Unknown"),
            "page": doc["metadata"].get("page", "N/A"),
            "score": doc.get("score", 0),
            "overlap_tokens": doc.get("overlap_tokens", [])
        })

    return {
        "success":True,
        "question": question,
        "answer": answer,
        "sources": sources
    }