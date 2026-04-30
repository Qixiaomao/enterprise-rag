
"""
LangGraph Agent 模块 —— 将 RAG 检索 + 网络搜索包装为 Agent 工具

架构已搭好，标记了 TODO 的地方需要你填充核心逻辑。
"""

import uuid
import wikipedia

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage


from app.rag import hybrid_retrieve, rerank_docs


## 加一个缓存
_retrieval_docs = [] # 模块级缓存，存最近一次检索结果，方便 Agent 调用工具时访问


# ============================================================
# 工具 1：知识库检索（你来写核心逻辑）
# ============================================================

@tool
def retrieve_tool(query: str) -> str:
    """检索企业知识库，获取与查询相关的文档内容和来源。当用户询问内部文档、技术知识、项目信息时调用此工具。"""
    # DONE: 实现检索逻辑
    # 提示：
    #   1. candidates = hybrid_retrieve(query, dense_k=4, bm25_k=4)
    candidates = hybrid_retrieve(query,dense_k=4,bm25_k=4)
    #   2. docs = rerank_docs(query, candidates, top_n=3)
    docs = rerank_docs(query,candidates,top_n=3)
    #   3. 遍历 docs，每篇文档格式化成可读字符串：
    global _retrieval_docs
    _retrieval_docs = [] # 更新缓存
    if not docs:
        return "未在知识库中找到相关文档。"
    parts = []
    for i, doc in enumerate(docs,1):
        source = doc["metadata"].get("source_file", "Unknown")
        page = doc["metadata"].get("page","N/A")
        content = doc["page_content"][:300] # 只取前300字符
        parts.append(f"来源[{i}]：{source} | 页: {page}\n内容：{content}")
        
    return "\n\n".join(parts)
    


# ============================================================
# 工具 2：网络搜索（你来写核心逻辑）
# ============================================================

@tool
def web_search_tool(query: str) -> str:
    """搜索互联网获取最新信息。当用户询问知识库以外的时事、新闻、实时数据时调用。"""
    # DONE: 实现网络搜索
    # 提示：
    #   1. from duckduckgo_search import DDGS
    #   2. results = DDGS().text(query, max_results=3)
    wikipedia.set_lang("zh") # 设置中文搜索
    results = wikipedia.search(query, results=3)  # DONE: 替换为 wikipedia
    #   3. 每条结果格式化成 "标题：xxx\n链接：xxx\n摘要：xxx"
    formatted_results = []
    #   4. 如果没有结果或异常，返回 "搜索失败或未找到结果。"
    if not results:
        return "搜索失败或未找到结果。"
    for result in results:
        title = result.get("title", "No Title")
        link = result.get("href", "No Link")
        snippet = result.get("body", "No Snippet")
        formatted_results.append(f"标题：{title}\n链接：{link}\n摘要：{snippet}")
    return "\n\n".join(formatted_results)


# ============================================================
# 模型与 Agent 初始化（你来写核心逻辑）
# ============================================================

# DONE: 初始化 ChatOllama 模型
model = ChatOllama(
        model = "qwen2.5:1.5b",
        base_url = "http://localhost:11434",
        temperature = 0
    )  # 替换为 ChatOllama(model="qwen2.5:1.5b", base_url="http://localhost:11434", temperature=0)

# 记忆组件（多轮对话靠它）
memory = MemorySaver()

# DONE: 创建 Agent，串联 model + tools + memory
agent = create_react_agent(
    model = model,
    tools = [retrieve_tool],
    checkpointer = memory
    )  # 替换为 create_react_agent(model, tools=[retrieve_tool, web_search_tool], checkpointer=memory)


# ============================================================
# 对外接口（已写好，可直接用）
# ============================================================

def chat(question: str, thread_id: str = None) -> dict:
    """单轮对话入口：向 Agent 发送问题，返回答案与来源"""
    if agent is None:
        raise RuntimeError("Agent 尚未初始化，请先完成 model 和 agent 的赋值。")

    if thread_id is None:
        thread_id = str(uuid.uuid4())

    # 调用 Agent（MemorySaver 自动管理对话历史）
    result = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    messages = result["messages"]
    answer = messages[-1].content

    # Done: 从 messages 中提取检索工具返回的文档作为 sources
    # 提示：遍历 messages，找到 name="retrieve_tool" 的 ToolMessage，解析其 content
    sources = list(_retrieval_docs)
    
    
    return {
        "success": True,
        "thread_id": thread_id,
        "question": question,
        "answer": answer,
        "sources": [],  # Done: 填充来源信息
    }


def new_session() -> str:
    """创建新会话"""
    return str(uuid.uuid4())
