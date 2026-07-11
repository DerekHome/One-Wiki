"use client";

import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import { Table, TableCell, TableHeader, TableRow } from "@tiptap/extension-table";
import { ChangeEvent, useEffect, useRef } from "react";

type Props = { value: string; onChange: (value: string) => void };

function escapeHtml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function toEditorContent(value: string) {
  if (/<\/?[a-z][\s\S]*>/i.test(value)) return value;
  const result: string[] = [];
  let list: string[] = [];
  const flushList = () => { if (list.length) { result.push(`<ul>${list.join("")}</ul>`); list = []; } };
  for (const rawLine of value.split("\n")) {
    const line = escapeHtml(rawLine);
    if (rawLine.startsWith("- ")) { list.push(`<li>${escapeHtml(rawLine.slice(2))}</li>`); continue; }
    flushList();
    if (rawLine.startsWith("### ")) result.push(`<h3>${escapeHtml(rawLine.slice(4))}</h3>`);
    else if (rawLine.startsWith("## ")) result.push(`<h2>${escapeHtml(rawLine.slice(3))}</h2>`);
    else if (rawLine.startsWith("# ")) result.push(`<h1>${escapeHtml(rawLine.slice(2))}</h1>`);
    else if (rawLine.startsWith("> ")) result.push(`<blockquote><p>${escapeHtml(rawLine.slice(2))}</p></blockquote>`);
    else if (line) result.push(`<p>${line}</p>`);
  }
  flushList();
  return result.join("") || "<p></p>";
}

export function RichTextEditor({ value, onChange }: Props) {
  const importInput = useRef<HTMLInputElement>(null);
  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      Image.configure({ allowBase64: false }),
      Placeholder.configure({ placeholder: "从一句清晰的结论开始…" }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
    ],
    content: toEditorContent(value),
    editorProps: { attributes: { class: "rich-text-content" } },
    onUpdate: ({ editor: instance }) => onChange(instance.getHTML()),
  });

  useEffect(() => {
    const content = toEditorContent(value);
    if (editor && content !== editor.getHTML()) editor.commands.setContent(content, { emitUpdate: false });
  }, [editor, value]);

  if (!editor) return <div className="rich-text-loading">正在加载编辑器…</div>;
  const addImage = () => {
    const url = window.prompt("输入图片 URL（仅支持 http 或 https）");
    if (url?.match(/^https?:\/\//i)) editor.chain().focus().setImage({ src: url }).run();
  };
  const importDocument = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const extension = file.name.split(".").pop()?.toLowerCase();
    if (!extension || !["md", "markdown", "html", "htm"].includes(extension)) {
      window.alert("请选择 Markdown 或 HTML 文件。");
      event.target.value = "";
      return;
    }
    const source = await file.text();
    const content = ["md", "markdown"].includes(extension) ? toEditorContent(source) : source;
    editor.commands.setContent(content);
    onChange(editor.getHTML());
    event.target.value = "";
  };

  return <div className="rich-text-editor">
    <div className="editor-toolbar" role="toolbar" aria-label="正文格式">
      <button type="button" onClick={() => editor.chain().focus().toggleBold().run()} className={editor.isActive("bold") ? "active" : ""}><b>B</b></button>
      <button type="button" onClick={() => editor.chain().focus().toggleItalic().run()} className={editor.isActive("italic") ? "active" : ""}><i>I</i></button>
      <button type="button" onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} className={editor.isActive("heading", { level: 2 }) ? "active" : ""}>标题</button>
      <button type="button" onClick={() => editor.chain().focus().toggleBulletList().run()} className={editor.isActive("bulletList") ? "active" : ""}>列表</button>
      <button type="button" onClick={() => editor.chain().focus().toggleOrderedList().run()} className={editor.isActive("orderedList") ? "active" : ""}>编号</button>
      <button type="button" onClick={() => editor.chain().focus().toggleBlockquote().run()} className={editor.isActive("blockquote") ? "active" : ""}>引用</button>
      <button type="button" onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}>表格</button>
      <button type="button" onClick={addImage}>图片</button>
      <button type="button" onClick={() => importInput.current?.click()}>导入 MD / HTML</button>
      <button type="button" onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()}>撤销</button>
      <button type="button" onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()}>重做</button>
    </div>
    <input ref={importInput} className="file-import" type="file" accept=".md,.markdown,.html,.htm,text/markdown,text/html" onChange={importDocument} />
    <EditorContent editor={editor} />
  </div>;
}
