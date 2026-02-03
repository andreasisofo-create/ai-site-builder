import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Site Builder
          </h1>
          <p className="text-xl mb-8 text-primary-100">
            Crea siti web professionali con l&apos;AI in pochi minuti
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard" className="btn-primary text-lg">
              Inizia Ora
            </Link>
            <Link href="/docs" className="btn bg-white text-primary-600 hover:bg-gray-100 text-lg">
              Documentazione
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">
            Cosa puoi fare
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              title="Drag & Drop"
              description="Costruisci il tuo sito trascinando componenti"
              icon="🎨"
            />
            <FeatureCard
              title="AI Powered"
              description="Genera contenuti e design con l'intelligenza artificiale"
              icon="🤖"
            />
            <FeatureCard
              title="Deploy Automatico"
              description="Pubblica su Vercel con un solo click"
              icon="🚀"
            />
          </div>
        </div>
      </section>
    </main>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="card text-center">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
