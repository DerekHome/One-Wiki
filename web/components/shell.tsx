"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, User } from "@/lib/api";

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
      <aside className="sidebar">
        <Link href="/" className="brand"><span>✦</span> 智识库</Link>
        <p className="brand-note">让可信知识随时可用</p>
        <nav>
          <Link href="/">发现知识</Link>
          <Link href="/search">搜索</Link>
          {user && <Link href="/favorites">我的收藏</Link>}
          <Link href="/ask">AI 问答</Link>
          {user && ["contributor", "editor", "admin"].includes(user.role) && <Link href="/knowledge/new">创建知识</Link>}
        </nav>
        <div className="sidebar-bottom">
          {user ? <><span className="user-name">{user.name}</span><button className="text-button" onClick={logout}>退出登录</button></> : <Link href="/login">登录</Link>}
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
