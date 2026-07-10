import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "智识库",
  description: "团队统一、可信的知识入口"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
