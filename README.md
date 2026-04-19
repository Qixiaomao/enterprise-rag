# Enterprise RAG Assistant / 企业级 RAG 智能知识库（v1.0）

## Overview / 项目简介

Enterprise RAG Assistant is a local Retrieval-Augmented Generation (RAG) prototype that supports document ingestion, chunking, vector indexing, semantic retrieval, and context-aware question answering with a local LLM.

企业级 RAG 智能知识库（v1.0）是一个本地化知识问答原型系统，支持文档导入、文本切块、向量索引、语义检索，以及基于本地大语言模型的上下文问答能力。

This project is designed to demonstrate practical AI application engineering skills for real-world enterprise scenarios.

本项目旨在展示面向真实企业场景的 AI 应用工程能力。

---

## Features / 功能特性

- PDF document ingestion / PDF 文档导入
- Recursive chunking / 智能文本切块
- Embedding-based semantic retrieval / 基于向量语义检索
- Local vector database with Chroma / 本地 Chroma 向量数据库
- Local LLM generation via Ollama + Qwen / 本地模型问答（Ollama + Qwen）
- Fully offline deployable prototype / 可本地离线运行

---

## Tech Stack / 技术栈

### Backend
- Python 3.11
- FastAPI

### RAG Pipeline
- LangChain
- Chroma
- Sentence Transformers

### Local LLM
- Ollama
- Qwen2.5:1.5B

---

## Project Structure / 项目结构

```text
enterprise-rag/
├── app/
│   ├── main.py
│   ├── ingest.py
│   └── rag.py
├── data/
│   ├── raw/
│   └── vector_db/
├── requirements.txt
├── .gitignore
└── README.md

```

---
## Quick Start / 快速开始
1. Create Virtual Environment / 创建虚拟环境
```bash:
python -m venv .venv
```

Activate:

```bash:
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

2. Install Dependencies / 安装依赖
```bash:
pip install -r requirements.txt
```
3. Start Ollama / 启动本地模型
```bash:
ollama run qwen2.5:1.5b
```
4. Build Vector Database / 构建知识库索引
```bash:
python app/ingest.py
```
5. Run Retrieval QA / 启动问答系统
```bash:
python app/rag.py
```
### Example / 示例
Qustion / 问题:
```bash:
CUDA 里共享内存有什么作用？
```

Answer / 回答:
```bash:
共享内存位于 SM 内部，延迟低，常用于线程块内数据共享与缓存，可显著降低全局显存访问开销，但需避免 Bank Conflict。
```
---
## Roadmap / 后续规划
Hybrid Search (BM25 + Dense Retrieval)
Reranker Integration
Source Citation
Multi-user Support
FastAPI REST API
Web UI / Dify Integration
Evaluation Dashboard


## Author / 作者
7

Focused on AI Applications, RAG Systems, and ML Systems Engineering.

专注方向：AI 应用开发、RAG 系统、大模型工程化、ML Systems。