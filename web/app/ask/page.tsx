"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Shell } from "@/components/shell";
import { api } from "@/lib/api";

type Answer = { answer: string; mode: string; citations: {title:string; slug:string; excerpt:string}[] };
export default function AskPage() {
  const [question, setQuestion] = useState(""); const [result, setResult] = useState<Answer | null>(null); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function ask(event: FormEvent) { event.preventDefault(); setLoading(true); setError(""); try { setResult(await api<Answer>("/ai/answers", {method:"POST", body:JSON.stringify({question})})); } catch (e) { setError(e instanceof Error ? e.message : "提问失败"); } finally { setLoading(false); } }
  return <Shell><section className="ask-layout"><span className="eyebrow">AI 问答</span><h1>从已发布知识中寻找答案</h1><p className="summary">回答始终附带来源；资料不足时会明确说明。</p>
    <form className="form-grid" onSubmit={ask}><div className="field"><label>你的问题</label><textarea style={{minHeight:130}} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="例如：这个产品适合解决哪些客户问题？" required /></div><button className="primary" disabled={loading}>{loading ? "正在检索…" : "开始提问"}</button></form>
    {error && <p className="error">{error}</p>}{result && <div className="answer">{result.mode === "search-fallback" && <div className="notice">尚未配置大模型服务，以下为可信知识检索结果。</div>}<div>{result.answer}</div><div className="citation-list">{result.citations.map((item) => <Link className="citation" href={`/knowledge/${item.slug}`} key={item.slug}><strong>{item.title}</strong><small>{item.excerpt}</small></Link>)}</div></div>}
  </section></Shell>;
}
