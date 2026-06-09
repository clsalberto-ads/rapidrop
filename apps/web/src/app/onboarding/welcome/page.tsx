"use client";

import { useRouter } from "next/navigation";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

export default function WelcomePage() {
  const router = useRouter();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="text-center">
            <div className="text-4xl mb-4">🎉</div>
            <h1 className="text-2xl font-bold text-gray-900">
              Bem-vindo, {user?.name || "lojista"}!
            </h1>
            <p className="text-gray-500 mt-2">
              Sua conta RapiDrop foi criada com sucesso.
            </p>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900">Checklist de onboarding</h3>
              <ul className="mt-2 space-y-2">
                <li className="flex items-center gap-2 text-sm text-blue-700">
                  <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs">✓</span>
                  Conta criada
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-500">
                  <span className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-xs">2</span>
                  Configurar horário de funcionamento
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-500">
                  <span className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-xs">3</span>
                  Definir área de entrega
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-500">
                  <span className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-xs">4</span>
                  Adicionar produtos ao catálogo
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-500">
                  <span className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-xs">5</span>
                  Convidar entregadores
                </li>
              </ul>
            </div>
            <Button className="w-full" onClick={() => router.push("/app")}>
              Ir para o painel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
