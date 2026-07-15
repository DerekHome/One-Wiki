"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BookmarkSimple, GearSix, SignOut, Sparkle } from "@phosphor-icons/react";
import { api, User } from "@/lib/api";
import { KnowledgeTree } from "@/components/knowledge-tree";

export function Shell({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [siteName, setSiteName] = useState("One WIKI");

  useEffect(() => {
    api<User>("/auth/me").then(setUser).catch(() => setUser(null));
    api<{ site_name: string }>("/settings/public").then((value) => setSiteName(value.site_name)).catch(() => undefined);
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
          <span className="logo-text"><strong>{siteName}</strong><small>团队知识资源库</small></span>
        </Link>
      </header>
      <aside className="sidebar">
        <KnowledgeTree />
        <nav className="dashboard-nav sidebar-actions">
          {user?.can_access_settings && <Link href="/settings"><GearSix size={17} weight="fill" />&#x7cfb;&#x7edf;&#x8bbe;&#x7f6e;</Link>}
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
