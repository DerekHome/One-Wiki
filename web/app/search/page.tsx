"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { PageCard } from "@/components/page-card";
import { Shell } from "@/components/shell";
import { api, Page } from "@/lib/api";

function SearchContent() {
  const params = useSearchParams(); const initial = params.get("q") ?? "";
  const [query, setQuery] = useState(initial); const [pages, setPages] = useState<Page[]>([]); const [error, setError] = useState("");
  async function run(value = query) { if (!value.trim()) return; setError(""); try { setPages(await api<Page[]>(`/search?q=${encodeURIComponent(value.trim())}`)); } catch (reason) { setError(reason instanceof Error ? reason.message : "搜索失败"); } }
  useEffect(() => { if (initial) run(initial); }, [initial]);
  function submit(event: FormEvent) { event.preventDefault(); run(); }
  return <Shell><section className="form-page"><span className="eyebrow">知识搜索</span><h1>找到可靠的原始知识</h1>
    <form className="search-box" onSubmit={submit}><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="输入关键词" autoFocus /><button>搜索</button></form>
    {error && <p className="error">{error}</p>}
    <section className="section">{pages.length ? <div className="cards">{pages.map((page) => <PageCard page={page} key={page.id} />)}</div> : initial && <div className="empty">没有找到结果。换一个更具体的词，或到 AI 问答继续探索。</div>}</section>
  </section></Shell>;
}

export default function SearchPage() {
  return <Suspense fallback={<Shell><div className="empty">正在加载搜索…</div></Shell>}><SearchContent /></Suspense>;
}
