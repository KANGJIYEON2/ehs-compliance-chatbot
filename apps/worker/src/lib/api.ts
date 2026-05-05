import { useAuthStore } from "../stores/authStore";

const API_BASE =
  (import.meta as any)?.env?.VITE_API_URL?.replace(/\/+$/, "") ||
  "http://127.0.0.1:8000";

export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const { accessToken, refreshToken, logout } = useAuthStore.getState();

  const headers = new Headers(options.headers);
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  let res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // 401 → try refresh
  if (res.status === 401 && refreshToken) {
    const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (refreshRes.ok) {
      const tokens = await refreshRes.json();
      const { user } = useAuthStore.getState();
      if (user) {
        useAuthStore.getState().setAuth(tokens, user);
      }
      headers.set("Authorization", `Bearer ${tokens.access_token}`);
      res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    } else {
      logout();
      window.location.href = "/login";
    }
  }

  return res;
}

export { API_BASE };
