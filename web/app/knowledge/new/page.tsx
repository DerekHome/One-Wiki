import { Shell } from "@/components/shell";
import { KnowledgeForm } from "@/components/knowledge-form";

export default function NewKnowledgePage() { return <Shell><section className="form-page"><span className="eyebrow">创建知识</span><h1>把经验写成可复用的答案</h1><p className="summary">先保存为草稿，确认后再发布。草稿不会进入搜索和 AI 引用。</p><KnowledgeForm /></section></Shell>; }
