"use client";

import { useEffect, useMemo, useState } from "react";

type DocumentItem = {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  created_at: string;
  updated_at: string;
};

type SourceItem = {
  document_id: string;
  filename: string;
  content: string;
  score: number;
};

type UploadLog = {
  name: string;
  status: "queued" | "success" | "error";
  message: string;
};

const API_BASE = "/api/proxy";

function formatBytes(bytes: number) {
  if (!bytes) return "0 KB";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<"online" | "offline">(
    "offline"
  );
  const [token, setToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [uploadLog, setUploadLog] = useState<UploadLog[]>([]);
  const [ragQuery, setRagQuery] = useState("");
  const [ragTopK, setRagTopK] = useState(4);
  const [ragAnswer, setRagAnswer] = useState<string | null>(null);
  const [ragSources, setRagSources] = useState<SourceItem[]>([]);
  const [ragLoading, setRagLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "overview" | "documents" | "rag"
  >("overview");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => setBackendStatus(res.ok ? "online" : "offline"))
      .catch(() => setBackendStatus("offline"));
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem("rag_admin_token");
    const storedEmail = localStorage.getItem("rag_admin_email");
    if (storedToken) setToken(storedToken);
    if (storedEmail) setUserEmail(storedEmail);
  }, []);

  useEffect(() => {
    if (token) {
      fetchDocuments();
    }
  }, [token]);

  const statusStyles = useMemo(
    () => ({
      ready: "bg-[var(--sun-400)] text-[var(--ink-900)]",
      processing: "bg-[var(--sun-600)] text-white",
      failed: "bg-[var(--danger-500)] text-white",
      completed: "bg-[var(--sage-700)] text-white",
    }),
    []
  );

  async function login() {
    setLoginError(null);
    const body = new URLSearchParams();
    body.set("username", loginEmail);
    body.set("password", loginPassword);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setLoginError(data.detail ?? "로그인에 실패했습니다.");
      return;
    }

    const data = await res.json();
    localStorage.setItem("rag_admin_token", data.access_token);
    localStorage.setItem("rag_admin_email", loginEmail);
    setToken(data.access_token);
    setUserEmail(loginEmail);
    setLoginEmail("");
    setLoginPassword("");
  }

  function logout() {
    localStorage.removeItem("rag_admin_token");
    localStorage.removeItem("rag_admin_email");
    setToken(null);
    setUserEmail(null);
  }

  async function fetchDocuments() {
    if (!token) return;
    setDocsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/documents/?limit=50`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        setDocs([]);
      } else {
        const data = (await res.json()) as DocumentItem[];
        setDocs(data);
      }
    } finally {
      setDocsLoading(false);
    }
  }

  async function handleUpload() {
    if (!uploadFiles || !token) return;
    const files = Array.from(uploadFiles);
    setUploadLog(
      files.map((file) => ({
        name: file.name,
        status: "queued",
        message: "업로드 대기 중",
      }))
    );

    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);
      try {
        const res = await fetch(`${API_BASE}/documents/upload`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });
        if (!res.ok) {
          const message = await res.text();
          setUploadLog((prev) =>
            prev.map((entry) =>
              entry.name === file.name
                ? {
                    ...entry,
                    status: "error",
                    message: message || "업로드 실패",
                  }
                : entry
            )
          );
          continue;
        }
        const data = await res.json();
        setUploadLog((prev) =>
          prev.map((entry) =>
            entry.name === file.name
              ? {
                  ...entry,
                  status: "success",
                  message: `처리 큐 등록 (${data.task_id})`,
                }
              : entry
          )
        );
      } catch (err) {
        setUploadLog((prev) =>
          prev.map((entry) =>
            entry.name === file.name
              ? {
                  ...entry,
                  status: "error",
                  message: "네트워크 오류",
                }
              : entry
          )
        );
      }
    }

    await fetchDocuments();
  }

  async function deleteDocument(id: string) {
    if (!token) return;
    const confirmed = confirm("정말로 삭제하시겠습니까? 복구 불가합니다.");
    if (!confirmed) return;

    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      fetchDocuments();
    }
  }

  async function runRagTest() {
    if (!ragQuery) return;
    setRagLoading(true);
    setRagAnswer(null);
    setRagSources([]);
    try {
      const res = await fetch(`${API_BASE}/chat/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: ragQuery, top_k: ragTopK }),
      });
      if (res.ok) {
        const data = await res.json();
        setRagAnswer(data.answer);
        setRagSources(data.sources ?? []);
      } else {
        setRagAnswer("요청이 실패했습니다.");
      }
    } finally {
      setRagLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="app-shell flex items-center justify-center px-6 py-20">
        <div className="fade-up relative z-10 w-full max-w-xl rounded-[32px] bg-[var(--card)] p-10 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-[var(--ink-600)]">
                Enterprise RAG
              </p>
              <h1 className="mt-3 text-3xl font-semibold text-[var(--ink-900)]">
                Admin Console
              </h1>
            </div>
            <span className="rounded-full border border-[var(--ink-200)] px-4 py-1 text-xs font-semibold text-[var(--ink-600)]">
              {backendStatus === "online" ? "Backend Online" : "Backend Offline"}
            </span>
          </div>

          <div className="mt-10 space-y-5">
            <div>
              <label className="text-sm font-semibold text-[var(--ink-600)]">
                Email
              </label>
              <input
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder="admin@example.com"
                className="mt-2 w-full rounded-2xl border border-[var(--ink-200)] bg-white px-4 py-3 text-sm shadow-sm focus:border-[var(--sun-600)] focus:outline-none"
              />
            </div>
            <div>
              <label className="text-sm font-semibold text-[var(--ink-600)]">
                Password
              </label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="admin123"
                className="mt-2 w-full rounded-2xl border border-[var(--ink-200)] bg-white px-4 py-3 text-sm shadow-sm focus:border-[var(--sun-600)] focus:outline-none"
              />
            </div>
            {loginError && (
              <p className="text-sm text-[var(--danger-500)]">{loginError}</p>
            )}
            <button
              onClick={login}
              className="w-full rounded-2xl bg-[var(--ink-900)] px-6 py-3 text-sm font-semibold text-[var(--ink-100)] transition hover:opacity-90"
            >
              Login
            </button>
          </div>

          <div className="mt-8 rounded-2xl border border-[var(--ink-200)] bg-white/60 px-5 py-4 text-sm text-[var(--ink-600)]">
            초기 관리자 계정: admin@example.com / admin123
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <div className="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 pb-16 pt-10">
        <header className="flex flex-col gap-6 rounded-[32px] bg-[var(--card)] p-8 shadow-[var(--shadow)] backdrop-blur fade-up">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-[var(--ink-600)]">
                Enterprise RAG
              </p>
              <h1 className="mt-2 text-3xl font-semibold text-[var(--ink-900)]">
                Admin Console
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full border border-[var(--ink-200)] px-4 py-1 text-xs font-semibold text-[var(--ink-600)]">
                {backendStatus === "online" ? "Backend Online" : "Backend Offline"}
              </span>
              <span className="rounded-full bg-[var(--ink-900)] px-4 py-1 text-xs font-semibold text-[var(--ink-100)]">
                {userEmail ?? "admin"}
              </span>
              <button
                onClick={logout}
                className="rounded-full border border-[var(--ink-200)] px-4 py-1 text-xs font-semibold text-[var(--ink-600)] transition hover:border-[var(--ink-600)]"
              >
                Logout
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-3 text-sm text-[var(--ink-600)]">
            <span className="rounded-full bg-white/80 px-4 py-2">
              Backend: proxied /api/v1
            </span>
            <span className="rounded-full bg-white/80 px-4 py-2">
              Documents: {docs.length}
            </span>
            <span className="rounded-full bg-white/80 px-4 py-2">
              Last refresh: {docsLoading ? "loading..." : new Date().toLocaleTimeString()}
            </span>
          </div>
        </header>

        <nav className="flex flex-wrap gap-3 text-sm font-semibold text-[var(--ink-600)] fade-up">
          {[
            { id: "overview", label: "Overview" },
            { id: "documents", label: "Documents" },
            { id: "rag", label: "RAG Test" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() =>
                setActiveTab(tab.id as "overview" | "documents" | "rag")
              }
              className={`rounded-full px-5 py-2 transition ${
                activeTab === tab.id
                  ? "bg-[var(--ink-900)] text-[var(--ink-100)]"
                  : "bg-white/70 hover:bg-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {activeTab === "overview" && (
          <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="fade-up rounded-[32px] bg-[var(--card)] p-8 shadow-[var(--shadow)] backdrop-blur">
              <h2 className="text-xl font-semibold text-[var(--ink-900)]">
                Upload New Documents
              </h2>
              <p className="mt-2 text-sm text-[var(--ink-600)]">
                문서를 업로드하면 비동기 처리 큐로 넘어가며, 처리 상태는
                목록에서 확인할 수 있어요.
              </p>
              <div className="mt-6 space-y-4">
                <input
                  type="file"
                  multiple
                  onChange={(e) => setUploadFiles(e.target.files)}
                  className="w-full rounded-2xl border border-dashed border-[var(--ink-200)] bg-white/70 p-6 text-sm"
                />
                <button
                  onClick={handleUpload}
                  className="w-full rounded-2xl bg-[var(--sun-600)] px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90"
                >
                  Upload & Queue
                </button>
              </div>

              <div className="mt-6 space-y-3">
                {uploadLog.length === 0 && (
                  <p className="text-sm text-[var(--ink-600)]">
                    업로드 로그가 아직 없습니다.
                  </p>
                )}
                {uploadLog.map((entry) => (
                  <div
                    key={entry.name}
                    className="flex items-center justify-between rounded-2xl border border-[var(--ink-200)] bg-white/70 px-4 py-3 text-sm"
                  >
                    <div>
                      <p className="font-semibold text-[var(--ink-900)]">
                        {entry.name}
                      </p>
                      <p className="text-xs text-[var(--ink-600)]">
                        {entry.message}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        entry.status === "success"
                          ? "bg-[var(--sage-700)] text-white"
                          : entry.status === "error"
                          ? "bg-[var(--danger-500)] text-white"
                          : "bg-[var(--sun-400)] text-[var(--ink-900)]"
                      }`}
                    >
                      {entry.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="fade-up rounded-[32px] bg-[var(--card)] p-8 shadow-[var(--shadow)] backdrop-blur">
              <h2 className="text-xl font-semibold text-[var(--ink-900)]">
                Document Snapshot
              </h2>
              <p className="mt-2 text-sm text-[var(--ink-600)]">
                최근 문서 상태를 요약해서 보여줍니다.
              </p>
              <div className="mt-6 space-y-3">
                {docs.slice(0, 5).map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between rounded-2xl border border-[var(--ink-200)] bg-white/70 px-4 py-3 text-sm"
                  >
                    <div>
                      <p className="font-semibold text-[var(--ink-900)]">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-[var(--ink-600)]">
                        {formatBytes(doc.file_size)} ·{" "}
                        {formatDate(doc.created_at)}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        statusStyles[
                          doc.status.toLowerCase() as keyof typeof statusStyles
                        ] ?? "bg-[var(--ink-200)] text-[var(--ink-900)]"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                ))}
                {docs.length === 0 && (
                  <p className="text-sm text-[var(--ink-600)]">
                    아직 등록된 문서가 없습니다.
                  </p>
                )}
              </div>
              <button
                onClick={fetchDocuments}
                className="mt-6 w-full rounded-2xl border border-[var(--ink-200)] px-4 py-3 text-sm font-semibold text-[var(--ink-600)] transition hover:border-[var(--ink-600)]"
              >
                Refresh Documents
              </button>
            </div>
          </section>
        )}

        {activeTab === "documents" && (
          <section className="fade-up rounded-[32px] bg-[var(--card)] p-8 shadow-[var(--shadow)] backdrop-blur">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-[var(--ink-900)]">
                  Registered Documents
                </h2>
                <p className="mt-2 text-sm text-[var(--ink-600)]">
                  처리 상태와 파일 정보를 확인하고 문서를 관리합니다.
                </p>
              </div>
              <button
                onClick={fetchDocuments}
                className="rounded-full border border-[var(--ink-200)] px-4 py-2 text-sm font-semibold text-[var(--ink-600)] transition hover:border-[var(--ink-600)]"
              >
                Refresh
              </button>
            </div>

            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-y-3 text-left text-sm">
                <thead className="text-xs uppercase tracking-[0.2em] text-[var(--ink-600)]">
                  <tr>
                    <th className="px-3">Filename</th>
                    <th className="px-3">Type</th>
                    <th className="px-3">Size</th>
                    <th className="px-3">Status</th>
                    <th className="px-3">Created</th>
                    <th className="px-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {docs.map((doc) => (
                    <tr
                      key={doc.id}
                      className="rounded-2xl bg-white/80 shadow-sm"
                    >
                      <td className="px-3 py-4 font-semibold text-[var(--ink-900)]">
                        {doc.filename}
                        <p className="text-xs font-normal text-[var(--ink-600)]">
                          {doc.id}
                        </p>
                      </td>
                      <td className="px-3 py-4">{doc.file_type}</td>
                      <td className="px-3 py-4">
                        {formatBytes(doc.file_size)}
                      </td>
                      <td className="px-3 py-4">
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${
                            statusStyles[
                              doc.status.toLowerCase() as keyof typeof statusStyles
                            ] ?? "bg-[var(--ink-200)] text-[var(--ink-900)]"
                          }`}
                        >
                          {doc.status}
                        </span>
                      </td>
                      <td className="px-3 py-4">
                        {formatDate(doc.created_at)}
                      </td>
                      <td className="px-3 py-4">
                        <button
                          onClick={() => deleteDocument(doc.id)}
                          className="rounded-full border border-[var(--danger-500)] px-3 py-1 text-xs font-semibold text-[var(--danger-500)] transition hover:bg-[var(--danger-500)] hover:text-white"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {docsLoading && (
                <p className="mt-6 text-sm text-[var(--ink-600)]">
                  문서 목록을 불러오는 중입니다...
                </p>
              )}
            </div>
          </section>
        )}

        {activeTab === "rag" && (
          <section className="grid gap-8 lg:grid-cols-[1fr_1.1fr]">
            <div className="fade-up rounded-[32px] bg-[var(--card)] p-8 shadow-[var(--shadow)] backdrop-blur">
              <h2 className="text-xl font-semibold text-[var(--ink-900)]">
                RAG Quality Test
              </h2>
              <p className="mt-2 text-sm text-[var(--ink-600)]">
                실제 질문을 던져 답변과 근거 문서를 확인하세요.
              </p>
              <div className="mt-6 space-y-4">
                <textarea
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  placeholder="예: 재택 근무 규정이 어떻게 되나요?"
                  className="min-h-[140px] w-full rounded-2xl border border-[var(--ink-200)] bg-white/70 p-4 text-sm focus:border-[var(--sage-700)] focus:outline-none"
                />
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 text-sm text-[var(--ink-600)]">
                    Top K
                    <input
                      type="range"
                      min={1}
                      max={10}
                      value={ragTopK}
                      onChange={(e) => setRagTopK(Number(e.target.value))}
                    />
                    <span className="rounded-full bg-white/80 px-3 py-1 text-xs">
                      {ragTopK}
                    </span>
                  </div>
                  <button
                    onClick={runRagTest}
                    className="rounded-full bg-[var(--sage-700)] px-6 py-2 text-sm font-semibold text-white transition hover:opacity-90"
                  >
                    {ragLoading ? "Generating..." : "Run Test"}
                  </button>
                </div>
              </div>
            </div>

            <div className="fade-up rounded-[32px] bg-[var(--card)] p-8 shadow-[var(--shadow)] backdrop-blur">
              <h2 className="text-xl font-semibold text-[var(--ink-900)]">
                Answer & Sources
              </h2>
              <div className="mt-4 space-y-4">
                <div className="rounded-2xl border border-[var(--ink-200)] bg-white/80 p-4 text-sm text-[var(--ink-900)]">
                  {ragAnswer ?? "아직 답변이 없습니다."}
                </div>
                <div className="space-y-3">
                  {ragSources.map((source, index) => (
                    <details
                      key={`${source.document_id}-${index}`}
                      className="rounded-2xl border border-[var(--ink-200)] bg-white/80 p-4"
                    >
                      <summary className="cursor-pointer text-sm font-semibold text-[var(--ink-900)]">
                        {source.filename} · score {source.score.toFixed(3)}
                      </summary>
                      <p className="mt-3 text-sm text-[var(--ink-600)]">
                        {source.content}
                      </p>
                    </details>
                  ))}
                  {ragSources.length === 0 && (
                    <p className="text-sm text-[var(--ink-600)]">
                      근거 문서가 아직 없습니다.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
