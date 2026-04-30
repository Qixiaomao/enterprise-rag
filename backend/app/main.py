from pathlib import Path
import shutil
from typing import Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ingest import DATA_DIR, build_vector_db, load_documents, split_documents
from app.rag import ask_ollama, build_prompt, hybrid_retrieve, rerank_docs


RAW_DIR = Path(DATA_DIR)
RAW_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Enterprise RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None  # None 表示新会话


# 根路径接口：用于快速确认服务是否启动
@app.get("/")
def root():
    return {"message": "Enterprise RAG API is running."}


# 健康检查接口：用于监控或前端探活
@app.get("/health")
def health():
    return {"status": "ok", "service": "enterprise-rag-backend"}


# 问答接口：执行检索、重排、生成并返回答案与来源
@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        return {
            "success": False,
            "question": question,
            "answer": "问题不能为空。",
            "sources": [],
        }

    candidates = hybrid_retrieve(question, dense_k=2, bm25_k=2)
    if not candidates:
        return {
            "success": False,
            "question": question,
            "answer": "未检索到相关文档，请先检查知识库是否已构建。",
            "sources": [],
        }

    docs = rerank_docs(question, candidates, top_n=2)
    prompt = build_prompt(question, docs)
    answer = ask_ollama(prompt)

    sources = []
    for doc in docs:
        sources.append(
            {
                "source_file": doc["metadata"].get("source_file", "Unknown"),
                "page": doc["metadata"].get("page", "N/A"),
                "score": doc.get("score", 0),
                "overlap_tokens": doc.get("overlap_tokens", []),
            }
        )

    return {
        "success": True,
        "question": question,
        "answer": answer,
        "sources": sources,
    }


# Agent 多轮对话接口：支持工具调用 + 上下文记忆
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    from app.agent import chat as agent_chat

    question = request.question.strip()
    if not question:
        return {
            "success": False,
            "question": question,
            "answer": "问题不能为空。",
            "thread_id": request.thread_id,
        }

    try:
        result = agent_chat(question, thread_id=request.thread_id)
        return result
    except RuntimeError as e:
        return {
            "success": False,
            "question": question,
            "answer": f"Agent 初始化失败: {str(e)}",
            "thread_id": request.thread_id,
        }


# 文件上传接口：接收 PDF 并保存到原始文档目录
# 采取异步操作以提高性能，尤其是对于较大的文件
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = RAW_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "filename": file.filename,
        "save_to": str(file_path),
    }


# 文档列表接口：返回当前知识库原始 PDF 清单
@app.get("/documents")
def list_documents():
    files = []
    for f in RAW_DIR.glob("*.pdf"):
        if f.is_file():
            files.append(
                {
                    "filename": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 2),
                }
            )

    return {
        "success": True,
        "count": len(files),
        "documents": files,
    }


# 重建知识库接口：重新执行加载、切分和向量化流程
@app.post("/rebuild")
def rebuild_knowledge_base():
    docs = load_documents()
    chunks = split_documents(docs)
    build_vector_db(chunks)

    return {
        "success": True,
        "message": "知识库重建完成。",
        "documents_loaded": len(docs),
    }
