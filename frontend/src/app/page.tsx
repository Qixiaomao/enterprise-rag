"use client";

import { FormEvent, useState } from "react";

type SourceItem = {
  source_file: string;
  page: number | string;
  score: number;
  overlap_tokens: string[];
};

type AskResponse = {
  success: boolean;
  question: string;
  answer: string;
  sources: SourceItem[];
};

export default function Home() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!question.trim()) {
      setError("请输入问题。");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`请求失败，状态码: ${response.status}`);
      }

      const data: AskResponse = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("调用后端接口失败，请检查 FastAPI 服务是否正常启动。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Enterprise RAG Assistant
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            企业知识库智能助手 · Next.js + FastAPI
          </p>
        </header>

        <section className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="question"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                输入你的问题
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="例如：CUDA 里共享内存有什么作用？"
                className="min-h-[120px] w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-slate-500"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={loading}
                className="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "查询中..." : "提交问题"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setQuestion("");
                  setResult(null);
                  setError("");
                }}
                className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
              >
                清空
              </button>
            </div>
          </form>
        </section>

        {error && (
          <section className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </section>
        )}

        {result && (
          <section className="mt-6 space-y-6">
            <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
              <h2 className="text-lg font-semibold text-slate-900">问题</h2>
              <p className="mt-3 text-sm leading-7 text-slate-700">
                {result.question}
              </p>
            </div>

            <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
              <h2 className="text-lg font-semibold text-slate-900">回答</h2>
              <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-700">
                {result.answer}
              </p>
            </div>

            <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
              <h2 className="text-lg font-semibold text-slate-900">来源</h2>

              {result.sources.length === 0 ? (
                <p className="mt-3 text-sm text-slate-500">暂无来源信息。</p>
              ) : (
                <div className="mt-4 space-y-4">
                  {result.sources.map((source, index) => (
                    <div
                      key={`${source.source_file}-${index}`}
                      className="rounded-xl border border-slate-200 p-4"
                    >
                      <div className="text-sm font-medium text-slate-800">
                        [{index + 1}] {source.source_file}
                      </div>
                      <div className="mt-2 text-sm text-slate-600">
                        Page: {source.page} | Score: {source.score}
                      </div>
                      <div className="mt-2 text-sm text-slate-600">
                        Overlap Tokens:{" "}
                        {source.overlap_tokens.length > 0
                          ? source.overlap_tokens.join(", ")
                          : "无"}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}