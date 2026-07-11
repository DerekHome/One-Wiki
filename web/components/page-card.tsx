import Link from "next/link";
import { formatDate, Page } from "@/lib/api";

export function PageCard({ page }: { page: Page }) {
  return (
    <Link href={`/knowledge/${page.slug}`} className="page-card">
      <div className="resource-preview"><span>{page.topic?.name ?? "未分类"}</span><strong>{page.title}</strong><p>{page.summary || "团队知识资源"}</p></div>
      <div className="card-body"><h3>{page.title}</h3><p>{page.summary || page.content.replace(/<[^>]+>/g, "").slice(0, 80)}</p><div className="card-footer"><span>{page.tags.slice(0, 2).map((tag) => `#${tag}`).join(" ") || "知识"}</span><time>{formatDate(page.updated_at)}</time></div></div>
    </Link>
  );
}
