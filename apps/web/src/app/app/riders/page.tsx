"use client";

import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type Rider = {
  id: string;
  name: string;
  phone: string;
  vehicle_type: string;
  document: string;
  pix_key: string | null;
  is_online: boolean;
  is_active: boolean;
  created_at: string;
};

type RiderListResponse = {
  riders: Rider[];
  total: number;
};

const vehicleLabels: Record<string, string> = {
  motorcycle: "Moto",
  bicycle: "Bicicleta",
  car: "Carro",
  walking: "A pé",
};

const vehicleIcons: Record<string, string> = {
  motorcycle: "🏍",
  bicycle: "🚲",
  car: "🚗",
  walking: "🚶",
};

const emptyRider = {
  name: "",
  phone: "",
  vehicle_type: "motorcycle",
  document: "",
  pix_key: "",
};

export default function RidersPage() {
  const { token } = useAuth();
  const [riders, setRiders] = useState<Rider[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Rider | null>(null);
  const [form, setForm] = useState<Record<string, any>>({ ...emptyRider });
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<RiderListResponse>("/api/v1/riders", token);
      setRiders(data.riders);
    } catch (err) {
      console.error("Failed to load riders", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleNew = () => {
    setEditing(null);
    setForm({ ...emptyRider });
    setShowForm(true);
  };

  const handleEdit = (rider: Rider) => {
    setEditing(rider);
    setForm({
      name: rider.name,
      phone: rider.phone,
      vehicle_type: rider.vehicle_type,
      document: rider.document,
      pix_key: rider.pix_key || "",
    });
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!token || !form.name.trim()) return;
    setSaving(true);
    try {
      const body = {
        name: form.name.trim(),
        phone: form.phone.trim(),
        vehicle_type: form.vehicle_type,
        document: form.document.trim(),
        pix_key: form.pix_key?.trim() || null,
      };

      if (editing) {
        await api.put(`/api/v1/riders/${editing.id}`, body, token);
      } else {
        await api.post("/api/v1/riders", body, token);
      }
      setShowForm(false);
      setEditing(null);
      await fetchData();
    } catch (err) {
      console.error("Failed to save rider", err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (rider: Rider) => {
    if (!token) return;
    if (!confirm(`Desativar entregador "${rider.name}"?`)) return;
    try {
      await api.delete(`/api/v1/riders/${rider.id}`, token);
      await fetchData();
    } catch (err) {
      console.error("Failed to deactivate rider", err);
    }
  };

  const filteredRiders = riders.filter((r) => {
    if (search) {
      const q = search.toLowerCase();
      if (!r.name.toLowerCase().includes(q) && !r.phone.includes(q)) return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Entregadores</h1>
          <p className="text-gray-500 mt-1">{riders.length} entregadores cadastrados</p>
        </div>
        <Button onClick={handleNew}>Novo entregador</Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por nome ou telefone..."
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
        />
      </div>

      {/* Form */}
      {showForm && (
        <div className="mb-8 p-6 bg-white rounded-xl border space-y-4">
          <h3 className="font-medium text-gray-900">
            {editing ? `Editar: ${editing.name}` : "Novo entregador"}
          </h3>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                placeholder="Nome do entregador"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
              <input
                type="text"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                placeholder="(84) 99999-9999"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Veículo</label>
              <select
                value={form.vehicle_type}
                onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
              >
                {Object.entries(vehicleLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {vehicleIcons[value]} {label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Documento (CPF/CNPJ)
              </label>
              <input
                type="text"
                value={form.document}
                onChange={(e) => setForm({ ...form, document: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                placeholder="000.000.000-00"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Chave PIX (opcional)
              </label>
              <input
                type="text"
                value={form.pix_key}
                onChange={(e) => setForm({ ...form, pix_key: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                placeholder="CPF, email ou telefone"
              />
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button onClick={handleSave} isLoading={saving}>
              {editing ? "Salvar" : "Cadastrar"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowForm(false);
                setEditing(null);
              }}
            >
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {/* Rider list */}
      {filteredRiders.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border">
          <p className="text-gray-500">Nenhum entregador encontrado.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredRiders.map((rider) => (
            <div
              key={rider.id}
              className={`bg-white rounded-xl border p-5 ${
                !rider.is_active ? "opacity-50" : ""
              }`}
            >
              {/* Status indicator */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-2.5 h-2.5 rounded-full ${
                      rider.is_online ? "bg-green-500" : "bg-gray-300"
                    }`}
                  />
                  <span className="text-sm font-medium text-gray-900">{rider.name}</span>
                </div>
                <span className="text-xl">{vehicleIcons[rider.vehicle_type] || "🏍"}</span>
              </div>

              {/* Details */}
              <div className="space-y-1.5 text-sm text-gray-500">
                <div className="flex justify-between">
                  <span>Telefone</span>
                  <span className="text-gray-700">{rider.phone}</span>
                </div>
                <div className="flex justify-between">
                  <span>Veículo</span>
                  <span className="text-gray-700">
                    {vehicleLabels[rider.vehicle_type] || rider.vehicle_type}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Documento</span>
                  <span className="text-gray-700 font-mono text-xs">{rider.document}</span>
                </div>
                {rider.pix_key && (
                  <div className="flex justify-between">
                    <span>PIX</span>
                    <span className="text-gray-700 font-mono text-xs">{rider.pix_key}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Status</span>
                  <span
                    className={`font-medium text-xs px-2 py-0.5 rounded-full ${
                      !rider.is_active
                        ? "bg-red-100 text-red-700"
                        : rider.is_online
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {!rider.is_active
                      ? "Inativo"
                      : rider.is_online
                        ? "Online"
                        : "Offline"}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between mt-4 pt-3 border-t">
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(rider)}
                    className="text-xs text-primary-600 hover:text-primary-800"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDelete(rider)}
                    className="text-xs text-red-500 hover:text-red-700"
                  >
                    Desativar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
