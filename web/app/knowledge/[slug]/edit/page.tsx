"use client";

import { useParams } from "next/navigation";
import { Shell } from "@/components/shell";
import { KnowledgeForm } from "@/components/knowledge-form";

export default function EditKnowledgePage() {
  const params = useParams<{ slug: string }>();

  return (
    <Shell>
      <section className="form-page">
        <span className="eyebrow">编辑知识</span>
        <h1>完善并发布</h1>
        <KnowledgeForm pageId={params.slug} />
      </section>
    </Shell>
  );
}
