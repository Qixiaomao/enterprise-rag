# Enterprise RAG 升级路线

## 项目现状评估

- 混合检索（dense + BM25）✅
- 简单 jieba 重排序 ✅
- 单轮问答 API ✅
- 文档入库 + 管理 ✅
- 评估框架 ✅
- 前后端分离 ✅
- **多轮对话 / Agent** ❌
- **Multi-Agent 协作 / Harness** ❌
- **流式输出** ❌
- **Cross-Encoder 重排序** ❌
- **配置管理 / 可观测 / 容器化** ❌

---

## 阶段一：LangGraph Agent 改造（第 1-2 周）🔴 最优先

**目标：把单轮 RAG 升级为带 Tool Calling 的多轮对话 Agent**

### 要做的
- 封装 `retrieve_tool`：把现有混合检索包装成 Agent 可调用的工具
- 添加 `web_search_tool`：DuckDuckGo 免费搜索
- LangGraph create_react_agent 编排工具调用
- MemorySaver 实现多轮对话记忆
- 新增 `POST /chat` 端点（替代现有 `POST /ask`）

### 验收标准
- 用户问"总结一下 CUDA 优化的要点"，Agent 自动调用检索工具
- 用户追问"刚才说的第二点再详细讲讲"，Agent 能记住上下文
- 能跑通至少 5 轮连续对话不丢失上下文

---

## 阶段一扩展：Multi-Agent Harness（第 2-3 周）🔶 紧跟阶段一

**目标：单 Agent 跑稳后，快速升级为 Supervisor 多 Agent 协作系统**

### 架构思路

方案 A — 按能力域拆分：

```
Supervisor（调度者）+ RAG Agent + Web Agent + Reviewer Agent
```

共享 Harness 层：MemorySaver / Checkpointer / 错误恢复 / 全链路 Trace

### 要做的

- **Supervisor Agent**：LLM 意图路由，决定调用哪个子 Agent，汇总结果
  - 意图分类：查文档 / 搜网络 / 交叉验证 / 直接回答
  - 模型建议升级到 qwen2.5:7b（1.5b 逻辑判断不够稳）
- **RAG Agent**（现有 agent 降级为子 Agent）：在 retrieve_tool 基础上加 query_rewrite_tool（搜得不好自己改关键词重搜）
- **Web Agent**（现有 web_search_tool 独立成 Agent）：支持多轮搜索 + 结果筛选
- **Reviewer Agent**（新增）：事实核验、来源追溯、回答一致性检查
- **Harness 层统一能力**：
  - 统一 State 定义（所有 Agent 共享一个 State 字典）
  - 统一错误恢复（工具调用失败 → 自动重试/降级）
  - 全链路 Trace（每个 Agent 的决策过程可追溯）

### LangGraph 实现方式

- 使用 `create_react_agent` 分别构建 3 个子 Agent
- Supervisor 用 `Command` + 条件边实现路由
- 子 Agent 之间通过共享 State 通信
- 复用阶段一的 MemorySaver（一个 Checkpointer 管所有 Agent 记忆）

### 验收标准

- 用户问跨域问题（如"内部制度 vs 外部最佳实践"），Supervisor 自动拆解并调度
- 子 Agent 调用失败时，Supervisor 能感知并降级处理
- 能追踪到"Supervisor 为什么选了 RAG Agent"的决策依据
- 至少跑通 3 个典型多 Agent 协作场景

### 面试/公众号价值

- 面试谈点："从单 Agent 到 Multi-Agent 的演进，我是怎么设计 Supervisor 路由的"
- 公众号选题：《为什么一个 Agent 不够用？我的多 Agent 协作实践》
- Harness Engineering 概念落地：Memory / Trace / Error Recovery 的统一管理

---

## 阶段二：检索质量升级（第 3-4 周）

### 要做的
- jieba 词重叠 → `BAAI/bge-reranker-base` Cross-Encoder
- Query Rewriting：用 LLM 改写用户问题再检索
- 检索 top-k 从 4 → 20，Reranker 精选 top-3
- 增加 HyDE（假设性文档嵌入）检索策略

### 验收标准
- Top-1 检索准确率从 90% → 95%+
- 答案正确性得分从 75% → 85%+

---

## 阶段三：流式输出 + 体验优化（第 4-5 周）

### 要做的
- `POST /chat/stream` SSE 端点
- 前端打字机效果显示
- 对话历史侧边栏
- 会话管理（新建、切换、删除对话）

### 验收标准
- 第一个 token 在 500ms 内开始显示
- 对话历史可持久化，刷新页面不丢失

---

## 阶段四：工程化收尾（第 5-6 周）

### 要做的
- pydantic-settings 管理所有配置
- Docker Compose（一键启动前后端 + Ollama）
- 日志系统 + LangSmith trace
- API 限流 + 基本认证
- 模型升级到 qwen2.5:7b 或 14b

### 验收标准
- `docker compose up` 一条命令启动全部服务
- 有完整的日志和请求追踪

---

## 面试准备清单（持续进行）

- [ ] 3 个核心项目整理到 GitHub，README 含架构图 + Demo
- [ ] 准备一条"故事线"：为什么从底层转到应用层
- [ ] 准备回答：RAG 检索不准怎么排查？
- [ ] 准备回答：Agent 工具调用失败怎么处理？
- [ ] 准备回答：多轮对话上下文怎么管理？
- [ ] 准备回答：混合检索 vs 纯语义检索的取舍？
- [ ] 准备回答：为什么用 Supervisor 模式而不是 Swarm？多 Agent 怎么防止通信爆炸？
- [ ] 准备回答：Harness Engineering 是什么？你怎么在你的项目里实践的？
- [ ] 突出 CUDA/Transformer 底层经验的分析深度
