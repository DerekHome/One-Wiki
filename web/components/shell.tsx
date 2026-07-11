"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BookmarkSimple, SignOut, Sparkle } from "@phosphor-icons/react";
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
      <header className="dashboard-header">
        <Link href="/" className="dashboard-title" aria-label="One WIKI 首页">
          <span className="logo-mark">W</span>
          <span className="logo-text"><strong>One WIKI</strong><small>团队知识资源库</small></span>
        </Link>
      </header>
      <aside className="sidebar">
        <KnowledgeTree />
        <nav className="dashboard-nav sidebar-actions">
          {user && <Link href="/favorites"><BookmarkSimple size={17} weight="fill" />我的收藏</Link>}
          <Link href="/ask"><Sparkle size={17} weight="fill" />AI 问答</Link>
        </nav>
        <div className="sidebar-bottom">
          {user ? <><span className="user-name">{user.name}</span><button className="text-button" onClick={logout}><SignOut size={16} />退出登录</button></> : <Link href="/login">登录</Link>}
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
