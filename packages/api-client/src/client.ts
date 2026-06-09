const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  token?: string;
};

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (options.token) {
      headers["Authorization"] = `Bearer ${options.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method: options.method || "GET",
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "Unknown error" }));
      throw new Error(error.detail || error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  get<T>(path: string, token?: string) {
    return this.request<T>(path, { token });
  }

  post<T>(path: string, body: unknown, token?: string) {
    return this.request<T>(path, { method: "POST", body, token });
  }

  put<T>(path: string, body: unknown, token?: string) {
    return this.request<T>(path, { method: "PUT", body, token });
  }

  delete<T>(path: string, token?: string) {
    return this.request<T>(path, { method: "DELETE", token });
  }
}

export const apiClient = new ApiClient(API_URL);
