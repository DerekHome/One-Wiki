"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, Page, Topic } from "@/lib/api";
import { RichTextEditor } from "@/components/rich-text-editor";
import { AttachmentLibrary } from "@/components/attachment-library";

type Values = { title: string; summary: string; content: string; topic_id: string; tags: string; review_at: string };
const empty: Values = { title: "", summary: "", content: "<h1>知识标题</h1><p>从一句清楚的结论开始。</p><h2>适用范围</h2><p>说明适用的场景与前置条件。</p><h2>详细说明</h2><p>补充步骤、示例或相关概念。</p>", topic_id: "", tags: "", review_at: "" };

export function KnowledgeForm({ pageId }: { pageId?: string }) {
  const [topics, setTopics] = useState<Topic[]>([]); const [values, setValues] = useState<Values>(empty); const [page, setPage] = useState<Page | null>(null); const [error, setError] = useState(""); const [saving, setSaving] = useState(false);
  useEffect(() => { api<Topic[]>("/topics").then(setTopics).catch(() => {}); if (pageId) api<Page>(`/pages/id/${pageId}`).then((item) => { setPage(item); setValues({ title:item.title, summary:item.summary, content:item.content, topic_id:item.topic?.id ?? "", tags:item.tags.join(", "), review_at:"" }); }).catch((e) => setError(e.message)); }, [pageId]);
  function update(field: keyof Values, value: string) { setValues((old) => ({...old, [field]: value})); }
  const payload = () => ({ title: values.title, summary: values.summary, content: values.content, topic_id: values.topic_id || null, tags: values.tags.split(/[,，]/).map((v) => v.trim()).filter(Boolean), review_at: values.review_at ? new Date(values.review_at).toISOString() : null });
  async function save(event: FormEvent) { event.preventDefault(); setSaving(true); setError(""); try { let result = pageId ? await api<Page>(`/pages/${pageId}`, {method:"PUT", body:JSON.stringify(payload())}) : await api<Page>("/pages", {method:"POST", body:JSON.stringify(payload())}); if (!pageId) result = await api<Page>(`/pages/${result.id}/publish`, {method:"POST", body:JSON.stringify({change_note:"创建并发布知识"})}); window.location.href = `/knowledge/${result.slug}`; } catch (e) { setError(e instanceof Error ? e.message : "保存失败"); } finally { setSaving(false); } }
  async function publish() { if (!pageId) return; setSaving(true); setError(""); try { const result = await api<Page>(`/pages/${pageId}/publish`, {method:"POST", body:JSON.stringify({change_note:"更新知识内容"})}); window.location.href = `/knowledge/${result.slug}`; } catch (e) { setError(e instanceof Error ? e.message : "发布失败"); } finally { setSaving(false); } }
  return <form className="form-grid" onSubmit={save}>
    <div className="form-meta-grid">
      <div className="field"><label>知识标题</label><input value={values.title} onChange={(e) => update("title", e.target.value)} required placeholder="用一句清晰的话描述主题" /></div>
      <div className="field"><label>一句话摘要</label><input value={values.summary} onChange={(e) => update("summary", e.target.value)} placeholder="先告诉读者这篇知识解决什么问题" /></div>
      <div className="field"><label>主题</label><select value={values.topic_id} onChange={(e) => update("topic_id", e.target.value)}><option value="">未分类</option>{topics.map((topic) => <option value={topic.id} key={topic.id}>{topic.name}</option>)}</select></div>
      <div className="field"><label>标签</label><input value={values.tags} onChange={(e) => update("tags", e.target.value)} placeholder="用逗号分隔，例如：产品、入门" /></div>
    </div>
    <div className="field content-field"><label>正文</label><RichTextEditor value={values.content} onChange={(content) => update("content", content)} /><span className="helper">支持标题、列表、引用、表格和图片。图片可使用已上传附件或可信 HTTPS 地址。</span></div>
    {page && <AttachmentLibrary pageId={page.id} editable />}
    {error && <div className="error">{error}</div>}<div className="form-actions"><button className="primary" disabled={saving}>{saving ? "正在保存…" : pageId ? "保存草稿" : "发布知识"}</button>{page && <button type="button" className="secondary" disabled={saving} onClick={publish}>发布版本 {page.current_version + 1}</button>}</div>
  </form>;
}
