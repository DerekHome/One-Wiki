"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, Page, Topic } from "@/lib/api";

type Values = { title: string; summary: string; content: string; topic_id: string; tags: string; review_at: string };
const empty: Values = { title: "", summary: "", content: "# 知识标题\n\n从一句清楚的结论开始。\n\n## 适用范围\n\n说明适用的场景与前置条件。\n\n## 详细说明\n\n补充步骤、示例或相关概念。", topic_id: "", tags: "", review_at: "" };

export function KnowledgeForm({ pageId }: { pageId?: string }) {
  const [topics, setTopics] = useState<Topic[]>([]); const [values, setValues] = useState<Values>(empty); const [page, setPage] = useState<Page | null>(null); const [error, setError] = useState(""); const [saving, setSaving] = useState(false);
  useEffect(() => { api<Topic[]>("/topics").then(setTopics).catch(() => {}); if (pageId) api<Page>(`/pages/id/${pageId}`).then((item) => { setPage(item); setValues({ title:item.title, summary:item.summary, content:item.content, topic_id:item.topic?.id ?? "", tags:item.tags.join(", "), review_at:"" }); }).catch((e) => setError(e.message)); }, [pageId]);
  function update(field: keyof Values, value: string) { setValues((old) => ({...old, [field]: value})); }
  const payload = () => ({ title: values.title, summary: values.summary, content: values.content, topic_id: values.topic_id || null, tags: values.tags.split(/[,，]/).map((v) => v.trim()).filter(Boolean), review_at: values.review_at ? new Date(values.review_at).toISOString() : null });
  async function save(event: FormEvent) { event.preventDefault(); setSaving(true); setError(""); try { const result = pageId ? await api<Page>(`/pages/${pageId}`, {method:"PUT", body:JSON.stringify(payload())}) : await api<Page>("/pages", {method:"POST", body:JSON.stringify(payload())}); window.location.href = `/knowledge/${result.slug}`; } catch (e) { setError(e instanceof Error ? e.message : "保存失败"); } finally { setSaving(false); } }
  async function publish() { if (!pageId) return; setSaving(true); setError(""); try { const result = await api<Page>(`/pages/${pageId}/publish`, {method:"POST", body:JSON.stringify({change_note:"更新知识内容"})}); window.location.href = `/knowledge/${result.slug}`; } catch (e) { setError(e instanceof Error ? e.message : "发布失败"); } finally { setSaving(false); } }
  return <form className="form-grid" onSubmit={save}>
    <div className="field"><label>知识标题</label><input value={values.title} onChange={(e) => update("title", e.target.value)} required placeholder="用一句清晰的话描述主题" /></div>
    <div className="field"><label>一句话摘要</label><input value={values.summary} onChange={(e) => update("summary", e.target.value)} placeholder="先告诉读者这篇知识解决什么问题" /></div>
    <div className="field"><label>主题</label><select value={values.topic_id} onChange={(e) => update("topic_id", e.target.value)}><option value="">未分类</option>{topics.map((topic) => <option value={topic.id} key={topic.id}>{topic.name}</option>)}</select></div>
    <div className="field"><label>标签</label><input value={values.tags} onChange={(e) => update("tags", e.target.value)} placeholder="用逗号分隔，例如：产品、入门" /></div>
    <div className="field"><label>正文</label><textarea value={values.content} onChange={(e) => update("content", e.target.value)} required /><span className="helper">第一版使用轻量 Markdown；以 #、##、### 组织层级。</span></div>
    {error && <div className="error">{error}</div>}<div className="form-actions"><button className="primary" disabled={saving}>{saving ? "正在保存…" : "保存草稿"}</button>{page && <button type="button" className="secondary" disabled={saving} onClick={publish}>发布版本 {page.current_version + 1}</button>}</div>
  </form>;
}
