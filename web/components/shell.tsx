"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BookmarkSimple, GearSix, Moon, SignOut, Sparkle, Sun } from "@phosphor-icons/react";
import { api, User } from "@/lib/api";
import { KnowledgeTree } from "@/components/knowledge-tree";

function getInitialTheme(): "light" | "dark" {
  if (typeof window === "undefined") {
    return "light";
  }
  const savedTheme = window.localStorage.getItem("one-wiki-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  return savedTheme === "dark" || (!savedTheme && prefersDark) ? "dark" : "light";
}

export function Shell({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [siteName, setSiteName] = useState("One WIKI");
  const [theme, setTheme] = useState<"light" | "dark">(getInitialTheme);

  useEffect(() => {
    api<User>("/auth/me").then(setUser).catch(() => setUser(null));
    api<{ site_name: string }>("/settings/public").then((value) => setSiteName(value.site_name)).catch(() => undefined);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    window.localStorage.setItem("one-wiki-theme", theme);
  }, [theme]);

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
        <button
          className="theme-switch"
          type="button"
          role="switch"
          aria-checked={theme === "dark"}
          aria-label={theme === "dark" ? "\u5207\u6362\u5230\u4eae\u8272\u6a21\u5f0f" : "\u5207\u6362\u5230\u6697\u8272\u6a21\u5f0f"}
          title={theme === "dark" ? "\u5207\u6362\u5230\u4eae\u8272\u6a21\u5f0f" : "\u5207\u6362\u5230\u6697\u8272\u6a21\u5f0f"}
          data-theme={theme}
          onClick={() => setTheme((value) => value === "dark" ? "light" : "dark")}
        >
          <span className="theme-switch-thumb" />
          <span className="theme-switch-icon theme-switch-sun"><Sun size={15} weight="fill" /></span>
          <span className="theme-switch-icon theme-switch-moon"><Moon size={15} weight="fill" /></span>
        </button>
        <div className="header-utility">
          <div className="header-user">
            {user ? (
              <>
                <span className="user-name">{user.name}</span>
                <span className="logout-tray">
                  <button className="icon-button logout-button" onClick={logout} title={"\u9000\u51fa\u767b\u5f55"} aria-label={"\u9000\u51fa\u767b\u5f55"}><SignOut size={17} /></button>
                </span>
              </>
            ) : (
              <Link href="/login">{"\u767b\u5f55"}</Link>
            )}
          </div>
        </div>
      </header>
      <aside className="sidebar">
        <KnowledgeTree />
        <nav className="dashboard-nav sidebar-actions" aria-label={"\u4e3b\u8981\u529f\u80fd"}>
          {user?.can_access_settings && <Link href="/settings"><GearSix size={18} weight="fill" />{"\u8bbe\u7f6e"}</Link>}
          {user && <Link href="/favorites"><BookmarkSimple size={18} weight="fill" />{"\u6536\u85cf"}</Link>}
          <Link href="/ask"><Sparkle size={18} weight="fill" />{"\u95ee\u7b54"}</Link>
        </nav>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
