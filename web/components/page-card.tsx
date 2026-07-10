import Link from "next/link";
import { formatDate, Page } from "@/lib/api";

export function PageCard({ page }: { page: Page }) {
  return (
    <Link href={`/knowledge/${page.slug}`} className="page-card">
      <div className="card-meta">{page.topic?.name ?? "未分类"} · 已验证版本 {page.current_version}</div>
      <h3>{page.title}</h3>
      <p>{page.summary || page.content.slice(0, 110)}</p>
      <div className="card-footer"><span>{page.tags.map((tag) => `#${tag}`).join(" ")}</span><time>{formatDate(page.updated_at)}</time></div>
    </Link>
  );
}
