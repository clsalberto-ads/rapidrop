"use client";

import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type Settings = {
  operating_hours: Array<{
    day_of_week: number;
    open_time: string;
    close_time: string;
    is_open: boolean;
  }>;
  delivery_area: {
    type: string;
    radius_km: number | null;
    neighborhoods: string[] | null;
    base_address_lat: number | null;
    base_address_lng: number | null;
  };
  delivery_fee: {
    type: string;
    fixed_fee_cents: number | null;
    per_km_cents: number | null;
    free_above_cents: number | null;
  };
};

const DAY_NAMES = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"];

export default function SettingsPage() {
  const { token } = useAuth();
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [tab, setTab] = useState<"hours" | "delivery" | "fee">("hours");

  useEffect(() => {
    if (!token) return;
    api.get<Settings>("/api/v1/merchants/me/settings", token)
      .then(setSettings)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

  const handleSave = async () => {
    if (!token || !settings) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.put("/api/v1/merchants/me/settings", settings, token);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error("Failed to save settings", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!settings) {
    return <div className="text-gray-500">Erro ao carregar configurações.</div>;
  }

  const tabs: { key: typeof tab; label: string }[] = [
    { key: "hours", label: "Horário de Funcionamento" },
    { key: "delivery", label: "Área de Entrega" },
    { key: "fee", label: "Taxa de Entrega" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configurações da Loja</h1>
          <p className="text-gray-500 mt-1">Configure horários, área e taxa de entrega</p>
        </div>
        <Button onClick={handleSave} isLoading={saving}>
          {saved ? "Salvo!" : "Salvar alterações"}
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-8 border-b border-gray-200">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              tab === t.key
                ? "border-primary-600 text-primary-700"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Operating Hours */}
      {tab === "hours" && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500 mb-4">
            Defina os horários de funcionamento da sua loja para cada dia da semana.
          </p>
          {settings.operating_hours.length === 0 && (
            <p className="text-sm text-gray-400 italic">
              Nenhum horário configurado. Preencha abaixo.
            </p>
          )}
          {DAY_NAMES.map((dayName, idx) => {
            const hour = settings.operating_hours.find((h) => h.day_of_week === idx) || {
              day_of_week: idx,
              open_time: "08:00",
              close_time: "22:00",
              is_open: true,
            };
            return (
              <div key={idx} className="flex items-center gap-4 p-4 bg-white rounded-lg border">
                <div className="w-24 font-medium text-gray-700">{dayName}</div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={hour.is_open}
                    onChange={(e) => {
                      const newHours = [...settings.operating_hours.filter((h) => h.day_of_week !== idx)];
                      newHours.push({ ...hour, is_open: e.target.checked });
                      setSettings({ ...settings, operating_hours: newHours });
                    }}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-600">Aberto</span>
                </label>
                {hour.is_open && (
                  <>
                    <input
                      type="time"
                      value={hour.open_time}
                      onChange={(e) => {
                        const newHours = [...settings.operating_hours.filter((h) => h.day_of_week !== idx)];
                        newHours.push({ ...hour, open_time: e.target.value });
                        setSettings({ ...settings, operating_hours: newHours });
                      }}
                      className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
                    />
                    <span className="text-gray-400">até</span>
                    <input
                      type="time"
                      value={hour.close_time}
                      onChange={(e) => {
                        const newHours = [...settings.operating_hours.filter((h) => h.day_of_week !== idx)];
                        newHours.push({ ...hour, close_time: e.target.value });
                        setSettings({ ...settings, operating_hours: newHours });
                      }}
                      className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
                    />
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Delivery Area */}
      {tab === "delivery" && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de área de entrega
            </label>
            <select
              value={settings.delivery_area.type}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  delivery_area: { ...settings.delivery_area, type: e.target.value },
                })
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
            >
              <option value="radius">Raio (km) a partir da loja</option>
              <option value="neighborhoods">Bairros específicos</option>
            </select>
          </div>

          {settings.delivery_area.type === "radius" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Raio de entrega (km)
              </label>
              <input
                type="number"
                value={settings.delivery_area.radius_km || ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    delivery_area: {
                      ...settings.delivery_area,
                      radius_km: Number(e.target.value) || null,
                    },
                  })
                }
                min={1}
                max={100}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
                placeholder="Ex: 10"
              />
              <p className="text-xs text-gray-400 mt-1">
                Apenas pedidos dentro deste raio serao aceitos.
              </p>
            </div>
          )}

          {settings.delivery_area.type === "neighborhoods" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bairros atendidos
              </label>
              <textarea
                value={(settings.delivery_area.neighborhoods || []).join("\n")}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    delivery_area: {
                      ...settings.delivery_area,
                      neighborhoods: e.target.value.split("\n").filter(Boolean),
                    },
                  })
                }
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-md"
                rows={5}
                placeholder="Digite um bairro por linha"
              />
              <p className="text-xs text-gray-400 mt-1">Um bairro por linha.</p>
            </div>
          )}
        </div>
      )}

      {/* Delivery Fee */}
      {tab === "fee" && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de taxa de entrega
            </label>
            <select
              value={settings.delivery_fee.type}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  delivery_fee: { ...settings.delivery_fee, type: e.target.value },
                })
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
            >
              <option value="fixed">Taxa fixa</option>
              <option value="per_km">Por km</option>
              <option value="free_above">Gratis acima de valor</option>
            </select>
          </div>

          {settings.delivery_fee.type === "fixed" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Taxa fixa (R$)
              </label>
              <input
                type="number"
                value={(settings.delivery_fee.fixed_fee_cents || 0) / 100}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    delivery_fee: {
                      ...settings.delivery_fee,
                      fixed_fee_cents: Math.round(Number(e.target.value) * 100),
                    },
                  })
                }
                min={0}
                step={0.5}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
                placeholder="Ex: 5.00"
              />
            </div>
          )}

          {settings.delivery_fee.type === "per_km" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Valor por km (R$)
              </label>
              <input
                type="number"
                value={(settings.delivery_fee.per_km_cents || 0) / 100}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    delivery_fee: {
                      ...settings.delivery_fee,
                      per_km_cents: Math.round(Number(e.target.value) * 100),
                    },
                  })
                }
                min={0}
                step={0.5}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
                placeholder="Ex: 2.00"
              />
            </div>
          )}

          {settings.delivery_fee.type === "free_above" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pedido minimo para entrega gratuita (R$)
              </label>
              <input
                type="number"
                value={(settings.delivery_fee.free_above_cents || 0) / 100}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    delivery_fee: {
                      ...settings.delivery_fee,
                      free_above_cents: Math.round(Number(e.target.value) * 100),
                      fixed_fee_cents: settings.delivery_fee.fixed_fee_cents,
                    },
                  })
                }
                min={0}
                step={5}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
                placeholder="Ex: 30.00"
              />
              <p className="text-xs text-gray-400 mt-1">
                Pedidos abaixo deste valor pagam a taxa fixa configurada.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
