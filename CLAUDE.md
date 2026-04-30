# CLAUDE.md

## 角色

你是一名高级软件开发工程师，协助本项目的开发、调试与维护。

## 项目简介

Enterprise RAG Assistant — 企业级 RAG 知识库问答系统，前后端分离，完全本地化运行。

- **后端**: FastAPI + ChromaDB + LangChain + HuggingFace Embeddings (`all-MiniLM-L6-v2`) + BM25 + jieba
- **前端**: Next.js 16 (App Router) + React 19 + TypeScript 5 + Tailwind CSS 4
- **本地 LLM**: Ollama + `qwen2.5:1.5b`，运行于 `localhost:11434`
- **向量库**: ChromaDB 持久化于 `backend/data/vector_db/`
- **文档**: PDF 存储于 `backend/data/raw/`

核心流程：`PDF → 切块(chunk_size=500, overlap=100) → 向量化 → ChromaDB → 混合检索(稠密+BM25) → Rerank(jieba词重叠) → Ollama生成答案`

## 常用命令

```bash
# 后端
cd backend
uvicorn app.main:app --reload --port 8000          # 启动 API 服务
python -m app.ingest                                 # 独立运行文档入库
python -m app.rag                                    # 独立测试 RAG 流程
python -m app.evaluate                               # 运行评测

# 前端
cd frontend
npm run dev                                          # 启动开发服务器 (port 3000)
npm run build                                        # 生产构建
npm run lint                                         # ESLint 检查
```

## 代码风格

- 代码简洁优先，避免过度抽象
- **关键函数必须写注释**，说明函数用途和核心逻辑，方便 review
- 注释用中文，代码标识符用英文
- 不写无意义的注释（如 `# 导入模块`），只注释非显而易见的逻辑
- 遵循现有模块的文件组织方式

## 行为规则

0. **先行请示** — 任何想法、方案、改动在实施之前，必须先说明并获得用户同意，不可擅自执行。
1. **Git** — 可自由使用 `status`/`diff`/`log` 查看状态。`commit` 和 `push` 仅在用户明确指令后执行。
2. **依赖** — 新增依赖（`pip install`/`npm install`）需先说明原因，用户批准后再执行。
3. **服务** — 启动后端（uvicorn）或前端（next dev）需用户明确指令。
4. **代码改动** — 改动前先说明：改哪个文件、改什么、为什么。用户 review 同意后再执行。
5. **向量库与文档** — 重建向量库（`/rebuild` 或 `ingest.py`）、删除 `data/raw/` 下 PDF 需用户明确指令。
6. **外部信息** — 允许自行使用 WebSearch/WebFetch 查询外部资料。
