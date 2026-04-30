"use client";

import { useEffect, useState } from "react";

type DocumentItem = {
  filename: string;
  size_kb: number;
};

export default function AdminPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchDocuments = async () => {
    const res = await fetch("http://127.0.0.1:8000/documents");
    const data = await res.json();
    setDocuments(data.documents || []);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const uploadFile = async () => {
    if (!file) {
      setMessage("请先选择 PDF 文件。");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setMessage(data.success ? `上传成功：${data.filename}` : "上传失败");
      setFile(null);
      await fetchDocuments();
    } catch {
      setMessage("上传接口调用失败。");
    } finally {
      setLoading(false);
    }
  };

  const rebuildIndex = async () => {
    setLoading(true);
    setMessage("正在重建知识库...");

    try {
      const res = await fetch("http://127.0.0.1:8000/rebuild", {
        method: "POST",
      });

      const data = await res.json();
      setMessage(data.success ? "知识库重建成功。" : "知识库重建失败。");
    } catch {
      setMessage("重建接口调用失败。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Knowledge Base Admin
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            文档上传 · 知识库管理 · 在线重建索引
          </p>
        </header>

        <section className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">上传文档</h2>

          <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full rounded-xl border border-slate-300 px-4 py-2 text-sm"
            />

            <button
              onClick={uploadFile}
              disabled={loading}
              className="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
            >
              上传
            </button>

            <button
              onClick={rebuildIndex}
              disabled={loading}
              className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-60"
            >
              重建知识库
            </button>
          </div>

          {message && (
            <p className="mt-4 rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
              {message}
            </p>
          )}
        </section>

        <section className="mt-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">文档列表</h2>

          {documents.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">暂无文档。</p>
          ) : (
            <div className="mt-4 space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.filename}
                  className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3"
                >
                  <span className="text-sm font-medium text-slate-800">
                    {doc.filename}
                  </span>
                  <span className="text-sm text-slate-500">
                    {doc.size_kb} KB
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}