"""
LangGraph Agent 最小示例 —— 骨架文件

架构代码（导入 / 循环 / 配置）已写好，你只需要填充标记了 # TODO 的核心逻辑。

运行前确保 Ollama 已启动，模型已拉取。
"""

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.tools import tool


# ============================================================
# 第一部分：定义工具（你来写）
# ============================================================

# TODO: 用 @tool 装饰器定义 2 个工具函数
# 提示：docstring 就是工具的描述，LLM 会根据它决定是否调用
# 提示：参数类型注解必须写，LLM 靠它理解参数含义
# 提示：返回值是字符串，LLM 会读这个字符串作为工具执行结果
#
# 工具 1：get_text_length —— 统计一段文本的字符数
#        输入：text: str
#        输出：f"文本长度为 {len(text)} 个字符"
#
# 工具 2：calculator —— 计算数学表达式
#        输入：expression: str（如 "3 + 5 * 2"）
#        输出：f"计算结果：{result}"

@tool 
def get_text_length(text: str) -> str:
    "计算输入文本的字符数，返回文本长度"
    return f"文本长度为{len(text)}个字符"


@tool
def calculator(expression: str) -> str:
    "计算一个数学表达式，返回计算结果"
    try:
        #注意：eval 有安全风险，实际项目中请用更安全的解析库
        result = eval(expression, {"__builtins__":{}})
        return f"计算结果:{result}"
    except Exception as e:
        return f"计算错误:{str(e)}"    
    
    
# ============================================================
# 第二部分：初始化模型和 Agent（你来写）
# ============================================================

# 初始化 Ollama 模型
# DONE: 创建 ChatOllama 实例
# 提示：ChatOllama(model="模型名", base_url="http://localhost:11434", temperature=0)
#
# ⚠️ 注意：qwen2.5:1.5b 可能不支持原生 tool calling。
# 如果调不通，换 qwen2.5:7b 或 qwen3:8b（先 ollama pull）
# 或者用 ChatOpenAI 接 DeepSeek API 做实验（tool calling 更稳定）

# 定义了模型之后，接下来要把模型、工具和记忆串起来，创建一个 Agent。
model = ChatOllama(
        model = "qwen2.5:1.5b",
        base_url = "http://localhost:11434",
        temperature = 0
    )  # DONE: 替换为 ChatOllama(...)

# 初始化记忆（多轮对话靠它）
memory = MemorySaver()

# 创建 Agent
# DONE: 用 create_react_agent 把 model + tools + memory 串起来
# 提示：create_react_agent(model, tools=[...], checkpointer=memory)

agent = create_react_agent(
    tools = [get_text_length, calculator],
    model = model,
    checkpointer = memory
    )  # DONE: 替换为 create_react_agent(...)


# ============================================================
# 第三部分：交互循环（已写好，可以跑）
# ============================================================

def main():
    if agent is None or model is None:
        print("❌ 请先完成 agent 和 model 的初始化（替换 None）。")
        return

    print("=" * 50)
    print("🤖 LangGraph Agent 已就绪")
    print("输入 'exit' 退出 | 输入 'new' 开始新会话")
    print("=" * 50)

    thread_id = "session-1"

    while True:
        try:
            user_input = input("\n🧑 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("👋 再见！")
            break

        if user_input.lower() == "new":
            thread_id = f"session-{hash(user_input) % 10000}"
            print(f"🆕 新会话: {thread_id}")
            continue

        # 调用 Agent
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        # 提取最后一条 AI 消息
        # TODO: 思考一下，如果 agent 调了工具，result["messages"] 里有哪些消息？
        # 提示：自己 print(result["messages"]) 看看结构
        last_message = result["messages"][-1]
        print(f"messages: {result['messages']}")
        print(f"\n🤖 Agent: {last_message.content}")


if __name__ == "__main__":
    main()
