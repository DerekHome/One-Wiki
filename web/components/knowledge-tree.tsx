"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Article, CaretDown, CaretRight, Folder } from "@phosphor-icons/react";
import { api, Page, Topic } from "@/lib/api";

type TopicNode = Topic & {
  children: TopicNode[];
  pages: Page[];
};

function buildTree(topics: Topic[], pages: Page[]) {
  const nodes = new Map<string, TopicNode>();
  topics.forEach((topic) => nodes.set(topic.id, { ...topic, children: [], pages: [] }));

  const roots: TopicNode[] = [];
  nodes.forEach((node) => {
    const parent = node.parent_id ? nodes.get(node.parent_id) : null;
    if (parent) parent.children.push(node);
    else roots.push(node);
  });

  pages.forEach((page) => {
    if (page.topic?.id && nodes.has(page.topic.id)) nodes.get(page.topic.id)!.pages.push(page);
  });

  const sortNodes = (items: TopicNode[]) => {
    items.sort((left, right) => left.name.localeCompare(right.name, "zh-CN"));
    items.forEach((item) => {
      item.pages.sort((left, right) => left.title.localeCompare(right.title, "zh-CN"));
      sortNodes(item.children);
    });
  };
  sortNodes(roots);
  return roots;
}

function TopicBranch({ node, activeTopic }: { node: TopicNode; activeTopic: string | null }) {
  const [open, setOpen] = useState(true);
  const hasChildren = node.children.length > 0 || node.pages.length > 0;

  return (
    <li className="tree-node">
      <div className={`tree-topic${activeTopic === node.id ? " active" : ""}`}>
        <button
          type="button"
          className="tree-toggle"
          onClick={() => setOpen((value) => !value)}
          disabled={!hasChildren}
          aria-label={open ? "收起目录" : "展开目录"}
        >
          {hasChildren ? open ? <CaretDown size={12} /> : <CaretRight size={12} /> : <span />}
        </button>
        <Link href={`/?topic=${node.id}`}>
          <Folder size={15} weight="fill" />
          <span>{node.name}</span>
        </Link>
      </div>
      {open && hasChildren && (
        <ul className="tree-children">
          {node.children.map((child) => <TopicBranch node={child} activeTopic={activeTopic} key={child.id} />)}
          {node.pages.map((page) => (
            <li className="tree-page" key={page.id}>
              <Link href={`/knowledge/${page.slug}`}>
                <Article size={14} />
                <span>{page.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}

export function KnowledgeTree() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [pages, setPages] = useState<Page[]>([]);
  const [activeTopic, setActiveTopic] = useState<string | null>(null);

  useEffect(() => {
    api<Topic[]>("/topics").then(setTopics).catch(() => setTopics([]));
    api<Page[]>("/pages?limit=200").then(setPages).catch(() => setPages([]));
  }, []);

  useEffect(() => {
    const updateActiveTopic = () => setActiveTopic(new URLSearchParams(window.location.search).get("topic"));
    updateActiveTopic();
    window.addEventListener("popstate", updateActiveTopic);
    return () => window.removeEventListener("popstate", updateActiveTopic);
  }, []);

  const tree = useMemo(() => buildTree(topics, pages), [topics, pages]);
  const uncategorizedPages = pages.filter((page) => !page.topic);

  if (!tree.length && !uncategorizedPages.length) {
    return <section className="knowledge-tree"><h2>目录</h2><p className="tree-empty">暂无可浏览知识</p></section>;
  }

  return (
    <section className="knowledge-tree">
      <div className="tree-head">
        <h2>知识目录</h2>
        <Link href="/">全部</Link>
      </div>
      <ul className="tree-root">
        {tree.map((node) => <TopicBranch node={node} activeTopic={activeTopic} key={node.id} />)}
        {uncategorizedPages.length > 0 && (
          <li className="tree-node">
            <div className="tree-topic"><span className="tree-toggle" /><Link href="/"><Folder size={15} weight="fill" /><span>未分类</span></Link></div>
            <ul className="tree-children">
              {uncategorizedPages.map((page) => (
                <li className="tree-page" key={page.id}>
                  <Link href={`/knowledge/${page.slug}`}><Article size={14} /><span>{page.title}</span></Link>
                </li>
              ))}
            </ul>
          </li>
        )}
      </ul>
    </section>
  );
}
