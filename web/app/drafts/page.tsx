"use client";

import { useEffect, useState } from "react";
import { PageCard } from "@/components/page-card";
import { Shell } from "@/components/shell";
import { api, Page } from "@/lib/api";

export default function DraftsPage() {
  const [pages, setPages] = useState<Page[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Page[]>("/pages/drafts").then(setPages).catch((cause) => setError(cause instanceof Error ? cause.message : "加载草稿失败"));
  }, []);

  return <Shell>
    <section className="section favorites-page">
      <span className="eyebrow">创作工作台</span>
      <h1>草稿箱</h1>
      <p className="section-intro">这里集中存放尚未发布的知识草稿，确认内容后可进入详情页发布。</p>
      {error ? <div className="error">{error}</div> : pages.length ? <div className="cards">{pages.map((page) => <PageCard page={page} key={page.id} />)}</div> : <div className="empty">暂时没有草稿。点击左侧“+”新建知识，保存后会出现在这里。</div>}
    </section>
  </Shell>;
}
