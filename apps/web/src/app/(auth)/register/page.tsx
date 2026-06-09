"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

type Step1Data = { email: string; password: string };
type Step2Data = { name: string; business_name: string; document: string; phone: string };

const segments = [
  { value: "food", label: "Restaurante", icon: "🍕", desc: "Pizzarias, hamburguerias, marmitas" },
  { value: "pharmacy", label: "Farmácia", icon: "💊", desc: "Medicamentos, manipulação, perfumaria" },
  { value: "grocery", label: "Mercado", icon: "🛒", desc: "Mercearia, hortifrúti, bebidas" },
];

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [name, setName] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [document, setDocument] = useState("");
  const [phone, setPhone] = useState("");

  const [segment, setSegment] = useState("");

  function validateStep1(): boolean {
    if (!email || !password) { setError("Preencha todos os campos"); return false; }
    if (password.length < 6) { setError("Senha deve ter no mínimo 6 caracteres"); return false; }
    if (password !== confirmPassword) { setError("Senhas não conferem"); return false; }
    return true;
  }

  function validateStep2(): boolean {
    if (!name || !businessName || !document || !phone) { setError("Preencha todos os campos"); return false; }
    return true;
  }

  async function handleSubmit() {
    if (!segment) { setError("Selecione um segmento"); return; }
    setError("");
    setIsLoading(true);

    try {
      await register({
        email, password, name,
        business_name: businessName,
        document, phone, segment,
      });
      router.push("/onboarding/welcome");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao cadastrar");
    } finally {
      setIsLoading(false);
    }
  }

  const stepIndicator = (
    <div className="flex items-center justify-center gap-2 mb-6">
      {[1, 2, 3].map((s) => (
        <div key={s} className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            s <= step ? "bg-primary-600 text-white" : "bg-gray-200 text-gray-500"
          }`}>
            {s}
          </div>
          {s < 3 && <div className={`w-8 h-0.5 ${s < step ? "bg-primary-600" : "bg-gray-200"}`} />}
        </div>
      ))}
    </div>
  );

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Criar conta</h1>
          <p className="text-sm text-gray-500 mt-1">
            {step === 1 && "Informe seu email e crie uma senha"}
            {step === 2 && "Dados da sua loja"}
            {step === 3 && "Qual o segmento da sua loja?"}
          </p>
        </div>
      </CardHeader>
      <CardContent>
        {stepIndicator}

        {error && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200 mb-4">
            {error}
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <Input id="email" label="Email" type="email" placeholder="seu@email.com"
              value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input id="password" label="Senha" type="password" placeholder="Mínimo 6 caracteres"
              value={password} onChange={(e) => setPassword(e.target.value)} required />
            <Input id="confirmPassword" label="Confirmar senha" type="password"
              value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
            <Button className="w-full" onClick={() => { setError(""); if (validateStep1()) setStep(2); }}>
              Continuar
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <Input id="name" label="Nome da loja" placeholder="Pizzaria do João"
              value={name} onChange={(e) => setName(e.target.value)} required />
            <Input id="businessName" label="Razão social" placeholder="Pizzaria do João Ltda"
              value={businessName} onChange={(e) => setBusinessName(e.target.value)} required />
            <Input id="document" label="CNPJ/CPF" placeholder="00.000.000/0001-00"
              value={document} onChange={(e) => setDocument(e.target.value)} required />
            <Input id="phone" label="Telefone" placeholder="(11) 99999-9999"
              value={phone} onChange={(e) => setPhone(e.target.value)} required />
            <div className="flex gap-3">
              <Button variant="outline" className="flex-1" onClick={() => setStep(1)}>Voltar</Button>
              <Button className="flex-1" onClick={() => { setError(""); if (validateStep2()) setStep(3); }}>
                Continuar
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div className="grid gap-3">
              {segments.map((seg) => (
                <button
                  key={seg.value}
                  onClick={() => setSegment(seg.value)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    segment === seg.value
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{seg.icon}</span>
                    <div>
                      <p className="font-medium text-gray-900">{seg.label}</p>
                      <p className="text-sm text-gray-500">{seg.desc}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <Button variant="outline" className="flex-1" onClick={() => setStep(2)}>Voltar</Button>
              <Button className="flex-1" isLoading={isLoading} onClick={handleSubmit}>
                Criar conta
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
