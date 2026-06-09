"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (isAuthenticated) {
    router.push("/app");
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(email, password);
      router.push("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao fazer login");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">RapiDrop</h1>
          <p className="text-sm text-gray-500 mt-1">Faça login no seu painel</p>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
              {error}
            </div>
          )}
          <Input
            id="email"
            label="Email"
            type="email"
            placeholder="seu@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            id="password"
            label="Senha"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <div className="flex items-center justify-end">
            <Link href="#" className="text-sm text-primary-600 hover:text-primary-700">
              Esqueceu a senha?
            </Link>
          </div>
          <Button type="submit" className="w-full" isLoading={isLoading}>
            Entrar
          </Button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Não tem conta?{" "}
          <Link href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
            Cadastre-se
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
