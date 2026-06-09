"use client";

import { useAuth } from "@/lib/auth";

export default function AppDashboard() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          {user.business_name} &middot; {user.segment}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl border p-6 bg-white">
          <h3 className="text-sm font-medium text-gray-500">Pedidos hoje</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
        </div>
        <div className="rounded-xl border p-6 bg-white">
          <h3 className="text-sm font-medium text-gray-500">Entregadores</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
        </div>
        <div className="rounded-xl border p-6 bg-white">
          <h3 className="text-sm font-medium text-gray-500">Produtos</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
        </div>
      </div>
    </div>
  );
}
