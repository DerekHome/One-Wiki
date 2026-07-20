import type { Metadata } from "next";
import "./globals.css";
import "./apple-theme.css";

export const metadata: Metadata = {
  title: "One WIKI",
  description: "团队统一、可信的知识入口"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html: `(() => {
  try {
    const saved = localStorage.getItem("one-wiki-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if ((saved || (prefersDark ? "dark" : "light")) === "dark") {
      document.documentElement.classList.add("dark");
    }
  } catch {}
})();`
          }}
        />
        {children}
      </body>
    </html>
  );
}
