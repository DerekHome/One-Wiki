import Link from "next/link";
import { formatDate, Page } from "@/lib/api";

function excerpt(page: Page) {
  if (page.summary) return page.summary;
  return page.content.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim().slice(0, 96);
}

export function PageCard({ page }: { page: Page }) {
  const text = excerpt(page);
  return (
    <Link href={`/knowledge/${page.slug}`} className="page-card">
      <div className="card-top">
        <span className="card-topic">{page.topic?.name ?? "未分类"}</span>
        <time className="card-date">{formatDate(page.updated_at)}</time>
      </div>
      <h3>{page.title}</h3>
      <p>{text || "团队知识资源"}</p>
      {page.tags.length > 0 && (
        <div className="card-tags">
          {page.tags.slice(0, 3).map((tag) => (
            <span className="tag" key={tag}>#{tag}</span>
          ))}
        </div>
      )}
    </Link>
  );
}
