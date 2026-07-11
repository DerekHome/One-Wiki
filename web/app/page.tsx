"use client";

import Link from "next/link";
import { FormEvent, Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CaretRight, Funnel, MagnifyingGlass, Star } from "@phosphor-icons/react";
import { PageCard } from "@/components/page-card";
import { Shell } from "@/components/shell";
import { api, Page, Topic } from "@/lib/api";

function HomeContent() {
  const searchParams = useSearchParams();
  const selectedTopic = searchParams.get("topic");
  const [topics, setTopics] = useState<Topic[]>([]);
  const [pages, setPages] = useState<Page[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api<Topic[]>("/topics").then(setTopics).catch(() => setTopics([]));
  }, []);

  useEffect(() => {
    api<Page[]>("/pages?limit=200").then(setPages).catch(() => setPages([]));
  }, []);

  const activeTopic = useMemo(() => topics.find((topic) => topic.id === selectedTopic), [selectedTopic, topics]);
  const visiblePages = useMemo(() => {
    if (!selectedTopic) return pages;
    const childMap = new Map<string, string[]>();
    topics.forEach((topic) => {
      if (!topic.parent_id) return;
      childMap.set(topic.parent_id, [...(childMap.get(topic.parent_id) ?? []), topic.id]);
    });

    const topicIds = new Set<string>();
    const visit = (topicId: string) => {
      topicIds.add(topicId);
      (childMap.get(topicId) ?? []).forEach(visit);
    };
    visit(selectedTopic);
    return pages.filter((page) => page.topic?.id && topicIds.has(page.topic.id));
  }, [pages, selectedTopic, topics]);

  function search(event: FormEvent) {
    event.preventDefault();
    if (query.trim()) window.location.href = `/search?q=${encodeURIComponent(query.trim())}`;
  }

  return <Shell>
    <section className="dashboard-welcome">
      <CaretRight size={17} weight="fill" /><div><strong>欢迎来到智识库</strong><p>从这里浏览、沉淀和复用团队的重要资源。</p></div>
    </section>
    <section className="section">
      <div className="resource-toolbar"><div className="resource-title"><Star size={17} weight="fill" />团队资源</div><form className="resource-search" onSubmit={search}><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索资源" aria-label="搜索知识" /><button aria-label="搜索"><MagnifyingGlass size={17} /></button></form><Funnel className="toolbar-icon" size={17} /></div>
      <div className="topics">
        <Link className={`topic-chip${selectedTopic ? "" : " active"}`} href="/">全部</Link>
        {topics.map((topic) => <Link className={`topic-chip${selectedTopic === topic.id ? " active" : ""}`} key={topic.id} href={`/?topic=${topic.id}`}>{topic.name}</Link>)}
      </div>
    </section>
    <section className="section resource-section">
      <div className="section-head"><h2>{activeTopic ? activeTopic.name : "最近更新"}</h2>{selectedTopic ? <Link href="/">返回全部</Link> : <Link href="/search">查看全部</Link>}</div>
      {visiblePages.length ? <div className="cards">{visiblePages.map((page) => <PageCard page={page} key={page.id} />)}</div> : <div className="empty">{selectedTopic ? "这个目录下还没有发布知识。" : "登录后即可浏览团队知识。"}</div>}
    </section>
  </Shell>;
}

export default function HomePage() {
  return <Suspense fallback={null}><HomeContent /></Suspense>;
}
