import { NextRequest, NextResponse } from "next/server";

function backendBase(request: NextRequest) {
  const configured = process.env.NEXT_PUBLIC_API_BASE;
  if (configured) return configured.replace(/\/$/, "");
  return `${request.nextUrl.protocol}//${request.nextUrl.hostname}:8000/api/v1`;
}

export async function POST(request: NextRequest) {
  const form = await request.formData();
  const email = String(form.get("email") ?? "");
  const password = String(form.get("password") ?? "");
  const response = await fetch(`${backendBase(request)}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const redirectUrl = new URL(response.ok ? "/" : "/login?error=1", request.url);
  const redirect = NextResponse.redirect(redirectUrl, { status: 303 });
  const cookie = response.headers.get("set-cookie");
  if (cookie) redirect.headers.append("set-cookie", cookie);
  return redirect;
}
