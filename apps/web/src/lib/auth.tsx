"use client";

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { api } from "./api";

type User = {
  id: string;
  email: string;
  name: string;
  business_name: string;
  segment: string;
  is_active: boolean;
};

type AuthContext = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
};

type RegisterData = {
  email: string;
  password: string;
  name: string;
  business_name: string;
  document: string;
  phone: string;
  segment: string;
};

const AuthContext = createContext<AuthContext | null>(null);

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function storeTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = useCallback(async (tok: string) => {
    try {
      const data = await api.get<User>("/api/v1/auth/me", tok);
      setUser(data);
    } catch {
      clearTokens();
      setToken(null);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchUser(token).finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [token, fetchUser]);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.post<{ access_token: string; refresh_token: string }>(
      "/api/v1/auth/login",
      { email, password }
    );
    storeTokens(data.access_token, data.refresh_token);
    setToken(data.access_token);
    await fetchUser(data.access_token);
  }, [fetchUser]);

  const register = useCallback(async (regData: RegisterData) => {
    const data = await api.post<{ access_token: string; refresh_token: string }>(
      "/api/v1/auth/register",
      regData
    );
    storeTokens(data.access_token, data.refresh_token);
    setToken(data.access_token);
    await fetchUser(data.access_token);
  }, [fetchUser]);

  const logout = useCallback(() => {
    clearTokens();
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
