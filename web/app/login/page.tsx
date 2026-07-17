"use client";

import Link from "next/link";
import { FormEvent, Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";

function LoginContent() {
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState(searchParams.get("error") ? "登录失败，请检查邮箱和密码" : "");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      window.location.href = "/";
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "\u767b\u5f55\u5931\u8d25");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth">
      <form className="auth-card" action="/auth/login" method="post" onSubmit={submit}>
        <div className="eyebrow">&#x6b22;&#x8fce;&#x56de;&#x6765;</div>
        <h1>&#x767b;&#x5f55;&#x667a;&#x8bc6;&#x5e93;</h1>
        <p>&#x4f7f;&#x7528;&#x56e2;&#x961f;&#x8d26;&#x53f7;&#x8bbf;&#x95ee;&#x53ef;&#x4fe1;&#x77e5;&#x8bc6;&#x3002;</p>
        <div className="form-grid">
          <div className="field">
            <label>&#x90ae;&#x7bb1;</label>
            <input name="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>
          <div className="field">
            <label>&#x5bc6;&#x7801;</label>
            <input name="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={loading}>{loading ? "\u6b63\u5728\u767b\u5f55..." : "\u767b\u5f55"}</button>
        </div>
        <p className="helper" style={{ marginTop: 18 }}>&#x9ed8;&#x8ba4;&#x7ba1;&#x7406;&#x5458;&#xff1a;admin@example.com / ChangeMe123!</p>
        <p className="helper auth-switch">&#x8fd8;&#x6ca1;&#x6709;&#x8d26;&#x53f7;&#xff1f;<Link href="/register">&#x6ce8;&#x518c;&#x65b0;&#x8d26;&#x53f7;</Link></p>
      </form>
    </main>
  );
}

export default function LoginPage() {
  return <Suspense fallback={null}><LoginContent /></Suspense>;
}
