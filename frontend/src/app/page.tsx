"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import Image from "next/image";
import {
  ArrowRightIcon,
  SparklesIcon,
  BoltIcon,     // Was ZapIcon
  SwatchIcon,   // Was PaletteIcon
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  CursorArrowRaysIcon,
  CodeBracketIcon,
  CheckIcon,
  PlayIcon,
  ChevronRightIcon,
  StarIcon,
  ArrowUpRightIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/react/24/outline";

export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const features = [
    {
      icon: SparklesIcon,
      title: "AI Generativa",
      description: "Descrivi il tuo business e ottieni un sito professionale in 60 secondi. L'AI crea layout, testi e design su misura."
    },
    {
      icon: SwatchIcon,
      title: "Design Completo",
      description: "Ogni sito include hero, about, servizi, contatti e footer. Design responsive e moderno con Tailwind CSS."
    },
    {
      icon: GlobeAltIcon,
      title: "Dominio Incluso",
      description: "Ottieni un sottodominio gratuito o collega il tuo dominio personalizzato. SSL e hosting inclusi."
    },
    {
      icon: DevicePhoneMobileIcon,
      title: "Mobile First",
      description: "Ogni sito è ottimizzato per tutti i dispositivi. Mobile, tablet e desktop perfetti fin dal primo pixel."
    },
    {
      icon: CursorArrowRaysIcon,
      title: "Editor Visuale",
      description: "Modifica il tuo sito con un click. Cambia colori, testi e immagini senza scrivere una riga di codice."
    },
    {
      icon: CodeBracketIcon,
      title: "Codice Pulito",
      description: "HTML5 semantico con Tailwind CSS. Ottimizzato per SEO e performance. Export disponibile."
    }
  ];

  const steps = [
    {
      number: "01",
      title: "Descrivi",
      description: "Raccontaci del tuo business, i tuoi servizi e il tuo stile preferito."
    },
    {
      number: "02",
      title: "Genera",
      description: "La nostra AI crea il tuo sito completo in meno di 60 secondi."
    },
    {
      number: "03",
      title: "Personalizza",
      description: "Modifica colori, testi e immagini con il nostro editor visuale."
    },
    {
      number: "04",
      title: "Pubblica",
      description: "Vai online con un click. Dominio e SSL inclusi automaticamente."
    }
  ];

  const testimonials = [
    {
      quote: "Ho creato il sito del mio ristorante in 10 minuti. Il design è professionale e i clienti lo adorano.",
      author: "Marco Rossi",
      role: "Proprietario, Ristorante Da Mario",
      avatar: "MR"
    },
    {
      quote: "Finalmente un servizio che capisce le esigenze dei piccoli business. Prezzo giusto, risultato eccellente.",
      author: "Laura Bianchi",
      role: "CEO, Studio Legale Bianchi",
      avatar: "LB"
    },
    {
      quote: "L'AI ha capito esattamente lo stile che volevo. Ho solo dovuto fare piccole modifiche.",
      author: "Giuseppe Verdi",
      role: "Fotografo Professionista",
      avatar: "GV"
    }
  ];

  const pricingPlans = [
    {
      name: "Starter",
      price: "Gratis",
      period: "Per iniziare",
      description: "Prova la potenza dell'AI gratuitamente",
      features: [
        "1 generazione AI",
        "3 modifiche via chat",
        "Preview completa del sito",
        "Solo anteprima (no pubblicazione)"
      ],
      cta: "Inizia Gratis",
      popular: false
    },
    {
      name: "Creazione Sito",
      price: "€200",
      period: "Pagamento unico",
      description: "Il tuo sito professionale online",
      features: [
        "3 generazioni AI",
        "20 modifiche via chat",
        "Homepage + 1 pagina extra",
        "Pubblicazione su sottodominio",
        "Certificato SSL incluso",
        "Hosting illimitato",
        "Pagine aggiuntive a €70/cad."
      ],
      cta: "Crea il tuo sito",
      popular: true
    },
    {
      name: "Premium",
      price: "€500",
      period: "Pagamento unico",
      description: "Tutto incluso, senza limiti",
      features: [
        "5 generazioni AI",
        "30 modifiche via chat",
        "Pagine illimitate",
        "Dominio personalizzato incluso",
        "Certificato SSL incluso",
        "Hosting illimitato",
        "Priorità di generazione"
      ],
      cta: "Scegli Premium",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white overflow-x-hidden">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? "bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-white/5" : "bg-transparent"
        }`}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16 lg:h-20">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 via-violet-500 to-purple-600 flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-semibold tracking-tight">E-quipe</span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden lg:flex items-center gap-8">
              <a href="#features" className="text-sm text-slate-300 hover:text-white transition-colors">Funzionalità</a>
              <a href="#how-it-works" className="text-sm text-slate-300 hover:text-white transition-colors">Come Funziona</a>
              <a href="#pricing" className="text-sm text-slate-300 hover:text-white transition-colors">Prezzi</a>
              <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white transition-colors">Dashboard</Link>
            </div>

            {/* CTA */}
            <div className="hidden lg:flex items-center gap-4">
              <Link
                href="/auth"
                className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Accedi
              </Link>
              <Link
                href="/auth"
                className="px-5 py-2.5 bg-white text-black rounded-full text-sm font-semibold hover:bg-slate-200 transition-colors"
              >
                Inizia Ora
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 hover:bg-white/5 rounded-lg transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <XMarkIcon className="w-6 h-6" /> : <Bars3Icon className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-[#0a0a0a]/95 backdrop-blur-xl border-b border-white/5">
            <div className="px-6 py-4 space-y-4">
              <a href="#features" className="block text-slate-300 hover:text-white py-2">Funzionalità</a>
              <a href="#how-it-works" className="block text-slate-300 hover:text-white py-2">Come Funziona</a>
              <a href="#pricing" className="block text-slate-300 hover:text-white py-2">Prezzi</a>
              <Link href="/dashboard" className="block text-slate-300 hover:text-white py-2">Dashboard</Link>
              <hr className="border-white/10" />
              <Link href="/auth" className="block w-full py-3 bg-white text-black rounded-full font-semibold text-center">
                Inizia Ora
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[128px] animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-violet-600/15 rounded-full blur-[100px] animate-pulse delay-1000" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-600/10 rounded-full blur-[150px]" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
                <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-sm text-slate-300">AI-Powered Website Builder</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.1] tracking-tight mb-6">
                Il tuo sito
                <br />
                <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
                  professionale
                </span>
                <br />
                in 60 secondi.
              </h1>

              <p className="text-lg lg:text-xl text-slate-400 max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed">
                Descrivi il tuo business, carica il logo e lascia che la nostra AI
                crei un sito web completo, responsive e pronto per pubblicare.
              </p>

              <div className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                <Link
                  href="/auth"
                  className="group w-full sm:w-auto px-8 py-4 bg-white text-black rounded-full font-semibold text-lg hover:bg-slate-200 transition-all flex items-center justify-center gap-2"
                >
                  Crea il Tuo Sito
                  <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <button className="group w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 rounded-full font-semibold text-lg hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                  <PlayIcon className="w-5 h-5" />
                  Guarda Demo
                </button>
              </div>

              {/* Trust Badges */}
              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 mt-12 pt-8 border-t border-white/10">
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">Nessun codice richiesto</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">Pagamento unico</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">Dominio incluso</span>
                </div>
              </div>
            </div>

            {/* Right Visual - Dashboard Mock */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 bg-[#111]">
                {/* Mock Header */}
                <div className="h-10 bg-[#1a1a1a] flex items-center px-4 gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                    <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  </div>
                  <div className="flex-1 flex justify-center">
                    <div className="px-4 py-1 rounded-md bg-white/5 text-xs text-slate-400">
                      ristorante-da-mario.e-quipe.app
                    </div>
                  </div>
                </div>

                {/* Mock Content */}
                <div className="aspect-[4/3] relative">
                  <Image
                    src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=900&fit=crop"
                    alt="Website Preview"
                    fill
                    className="object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a]/60 to-transparent" />

                  {/* Mock UI Elements */}
                  <div className="absolute inset-0 p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <div className="text-white font-semibold text-lg">Ristorante Da Mario</div>
                      <div className="flex gap-4 text-sm text-white/80">
                        <span>Menu</span>
                        <span>Chi Siamo</span>
                        <span>Contatti</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-3xl font-bold text-white mb-2">Il vero gusto della tradizione</h3>
                      <p className="text-white/80 mb-4">Cucina romana autentica dal 1985</p>
                      <button className="px-6 py-2 bg-white text-black rounded-full text-sm font-medium">
                        Prenota un tavolo
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Cards */}
              <div className="absolute -bottom-6 -left-6 p-4 rounded-xl bg-[#111]/90 backdrop-blur-xl border border-white/10 shadow-xl">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <CheckIcon className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Sito Pubblicato!</p>
                    <p className="text-xs text-slate-400">Online in 45 secondi</p>
                  </div>
                </div>
              </div>

              <div className="absolute -top-4 -right-4 p-4 rounded-xl bg-[#111]/90 backdrop-blur-xl border border-white/10 shadow-xl">
                <div className="flex items-center gap-2">
                  <SparklesIcon className="w-5 h-5 text-violet-400" />
                  <span className="text-sm font-medium">Generato con AI</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Logos Section */}
      <section className="py-12 border-y border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-center text-sm text-slate-500 mb-8 uppercase tracking-wider">
            Trusted by innovative businesses
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 lg:gap-16 opacity-50">
            {["TechStart", "BellaVita", "Artisan", "GreenLife", "UrbanStyle"].map((brand) => (
              <div key={brand} className="text-xl font-bold text-slate-400">
                {brand}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
              Tutto ciò che serve per
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent"> andare online</span>
            </h2>
            <p className="text-lg text-slate-400">
              Non serve essere designer o sviluppatori. La nostra AI crea siti professionali
              che sembrano fatti a mano da un esperto.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <div
                key={idx}
                className="group p-6 lg:p-8 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] hover:border-white/10 transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-white/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 lg:py-32 bg-white/[0.01]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
                Da zero al tuo sito
                <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent"> in 4 passaggi</span>
              </h2>
              <p className="text-lg text-slate-400 mb-12">
                Abbiamo semplificato il processo di creazione di un sito web.
                Nessuna competenza tecnica richiesta.
              </p>

              <div className="space-y-8">
                {steps.map((step, idx) => (
                  <div key={idx} className="flex gap-6">
                    <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-white/10 flex items-center justify-center">
                      <span className="text-lg font-bold text-blue-400">{step.number}</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                      <p className="text-slate-400">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Visual */}
            <div className="relative">
              <div className="aspect-square rounded-3xl overflow-hidden border border-white/10 bg-[#111] relative">
                <Image
                  src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=800&fit=crop"
                  alt="Dashboard Preview"
                  fill
                  className="object-cover opacity-80"
                />
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-violet-600/20" />
              </div>

              {/* Stats Floating Card */}
              <div className="absolute -bottom-6 -left-6 p-6 rounded-2xl bg-[#111] border border-white/10 shadow-2xl">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <BoltIcon className="w-7 h-7 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold">60s</p>
                    <p className="text-sm text-slate-400">Tempo medio</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
              Amato dai clienti
            </h2>
            <p className="text-lg text-slate-400">
              Migliaia di business hanno già creato il loro sito con E-quipe.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, idx) => (
              <div
                key={idx}
                className="p-6 lg:p-8 rounded-2xl bg-white/[0.02] border border-white/5"
              >
                <div className="flex gap-1 mb-6">
                  {[...Array(5)].map((_, i) => (
                    <StarIcon key={i} className="w-5 h-5 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-lg text-slate-300 mb-6 leading-relaxed">
                  &ldquo;{testimonial.quote}&rdquo;
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center font-semibold">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-medium">{testimonial.author}</p>
                    <p className="text-sm text-slate-400">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 lg:py-32 bg-white/[0.01]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
              Prezzi semplici,
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent"> senza sorprese</span>
            </h2>
            <p className="text-lg text-slate-400">
              Paga una volta, tuo per sempre. Nessun abbonamento nascosto.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
            {pricingPlans.map((plan, idx) => (
              <div
                key={idx}
                className={`relative p-6 lg:p-8 rounded-2xl border ${plan.popular
                  ? "bg-gradient-to-b from-blue-600/10 to-transparent border-blue-500/30"
                  : "bg-white/[0.02] border-white/5"
                  }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1.5 bg-blue-600 rounded-full text-sm font-medium">
                      Più Popolare
                    </span>
                  </div>
                )}

                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">{plan.name}</h3>
                  <p className="text-slate-400 text-sm">{plan.description}</p>
                </div>

                <div className="mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-slate-400 ml-2">{plan.period}</span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-start gap-3 text-slate-300">
                      <CheckIcon className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/auth"
                  className={`block w-full py-3 rounded-full font-semibold text-center transition-all ${plan.popular
                    ? "bg-white text-black hover:bg-slate-200"
                    : "bg-white/5 border border-white/10 hover:bg-white/10"
                    }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 lg:py-32">
        <div className="max-w-5xl mx-auto px-6">
          <div className="relative p-12 lg:p-16 rounded-3xl overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-violet-600 to-purple-700" />
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />

            {/* Content */}
            <div className="relative text-center">
              <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold mb-6">
                Pronto a creare il tuo sito?
              </h2>
              <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
                Unisciti a migliaia di business che hanno già trasformato
                la loro presenza online con E-quipe.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  href="/auth"
                  className="group px-8 py-4 bg-white text-blue-600 rounded-full font-semibold text-lg hover:bg-slate-100 transition-all flex items-center gap-2"
                >
                  Inizia Gratuitamente
                  <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/dashboard"
                  className="px-8 py-4 bg-white/10 border border-white/20 rounded-full font-semibold text-lg hover:bg-white/20 transition-all"
                >
                  Vedi la Dashboard
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                  <SparklesIcon className="w-4 h-4 text-white" />
                </div>
                <span className="text-lg font-semibold">E-quipe</span>
              </Link>
              <p className="text-slate-400 max-w-sm">
                La piattaforma AI che crea siti web professionali in 60 secondi.
                Nessun codice, nessun abbonamento.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Prodotto</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#features" className="hover:text-white transition-colors">Funzionalità</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Prezzi</a></li>
                <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Supporto</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white transition-colors">Documentazione</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contatti</a></li>
                <li><a href="#" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-500 text-sm">
              © 2026 E-quipe. Tutti i diritti riservati.
            </p>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Termini</a>
              <a href="#" className="hover:text-white transition-colors">Cookie</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
