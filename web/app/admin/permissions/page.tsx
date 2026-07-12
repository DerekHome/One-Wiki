"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { api, Group, User } from "@/lib/api";
import { Shell } from "@/components/shell";

export default function PermissionPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [groupName, setGroupName] = useState("");
  const [groupDescription, setGroupDescription] = useState("");
  const [groupCanEdit, setGroupCanEdit] = useState(false);
  const [selectedUser, setSelectedUser] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    const [nextUsers, nextGroups] = await Promise.all([api<User[]>("/admin/users"), api<Group[]>("/admin/groups")]);
    setUsers(nextUsers);
    setGroups(nextGroups);
    setSelectedUser((old) => old || nextUsers[0]?.id || "");
    setSelectedGroup((old) => old || nextGroups[0]?.id || "");
  }

  useEffect(() => {
    load().catch((reason) => setError(reason instanceof Error ? reason.message : "\u52a0\u8f7d\u5931\u8d25"));
  }, []);

  const editableGroups = useMemo(() => groups.filter((group) => group.can_edit).length, [groups]);

  async function createGroup(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api<Group>("/admin/groups", { method: "POST", body: JSON.stringify({ name: groupName, description: groupDescription, can_edit: groupCanEdit }) });
      setGroupName("");
      setGroupDescription("");
      setGroupCanEdit(false);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "\u521b\u5efa\u5206\u7ec4\u5931\u8d25");
    } finally {
      setLoading(false);
    }
  }

  async function assignGroup(event: FormEvent) {
    event.preventDefault();
    if (!selectedUser || !selectedGroup) return;
    setError("");
    setLoading(true);
    try {
      await api<Group>(`/admin/groups/${selectedGroup}/members`, { method: "POST", body: JSON.stringify({ user_id: selectedUser }) });
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "\u52a0\u5165\u5206\u7ec4\u5931\u8d25");
    } finally {
      setLoading(false);
    }
  }

  async function toggleGroup(group: Group) {
    setError("");
    setLoading(true);
    try {
      await api<Group>(`/admin/groups/${group.id}`, { method: "PUT", body: JSON.stringify({ name: group.name, description: group.description, can_edit: !group.can_edit }) });
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "\u66f4\u65b0\u5206\u7ec4\u5931\u8d25");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell>
      <section className="form-page permissions-page">
        <span className="eyebrow">&#x7ba1;&#x7406;&#x5458;</span>
        <h1>&#x6743;&#x9650;&#x7ba1;&#x7406;</h1>
        <p className="summary">&#x7528;&#x5206;&#x7ec4;&#x6765;&#x7ba1;&#x7406;&#x7528;&#x6237;&#x6743;&#x9650;&#xff1a;&#x53ef;&#x7f16;&#x8f91;&#x5206;&#x7ec4;&#x53ef;&#x4ee5;&#x521b;&#x5efa;&#x3001;&#x4fee;&#x6539;&#x3001;&#x53d1;&#x5e03;&#x548c;&#x5f52;&#x6863;&#x77e5;&#x8bc6;&#xff1b;&#x975e;&#x53ef;&#x7f16;&#x8f91;&#x5206;&#x7ec4;&#x53ea;&#x80fd;&#x9605;&#x8bfb;&#x548c;&#x6536;&#x85cf;&#x3002;</p>
        {error && <div className="error">{error}</div>}

        <div className="permission-stats">
          <div><strong>{users.length}</strong><span>&#x7528;&#x6237;</span></div>
          <div><strong>{groups.length}</strong><span>&#x5206;&#x7ec4;</span></div>
          <div><strong>{editableGroups}</strong><span>&#x53ef;&#x7f16;&#x8f91;&#x5206;&#x7ec4;</span></div>
        </div>

        <div className="permission-grid">
          <form className="permission-panel" onSubmit={createGroup}>
            <h2>&#x65b0;&#x5efa;&#x5206;&#x7ec4;</h2>
            <div className="field"><label>&#x5206;&#x7ec4;&#x540d;</label><input value={groupName} onChange={(event) => setGroupName(event.target.value)} required /></div>
            <div className="field"><label>&#x8bf4;&#x660e;</label><input value={groupDescription} onChange={(event) => setGroupDescription(event.target.value)} /></div>
            <label className="check-row"><input type="checkbox" checked={groupCanEdit} onChange={(event) => setGroupCanEdit(event.target.checked)} /> <span>&#x5141;&#x8bb8;&#x7f16;&#x8f91;&#x77e5;&#x8bc6;</span></label>
            <button className="primary" disabled={loading}>&#x521b;&#x5efa;&#x5206;&#x7ec4;</button>
          </form>

          <form className="permission-panel" onSubmit={assignGroup}>
            <h2>&#x5206;&#x914d;&#x7528;&#x6237;</h2>
            <div className="field"><label>&#x7528;&#x6237;</label><select value={selectedUser} onChange={(event) => setSelectedUser(event.target.value)}>{users.map((user) => <option key={user.id} value={user.id}>{user.name} ? {user.email}</option>)}</select></div>
            <div className="field"><label>&#x5206;&#x7ec4;</label><select value={selectedGroup} onChange={(event) => setSelectedGroup(event.target.value)}>{groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></div>
            <button className="primary" disabled={loading || !selectedUser || !selectedGroup}>&#x52a0;&#x5165;&#x5206;&#x7ec4;</button>
          </form>
        </div>

        <div className="permission-list">
          {groups.map((group) => (
            <article className="permission-group" key={group.id}>
              <div>
                <h2>{group.name}</h2>
                <p>{group.description || "No description"}</p>
              </div>
              <button className={group.can_edit ? "permission-toggle active" : "permission-toggle"} onClick={() => toggleGroup(group)} disabled={loading}>
                {group.can_edit ? "\u53ef\u7f16\u8f91" : "\u53ea\u8bfb"}
              </button>
              <div className="permission-members">
                {group.members.length ? group.members.map((member) => <span key={member.id}>{member.name}</span>) : <span>&#x6682;&#x65e0;&#x7528;&#x6237;</span>}
              </div>
            </article>
          ))}
        </div>
      </section>
    </Shell>
  );
}
