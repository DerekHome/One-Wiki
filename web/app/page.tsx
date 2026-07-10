"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { PageCard } from "@/components/page-card";
import { Shell } from "@/components/shell";
import { api, Page, Topic } from "@/lib/api";

export default function HomePage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [pages, setPages] = useState<Page[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api<Topic[]>("/topics").then(setTopics).catch(() => setTopics([]));
    api<Page[]>("/pages").then(setPages).catch(() => setPages([]));
  }, []);

  function search(event: FormEvent) {
    event.preventDefault();
    if (query.trim()) window.location.href = `/search?q=${encodeURIComponent(query.trim())}`;
  }

  return <Shell>
    <section className="hero">
      <span className="eyebrow">团队知识平台</span>
      <h1>每个答案，都有可信来源。</h1>
      <p>从主题浏览、关键词搜索或 AI 问答开始，让团队知识更容易发现、理解和复用。</p>
      <form className="search-box" onSubmit={search}>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索知识，例如：产品定位、客户价值、使用方法" aria-label="搜索知识" />
        <button>搜索</button>
      </form>
    </section>
    <section className="section">
      <div className="section-head"><h2>按主题探索</h2></div>
      <div className="topics">{topics.map((topic) => <Link className="topic-chip" key={topic.id} href={`/search?topic=${topic.id}`}>{topic.name}</Link>)}</div>
    </section>
    <section className="section">
      <div className="section-head"><h2>最近更新</h2><Link href="/search">查看全部</Link></div>
      {pages.length ? <div className="cards">{pages.map((page) => <PageCard page={page} key={page.id} />)}</div> : <div className="empty">登录后即可浏览团队知识。</div>}
    </section>
  </Shell>;
}
