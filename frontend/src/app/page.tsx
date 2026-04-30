"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type SourceItem = {
  source_file: string;
  page: number | string;
  score: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: SourceItem[];
};

type DocumentItem = {
  filename: string;
  size_kb: number;
};

const API = "http://127.0.0.1:8000";

export default function Home() {
  // === 对话状态 ===
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string>("");
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // === 侧边栏状态 ===
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [adminMsg, setAdminMsg] = useState("");
  const [adminLoading, setAdminLoading] = useState(false);

  // 滚动到最新消息
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // 拉取文档列表
  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API}/documents`);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch {
      // ignore
    }
  };

  // 展开侧边栏时加载文档
  useEffect(() => {
    if (sidebarOpen) fetchDocuments();
  }, [sidebarOpen]);

  // === 对话操作 ===
  const newChat = () => {
    setMessages([]);
    setThreadId("");
    setError("");
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const question = input.trim();
    if (!question) return;

    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          thread_id: threadId || null,
        }),
      });

      const data = await response.json();

      if (data.success) {
        if (data.thread_id && !threadId) setThreadId(data.thread_id);

        const assistantMsg: Message = {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } else {
        setError(data.answer || "请求失败");
      }
    } catch {
      setError("调用后端接口失败，请检查 FastAPI 服务是否启动。");
    } finally {
      setLoading(false);
    }
  };

  // === 文档管理操作 ===
  const uploadFile = async () => {
    if (!file) {
      setAdminMsg("请先选择 PDF 文件。");
      return;
    }
    setAdminLoading(true);
    setAdminMsg("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: formData });
      const data = await res.json();
      setAdminMsg(data.success ? `上传成功：${data.filename}` : "上传失败");
      setFile(null);
      if (data.success) await fetchDocuments();
    } catch {
      setAdminMsg("上传失败，请检查后端服务。");
    } finally {
      setAdminLoading(false);
    }
  };

  const rebuildIndex = async () => {
    setAdminLoading(true);
    setAdminMsg("正在重建知识库...");
    try {
      const res = await fetch(`${API}/rebuild`, { method: "POST" });
      const data = await res.json();
      setAdminMsg(data.success ? "知识库重建成功。" : "知识库重建失败。");
    } catch {
      setAdminMsg("重建失败，请检查后端服务。");
    } finally {
      setAdminLoading(false);
    }
  };

  return (
    <main className="flex h-screen bg-slate-50">
      {/* ==================== 侧边栏 ==================== */}
      <aside
        className={`flex-shrink-0 overflow-y-auto border-r border-slate-200 bg-white transition-all ${
          sidebarOpen ? "w-80 px-4 py-4" : "w-0 overflow-hidden"
        }`}
      >
        {sidebarOpen && (
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-slate-900">知识库管理</h2>

            {/* 上传 */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                上传 PDF
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <button
                onClick={uploadFile}
                disabled={adminLoading || !file}
                className="mt-2 w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
              >
                上传
              </button>
            </div>

            {/* 重建 */}
            <div>
              <button
                onClick={rebuildIndex}
                disabled={adminLoading}
                className="w-full rounded-lg border border-slate-300 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
              >
                重建知识库
              </button>
            </div>

            {adminMsg && (
              <p className="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-600">
                {adminMsg}
              </p>
            )}

            {/* 文档列表 */}
            <div>
              <h3 className="mb-2 text-sm font-semibold text-slate-700">
                文档列表 ({documents.length})
              </h3>
              {documents.length === 0 ? (
                <p className="text-xs text-slate-400">暂无文档</p>
              ) : (
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <div
                      key={doc.filename}
                      className="rounded-lg border border-slate-200 px-3 py-2 text-xs"
                    >
                      <span className="font-medium text-slate-800">{doc.filename}</span>
                      <span className="ml-2 text-slate-400">{doc.size_kb} KB</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </aside>

      {/* ==================== 聊天区 ==================== */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* 顶栏 */}
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
          <div className="flex items-center gap-3">
            {/* 侧边栏开关 */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 transition"
            >
              {sidebarOpen ? "收起" : "文档"}
            </button>
            <div>
              <h1 className="text-lg font-bold text-slate-900">
                Enterprise RAG Assistant
              </h1>
              <p className="text-xs text-slate-500">
                {threadId ? `会话: ${threadId.slice(0, 8)}...` : "新会话"}
              </p>
            </div>
          </div>
          <button
            onClick={newChat}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 transition"
          >
            新对话
          </button>
        </header>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 && !loading && (
            <div className="mt-20 text-center text-slate-400">
              <p className="text-lg">开始提问吧</p>
              <p className="mt-1 text-sm">使用下方输入框发送消息，或点击「文档」管理知识库</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`mb-4 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-7 ${
                  msg.role === "user"
                    ? "bg-slate-900 text-white"
                    : "bg-white text-slate-800 shadow-sm ring-1 ring-slate-200"
                }`}
              >
                <p className="whitespace-pre-line">{msg.content}</p>

                {msg.sources && msg.sources.length > 0 && (
                  <details className="mt-3 border-t border-slate-100 pt-2">
                    <summary className="cursor-pointer text-xs font-medium text-slate-500">
                      来源 ({msg.sources.length})
                    </summary>
                    <div className="mt-2 space-y-1">
                      {msg.sources.map((s, si) => (
                        <div key={si} className="text-xs text-slate-500">
                          [{si + 1}] {s.source_file} · Page {s.page} · Score {s.score}
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="mb-4 flex justify-start">
              <div className="rounded-2xl bg-white px-4 py-3 text-sm text-slate-400 shadow-sm ring-1 ring-slate-200">
                Agent 思考中...
              </div>
            </div>
          )}

          {error && (
            <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* 输入区 */}
        <div className="border-t border-slate-200 bg-white px-6 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的问题..."
              disabled={loading}
              className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none transition focus:border-slate-500 disabled:bg-slate-100"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-slate-900 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              发送
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
