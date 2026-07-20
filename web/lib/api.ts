export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export type Topic = { id: string; name: string; slug: string; description: string; parent_id: string | null };
export type Page = {
  id: string; slug: string; title: string; summary: string; content: string; status: string;
  topic: Topic | null; tags: string[]; current_version: number; updated_at: string;
  owner: { name: string; username: string; email: string } | null;
};
export type User = { id: string; name: string; username: string; email: string; role: string; is_active: boolean; can_edit: boolean; can_access_settings: boolean; permissions: string[]; groups: { id: string; name: string; can_edit: boolean; permissions: string[] }[] };
export type Group = { id: string; name: string; description: string; can_edit: boolean; permissions: string[]; members: { id: string; name: string; username: string; email: string }[] };
export type PermissionItem = { key: string; label: string; category: string };
export type AdminSummary = {
  pages: number; published: number; drafts: number; users: number;
  active_users: number; groups: number; topics: number; files: number;
};
export type AdminSettings = {
  site_name: string; registration_enabled: boolean; session_days: number; max_upload_size_mb: number;
  database_url_configured: boolean; database_url_masked: string; database_managed_by_environment: boolean; current_database_driver: string;
  ai_enabled: boolean; llm_base_url: string; llm_model: string; llm_api_key_configured: boolean;
  permissions: string[]; permission_catalog: PermissionItem[]; restart_required_fields: string[]; is_admin: boolean;
};
export type FileAsset = { id: string; name: string; content_type: string; size: number; sha256: string; created_at: string };

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...init, headers, credentials: "include" });
  } catch (cause) {
    console.error(`[One Wiki API] ${init.method ?? "GET"} ${path} network failure`);
    throw cause;
  }
  if (!response.ok) {
    console.error(`[One Wiki API] ${init.method ?? "GET"} ${path} failed with ${response.status}`);
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? "请求失败，请稍后重试");
  }
  return response.json() as Promise<T>;
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium" }).format(new Date(value));
}
