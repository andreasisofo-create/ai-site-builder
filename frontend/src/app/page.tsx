"use client";

import Link from "next/link";
import { useState } from "react";
import { 
  RocketIcon, 
  PaletteIcon, 
  GlobeIcon,
  ChevronDownIcon,
  CheckIcon,
  ArrowRightIcon,
  ZapIcon,
  ShieldIcon,
  ClockIcon,
  LayoutIcon,
  CodeIcon,
  MonitorIcon
} from "lucide-react";
import Image from "next/image";

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [lang, setLang] = useState<'en' | 'it'>('it');

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const t = {
    en: {
      nav: {
        features: "Features",
        howItWorks: "How It Works",
        pricing: "Pricing",
        faq: "FAQ",
        getStarted: "Get Started"
      },
      hero: {
        title1: "Professional websites",
        title2: "in minutes.",
        subtitle: "Create stunning, professional websites without writing code. Just describe your business and our platform builds your perfect site instantly.",
        ctaPrimary: "Create Your Site",
        ctaSecondary: "See How It Works",
        stat1: "Average Build Time",
        stat2: "Starting Price",
        stat3: "Yours Forever"
      },
      features: {
        title: "Built for professionals.",
        subtitle: "Everything you need for a perfect online presence.",
        items: [
          { title: "Lightning Fast", desc: "Get your complete website in under 60 seconds. No waiting, no hassle. Just instant results tailored to your needs." },
          { title: "Fully Customizable", desc: "Every element is editable. Change colors, text, images, and layouts with our intuitive drag-and-drop editor." },
          { title: "Professional Design", desc: "Industry-leading templates and design systems crafted by expert designers for any business type." },
          { title: "Secure & Reliable", desc: "Enterprise-grade security with SSL certificates, DDoS protection, and 99.9% uptime guarantee." },
          { title: "Free Domain Included", desc: "Get a free subdomain or connect your own custom domain. We handle all the technical DNS setup." },
          { title: "No Hidden Fees", desc: "Pay once, own forever. No monthly subscriptions, no recurring charges. Your site is 100% yours." }
        ]
      },
      howItWorks: {
        title: "How it works.",
        subtitle: "Four simple steps to your dream website.",
        steps: [
          { title: "Describe Your Vision", desc: "Tell us about your business, your style, and what you need. The more details, the better we can match your vision." },
          { title: "We Build Your Site", desc: "Our advanced platform creates a complete website with professional design in under 60 seconds." },
          { title: "Customize & Refine", desc: "Make adjustments with our visual editor. Change any element instantly with simple point-and-click." },
          { title: "Publish & Go Live", desc: "Choose your domain, connect it, and launch your site to the world. It's that simple." }
        ]
      },
      pricing: {
        title: "Simple, transparent pricing.",
        subtitle: "Pay once. Own forever. No hidden fees.",
        popular: "Most Popular",
        plans: [
          { name: "Starter", price: "Free", period: "Build your site", features: ["Create up to 3 projects", "Preview & editing", "Basic templates"] },
          { name: "Homepage", price: "€200", period: "One-time payment", features: ["1 Professional Homepage", "Custom Domain", "SSL Certificate", "Hosting Included", "Unlimited Edits (30 days)"] },
          { name: "Extra Pages", price: "€70", period: "Per additional page", features: ["About, Services, Contact", "Gallery, Portfolio, Blog", "Professional content", "Matching design"] }
        ]
      },
      faq: {
        title: "Frequently asked questions.",
        items: [
          { q: "What is E-quipe Site Builder?", a: "E-quipe Site Builder is a revolutionary platform that creates professional websites in minutes. You simply describe your business and vision, and our platform generates a complete, customized website ready to publish." },
          { q: "How long does it take to create a website?", a: "Most websites are generated in under 60 seconds. After that, you can spend as much time as you want refining and customizing until it's perfect." },
          { q: "Do I need coding skills?", a: "Absolutely not! Our platform is designed for everyone. The system handles all the technical aspects, and our visual editor makes customization simple and intuitive." },
          { q: "Can I use my own domain?", a: "Yes! You can connect any custom domain you own, or get a free subdomain (yoursite.e-quipe.app). We handle all the technical DNS configuration for you." },
          { q: "What do I get for €200?", a: "You get a complete, professional homepage with custom design, hosting, SSL certificate, and your chosen domain. You own the site 100% with no recurring fees. Additional pages are €70 each." },
          { q: "Can I edit my site after publishing?", a: "Yes! You have 30 days of unlimited edits included. After that, you can still make changes anytime through our editor or contact us for assistance." }
        ]
      },
      cta: {
        title: "Ready to create your site?",
        subtitle: "Join thousands of businesses who've transformed their online presence with E-quipe.",
        button: "Start Building"
      },
      footer: {
        rights: "© 2026 E-quipe. All rights reserved.",
        privacy: "Privacy",
        terms: "Terms",
        contact: "Contact"
      }
    },
    it: {
      nav: {
        features: "Funzionalità",
        howItWorks: "Come Funziona",
        pricing: "Prezzi",
        faq: "FAQ",
        getStarted: "Inizia Ora"
      },
      hero: {
        title1: "Siti web professionali",
        title2: "in pochi minuti.",
        subtitle: "Crea siti web straordinari e professionali senza scrivere codice. Descrivi la tua attività e la nostra piattaforma costruisce il sito perfetto istantaneamente.",
        ctaPrimary: "Crea il Tuo Sito",
        ctaSecondary: "Vedi Come Funziona",
        stat1: "Tempo Medio di Creazione",
        stat2: "Prezzo di Partenza",
        stat3: "Tuo per Sempre"
      },
      features: {
        title: "Costruito per professionisti.",
        subtitle: "Tutto ciò che ti serve per una presenza online perfetta.",
        items: [
          { title: "Velocità Fulminea", desc: "Ottieni il tuo sito web completo in meno di 60 secondi. Nessuna attesa, nessun problema. Solo risultati istantanei su misura per te." },
          { title: "Completamente Personalizzabile", desc: "Ogni elemento è modificabile. Cambia colori, testo, immagini e layout con il nostro editor drag-and-drop intuitivo." },
          { title: "Design Professionale", desc: "Template e sistemi di design di livello industriale creati da designer esperti per qualsiasi tipo di attività." },
          { title: "Sicuro e Affidabile", desc: "Sicurezza di livello enterprise con certificati SSL, protezione DDoS e garanzia di uptime 99.9%." },
          { title: "Dominio Incluso Gratis", desc: "Ottieni un sottodominio gratuito o collega il tuo dominio personalizzato. Gestiamo noi tutta la configurazione DNS." },
          { title: "Nessun Costo Nascosto", desc: "Paga una volta, tuo per sempre. Nessun abbonamento mensile, nessun addebito ricorrente. Il sito è 100% tuo." }
        ]
      },
      howItWorks: {
        title: "Come funziona.",
        subtitle: "Quattro semplici passaggi per il sito dei tuoi sogni.",
        steps: [
          { title: "Descrivi la Tua Visione", desc: "Parlaci della tua attività, del tuo stile e di cosa ti serve. Più dettagli, meglio possiamo realizzare la tua visione." },
          { title: "Costruiamo il Tuo Sito", desc: "La nostra piattaforma avanzata crea un sito web completo con design professionale in meno di 60 secondi." },
          { title: "Personalizza e Perfeziona", desc: "Apporta modifiche con il nostro editor visuale. Cambia qualsiasi elemento istantaneamente con un semplice punto-e-clicca." },
          { title: "Pubblica e Vai Online", desc: "Scegli il tuo dominio, collegalo e lancia il tuo sito nel mondo. È semplice così." }
        ]
      },
      pricing: {
        title: "Prezzi semplici e trasparenti.",
        subtitle: "Paga una volta. Tuo per sempre. Nessun costo nascosto.",
        popular: "Più Popolare",
        plans: [
          { name: "Starter", price: "Gratis", period: "Costruisci il tuo sito", features: ["Crea fino a 3 progetti", "Anteprima e editing", "Template di base"] },
          { name: "Homepage", price: "€200", period: "Pagamento unico", features: ["1 Homepage Professionale", "Dominio Personalizzato", "Certificato SSL", "Hosting Incluso", "Modifiche Illimitate (30 giorni)"] },
          { name: "Pagine Extra", price: "€70", period: "Per pagina aggiuntiva", features: ["Chi Siamo, Servizi, Contatti", "Galleria, Portfolio, Blog", "Contenuti professionali", "Design coordinato"] }
        ]
      },
      faq: {
        title: "Domande frequenti.",
        items: [
          { q: "Cos'è E-quipe Site Builder?", a: "E-quipe Site Builder è una piattaforma rivoluzionaria che crea siti web professionali in pochi minuti. Descrivi semplicemente la tua attività e la tua visione, e la nostra piattaforma genera un sito web completo e personalizzato pronto per essere pubblicato." },
          { q: "Quanto tempo ci vuole per creare un sito web?", a: "La maggior parte dei siti web viene generata in meno di 60 secondi. Dopo di che, puoi dedicare tutto il tempo che vuoi a perfezionare e personalizzare finché non è perfetto." },
          { q: "Ho bisogno di competenze di programmazione?", a: "Assolutamente no! La nostra piattaforma è progettata per tutti. Il sistema gestisce tutti gli aspetti tecnici, e il nostro editor visuale rende la personalizzazione semplice e intuitiva." },
          { q: "Posso usare il mio dominio?", a: "Sì! Puoi collegare qualsiasi dominio personalizzato che possiedi, oppure ottenere un sottodominio gratuito (iltuosito.e-quipe.app). Gestiamo noi tutta la configurazione tecnica DNS per te." },
          { q: "Cosa ottengo per €200?", a: "Ottieni una homepage completa e professionale con design personalizzato, hosting, certificato SSL e il dominio scelto. Il sito è tuo al 100% senza costi ricorrenti. Le pagine aggiuntive sono €70 ciascuna." },
          { q: "Posso modificare il sito dopo la pubblicazione?", a: "Sì! Hai inclusi 30 giorni di modifiche illimitate. Dopo di che, puoi comunque apportare modifiche in qualsiasi momento attraverso il nostro editor o contattarci per assistenza." }
        ]
      },
      cta: {
        title: "Pronto a creare il tuo sito?",
        subtitle: "Unisciti a migliaia di attività che hanno trasformato la loro presenza online con E-quipe.",
        button: "Inizia a Costruire"
      },
      footer: {
        rights: "© 2026 E-quipe. Tutti i diritti riservati.",
        privacy: "Privacy",
        terms: "Termini",
        contact: "Contatti"
      }
    }
  };

  const current = t[lang];

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-600/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 border-b border-white/10 backdrop-blur-xl bg-slate-950/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image 
              src="/logo.png" 
              alt="E-quipe Logo" 
              width={40} 
              height={40}
              className="h-10 w-auto"
            />
            <span className="text-xl font-bold">E-quipe</span>
          </div>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-slate-400 hover:text-white transition-colors">{current.nav.features}</a>
            <a href="#how-it-works" className="text-slate-400 hover:text-white transition-colors">{current.nav.howItWorks}</a>
            <a href="#pricing" className="text-slate-400 hover:text-white transition-colors">{current.nav.pricing}</a>
            <a href="#faq" className="text-slate-400 hover:text-white transition-colors">{current.nav.faq}</a>
          </div>

          <div className="flex items-center gap-4">
            {/* Language Toggle */}
            <button 
              onClick={() => setLang(lang === 'en' ? 'it' : 'en')}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/20 text-sm hover:bg-white/5 transition-colors"
            >
              <GlobeIcon className="w-4 h-4" />
              {lang === 'en' ? 'EN' : 'IT'}
            </button>
            
            <Link 
              href="/auth" 
              className="px-6 py-2.5 bg-white text-slate-950 rounded-full font-semibold hover:bg-slate-200 transition-colors"
            >
              {current.nav.getStarted}
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-8">
                <ZapIcon className="w-4 h-4" />
                <span>E-quipe Platform</span>
              </div>
              
              <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                {current.hero.title1}
                <br />
                <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
                  {current.hero.title2}
                </span>
              </h1>
              
              <p className="text-xl text-slate-400 mb-10">
                {current.hero.subtitle}
              </p>
              
              <div className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                <Link 
                  href="/auth"
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-full font-semibold text-lg hover:opacity-90 transition-opacity flex items-center gap-2"
                >
                  <RocketIcon className="w-5 h-5" />
                  {current.hero.ctaPrimary}
                </Link>
                <a 
                  href="#how-it-works"
                  className="px-8 py-4 border border-white/20 rounded-full font-semibold text-lg hover:bg-white/5 transition-colors"
                >
                  {current.hero.ctaSecondary}
                </a>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-8 mt-12 pt-10 border-t border-white/10">
                <div>
                  <div className="text-3xl font-bold text-white">60s</div>
                  <div className="text-slate-500 text-sm">{current.hero.stat1}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-white">€200</div>
                  <div className="text-slate-500 text-sm">{current.hero.stat2}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-white">100%</div>
                  <div className="text-slate-500 text-sm">{current.hero.stat3}</div>
                </div>
              </div>
            </div>

            {/* Hero Image */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
                <img 
                  src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop" 
                  alt="Website Builder Dashboard"
                  className="w-full h-auto"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-sm font-medium">E-quipe Builder...</span>
                    </div>
                    <div className="mt-2 h-2 bg-white/20 rounded-full overflow-hidden">
                      <div className="h-full w-3/4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-24 bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              {current.features.title}
            </h2>
            <p className="text-xl text-slate-400">
              {current.features.subtitle}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {current.features.items.map((item, idx) => (
              <FeatureCard 
                key={idx}
                icon={[
                  <ZapIcon className="w-8 h-8" />,
                  <PaletteIcon className="w-8 h-8" />,
                  <LayoutIcon className="w-8 h-8" />,
                  <ShieldIcon className="w-8 h-8" />,
                  <GlobeIcon className="w-8 h-8" />,
                  <CheckIcon className="w-8 h-8" />
                ][idx]}
                title={item.title}
                description={item.desc}
              />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              {current.howItWorks.title}
            </h2>
            <p className="text-xl text-slate-400">
              {current.howItWorks.subtitle}
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {current.howItWorks.steps.map((step, idx) => (
              <StepCard 
                key={idx}
                number={(idx + 1).toString()}
                title={step.title}
                description={step.desc}
              />
            ))}
          </div>

          {/* Screenshot Demo */}
          <div className="mt-20 relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
            <img 
              src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&h=700&fit=crop" 
              alt="E-quipe Builder Interface"
              className="w-full h-auto"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative z-10 py-24 bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              {current.pricing.title}
            </h2>
            <p className="text-xl text-slate-400">
              {current.pricing.subtitle}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {current.pricing.plans.map((plan, idx) => (
              <div key={idx} className={`p-8 rounded-2xl border ${idx === 1 ? 'border-2 border-blue-500 bg-gradient-to-b from-blue-500/10 to-transparent relative' : 'border-white/10 bg-slate-900/50'}`}>
                {idx === 1 && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-500 rounded-full text-sm font-medium">
                    {current.pricing.popular}
                  </div>
                )}
                <div className="text-sm font-medium text-slate-400 mb-2">{plan.name}</div>
                <div className="text-4xl font-bold mb-1">{plan.price}</div>
                <div className="text-slate-500 mb-6">{plan.period}</div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-center gap-3">
                      <CheckIcon className="w-5 h-5 text-blue-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link 
                  href="/auth"
                  className={`w-full py-3 rounded-full font-semibold text-center block ${idx === 1 ? 'bg-blue-600 hover:bg-blue-500' : 'border border-white/20 hover:bg-white/5'} transition-colors`}
                >
                  {idx === 0 ? (lang === 'en' ? 'Start Free' : 'Inizia Gratis') : idx === 1 ? (lang === 'en' ? 'Get Started' : 'Inizia') : (lang === 'en' ? 'Add Pages' : 'Aggiungi Pagine')}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="relative z-10 py-24">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              {current.faq.title}
            </h2>
          </div>

          <div className="space-y-4">
            {current.faq.items.map((item, idx) => (
              <FaqItem 
                key={idx}
                question={item.q}
                answer={item.a}
                isOpen={openFaq === idx}
                onClick={() => toggleFaq(idx)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24">
        <div className="max-w-4xl mx-auto px-6">
          <div className="p-12 md:p-16 rounded-3xl bg-gradient-to-br from-blue-600 to-cyan-700 text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              {current.cta.title}
            </h2>
            <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
              {current.cta.subtitle}
            </p>
            <Link 
              href="/auth"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-full font-bold text-lg hover:bg-slate-100 transition-colors"
            >
              {current.cta.button}
              <ArrowRightIcon className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-12 border-t border-white/10">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Image 
                src="/logo.png" 
                alt="E-quipe Logo" 
                width={32} 
                height={32}
                className="h-8 w-auto"
              />
              <span className="font-bold">E-quipe</span>
            </div>
            <div className="text-slate-500 text-sm">
              {current.footer.rights}
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-slate-400 hover:text-white transition-colors">{current.footer.privacy}</a>
              <a href="#" className="text-slate-400 hover:text-white transition-colors">{current.footer.terms}</a>
              <a href="#" className="text-slate-400 hover:text-white transition-colors">{current.footer.contact}</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Component: Feature Card
function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 rounded-2xl border border-white/10 bg-slate-900/50 hover:bg-slate-800/50 transition-colors group">
      <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  );
}

// Component: Step Card
function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center text-2xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  );
}

// Component: FAQ Item
function FaqItem({ question, answer, isOpen, onClick }: { question: string; answer: string; isOpen: boolean; onClick: () => void }) {
  return (
    <div className="border border-white/10 rounded-xl overflow-hidden">
      <button 
        onClick={onClick}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
      >
        <span className="font-semibold">{question}</span>
        <ChevronDownIcon className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="px-6 pb-4 text-slate-400">
          {answer}
        </div>
      )}
    </div>
  );
}
