"use client";

import { useEffect, useState } from "react";
import { api, formatDate, PageVersion, PageVersionDetail } from "@/lib/api";

function ContentPreview({ text }: { text: string }) {
  if (/<\/?[a-z][\s\S]*>/i.test(text)) {
    return <div className="version-content rich-text-content" dangerouslySetInnerHTML={{ __html: text }} />;
  }
  return <div className="version-content">{text}</div>;
}

export function VersionHistory({ pageId, currentVersion }: { pageId: string; currentVersion: number }) {
  const [versions, setVersions] = useState<PageVersion[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [detail, setDetail] = useState<PageVersionDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api<PageVersion[]>(`/pages/${pageId}/versions`).then(setVersions).catch(() => setVersions([]));
  }, [pageId]);

  async function toggleVersion(versionNo: number) {
    if (expanded === versionNo) {
      setExpanded(null);
      setDetail(null);
      return;
    }
    setExpanded(versionNo);
    setLoading(true);
    setError("");
    try {
      setDetail(await api<PageVersionDetail>(`/pages/${pageId}/versions/${versionNo}`));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "加载版本失败");
      setDetail(null);
    } finally {
      setLoading(false);
    }
  }

  if (!versions.length) return null;

  return (
    <section className="version-history" aria-label="版本历史">
      <div className="version-history-head">
        <h2>版本历史</h2>
        <span>{versions.length} 个已发布版本</span>
      </div>
      <ol className="version-list">
        {versions.map((version) => (
          <li key={version.id} className={expanded === version.version_no ? "expanded" : undefined}>
            <button type="button" className="version-row" onClick={() => toggleVersion(version.version_no)}>
              <span className="version-no">v{version.version_no}{version.version_no === currentVersion ? " · 当前" : ""}</span>
              <span className="version-note">{version.change_note || "无变更说明"}</span>
              <span className="version-meta">{version.created_by?.name ?? "未知"} · {formatDate(version.created_at)}</span>
            </button>
            {expanded === version.version_no && (
              <div className="version-panel">
                {loading && <p className="empty compact-empty">正在加载版本内容…</p>}
                {error && <p className="error">{error}</p>}
                {detail && !loading && <ContentPreview text={detail.content} />}
              </div>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
