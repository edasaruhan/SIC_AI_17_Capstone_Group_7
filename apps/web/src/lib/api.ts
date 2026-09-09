import "server-only";

export type ApiState<T> = { ok: true; data: T } | { ok: false; kind: "unconfigured" | "error"; message: string };

export async function apiGet<T>(path: string): Promise<ApiState<T>> {
  const base = process.env.GP_API_URL; const token = process.env.GP_SERVER_TOKEN; const organization = process.env.GP_ORGANIZATION_ID;
  if (!base || !token || !organization) return { ok: false, kind: "unconfigured", message: "Set GP_API_URL, GP_SERVER_TOKEN, and GP_ORGANIZATION_ID on the Next.js server. Credentials are never sent to the browser." };
  try { const response = await fetch(new URL(path, base), { cache: "no-store", headers: { Authorization: `Bearer ${token}`, "X-Organization-ID": organization } }); if (!response.ok) return { ok: false, kind: "error", message: `The API returned ${response.status}. No placeholder values are shown.` }; return { ok: true, data: await response.json() as T }; } catch { return { ok: false, kind: "error", message: "The API could not be reached. Verify local services and workspace configuration." }; }
}
