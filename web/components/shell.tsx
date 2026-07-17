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
        <Link href="/" className="dashboard-title" aria-label={"One WIKI \u9996\u9875"}>
          <span className="logo-mark">W</span>
          <span className="logo-text"><strong>{siteName}</strong><small>{"\u56e2\u961f\u77e5\u8bc6\u8d44\u6e90\u5e93"}</small></span>
        </Link>
        <div className="header-utility">
          <nav className="dashboard-nav header-actions" aria-label={"\u4e3b\u8981\u529f\u80fd"}>
            {user?.can_access_settings && <Link href="/settings"><GearSix size={17} weight="fill" />{"\u7cfb\u7edf\u8bbe\u7f6e"}</Link>}
            {user && <Link href="/favorites"><BookmarkSimple size={17} weight="fill" />{"\u6211\u7684\u6536\u85cf"}</Link>}
            <Link href="/ask"><Sparkle size={17} weight="fill" />{"AI \u95ee\u7b54"}</Link>
          </nav>
          <div className="header-user">
            {user ? (
              <>
                <span className="user-name">{user.name}</span>
                <button className="icon-button logout-button" onClick={logout} title={"\u9000\u51fa\u767b\u5f55"} aria-label={"\u9000\u51fa\u767b\u5f55"}><SignOut size={17} /></button>
              </>
            ) : (
              <Link href="/login">{"\u767b\u5f55"}</Link>
            )}
          </div>
        </div>
      </header>
      <aside className="sidebar">
        <KnowledgeTree />
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
