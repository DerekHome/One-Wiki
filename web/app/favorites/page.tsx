"use client";

import { useEffect, useState } from "react";
import { PageCard } from "@/components/page-card";
import { Shell } from "@/components/shell";
import { api, Page } from "@/lib/api";

export default function FavoritesPage() {
  const [pages, setPages] = useState<Page[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Page[]>("/favorites").then(setPages).catch((cause) => setError(cause instanceof Error ? cause.message : "加载收藏失败"));
  }, []);

  return <Shell>
    <section className="section favorites-page">
      <span className="eyebrow">我的知识</span>
      <h1>我的收藏</h1>
      <p className="section-intro">将常用或重要的知识保存在这里，方便随时回看。</p>
      {error ? <div className="error">{error}</div> : pages.length ? <div className="cards">{pages.map((page) => <PageCard page={page} key={page.id} />)}</div> : <div className="empty">还没有收藏。阅读知识时点击“收藏”，它会出现在这里。</div>}
    </section>
  </Shell>;
}
