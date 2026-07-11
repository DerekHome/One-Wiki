"use client";

import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { MagnifyingGlass } from "@phosphor-icons/react";
import { PageCard } from "@/components/page-card";
import { Shell } from "@/components/shell";
import { api, Page, Topic } from "@/lib/api";

function HomeContent() {
  const searchParams = useSearchParams();
  const selectedTopic = searchParams.get("topic");
  const [topics, setTopics] = useState<Topic[]>([]);
  const [pages, setPages] = useState<Page[]>([]);
  const [query, setQuery] = useState("");
  const [timeRange, setTimeRange] = useState("all");
  const [sortOrder, setSortOrder] = useState("newest");

  useEffect(() => {
    api<Topic[]>("/topics").then(setTopics).catch(() => setTopics([]));
  }, []);

  useEffect(() => {
    api<Page[]>("/pages?limit=100").then(setPages).catch(() => setPages([]));
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

  const filteredPages = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    const now = Date.now();
    const days = timeRange === "all" ? null : Number(timeRange);

    return visiblePages
      .filter((page) => {
        if (!keyword) return true;
        const searchable = [page.title, page.summary, page.topic?.name ?? "", page.tags.join(" "), page.content].join(" ").toLowerCase();
        return searchable.includes(keyword);
      })
      .filter((page) => {
        if (!days) return true;
        const updatedAt = new Date(page.updated_at).getTime();
        return now - updatedAt <= days * 24 * 60 * 60 * 1000;
      })
      .sort((left, right) => {
        const diff = new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime();
        return sortOrder === "newest" ? diff : -diff;
      });
  }, [query, sortOrder, timeRange, visiblePages]);

  return <Shell>
    <section className="section section-compact">
      <div className="resource-filters" aria-label="知识筛选">
        <label className="filter-search">
          <MagnifyingGlass size={16} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="按标题、摘要、标签或正文筛选" aria-label="按关键字筛选知识" />
        </label>
        <label>
          <span>更新时间</span>
          <select value={timeRange} onChange={(event) => setTimeRange(event.target.value)} aria-label="按更新时间筛选">
            <option value="all">全部时间</option>
            <option value="7">最近 7 天</option>
            <option value="30">最近 30 天</option>
            <option value="90">最近 90 天</option>
          </select>
        </label>
        <label>
          <span>排序</span>
          <select value={sortOrder} onChange={(event) => setSortOrder(event.target.value)} aria-label="排序方式">
            <option value="newest">最新优先</option>
            <option value="oldest">最早优先</option>
          </select>
        </label>
        <span className="filter-count">{filteredPages.length} 条</span>
      </div>
    </section>
    <section className="section resource-section">
      <div className="section-head"><h2>{activeTopic ? activeTopic.name : "最近更新"}</h2><Link href="/knowledge/new">新增知识</Link></div>
      {filteredPages.length ? <div className="cards">{filteredPages.map((page) => <PageCard page={page} key={page.id} />)}</div> : <div className="empty">{visiblePages.length ? "没有符合当前筛选条件的知识。" : selectedTopic ? "这个目录下还没有发布知识。" : "登录后即可浏览团队知识。"}</div>}
    </section>
  </Shell>;
}

export default function HomePage() {
  return <Suspense fallback={null}><HomeContent /></Suspense>;
}
