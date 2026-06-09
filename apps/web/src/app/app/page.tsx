"use client";

import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AppDashboard() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">{user.business_name}</h1>
          <p className="text-gray-500">{user.email} · {user.segment}</p>
        </div>
        <button
          onClick={logout}
          className="text-sm text-gray-500 hover:text-red-600 transition-colors"
        >
          Sair
        </button>
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl border p-6 bg-white">
          <h3 className="font-medium text-gray-900">Pedidos hoje</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">0</p>
        </div>
        <div className="rounded-xl border p-6 bg-white">
          <h3 className="font-medium text-gray-900">Entregadores</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">0</p>
        </div>
        <div className="rounded-xl border p-6 bg-white">
          <h3 className="font-medium text-gray-900">Produtos</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">0</p>
        </div>
      </div>
    </div>
  );
}
