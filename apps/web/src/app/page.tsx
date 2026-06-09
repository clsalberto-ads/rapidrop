import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center space-y-6 max-w-2xl">
        <h1 className="text-5xl font-bold text-primary-600">
          RapiDrop
        </h1>
        <p className="text-xl text-gray-600">
          Delivery Intelligence para restaurantes, farmácias e mercados.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/app"
            className="rounded-lg bg-primary-600 px-6 py-3 text-white font-medium hover:bg-primary-700 transition-colors"
          >
            Acessar Painel
          </Link>
          <Link
            href="/admin"
            className="rounded-lg border border-gray-300 px-6 py-3 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Admin
          </Link>
        </div>
      </div>
    </main>
  );
}
