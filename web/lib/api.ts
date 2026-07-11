export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export type Topic = { id: string; name: string; slug: string; description: string };
export type Page = {
  id: string; slug: string; title: string; summary: string; content: string; status: string;
  topic: Topic | null; tags: string[]; current_version: number; updated_at: string;
  owner: { name: string; email: string } | null;
};
export type User = { id: string; name: string; email: string; role: string };

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
