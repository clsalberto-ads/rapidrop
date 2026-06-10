const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  token?: string;
};

/**
 * Token refresh queue — garante que múltiplas chamadas
 * 401 simultâneas gerem apenas UM refresh.
 */
let refreshPromise: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return null;

  try {
    const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      return null;
    }

    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    if (data.refresh_token) {
      localStorage.setItem("refresh_token", data.refresh_token);
    }
    return data.access_token;
  } catch {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return null;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  // Se já houver um refresh em andamento, aguarda ele
  if (refreshPromise) return refreshPromise;

  refreshPromise = doRefresh();
  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const token = options.token ?? localStorage.getItem("access_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response = await fetch(`${API_URL}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  // Interceptor de refresh automático
  if (response.status === 401 && token) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`;
      response = await fetch(`${API_URL}${path}`, {
        method: options.method || "GET",
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Erro desconhecido" }));
    throw new Error(error.detail || error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

async function requestFormData<T>(path: string, formData: FormData, token?: string): Promise<T> {
  const headers: Record<string, string> = {};
  const accessToken = token ?? localStorage.getItem("access_token");
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  let response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (response.status === 401 && accessToken) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`;
      response = await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers,
        body: formData,
      });
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Erro desconhecido" }));
    throw new Error(error.detail || error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: <T>(path: string, token?: string) => request<T>(path, { token }),
  post: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "POST", body, token }),
  put: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "PUT", body, token }),
  patch: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "PATCH", body, token }),
  delete: <T>(path: string, token?: string) => request<T>(path, { method: "DELETE", token }),
  upload: <T>(path: string, formData: FormData, token?: string) =>
    requestFormData<T>(path, formData, token),
};
