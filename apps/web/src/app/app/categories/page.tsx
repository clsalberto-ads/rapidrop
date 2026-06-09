"use client";

import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type Category = {
  id: string;
  name: string;
  sort_order: number;
  is_active: boolean;
  product_count: number;
};

type CategoryListResponse = {
  categories: Category[];
  total: number;
};

export default function CategoriesPage() {
  const { token } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Category | null>(null);
  const [name, setName] = useState("");
  const [sortOrder, setSortOrder] = useState(0);
  const [saving, setSaving] = useState(false);

  const fetchCategories = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.get<CategoryListResponse>("/api/v1/categories", token);
      setCategories(data.categories);
    } catch (err) {
      console.error("Failed to load categories", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const handleEdit = (cat: Category) => {
    setEditing(cat);
    setName(cat.name);
    setSortOrder(cat.sort_order);
    setShowForm(true);
  };

  const handleNew = () => {
    setEditing(null);
    setName("");
    setSortOrder(categories.length);
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!token || !name.trim()) return;
    setSaving(true);
    try {
      if (editing) {
        await api.put(`/api/v1/categories/${editing.id}`, { name, sort_order: sortOrder }, token);
      } else {
        await api.post("/api/v1/categories", { name, sort_order: sortOrder }, token);
      }
      setShowForm(false);
      setEditing(null);
      await fetchCategories();
    } catch (err) {
      console.error("Failed to save category", err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (cat: Category) => {
    if (!token) return;
    try {
      await api.delete(`/api/v1/categories/${cat.id}`, token);
      await fetchCategories();
    } catch (err) {
      console.error("Failed to deactivate category", err);
    }
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
          <h1 className="text-2xl font-bold text-gray-900">Categorias</h1>
          <p className="text-gray-500 mt-1">
            {categories.length} categorias cadastradas
          </p>
        </div>
        <Button onClick={handleNew}>Nova categoria</Button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="mb-8 p-6 bg-white rounded-xl border space-y-4">
          <h3 className="font-medium text-gray-900">
            {editing ? "Editar categoria" : "Nova categoria"}
          </h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-md"
              placeholder="Ex: Pizzas, Bebidas, Sobremesas"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ordem de exibicao
            </label>
            <input
              type="number"
              value={sortOrder}
              onChange={(e) => setSortOrder(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-24"
              min={0}
            />
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSave} isLoading={saving}>
              {editing ? "Salvar" : "Criar"}
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

      {/* List */}
      {categories.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border">
          <p className="text-gray-500">Nenhuma categoria cadastrada.</p>
          <p className="text-sm text-gray-400 mt-1">
            Crie categorias para organizar seus produtos.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Nome</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Ordem</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">Produtos</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">Ativo</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-gray-500">Acoes</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => (
                <tr key={cat.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{cat.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{cat.sort_order}</td>
                  <td className="px-4 py-3 text-sm text-center text-gray-500">{cat.product_count}</td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        cat.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {cat.is_active ? "Sim" : "Nao"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-right">
                    <button
                      onClick={() => handleEdit(cat)}
                      className="text-primary-600 hover:text-primary-800 mr-3"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDeactivate(cat)}
                      className="text-red-500 hover:text-red-700"
                    >
                      Desativar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
