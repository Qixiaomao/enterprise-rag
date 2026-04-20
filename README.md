# Enterprise RAG Assistant

A full-stack enterprise knowledge base QA system built with Next.js + FastAPI + Local LLM.

一个基于 Next.js + FastAPI + 本地大模型的企业知识库问答系统，支持文档检索、混合搜索、来源追踪与前后端分离部署。

---

## Demo Screenshot

![demo](./screenshots/home.jpg)

## Demo Preview

Supports:

- Natural language question answering
- Enterprise document retrieval
- Source citation tracing
- Full-stack local deployment
- Chinese hybrid search optimization

---

## Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- Python

### AI / Retrieval
- Ollama
- Qwen2.5:1.5B
- ChromaDB
- Dense Retrieval
- BM25
- Jieba Tokenizer
- Lightweight Reranker

---

## System Architecture

```text
User
 ↓
Next.js Frontend
 ↓ HTTP API
FastAPI Backend
 ├── Query Processing
 ├── Hybrid Retrieval
 │    ├── Dense Search (ChromaDB)
 │    └── BM25 Search
 ├── Lightweight Reranker
 ├── Prompt Builder
 └── Ollama Local LLM
       ↓
   Final Answer

Knowledge Base
 ├── PDF Documents
 ├── Chunking
 ├── Embeddings
 └── Vector Database
```

---

## Core Features

### Knowledge Base Pipeline
- PDF document ingestion
- Text chunking
- Embedding generation
- Vector database indexing

### Retrieval Pipeline
- Dense semantic search
- BM25 keyword retrieval
- Hybrid Retrieval
- Lightweight reranking

### Product Features
- Frontend QA interface
- RESTful API service
- Source references
- Relevance score display
- Local private deployment

---

## Benchmark (v1.4)

Evaluated on a 10-question internal benchmark set.

| Metric | Result |
|---|---|
| Top-1 Retrieval Accuracy | **90.0%** |
| Answer Correctness Score | **75.0%** |
| Avg End-to-End Latency | **3.319s** |

### Evaluation Domains
- CUDA / GPU optimization
- Internal policy documents
- RAG / API documentation

---

## API Example

### POST `/ask`

Request:

```json
{
  "question": "What is Bank Conflict?"
}
```

Response:

```json
{
  "success": true,
  "question": "What is Bank Conflict?",
  "answer": "...",
  "sources": [...]
}
```

---

## Project Structure

```text
enterprise-rag/
├── backend/
│   ├── app/
│   ├── data/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── evaluation/
└── README.md
```

---

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Local Model

```bash
ollama run qwen2.5:1.5b
```

---

## Resume Highlights

- Built a full-stack enterprise QA system with Next.js + FastAPI.
- Designed hybrid retrieval pipeline with **90% Top-1 accuracy**.
- Achieved **3.319s average response latency** in local deployment.
- Integrated local LLM inference with source tracing support.

---

## Roadmap

### v1.5
- [ ] File upload & online ingestion
- [ ] Knowledge base management UI
- [ ] Better answer formatting

### v1.6
- [ ] Multi-turn conversation memory
- [ ] Role-based access control
- [ ] Docker deployment

### v2.0
- [ ] Dify / Coze integration
- [ ] Cloud deployment
- [ ] Multi-user enterprise workspace

---

## Author

**7**

Focused on AI Applications / RAG Systems / ML Systems Engineering
```