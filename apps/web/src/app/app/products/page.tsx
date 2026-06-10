"use client";

import Image from "next/image";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type Variation = {
  id: string;
  name: string;
  price_cents_adjustment: number;
  is_default: boolean;
};

type Product = {
  id: string;
  category_id: string | null;
  category_name: string | null;
  name: string;
  description: string | null;
  price_cents: number;
  price_formatted: string;
  image_url: string | null;
  is_available: boolean;
  has_variations: boolean;
  variations: Variation[];
};

type ProductListResponse = {
  products: Product[];
  total: number;
};

type Category = {
  id: string;
  name: string;
};

type CategoryListResponse = {
  categories: Category[];
};

const emptyProduct = {
  category_id: null as string | null,
  name: "",
  description: "",
  price_cents: 0,
  is_available: true,
  unit_type: "unit",
};

export default function ProductsPage() {
  const { token } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form, setForm] = useState<Record<string, any>>({ ...emptyProduct });
  const [variations, setVariations] = useState<Variation[]>([]);
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [prodData, catData] = await Promise.all([
        api.get<ProductListResponse>("/api/v1/products", token),
        api.get<CategoryListResponse>("/api/v1/categories?only_active=true", token),
      ]);
      setProducts(prodData.products);
      setCategories(catData.categories);
    } catch (err) {
      console.error("Failed to load data", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleNew = () => {
    setEditing(null);
    setForm({ ...emptyProduct });
    setVariations([]);
    setShowForm(true);
  };

  const handleEdit = (prod: Product) => {
    setEditing(prod);
    setForm({
      category_id: prod.category_id,
      name: prod.name,
      description: prod.description || "",
      price_cents: prod.price_cents,
      is_available: prod.is_available,
      unit_type: "unit",
    });
    setVariations(prod.variations);
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!token || !form.name.trim()) return;
    setSaving(true);
    try {
      const body = {
        category_id: form.category_id || null,
        name: form.name,
        description: form.description || null,
        price_cents: Math.round(Number(form.price_cents)),
        is_available: form.is_available,
        unit_type: form.unit_type || "unit",
      };

      if (editing) {
        await api.put(`/api/v1/products/${editing.id}`, body, token);
      } else {
        await api.post("/api/v1/products", body, token);
      }
      setShowForm(false);
      setEditing(null);
      await fetchData();
    } catch (err) {
      console.error("Failed to save product", err);
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (prod: Product) => {
    if (!token) return;
    try {
      await api.patch(`/api/v1/products/${prod.id}/availability`, { is_available: !prod.is_available }, token);
      await fetchData();
    } catch (err) {
      console.error("Failed to toggle product", err);
    }
  };

  const handlePhotoUpload = async (productId: string, file: File) => {
    if (!token) return;
    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await api.upload<{ image_url: string }>(
        `/api/v1/products/${productId}/photo`,
        formData,
        token,
      );
      // Refresh to show new photo
      await fetchData();
      return result.image_url;
    } catch (err) {
      console.error("Failed to upload photo", err);
    }
  };

  const handleDelete = async (prod: Product) => {
    if (!token) return;
    if (!confirm(`Desativar "${prod.name}"?`)) return;
    try {
      await api.delete(`/api/v1/products/${prod.id}`, token);
      await fetchData();
    } catch (err) {
      console.error("Failed to delete product", err);
    }
  };

  const filteredProducts = products.filter((p) => {
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (categoryFilter && p.category_id !== categoryFilter) return false;
    return true;
  });

  // Variations helpers
  const addVariation = () => {
    setVariations([
      ...variations,
      { id: "", name: "", price_cents_adjustment: 0, is_default: variations.length === 0 },
    ]);
  };

  const updateVariation = (idx: number, field: string, value: any) => {
    const updated = [...variations];
    (updated[idx] as any)[field] = value;
    setVariations(updated);
  };

  const removeVariation = (idx: number) => {
    setVariations(variations.filter((_, i) => i !== idx));
  };

  const saveVariations = async (productId: string) => {
    if (!token) return;
    for (const v of variations) {
      const body = { name: v.name, price_cents_adjustment: v.price_cents_adjustment, is_default: v.is_default };
      if (v.id) {
        await api.put(`/api/v1/products/${productId}/variations/${v.id}`, body, token);
      } else {
        await api.post(`/api/v1/products/${productId}/variations`, body, token);
      }
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
          <h1 className="text-2xl font-bold text-gray-900">Produtos</h1>
          <p className="text-gray-500 mt-1">{products.length} produtos cadastrados</p>
        </div>
        <Button onClick={handleNew}>Novo produto</Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar produto..."
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-xs"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Todas as categorias</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* Form */}
      {showForm && (
        <div className="mb-8 p-6 bg-white rounded-xl border space-y-4">
          <h3 className="font-medium text-gray-900">
            {editing ? `Editar: ${editing.name}` : "Novo produto"}
          </h3>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                placeholder="Ex: Pizza Calabresa"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <select
                value={form.category_id || ""}
                onChange={(e) => setForm({ ...form, category_id: e.target.value || null })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
              >
                <option value="">Sem categoria</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Descricao</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                rows={2}
                placeholder="Descricao do produto (opcional)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Preco (R$)</label>
              <input
                type="number"
                value={form.price_cents / 100}
                onChange={(e) =>
                  setForm({ ...form, price_cents: Math.round(Number(e.target.value) * 100) })
                }
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full"
                min={0}
                step={0.5}
                placeholder="Ex: 29.90"
              />
            </div>
            <div className="flex items-end pb-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.is_available}
                  onChange={(e) => setForm({ ...form, is_available: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600"
                />
                <span className="text-sm text-gray-700">Disponivel</span>
              </label>
            </div>
          </div>

          {/* Variations */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-gray-700">Variacoes</h4>
              <Button variant="outline" size="sm" onClick={addVariation}>
                + Adicionar variacao
              </Button>
            </div>
            {variations.length === 0 && (
              <p className="text-sm text-gray-400 italic">
                Nenhuma variacao. Adicione tamanhos, sabores ou tipos (ex: Broto, Grande).
              </p>
            )}
            {variations.map((v, idx) => (
              <div key={idx} className="flex items-center gap-3 mb-2">
                <input
                  type="text"
                  value={v.name}
                  onChange={(e) => updateVariation(idx, "name", e.target.value)}
                  placeholder="Nome (ex: Grande)"
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1"
                />
                <input
                  type="number"
                  value={v.price_cents_adjustment / 100}
                  onChange={(e) =>
                    updateVariation(idx, "price_cents_adjustment", Math.round(Number(e.target.value) * 100))
                  }
                  placeholder="Ajuste R$"
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-28"
                  step={0.5}
                />
                <label className="flex items-center gap-1 text-sm text-gray-600">
                  <input
                    type="radio"
                    name="variation_default"
                    checked={v.is_default}
                    onChange={() =>
                      setVariations(
                        variations.map((vv, i) => ({ ...vv, is_default: i === idx }))
                      )
                    }
                    className="text-primary-600"
                  />
                  Padrao
                </label>
                <button
                  onClick={() => removeVariation(idx)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  Remover
                </button>
              </div>
            ))}
          </div>

          {/* Photo upload */}
          {editing && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Foto do produto</h4>
              {editing.image_url && (
                <div className="mb-2">
                  <Image
                    src={editing.image_url}
                    alt={editing.name}
                    width={128}
                    height={128}
                    className="w-32 h-32 object-cover rounded-lg border"
                    unoptimized
                  />
                </div>
              )}
              <label className="inline-flex items-center gap-2 cursor-pointer text-sm text-primary-600 hover:text-primary-800">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      await handlePhotoUpload(editing.id, file);
                    }
                  }}
                />
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {editing.image_url ? "Trocar foto" : "Adicionar foto"}
              </label>
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <Button onClick={handleSave} isLoading={saving}>
              {editing ? "Salvar" : "Criar produto"}
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

      {/* Product list */}
      {filteredProducts.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border">
          <p className="text-gray-500">Nenhum produto encontrado.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredProducts.map((prod) => (
            <div
              key={prod.id}
              className={`bg-white rounded-xl border p-5 ${
                !prod.is_available ? "opacity-60" : ""
              }`}
            >
              {prod.image_url && (
                <div className="mb-3 -mx-5 -mt-5 rounded-t-xl overflow-hidden h-36 bg-gray-100 relative">
                  <Image
                    src={prod.image_url}
                    alt={prod.name}
                    fill
                    className="object-cover"
                    unoptimized
                  />
                </div>
              )}
              <div className="flex items-start justify-between mb-2">
                <div className={prod.image_url ? "" : "mt-0"}>
                  <h3 className="font-medium text-gray-900">{prod.name}</h3>
                  {prod.category_name && (
                    <span className="text-xs text-gray-400">{prod.category_name}</span>
                  )}
                </div>
                <span className="text-lg font-bold text-primary-700">
                  {prod.price_formatted}
                </span>
              </div>

              {prod.description && (
                <p className="text-sm text-gray-500 mb-3 line-clamp-2">{prod.description}</p>
              )}

              {prod.variations.length > 0 && (
                <div className="mb-3 space-y-1">
                  <p className="text-xs text-gray-400 font-medium">Variacoes:</p>
                  {prod.variations.map((v) => (
                    <div key={v.id} className="flex justify-between text-xs text-gray-500">
                      <span>{v.name}</span>
                      <span>
                        {v.price_cents_adjustment > 0
                          ? `+R$ ${(v.price_cents_adjustment / 100).toFixed(2)}`
                          : v.is_default
                          ? "Padrao"
                          : ""}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between mt-3 pt-3 border-t">
                <label className="flex items-center gap-1.5 text-sm">
                  <input
                    type="checkbox"
                    checked={prod.is_available}
                    onChange={() => handleToggle(prod)}
                    className="rounded border-gray-300 text-primary-600"
                  />
                  <span className="text-gray-600">Disponivel</span>
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(prod)}
                    className="text-xs text-primary-600 hover:text-primary-800"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDelete(prod)}
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
