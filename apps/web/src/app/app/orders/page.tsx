"use client";

import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type OrderItem = {
  id: string;
  product_name: string;
  quantity: number;
  total_cents: number;
  special_notes: string | null;
};

type Order = {
  id: string;
  sequential_id: number;
  customer_id: string;
  rider_id: string | null;
  channel: string;
  status: string;
  items: OrderItem[];
  subtotal_cents: number;
  delivery_fee_cents: number;
  discount_cents: number;
  total_cents: number;
  payment_method: string;
  payment_status: string;
  customer_notes: string | null;
  created_at: string;
};

type OrderListResponse = {
  orders: Order[];
  total: number;
};

const statusLabels: Record<string, string> = {
  pending: "Pendente",
  confirmed: "Confirmado",
  preparing: "Preparando",
  ready: "Pronto",
  out_for_delivery: "Saiu para entrega",
  delivered: "Entregue",
  cancelled: "Cancelado",
};

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  confirmed: "bg-blue-100 text-blue-800",
  preparing: "bg-indigo-100 text-indigo-800",
  ready: "bg-green-100 text-green-800",
  out_for_delivery: "bg-purple-100 text-purple-800",
  delivered: "bg-gray-100 text-gray-600",
  cancelled: "bg-red-100 text-red-800",
};

const paymentStatusLabels: Record<string, string> = {
  pending: "Aguardando",
  approved: "Aprovado",
  declined: "Recusado",
  refunded: "Reembolsado",
};

const paymentStatusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  declined: "bg-red-100 text-red-800",
  refunded: "bg-gray-100 text-gray-600",
};

const channelLabels: Record<string, string> = {
  whatsapp: "WhatsApp",
  app: "App",
  web: "Site",
  phone: "Telefone",
};

function fmtPrice(cents: number) {
  return `R$ ${(cents / 100).toFixed(2)}`;
}

export default function OrdersPage() {
  const { token } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "100" });
      if (statusFilter) params.set("status", statusFilter);
      const data = await api.get<OrderListResponse>(
        `/api/v1/orders?${params}`,
        token,
      );
      setOrders(data.orders);
    } catch (err) {
      console.error("Failed to load orders", err);
    } finally {
      setLoading(false);
    }
  }, [token, statusFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    if (!token) return;
    try {
      await api.patch(`/api/v1/orders/${orderId}/status`, { status: newStatus }, token);
      await fetchData();
    } catch (err) {
      console.error("Failed to update order status", err);
    }
  };

  const toggleExpand = (id: string) => {
    const next = new Set(expanded);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpanded(next);
  };

  const nextStatus = (current: string): { status: string; label: string } | null => {
    const flow: Record<string, string> = {
      pending: "confirmed",
      confirmed: "preparing",
      preparing: "ready",
      ready: "out_for_delivery",
      out_for_delivery: "delivered",
    };
    const next = flow[current];
    if (!next) return null;
    return { status: next, label: statusLabels[next] };
  };

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
          <h1 className="text-2xl font-bold text-gray-900">Pedidos</h1>
          <p className="text-gray-500 mt-1">{orders.length} pedidos</p>
        </div>
      </div>

      {/* Status filter tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {["", ...Object.keys(statusLabels)].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors ${
              statusFilter === s
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {s ? statusLabels[s] : "Todos"}
          </button>
        ))}
      </div>

      {/* Order list */}
      {orders.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border">
          <p className="text-gray-500">Nenhum pedido encontrado.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => {
            const next = nextStatus(order.status);
            const isExpanded = expanded.has(order.id);

            return (
              <div key={order.id} className="bg-white rounded-xl border overflow-hidden">
                {/* Header */}
                <button
                  onClick={() => toggleExpand(order.id)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-lg font-bold text-gray-900">
                      #{order.sequential_id}
                    </span>
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        statusColors[order.status] || "bg-gray-100"
                      }`}
                    >
                      {statusLabels[order.status] || order.status}
                    </span>
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        paymentStatusColors[order.payment_status] || "bg-gray-100"
                      }`}
                    >
                      {paymentStatusLabels[order.payment_status] || order.payment_status}
                    </span>
                    <span className="text-xs text-gray-400">
                      {channelLabels[order.channel] || order.channel}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-primary-700">
                      {fmtPrice(order.total_cents)}
                    </span>
                    <svg
                      className={`w-4 h-4 text-gray-400 transition-transform ${
                        isExpanded ? "rotate-180" : ""
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="border-t px-4 py-4 space-y-4">
                    {/* Items */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Itens</h4>
                      <div className="space-y-1">
                        {order.items.map((item) => (
                          <div
                            key={item.id}
                            className="flex justify-between text-sm"
                          >
                            <span className="text-gray-600">
                              {item.quantity}x {item.product_name}
                              {item.special_notes && (
                                <span className="text-gray-400 ml-1">
                                  ({item.special_notes})
                                </span>
                              )}
                            </span>
                            <span className="text-gray-800 font-medium">
                              {fmtPrice(item.total_cents)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Totals */}
                    <div className="border-t pt-3 space-y-1 text-sm">
                      <div className="flex justify-between text-gray-500">
                        <span>Subtotal</span>
                        <span>{fmtPrice(order.subtotal_cents)}</span>
                      </div>
                      {order.delivery_fee_cents > 0 && (
                        <div className="flex justify-between text-gray-500">
                          <span>Taxa de entrega</span>
                          <span>{fmtPrice(order.delivery_fee_cents)}</span>
                        </div>
                      )}
                      {order.discount_cents > 0 && (
                        <div className="flex justify-between text-green-600">
                          <span>Desconto</span>
                          <span>-{fmtPrice(order.discount_cents)}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-gray-900 font-bold pt-1 border-t">
                        <span>Total</span>
                        <span>{fmtPrice(order.total_cents)}</span>
                      </div>
                    </div>

                    {/* Customer notes */}
                    {order.customer_notes && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
                        <strong>Obs do cliente:</strong> {order.customer_notes}
                      </div>
                    )}

                    {/* Status actions */}
                    <div className="flex gap-2 pt-2 border-t">
                      {next && (
                        <Button
                          size="sm"
                          onClick={() => handleStatusUpdate(order.id, next.status)}
                        >
                          Avançar para {next.label}
                        </Button>
                      )}
                      {order.status !== "cancelled" && order.status !== "delivered" && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleStatusUpdate(order.id, "cancelled")}
                        >
                          Cancelar pedido
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
