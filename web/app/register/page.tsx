"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api("/auth/register", { method: "POST", body: JSON.stringify({ username, password }) });
      window.location.href = "/";
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "\u6ce8\u518c\u5931\u8d25");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth">
      <form className="auth-card" onSubmit={submit}>
        <div className="eyebrow">&#x521b;&#x5efa;&#x8d26;&#x53f7;</div>
        <h1>&#x6ce8;&#x518c;&#x667a;&#x8bc6;&#x5e93;</h1>
        <p>&#x65b0;&#x8d26;&#x53f7;&#x4f1a;&#x5148;&#x8fdb;&#x5165;&#x53ea;&#x8bfb;&#x5206;&#x7ec4;&#xff0c;&#x7ba1;&#x7406;&#x5458;&#x53ef;&#x4ee5;&#x518d;&#x52a0;&#x5165;&#x53ef;&#x7f16;&#x8f91;&#x5206;&#x7ec4;&#x3002;</p>
        <div className="form-grid">
          <div className="field">
            <label>用户名</label>
            <input value={username} onChange={(event) => setUsername(event.target.value)} required />
          </div>
          <div className="field">
            <label>&#x5bc6;&#x7801;</label>
            <input type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required />
            <span className="helper">&#x81f3;&#x5c11; 8 &#x4f4d;&#x3002;</span>
          </div>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={loading}>{loading ? "\u6b63\u5728\u6ce8\u518c..." : "\u6ce8\u518c\u5e76\u8fdb\u5165"}</button>
        </div>
        <p className="helper auth-switch">&#x5df2;&#x6709;&#x8d26;&#x53f7;&#xff1f;<Link href="/login">&#x8fd4;&#x56de;&#x767b;&#x5f55;</Link></p>
      </form>
    </main>
  );
}
