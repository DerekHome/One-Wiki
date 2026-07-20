"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { AdminSettings, AdminSummary, api, Group, Page, User } from "@/lib/api";
import { Shell } from "@/components/shell";

type Tab = "overview" | "content" | "users" | "groups" | "general" | "database" | "ai";

export default function SettingsPage() {
  const [settings, setSettings] = useState<AdminSettings | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [pages, setPages] = useState<Page[]>([]);
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [tab, setTab] = useState<Tab>("overview");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [databaseUrl, setDatabaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "reader" });
  const [newGroup, setNewGroup] = useState({ name: "", description: "" });
  const [selectedUser, setSelectedUser] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");
  const can = (permission: string) => Boolean(settings?.permissions.includes(permission));

  async function load() {
    const next = await api<AdminSettings>("/admin/settings");
    setSettings(next);
    const requests: Promise<unknown>[] = [];
    if (next.permissions.includes("users.manage")) requests.push(api<User[]>("/admin/users").then(setUsers));
    if (next.permissions.includes("groups.manage")) requests.push(api<Group[]>("/admin/groups").then(setGroups));
    if (next.permissions.includes("content.edit") || next.permissions.includes("content.delete")) requests.push(api<Page[]>("/admin/pages").then(setPages));
    if (next.permissions.includes("statistics.view")) requests.push(api<AdminSummary>("/admin/summary").then(setSummary));
    await Promise.all(requests);
  }

  useEffect(() => { load().catch((reason) => setError(reason instanceof Error ? reason.message : "设置中心加载失败")); }, []);
  useEffect(() => { setSelectedUser((old) => old || users[0]?.id || ""); setSelectedGroup((old) => old || groups[0]?.id || ""); }, [users, groups]);

  const tabs = useMemo(() => [
    { id: "overview" as Tab, label: "概览", show: true },
    { id: "content" as Tab, label: "文档管理", show: can("content.edit") || can("content.delete") },
    { id: "users" as Tab, label: "用户管理", show: can("users.manage") },
    { id: "groups" as Tab, label: "群组与权限", show: can("groups.manage") },
    { id: "general" as Tab, label: "通用与安全", show: can("settings.configure") },
    { id: "database" as Tab, label: "数据库", show: can("database.configure") },
    { id: "ai" as Tab, label: "AI 服务", show: can("ai.configure") },
  ].filter((item) => item.show), [settings]);

  async function run(action: () => Promise<void>, success: string) {
    setBusy(true); setError(""); setMessage("");
    try { await action(); setMessage(success); } catch (reason) { setError(reason instanceof Error ? reason.message : "操作失败"); } finally { setBusy(false); }
  }
  async function saveSettings(values: Record<string, unknown>, success = "设置已保存") {
    await run(async () => { await api("/admin/settings", { method: "PUT", body: JSON.stringify(values) }); await load(); }, success);
  }
  async function createUser(event: FormEvent) {
    event.preventDefault();
    await run(async () => { await api("/admin/users", { method: "POST", body: JSON.stringify({ ...newUser, is_active: true }) }); setNewUser({ username: "", password: "", role: "reader" }); await load(); }, "用户已创建");
  }
  async function updateUser(user: User, changes: Partial<{ role: string; is_active: boolean }>) {
    await run(async () => { await api(`/admin/users/${user.id}`, { method: "PUT", body: JSON.stringify({ username: user.username, display_name: user.name, role: changes.role ?? user.role, is_active: changes.is_active ?? user.is_active }) }); await load(); }, "用户信息已更新");
  }
  async function deactivateUser(user: User) {
    if (!window.confirm(`确定停用“${user.name}”吗？该用户的历史文档归属会保留。`)) return;
    await run(async () => { await api(`/admin/users/${user.id}`, { method: "DELETE" }); await load(); }, "用户已停用");
  }
  async function createGroup(event: FormEvent) {
    event.preventDefault();
    await run(async () => { await api("/admin/groups", { method: "POST", body: JSON.stringify({ ...newGroup, permissions: [], can_edit: false }) }); setNewGroup({ name: "", description: "" }); await load(); }, "群组已创建");
  }
  async function togglePermission(group: Group, permission: string) {
    const permissions = group.permissions.includes(permission) ? group.permissions.filter((item) => item !== permission) : [...group.permissions, permission];
    await run(async () => { await api(`/admin/groups/${group.id}`, { method: "PUT", body: JSON.stringify({ name: group.name, description: group.description, permissions, can_edit: permissions.includes("content.edit") }) }); await load(); }, "群组权限已更新");
  }
  async function assignMember(event: FormEvent) {
    event.preventDefault(); if (!selectedUser || !selectedGroup) return;
    await run(async () => { await api(`/admin/groups/${selectedGroup}/members`, { method: "POST", body: JSON.stringify({ user_id: selectedUser }) }); await load(); }, "用户已加入群组");
  }
  async function removeMember(groupId: string, userId: string) { await run(async () => { await api(`/admin/groups/${groupId}/members/${userId}`, { method: "DELETE" }); await load(); }, "成员已移出群组"); }
  async function deleteGroup(group: Group) { if (window.confirm(`确定删除群组“${group.name}”吗？`)) await run(async () => { await api(`/admin/groups/${group.id}`, { method: "DELETE" }); await load(); }, "群组已删除"); }
  async function deleteDocument(page: Page) { if (window.confirm(`确定永久删除“${page.title}”吗？此操作不可恢复。`)) await run(async () => { await api(`/pages/${page.id}`, { method: "DELETE" }); await load(); }, "文档已删除"); }

  if (!settings && !error) return <Shell><div className="empty">正在加载设置中心…</div></Shell>;
  return <Shell><section className="settings-page">
    <header className="settings-header"><div><span className="eyebrow">系统管理</span><h1>设置中心</h1><p>集中管理知识库、成员、权限与基础设施配置。</p></div></header>
    {error && <div className="settings-alert error">{error}</div>}{message && <div className="settings-alert success">{message}</div>}
    <div className="settings-layout"><nav className="settings-nav">{tabs.map((item) => <button key={item.id} className={tab === item.id ? "active" : ""} onClick={() => setTab(item.id)}>{item.label}</button>)}</nav><div className="settings-content">
      {tab === "overview" && settings && <div className="settings-panel"><div className="panel-heading"><div><h2>系统概览</h2><p className="panel-intro">知识库当前的数据规模与运行概况。</p></div>{can("statistics.view") && <span className="access-badge">授权可见</span>}</div>{can("statistics.view") && summary && <div className="settings-stats statistics-grid"><div><strong>{summary.pages}</strong><span>文档总数</span></div><div><strong>{summary.published}</strong><span>已发布</span></div><div><strong>{summary.drafts}</strong><span>草稿</span></div><div><strong>{summary.topics}</strong><span>知识目录</span></div><div><strong>{summary.users}</strong><span>用户总数</span></div><div><strong>{summary.active_users}</strong><span>活跃用户</span></div><div><strong>{summary.groups}</strong><span>权限群组</span></div><div><strong>{summary.files}</strong><span>附件数量</span></div></div>}{can("statistics.view") && !summary && <div className="empty compact-empty">正在加载统计数据…</div>}<div className="settings-note"><strong>权限原则</strong><p>{can("statistics.view") ? "管理员自动拥有统计权限；其他用户只有在所属群组被授予“查看数据统计”后才能查看。" : "当前账号没有查看数量统计的权限。管理员可在“群组与权限”中授予查看权限。"}</p></div></div>}
      {tab === "content" && <div className="settings-panel"><h2>文档管理</h2><p className="panel-intro">查看全部状态的文档，并按授权进行编辑或永久删除。</p><div className="settings-table">{pages.map((page) => <div className="settings-row" key={page.id}><div><strong>{page.title}</strong><span>{page.status} · {page.topic?.name ?? "未分类"}</span></div><div className="row-actions">{can("content.edit") && <Link className="secondary" href={`/knowledge/${page.id}/edit`}>编辑</Link>}{can("content.delete") && <button className="danger-button" onClick={() => deleteDocument(page)} disabled={busy}>删除</button>}</div></div>)}</div></div>}
      {tab === "users" && <div className="settings-panel"><form className="settings-form compact user-create-form" id="user-create-form" onSubmit={createUser}><div className="panel-heading user-management-head"><div><h2>用户管理</h2><p className="panel-intro">使用用户名和密码登录，不再强制填写邮箱。</p></div><button className="primary" disabled={busy}>新增用户</button></div><div className="field"><label>用户名</label><input value={newUser.username} onChange={(e) => setNewUser({ ...newUser, username: e.target.value })} required /></div><div className="field"><label>初始密码</label><input type="password" minLength={8} value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} required /></div><div className="field"><label>角色</label><select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}><option value="reader">阅读者</option><option value="contributor">贡献者</option><option value="editor">编辑者</option><option value="admin">管理员</option></select></div></form><div className="settings-table">{users.map((user) => <div className="settings-row" key={user.id}><div><strong>{user.name}</strong><span>{user.username} · {user.is_active ? "正常" : "已停用"}</span></div><div className="row-actions"><select value={user.role} onChange={(e) => updateUser(user, { role: e.target.value })} disabled={busy}><option value="reader">阅读者</option><option value="contributor">贡献者</option><option value="editor">编辑者</option><option value="admin">管理员</option></select>{!user.is_active && <button className="secondary" onClick={() => updateUser(user, { is_active: true })}>启用</button>}{user.is_active && <button className="danger-button" onClick={() => deactivateUser(user)}>停用</button>}</div></div>)}</div></div>}
      {tab === "groups" && settings && <div className="settings-panel"><h2>群组与权限</h2><div className="settings-split"><form className="settings-form" onSubmit={createGroup}><h3>新增群组</h3><div className="field"><label>群组名称</label><input value={newGroup.name} onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })} required /></div><div className="field"><label>说明</label><input value={newGroup.description} onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })} /></div><button className="primary" disabled={busy}>创建群组</button></form><form className="settings-form" onSubmit={assignMember}><h3>分配成员</h3><div className="field"><label>用户</label><select value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)}>{users.map((user) => <option key={user.id} value={user.id}>{user.name} · {user.username}</option>)}</select></div><div className="field"><label>群组</label><select value={selectedGroup} onChange={(e) => setSelectedGroup(e.target.value)}>{groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></div><button className="primary" disabled={busy}>加入群组</button></form></div><div className="group-settings-list">{groups.map((group) => <article className="group-settings-card" key={group.id}><div className="group-title"><div><h3>{group.name}</h3><p>{group.description || "暂无说明"}</p></div>{!["Readers", "Editors"].includes(group.name) && <button className="danger-button" onClick={() => deleteGroup(group)}>删除群组</button>}</div><div className="permission-options">{settings.permission_catalog.map((item) => <label key={item.key}><input type="checkbox" checked={group.permissions.includes(item.key)} onChange={() => togglePermission(group, item.key)} disabled={busy} /><span><strong>{item.label}</strong><small>{item.category}</small></span></label>)}</div><div className="member-chips">{group.members.length ? group.members.map((member) => <button key={member.id} title="点击移出群组" onClick={() => removeMember(group.id, member.id)}>{member.name} ×</button>) : <span>暂无成员</span>}</div></article>)}</div></div>}
      {tab === "general" && settings && <form className="settings-panel settings-form" onSubmit={(event) => { event.preventDefault(); saveSettings({ site_name: settings.site_name, registration_enabled: settings.registration_enabled, session_days: settings.session_days, max_upload_size_mb: settings.max_upload_size_mb }); }}><h2>通用与安全</h2><div className="field"><label>站点名称</label><input value={settings.site_name} onChange={(e) => setSettings({ ...settings, site_name: e.target.value })} /></div><label className="setting-switch"><input type="checkbox" checked={settings.registration_enabled} onChange={(e) => setSettings({ ...settings, registration_enabled: e.target.checked })} /><span><strong>允许自主注册</strong><small>关闭后只能由用户管理员创建账号</small></span></label><div className="settings-split"><div className="field"><label>登录有效期（天）</label><input type="number" min={1} max={365} value={settings.session_days} onChange={(e) => setSettings({ ...settings, session_days: Number(e.target.value) })} /></div><div className="field"><label>单文件上限（MB）</label><input type="number" min={1} max={2048} value={settings.max_upload_size_mb} onChange={(e) => setSettings({ ...settings, max_upload_size_mb: Number(e.target.value) })} /></div></div><div className="settings-note">会话有效期和上传限制将在后端重启后生效。</div><button className="primary" disabled={busy}>保存通用设置</button></form>}
      {tab === "database" && settings && <div className="settings-panel"><h2>数据库配置</h2><div className="settings-note"><strong>当前驱动：{settings.current_database_driver}</strong><p>{settings.database_managed_by_environment ? "当前 DATABASE_URL 由环境变量管理，界面保存的地址不会覆盖环境变量。" : "新连接将在后端重启后生效。切换前请完整备份数据库和附件。"}</p></div><div className="field"><label>数据库连接地址</label><input type="password" value={databaseUrl} onChange={(e) => setDatabaseUrl(e.target.value)} placeholder={settings.database_url_masked || "postgresql+psycopg://user:password@host/database"} /></div><div className="form-actions"><button className="secondary" disabled={busy || !databaseUrl} onClick={() => run(async () => { await api("/admin/settings/database/test", { method: "POST", body: JSON.stringify({ database_url: databaseUrl }) }); }, "数据库连接测试成功")}>测试连接</button><button className="primary" disabled={busy || !databaseUrl} onClick={() => saveSettings({ database_url: databaseUrl }, "数据库配置已保存，重启后生效")}>保存数据库配置</button></div></div>}
      {tab === "ai" && settings && <form className="settings-panel settings-form" onSubmit={(event) => { event.preventDefault(); saveSettings({ ai_enabled: settings.ai_enabled, llm_base_url: settings.llm_base_url, llm_model: settings.llm_model, llm_api_key: apiKey || undefined }, "AI 配置已保存，重启后生效"); }}><h2>AI 服务</h2><label className="setting-switch"><input type="checkbox" checked={settings.ai_enabled} onChange={(e) => setSettings({ ...settings, ai_enabled: e.target.checked })} /><span><strong>启用 AI 问答</strong><small>关闭时仍使用知识检索结果作为降级回答</small></span></label><div className="field"><label>OpenAI-Compatible 地址</label><input value={settings.llm_base_url} onChange={(e) => setSettings({ ...settings, llm_base_url: e.target.value })} placeholder="https://provider.example/v1" /></div><div className="field"><label>模型名称</label><input value={settings.llm_model} onChange={(e) => setSettings({ ...settings, llm_model: e.target.value })} /></div><div className="field"><label>API Key</label><input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder={settings.llm_api_key_configured ? "已配置；留空表示保持不变" : "输入 API Key"} /></div><button className="primary" disabled={busy}>保存 AI 配置</button></form>}
    </div></div>
  </section></Shell>;
}
