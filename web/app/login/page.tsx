"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setLoading(true);
    try { await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }); window.location.href = "/"; }
    catch (reason) { setError(reason instanceof Error ? reason.message : "登录失败"); }
    finally { setLoading(false); }
  }
  return <main className="auth"><form className="auth-card" onSubmit={submit}>
    <div className="eyebrow">欢迎回来</div><h1>登录智识库</h1><p>使用团队账号访问可信知识。</p>
    <div className="form-grid"><div className="field"><label>邮箱</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></div>
    <div className="field"><label>密码</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></div>
    {error && <div className="error">{error}</div>}<button className="primary" disabled={loading}>{loading ? "正在登录…" : "登录"}</button></div>
    <p className="helper" style={{marginTop: 18}}>首次运行默认账号：admin@example.com / ChangeMe123!</p>
  </form></main>;
}
