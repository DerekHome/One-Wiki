"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BookmarkSimple, Brain, House, MagnifyingGlass, Plus, SignOut, Sparkle } from "@phosphor-icons/react";
import { api, User } from "@/lib/api";
import { KnowledgeTree } from "@/components/knowledge-tree";

export function Shell({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api<User>("/auth/me").then(setUser).catch(() => setUser(null));
  }, []);

  async function logout() {
    await api("/auth/logout", { method: "POST" });
    window.location.href = "/login";
  }

  return (
    <div className="app-shell">
      <header className="dashboard-header"><Link href="/" className="dashboard-title">智识库 <span>— 团队知识资源库</span></Link></header>
      <aside className="sidebar">
        <nav className="dashboard-nav">
          <Link href="/"><House size={17} weight="fill" />发现知识</Link>
          <Link href="/search"><MagnifyingGlass size={17} />搜索</Link>
          {user && <Link href="/favorites"><BookmarkSimple size={17} />我的收藏</Link>}
          <Link href="/ask"><Sparkle size={17} />AI 问答</Link>
          {user && ["contributor", "editor", "admin"].includes(user.role) && <Link href="/knowledge/new"><Plus size={17} />创建知识</Link>}
        </nav>
        <section className="sidebar-note"><h2>知识清单</h2><p>别让重要经验只停留在聊天记录里。</p><div><Brain size={17} weight="fill" /><span>沉淀可复用的知识、方法与资料。</span></div></section>
        <KnowledgeTree />
        <div className="sidebar-bottom">
          {user ? <><span className="user-name">{user.name}</span><button className="text-button" onClick={logout}><SignOut size={16} />退出登录</button></> : <Link href="/login">登录</Link>}
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
