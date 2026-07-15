"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/shell";
import { AttachmentLibrary } from "@/components/attachment-library";
import { api, formatDate, Page, User } from "@/lib/api";

function Content({ text }: { text: string }) {
  if (/<\/?[a-z][\s\S]*>/i.test(text)) return <article className="content rich-text-content" dangerouslySetInnerHTML={{ __html: text }} />;
  return <article className="content">{text.split("\n").map((line, index) => {
    if (line.startsWith("### ")) return <h3 key={index}>{line.slice(4)}</h3>;
    if (line.startsWith("## ")) return <h2 key={index}>{line.slice(3)}</h2>;
    if (line.startsWith("# ")) return <h1 key={index}>{line.slice(2)}</h1>;
    if (line.startsWith("- ")) return <p key={index}>• {line.slice(2)}</p>;
    return line ? <p key={index}>{line}</p> : <br key={index} />;
  })}</article>;
}

export default function KnowledgePage() {
  const params = useParams<{ slug: string }>(); const [page, setPage] = useState<Page | null>(null); const [favorite, setFavorite] = useState(false); const [user, setUser] = useState<User | null>(null); const [error, setError] = useState("");
  useEffect(() => {
    api<Page>(`/pages/${params.slug}`).then(setPage).catch((e) => setError(e.message));
    api<Page[]>("/favorites").then((items) => setFavorite(items.some((item) => item.slug === params.slug))).catch(() => setFavorite(false));
    api<User>("/auth/me").then(setUser).catch(() => setUser(null));
  }, [params.slug]);
  async function toggleFavorite() {
    if (!page) return;
    try { const result = await api<{ active: boolean }>(`/pages/${page.id}/favorite`, { method: "POST" }); setFavorite(result.active); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "收藏失败"); }
  }
  async function publishPage() {
    if (!page) return;
    try {
      const result = await api<Page>(`/pages/${page.id}/publish`, { method: "POST", body: JSON.stringify({ change_note: "发布知识" }) });
      setPage(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "发布失败");
    }
  }
  async function deletePage() {
    if (!page || !window.confirm(`确定永久删除“${page.title}”吗？此操作不可恢复。`)) return;
    try {
      await api<{ ok: boolean }>(`/pages/${page.id}`, { method: "DELETE" });
      window.location.href = "/";
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "删除失败");
    }
  }
  if (error) return <Shell><div className="empty">{error}。请先登录或返回首页。</div></Shell>;
  if (!page) return <Shell><div className="empty">正在加载知识…</div></Shell>;
  return <Shell><header className="page-header"><Link href="/" className="crumb">知识库 / {page.topic?.name ?? "未分类"}</Link><div className="page-title-row"><h1>{page.title}</h1><div className="page-actions">{user?.permissions.includes("content.edit") && page.status !== "published" && <button type="button" className="publish-link" onClick={publishPage}>发布知识</button>}{user?.permissions.includes("content.edit") && <Link className="edit-link" href={`/knowledge/${page.id}/edit`}>编辑知识</Link>}{user?.permissions.includes("content.delete") && <button type="button" className="danger-link" onClick={deletePage}>删除文档</button>}<button type="button" className={`favorite-button${favorite ? " active" : ""}`} onClick={toggleFavorite} aria-pressed={favorite}>{favorite ? "已收藏" : "收藏"}</button></div></div><p className="summary">{page.summary}</p>
    <div className="meta-row"><span>负责人：{page.owner?.name ?? "未设置"}</span><span>{page.status === "published" ? `已验证版本 ${page.current_version}` : "草稿，尚未发布"}</span><span>更新于 {formatDate(page.updated_at)}</span>{page.tags.map((tag) => <span className="tag" key={tag}>#{tag}</span>)}</div>
  </header><Content text={page.content} /><AttachmentLibrary pageId={page.id} /></Shell>;
}
