"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { API_BASE, api, FileAsset } from "@/lib/api";

type Props = { pageId: string; editable?: boolean };

function formatSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function fileType(file: FileAsset) {
  const extension = file.name.split(".").pop()?.toUpperCase();
  return extension || file.content_type.split("/").pop()?.toUpperCase() || "FILE";
}

export function AttachmentLibrary({ pageId, editable = false }: Props) {
  const [files, setFiles] = useState<FileAsset[]>([]);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const refresh = () => api<FileAsset[]>(`/pages/${pageId}/files`).then(setFiles).catch((cause) => setError(cause instanceof Error ? cause.message : "加载附件失败"));
  useEffect(() => { refresh(); }, [pageId]);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true); setError("");
    try {
      const body = new FormData(); body.append("file", file);
      await api<FileAsset>(`/files?page_id=${encodeURIComponent(pageId)}`, { method: "POST", body });
      await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "上传失败"); }
    finally { setUploading(false); event.target.value = ""; }
  }

  return <section className="attachment-section">
    <div className="attachment-section-head"><div><span className="eyebrow">附件资源库</span><h2>相关资料</h2></div>{editable && <label className="attachment-upload">{uploading ? "正在上传…" : "添加附件"}<input type="file" onChange={upload} disabled={uploading} /></label>}</div>
    {error && <div className="error">{error}</div>}
    {files.length ? <div className="attachment-grid">{files.map((file) => <a className="attachment-card" href={`${API_BASE}/files/${file.id}`} key={file.id} target="_blank" rel="noreferrer">
      <div className="attachment-preview">{file.content_type.startsWith("image/") ? <img src={`${API_BASE}/files/${file.id}`} alt="" /> : <span>{fileType(file)}</span>}</div>
      <div className="attachment-body"><h3>{file.name}</h3><p>{file.content_type || "文件"} · {formatSize(file.size)}</p><span className="attachment-tag">{fileType(file)}</span></div>
    </a>)}</div> : <div className="attachment-empty">{editable ? "还没有附件。上传资料后，它们会以资源卡片形式展示在这里。" : "暂无附件。"}</div>}
  </section>;
}
