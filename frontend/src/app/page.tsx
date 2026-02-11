"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useEffect, useRef, useCallback } from "react";
import dynamic from "next/dynamic";
import { motion, useInView, AnimatePresence } from "framer-motion";
import {
  ArrowRightIcon,
  SparklesIcon,
  BoltIcon,
  SwatchIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  CursorArrowRaysIcon,
  CheckIcon,
  ChevronDownIcon,
  StarIcon,
  Bars3Icon,
  XMarkIcon,
  ChatBubbleBottomCenterTextIcon,
  PaintBrushIcon,
  RocketLaunchIcon,
  MegaphoneIcon,
  ChartBarIcon,
  VideoCameraIcon,
  ShieldCheckIcon,
  EnvelopeIcon,
  CodeBracketIcon,
  Square3Stack3DIcon,
  TrophyIcon,
  CalculatorIcon,
} from "@heroicons/react/24/outline";

const VideoPlayer = dynamic(
  () => import("@/components/remotion/VideoPlayer"),
  { ssr: false }
);

// ==================== HOOKS ====================

function useCounter(target: number, suffix: string, inView: boolean) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!inView) return;
    let start = 0;
    const duration = 2000;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [inView, target]);
  return count + suffix;
}

// ==================== COMPONENTS ====================

function MagneticButton({
  children,
  className,
  href,
  onClick,
  asAnchor,
}: {
  children: React.ReactNode;
  className?: string;
  href?: string;
  onClick?: () => void;
  asAnchor?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 120) {
        setPos({ x: dx * 0.25, y: dy * 0.25 });
      }
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setPos({ x: 0, y: 0 });
  }, []);

  const style = {
    transform: `translate(${pos.x}px, ${pos.y}px)`,
    transition: "transform 0.3s cubic-bezier(0.23,1,0.32,1)",
  };

  if (href && !asAnchor) {
    return (
      <div
        ref={ref}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={style}
        className="inline-block"
      >
        <Link href={href} className={className}>
          {children}
        </Link>
      </div>
    );
  }

  if (href && asAnchor) {
    return (
      <div
        ref={ref}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={style}
        className="inline-block"
      >
        <a href={href} className={className}>
          {children}
        </a>
      </div>
    );
  }

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={style}
      className="inline-block"
    >
      <button onClick={onClick} className={className}>
        {children}
      </button>
    </div>
  );
}

function TiltCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState("");

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      const rotateX = (y - 0.5) * -10;
      const rotateY = (x - 0.5) * 10;
      setTransform(
        `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
      );
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setTransform("perspective(800px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)");
  }, []);

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
      style={{
        transform,
        transition: "transform 0.4s cubic-bezier(0.23,1,0.32,1)",
        willChange: "transform",
      }}
    >
      {children}
    </div>
  );
}

// ==================== MAIN PAGE ====================

export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [pricingMode, setPricingMode] = useState<"sito" | "sito+ads">(
    "sito+ads"
  );
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  // Cursor glow
  const [cursorPos, setCursorPos] = useState({ x: -200, y: -200 });

  // ROI calculator
  const [roiBudget, setRoiBudget] = useState(1000);
  const [roiBusiness, setRoiBusiness] = useState("ristorante");

  // Section refs
  const stepsRef = useRef(null);
  const stepsInView = useInView(stepsRef, { once: true, margin: "-100px" });
  const featuresRef = useRef(null);
  const featuresInView = useInView(featuresRef, { once: true, margin: "-100px" });
  const adsRef = useRef(null);
  const adsInView = useInView(adsRef, { once: true, margin: "-100px" });
  const timelineRef = useRef(null);
  const timelineInView = useInView(timelineRef, { once: true, margin: "-80px" });
  const roiRef = useRef(null);
  const roiInView = useInView(roiRef, { once: true, margin: "-80px" });
  const comparisonRef = useRef(null);
  const comparisonInView = useInView(comparisonRef, {
    once: true,
    margin: "-80px",
  });
  const statsRef = useRef(null);
  const statsInView = useInView(statsRef, { once: true, margin: "-100px" });

  // Cursor glow effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  // Scroll detection
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Stats counters
  const stat1 = useCounter(2847, "", statsInView);
  const stat2 = useCounter(148, "", statsInView);
  const stat3 = useCounter(1.2, "", statsInView);

  // ROI calculations
  const roiMultipliers: Record<string, { roi: number; clients: number; label: string }> = {
    ristorante: { roi: 3.2, clients: 0.04, label: "Ristorante" },
    studio: { roi: 2.8, clients: 0.025, label: "Studio Professionale" },
    ecommerce: { roi: 3.5, clients: 0.035, label: "E-commerce" },
    servizi: { roi: 3.0, clients: 0.03, label: "Servizi" },
  };

  const currentRoi = roiMultipliers[roiBusiness] || roiMultipliers.ristorante;
  const estimatedClients = Math.round(roiBudget * currentRoi.clients);
  const estimatedRoi = Math.round(roiBudget * currentRoi.roi);
  const estimatedRevenue = estimatedRoi - roiBudget;

  // ==================== DATA ====================

  const steps = [
    {
      icon: ChatBubbleBottomCenterTextIcon,
      title: "Descrivi",
      description: "Raccontaci del tuo business, i tuoi servizi e il tuo stile.",
    },
    {
      icon: SparklesIcon,
      title: "Genera",
      description: "L'AI crea il tuo sito completo in meno di 60 secondi.",
    },
    {
      icon: PaintBrushIcon,
      title: "Personalizza",
      description: "Modifica colori, testi e immagini con l'editor chat AI.",
    },
    {
      icon: RocketLaunchIcon,
      title: "Pubblica",
      description: "Vai online con un click. Dominio e SSL inclusi.",
    },
  ];

  const features = [
    {
      icon: SparklesIcon,
      title: "AI Generativa",
      description:
        "Descrivi il tuo business e ottieni un sito professionale in 60 secondi. L'AI crea layout, testi e design su misura.",
      large: true,
    },
    {
      icon: SwatchIcon,
      title: "19 Template Professionali",
      description:
        "8 categorie, 19 stili unici: ristoranti, SaaS, portfolio, e-commerce, business, blog, eventi.",
      large: true,
    },
    {
      icon: CursorArrowRaysIcon,
      title: "Editor Chat AI",
      description:
        "Modifica il tuo sito parlando con l'AI. Cambia colori, testi e layout in linguaggio naturale.",
      large: false,
    },
    {
      icon: BoltIcon,
      title: "Animazioni GSAP",
      description:
        "29 effetti professionali: scroll, parallax, text-split, magnetic e molto altro.",
      large: false,
    },
    {
      icon: DevicePhoneMobileIcon,
      title: "Mobile First",
      description:
        "Ogni sito e' ottimizzato per mobile, tablet e desktop fin dal primo pixel.",
      large: false,
    },
    {
      icon: GlobeAltIcon,
      title: "Pubblica con 1 Click",
      description:
        "Hosting, SSL e sottodominio inclusi. Collega il tuo dominio personalizzato.",
      large: false,
    },
    {
      icon: CodeBracketIcon,
      title: "HTML5 Semantico",
      description:
        "Codice pulito, SEO ottimizzato, accessibile. Pensato per piacere a Google.",
      large: false,
    },
    {
      icon: Square3Stack3DIcon,
      title: "Design Completo",
      description:
        "Hero, about, servizi, contatti, footer. Tutto incluso, tutto personalizzabile.",
      large: false,
    },
  ];

  const adsColumns = [
    {
      icon: MegaphoneIcon,
      title: "Meta Ads",
      subtitle: "Instagram + Facebook",
      items: [
        "Campagne Instagram & Facebook",
        "A/B testing creativo automatico",
        "DM automatici ai lead",
        "Targeting avanzato con AI",
      ],
      gradient: "from-blue-500/20 to-cyan-500/20",
      iconColor: "text-blue-400",
    },
    {
      icon: ChartBarIcon,
      title: "Google Ads",
      subtitle: "Search + Display",
      items: [
        "Campagne Search & Display",
        "Keyword optimization con AI",
        "Policy compliance garantita",
        "Bidding automatico intelligente",
      ],
      gradient: "from-violet-500/20 to-purple-500/20",
      iconColor: "text-violet-400",
    },
    {
      icon: VideoCameraIcon,
      title: "Contenuti AI",
      subtitle: "Video + Grafiche",
      items: [
        "Video con Higgsfield AI",
        "Grafiche per ads e social",
        "Avatar parlanti AI",
        "Contenuti ottimizzati per conversione",
      ],
      gradient: "from-purple-500/20 to-pink-500/20",
      iconColor: "text-purple-400",
    },
  ];

  const timelineMilestones = [
    {
      time: "Settimana 1",
      title: "L'AI crea il tuo sito",
      icon: SparklesIcon,
      color: "from-blue-500 to-cyan-500",
    },
    {
      time: "Settimana 2",
      title: "Lancio campagne Ads",
      icon: RocketLaunchIcon,
      color: "from-violet-500 to-purple-500",
    },
    {
      time: "Settimana 4",
      title: "Primi risultati",
      icon: ChartBarIcon,
      color: "from-purple-500 to-pink-500",
    },
    {
      time: "Mese 3",
      title: "Crescita stabile",
      icon: TrophyIcon,
      color: "from-amber-500 to-orange-500",
    },
  ];

  const pricingPlans = [
    {
      name: "STARTER",
      price: "199",
      period: "una tantum",
      description: "Il tuo sito AI, subito online",
      features: [
        "Sito AI (1 pagina)",
        "Hosting su sottodominio",
        "Certificato SSL incluso",
        "3 modifiche via chat",
      ],
      adsFeatures: [] as string[],
      cta: "Inizia Ora",
      popular: false,
    },
    {
      name: "BUSINESS",
      price: "49",
      period: "/mese",
      description: "Sito completo + primi clienti",
      features: [
        "Sito completo multi-pagina",
        "Dominio personalizzato",
        "Modifiche illimitate via chat",
        "SSL e hosting inclusi",
      ],
      adsFeatures: [
        "2 campagne Meta/mese",
        "Report mensile performance",
      ],
      cta: "Scegli Business",
      popular: true,
    },
    {
      name: "GROWTH",
      price: "99",
      period: "/mese",
      description: "Crescita accelerata con AI",
      features: [
        "Tutto di Business +",
        "Dominio personalizzato",
        "Modifiche illimitate",
        "Supporto prioritario",
      ],
      adsFeatures: [
        "Google Ads + Meta Ads",
        "DM automatici ai lead",
        "5 contenuti IA/mese",
        "Report settimanale",
      ],
      cta: "Scegli Growth",
      popular: false,
    },
    {
      name: "PREMIUM",
      price: "199",
      period: "/mese",
      description: "Tutto illimitato, strategia dedicata",
      features: [
        "Tutto di Growth +",
        "Pagine illimitate",
        "Priorita' massima generazione",
        "Account manager dedicato",
      ],
      adsFeatures: [
        "Campagne illimitate",
        "Contenuti IA illimitati",
        "Strategia dedicata mensile",
        "Supporto prioritario 24/7",
      ],
      cta: "Scegli Premium",
      popular: false,
    },
  ];

  const testimonials = [
    {
      quote:
        "Ho creato il sito in 10 minuti. Con le campagne Ads ho raddoppiato le prenotazioni in 3 mesi.",
      author: "Marco Rossi",
      role: "Ristorante Da Mario",
      avatar: "MR",
    },
    {
      quote:
        "Sito pronto in un'ora, campagne partite il giorno dopo. 15 nuovi clienti al mese.",
      author: "Laura Bianchi",
      role: "Studio Legale",
      avatar: "LB",
    },
    {
      quote:
        "L'AI ha capito esattamente il mio stile. Google Ads mi porta 15 contatti a settimana.",
      author: "Giuseppe Verdi",
      role: "Fotografo",
      avatar: "GV",
    },
  ];

  const faqs = [
    {
      q: "Come funziona la creazione del sito?",
      a: "Scegli un template dalla nostra galleria di 19 stili professionali, descrivi il tuo business in 3 semplici step e l'AI genera il tuo sito completo in meno di 60 secondi. Puoi poi personalizzarlo con l'editor chat AI.",
    },
    {
      q: "Quanto costa il servizio?",
      a: "Il piano Starter parte da \u20ac199 una tantum per il solo sito. Se vuoi anche la gestione Ads, i piani partono da \u20ac49/mese (Business) con campagne Meta incluse. Puoi sempre iniziare col sito e aggiungere Ads dopo.",
    },
    {
      q: "Chi gestisce le mie campagne Ads?",
      a: "Le campagne vengono preparate dalla nostra AI e poi riviste e approvate dagli esperti di E-quipe. Ogni campagna ha supervisione umana garantita e monitoraggio continuo.",
    },
    {
      q: "Posso usare il mio dominio?",
      a: "Certo! Dal piano Business in su puoi collegare il tuo dominio personalizzato. Il piano Starter include un sottodominio gratuito (tuonome.e-quipe.app).",
    },
    {
      q: "Cosa include il monitoraggio 24/7?",
      a: "Il nostro sistema monitora le performance delle tue campagne in tempo reale. Se un annuncio non performa, viene ottimizzato o sostituito automaticamente. Ricevi report periodici con metriche chiare.",
    },
    {
      q: "Posso iniziare solo col sito e aggiungere Ads dopo?",
      a: "Assolutamente si! Puoi partire col piano Starter (solo sito) e fare upgrade a Business o Growth in qualsiasi momento per attivare la gestione Ads.",
    },
    {
      q: "Come sono i siti generati?",
      a: "HTML5 semantico, Tailwind CSS, animazioni GSAP professionali, completamente responsive e SEO-friendly. Codice pulito che piace a Google.",
    },
    {
      q: "Quanto tempo ci vuole per vedere risultati Ads?",
      a: "Primi risultati in 2-4 settimane, crescita stabile in 2-3 mesi. Ogni campagna viene ottimizzata continuamente dall'AI con supervisione umana.",
    },
  ];

  const marqueeItems: string[] = [];

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white overflow-x-hidden relative">
      {/* ===== CURSOR GLOW ===== */}
      <div
        className="pointer-events-none fixed inset-0 z-[60] hidden lg:block"
        style={{
          background: `radial-gradient(600px circle at ${cursorPos.x}px ${cursorPos.y}px, rgba(139,92,246,0.06), rgba(59,130,246,0.03) 40%, transparent 70%)`,
        }}
      />

      {/* ===== NAVIGATION ===== */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? "bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20"
            : "bg-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link href="/" className="flex items-center">
              <Image src="/e-quipe-logo.png" alt="E-quipe" width={140} height={40} className="h-9 w-auto" />
            </Link>

            <div className="hidden lg:flex items-center gap-8">
              <a
                href="#features"
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Funzionalita&apos;
              </a>
              <a
                href="#how-it-works"
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Come Funziona
              </a>
              <a
                href="#ads-service"
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Servizio Ads
              </a>
              <a
                href="#pricing"
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Prezzi
              </a>
              <Link
                href="/dashboard"
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Dashboard
              </Link>
            </div>

            <div className="hidden lg:flex items-center gap-4">
              <Link
                href="/auth"
                className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Accedi
              </Link>
              <Link
                href="/auth"
                className="px-5 py-2.5 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full text-sm font-semibold hover:opacity-90 transition-opacity"
              >
                Crea il Tuo Sito
              </Link>
            </div>

            <button
              className="lg:hidden p-2 hover:bg-white/5 rounded-lg transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="w-6 h-6" />
              ) : (
                <Bars3Icon className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden bg-[#0a0a0a]/95 backdrop-blur-xl border-b border-white/5 overflow-hidden"
            >
              <div className="px-6 py-4 space-y-4">
                <a
                  href="#features"
                  className="block text-slate-300 hover:text-white py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Funzionalita&apos;
                </a>
                <a
                  href="#how-it-works"
                  className="block text-slate-300 hover:text-white py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Come Funziona
                </a>
                <a
                  href="#ads-service"
                  className="block text-slate-300 hover:text-white py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Servizio Ads
                </a>
                <a
                  href="#pricing"
                  className="block text-slate-300 hover:text-white py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Prezzi
                </a>
                <Link
                  href="/dashboard"
                  className="block text-slate-300 hover:text-white py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <hr className="border-white/10" />
                <Link
                  href="/auth"
                  className="block text-slate-300 hover:text-white py-2"
                >
                  Accedi
                </Link>
                <Link
                  href="/auth"
                  className="block w-full py-3 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full font-semibold text-center"
                >
                  Crea il Tuo Sito
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ===== HERO SECTION ===== */}
      <section className="relative min-h-screen flex items-center pt-20">
        {/* Animated gradient mesh background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="hero-orb hero-orb-1 absolute w-[700px] h-[700px] bg-blue-600/20 rounded-full blur-[128px]" />
          <div className="hero-orb hero-orb-2 absolute w-[500px] h-[500px] bg-violet-600/15 rounded-full blur-[100px]" />
          <div className="hero-orb hero-orb-3 absolute w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px]" />
          <div className="hero-orb hero-orb-4 absolute w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[100px]" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="text-center lg:text-left"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
                <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-sm text-slate-300">
                  AI-Powered Website Builder + Ads Management
                </span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.1] tracking-tight mb-6">
                Crea il tuo sito.
                <br />
                <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
                  Porta clienti.
                </span>
                <br />
                Cresci online.
              </h1>

              <p className="text-lg lg:text-xl text-slate-400 max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed">
                L&apos;unica piattaforma che crea il tuo sito in 60 secondi{" "}
                <strong className="text-slate-200">E</strong> ti porta clienti
                con campagne Meta e Google Ads gestite da esperti.
              </p>

              <div className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                <MagneticButton
                  href="/auth"
                  className="group w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full font-semibold text-lg hover:shadow-lg hover:shadow-violet-500/25 transition-all flex items-center justify-center gap-2"
                >
                  Crea il Tuo Sito
                  <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </MagneticButton>
                <MagneticButton
                  href="#ads-service"
                  asAnchor
                  className="group w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 rounded-full font-semibold text-lg hover:bg-white/10 transition-all flex items-center justify-center gap-2"
                >
                  Scopri il Servizio Ads
                  <ChevronDownIcon className="w-5 h-5 group-hover:translate-y-0.5 transition-transform" />
                </MagneticButton>
              </div>

              {/* Trust Badges */}
              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 mt-12 pt-8 border-t border-white/10">
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">Nessun codice</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">Setup in 60 secondi</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">Ads gestiti da esperti</span>
                </div>
              </div>
            </motion.div>

            {/* Right Visual - Remotion Video Player */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
              className="relative"
            >
              <VideoPlayer className="shadow-2xl shadow-purple-500/10" />

              {/* Floating accent cards */}
              <div className="absolute -bottom-4 -left-4 p-3 rounded-xl bg-[#111]/90 backdrop-blur-xl border border-white/10 shadow-xl hidden sm:block">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <CheckIcon className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Sito Pubblicato!</p>
                    <p className="text-xs text-slate-400">
                      Online in 45 secondi
                    </p>
                  </div>
                </div>
              </div>

              <div className="absolute -top-4 -right-4 p-3 rounded-xl bg-[#111]/90 backdrop-blur-xl border border-white/10 shadow-xl hidden sm:block">
                <div className="flex items-center gap-2">
                  <SparklesIcon className="w-5 h-5 text-violet-400" />
                  <span className="text-sm font-medium">Generato con AI</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ===== QUICK STATS STRIP ===== */}
      <section className="py-12 border-y border-white/5">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">60s</p>
              <p className="text-xs text-slate-500 mt-1">Tempo medio creazione</p>
            </div>
            <div>
              <p className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">19</p>
              <p className="text-xs text-slate-500 mt-1">Template professionali</p>
            </div>
            <div>
              <p className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">29</p>
              <p className="text-xs text-slate-500 mt-1">Effetti animazione</p>
            </div>
            <div>
              <p className="text-2xl font-bold bg-gradient-to-r from-pink-400 to-rose-400 bg-clip-text text-transparent">24/7</p>
              <p className="text-xs text-slate-500 mt-1">Monitoraggio Ads</p>
            </div>
          </div>
        </div>
      </section>

      {/* ===== COME FUNZIONA ===== */}
      <section id="how-it-works" className="py-24 lg:py-32" ref={stepsRef}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={stepsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6"
            >
              Da zero al tuo sito
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {" "}
                in 4 passaggi
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={stepsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-slate-400"
            >
              Nessuna competenza tecnica richiesta. Descrivi, genera,
              personalizza e pubblica.
            </motion.p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-12 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-blue-500/30 via-violet-500/30 to-purple-500/30" />

            {steps.map((step, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 40 }}
                animate={stepsInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: idx * 0.15 }}
                className="relative text-center"
              >
                <div className="relative z-10 w-24 h-24 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-white/10 flex items-center justify-center mx-auto mb-6">
                  <step.icon className="w-10 h-10 text-blue-400" />
                  <span className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-violet-500 flex items-center justify-center text-sm font-bold">
                    {idx + 1}
                  </span>
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== SITE BUILDER FEATURES (BENTO GRID) ===== */}
      <section
        id="features"
        className="py-24 lg:py-32 bg-white/[0.01]"
        ref={featuresRef}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={featuresInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6"
            >
              Tutto cio&apos; che serve per
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {" "}
                andare online
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={featuresInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-slate-400"
            >
              Non serve essere designer o sviluppatori. La nostra AI crea siti
              professionali che sembrano fatti a mano da un esperto.
            </motion.p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                animate={featuresInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: idx * 0.08 }}
                className={feature.large ? "lg:col-span-2" : ""}
              >
                <TiltCard
                  className="h-full p-6 lg:p-8 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] hover:border-white/10 transition-colors"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-white/5 flex items-center justify-center mb-5">
                    <feature.icon className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-slate-400 leading-relaxed text-sm">
                    {feature.description}
                  </p>
                </TiltCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== ADS SERVICE SECTION ===== */}
      <section id="ads-service" className="py-24 lg:py-32" ref={adsRef}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={adsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 mb-6">
                <MegaphoneIcon className="w-4 h-4 text-violet-400" />
                <span className="text-sm text-violet-300">
                  Servizio Ads Management
                </span>
              </span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={adsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6"
            >
              Non basta avere un sito.
              <br />
              <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Servono clienti.
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={adsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg text-slate-400"
            >
              Il nostro team gestisce le tue campagne Meta e Google Ads con il
              supporto dell&apos;intelligenza artificiale.
            </motion.p>
          </div>

          {/* 3-column ads features */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {adsColumns.map((col, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                animate={adsInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.2 + idx * 0.15 }}
              >
                <TiltCard className="h-full p-6 lg:p-8 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${col.gradient} border border-white/5 flex items-center justify-center mb-6`}
                  >
                    <col.icon className={`w-7 h-7 ${col.iconColor}`} />
                  </div>
                  <h3 className="text-xl font-semibold mb-1">{col.title}</h3>
                  <p className="text-sm text-slate-500 mb-5">{col.subtitle}</p>
                  <ul className="space-y-3">
                    {col.items.map((item, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 text-slate-300"
                      >
                        <CheckIcon className="w-5 h-5 text-violet-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{item}</span>
                      </li>
                    ))}
                  </ul>
                </TiltCard>
              </motion.div>
            ))}
          </div>

          {/* Ads flow diagram */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={adsInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <h3 className="text-center text-lg font-semibold mb-8 text-slate-300">
              Come funziona il servizio Ads
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl bg-blue-500/5 border border-blue-500/20 text-center">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                  <SparklesIcon className="w-5 h-5 text-blue-400" />
                </div>
                <p className="font-semibold text-sm mb-1">
                  L&apos;IA prepara tutto
                </p>
                <p className="text-xs text-slate-400">
                  Creativita&apos;, copy, targeting
                </p>
              </div>
              <div className="p-5 rounded-xl bg-violet-500/5 border border-violet-500/20 text-center relative">
                <div className="hidden md:block absolute left-0 top-1/2 -translate-x-full -translate-y-1/2 text-slate-600">
                  <ArrowRightIcon className="w-4 h-4" />
                </div>
                <div className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center mx-auto mb-3">
                  <ShieldCheckIcon className="w-5 h-5 text-violet-400" />
                </div>
                <p className="font-semibold text-sm mb-1">
                  Gli esperti rivedono e approvano
                </p>
                <p className="text-xs text-slate-400">
                  Supervisione umana esperta
                </p>
              </div>
              <div className="p-5 rounded-xl bg-purple-500/5 border border-purple-500/20 text-center relative">
                <div className="hidden md:block absolute left-0 top-1/2 -translate-x-full -translate-y-1/2 text-slate-600">
                  <ArrowRightIcon className="w-4 h-4" />
                </div>
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-3">
                  <ChartBarIcon className="w-5 h-5 text-purple-400" />
                </div>
                <p className="font-semibold text-sm mb-1">
                  Lancio + monitoraggio 24/7
                </p>
                <p className="text-xs text-slate-400">
                  Ottimizzazione continua
                </p>
              </div>
            </div>

            <div className="mt-8 flex justify-center">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                <ShieldCheckIcon className="w-5 h-5 text-emerald-400" />
                <span className="text-sm text-emerald-300">
                  100% conforme alle policy Google — supervisione umana garantita
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== BEFORE/AFTER TIMELINE ===== */}
      <section className="py-24 lg:py-32 bg-white/[0.01]" ref={timelineRef}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={timelineInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6"
            >
              Il tuo percorso verso la
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {" "}
                crescita
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={timelineInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-slate-400"
            >
              Da zero a una crescita stabile in poche settimane.
            </motion.p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-16 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-blue-500/20 via-violet-500/20 via-purple-500/20 to-amber-500/20" />

            {timelineMilestones.map((milestone, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 40 }}
                animate={timelineInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: idx * 0.2 }}
                className="relative text-center"
              >
                <div
                  className={`relative z-10 w-32 h-32 rounded-2xl bg-gradient-to-br ${milestone.color} p-[1px] mx-auto mb-6`}
                >
                  <div className="w-full h-full rounded-2xl bg-[#0a0a0a] flex items-center justify-center">
                    <milestone.icon className="w-12 h-12 text-white/80" />
                  </div>
                </div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-2">
                  {milestone.time}
                </p>
                <h3 className="text-lg font-semibold">{milestone.title}</h3>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== ROI CALCULATOR ===== */}
      <section className="py-24 lg:py-32" ref={roiRef}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={roiInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
                <CalculatorIcon className="w-4 h-4 text-emerald-400" />
                <span className="text-sm text-emerald-300">
                  Calcolatore ROI
                </span>
              </span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={roiInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6"
            >
              Quanto puoi
              <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                {" "}
                guadagnare?
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={roiInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg text-slate-400"
            >
              Scopri il ritorno stimato sul tuo investimento Ads.
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={roiInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="p-8 lg:p-10 rounded-2xl bg-white/[0.02] border border-white/10"
          >
            <div className="grid md:grid-cols-2 gap-10">
              {/* Inputs */}
              <div className="space-y-8">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-3">
                    Budget mensile Ads
                  </label>
                  <input
                    type="range"
                    min="200"
                    max="5000"
                    step="100"
                    value={roiBudget}
                    onChange={(e) => setRoiBudget(Number(e.target.value))}
                    className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-violet-500"
                  />
                  <div className="flex justify-between mt-2 text-sm text-slate-400">
                    <span>&euro;200</span>
                    <span className="text-lg font-bold text-white">
                      &euro;{roiBudget.toLocaleString("it-IT")}
                    </span>
                    <span>&euro;5.000</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-3">
                    Tipo di business
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(roiMultipliers).map(([key, val]) => (
                      <button
                        key={key}
                        onClick={() => setRoiBusiness(key)}
                        className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                          roiBusiness === key
                            ? "bg-violet-500/20 border border-violet-500/40 text-white"
                            : "bg-white/5 border border-white/5 text-slate-400 hover:bg-white/10"
                        }`}
                      >
                        {val.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Results */}
              <div className="space-y-6">
                <div className="p-5 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                  <p className="text-sm text-slate-400 mb-1">
                    Nuovi clienti stimati/mese
                  </p>
                  <motion.p
                    key={`clients-${estimatedClients}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-3xl font-bold text-emerald-400"
                  >
                    ~{estimatedClients}
                  </motion.p>
                </div>

                <div className="p-5 rounded-xl bg-blue-500/5 border border-blue-500/20">
                  <p className="text-sm text-slate-400 mb-1">Fatturato stimato/mese</p>
                  <motion.p
                    key={`roi-${estimatedRoi}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-3xl font-bold text-blue-400"
                  >
                    &euro;{estimatedRoi.toLocaleString("it-IT")}
                  </motion.p>
                </div>

                <div className="p-5 rounded-xl bg-violet-500/5 border border-violet-500/20">
                  <p className="text-sm text-slate-400 mb-1">
                    Guadagno netto stimato/mese
                  </p>
                  <motion.p
                    key={`revenue-${estimatedRevenue}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-3xl font-bold text-violet-400"
                  >
                    +&euro;{estimatedRevenue.toLocaleString("it-IT")}
                  </motion.p>
                </div>

                <p className="text-xs text-slate-500 text-center">
                  * Stime basate su dati medi di settore. I risultati possono variare.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== FAI DA TE vs CON E-QUIPE ===== */}
      <section className="py-24 lg:py-32 bg-white/[0.01]" ref={comparisonRef}>
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={comparisonInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6"
            >
              Fai da Te
              <span className="bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                {" "}
                vs{" "}
              </span>
              Con E-quipe
            </motion.h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Fai da Te */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={comparisonInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="p-8 rounded-2xl bg-red-500/[0.03] border border-red-500/10"
            >
              <h3 className="text-xl font-bold text-red-400 mb-6">Fai da Te</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <XMarkIcon className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Web designer:{" "}
                    <span className="line-through text-slate-500">
                      &euro;2.000-5.000
                    </span>
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <XMarkIcon className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Agenzia Ads:{" "}
                    <span className="line-through text-slate-500">
                      &euro;500-1.500/mese
                    </span>
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <XMarkIcon className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Tempo setup: 2-4 settimane
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <XMarkIcon className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Gestione continua a carico tuo
                  </span>
                </li>
              </ul>
              <div className="mt-8 pt-6 border-t border-red-500/10">
                <p className="text-sm text-slate-400">Totale primo anno</p>
                <p className="text-2xl font-bold text-red-400">
                  &euro;8.000 - 23.000
                </p>
              </div>
            </motion.div>

            {/* Con E-quipe */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={comparisonInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="p-8 rounded-2xl bg-emerald-500/[0.03] border border-emerald-500/10 relative"
            >
              <div className="absolute -top-3 right-6">
                <span className="px-3 py-1 bg-emerald-500 rounded-full text-xs font-bold text-black">
                  RISPARMIA FINO AL 96%
                </span>
              </div>
              <h3 className="text-xl font-bold text-emerald-400 mb-6">
                Con E-quipe
              </h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <CheckIcon className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Sito AI: da &euro;199 una tantum
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckIcon className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Ads gestiti: da &euro;49/mese
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckIcon className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    Online in 60 secondi
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckIcon className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    AI + supervisione umana inclusa
                  </span>
                </li>
              </ul>
              <div className="mt-8 pt-6 border-t border-emerald-500/10">
                <p className="text-sm text-slate-400">Totale primo anno</p>
                <motion.p
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={
                    comparisonInView
                      ? { opacity: 1, scale: 1 }
                      : {}
                  }
                  transition={{ duration: 0.6, delay: 0.8 }}
                  className="text-2xl font-bold text-emerald-400"
                >
                  da &euro;787
                </motion.p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ===== STATS / NUMBERS ===== */}
      <section className="py-20 border-y border-white/5" ref={statsRef}>
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={statsInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <p className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {stat1}+
              </p>
              <p className="text-sm text-slate-400 mt-2">Siti generati</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={statsInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-center"
            >
              <p className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
                {stat2}
              </p>
              <p className="text-sm text-slate-400 mt-2">
                Campagne ads attive
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={statsInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-center"
            >
              <p className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                &euro;{stat3}M+
              </p>
              <p className="text-sm text-slate-400 mt-2">
                Fatturato generato ai clienti
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={statsInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="text-center"
            >
              <p className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                4.8/5
              </p>
              <p className="text-sm text-slate-400 mt-2">
                Rating medio clienti
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ===== PRICING SECTION ===== */}
      <section id="pricing" className="py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
              Prezzi semplici,
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {" "}
                senza sorprese
              </span>
            </h2>
            <p className="text-lg text-slate-400 mb-8">
              Inizia col sito, aggiungi le Ads quando sei pronto a crescere.
            </p>

            {/* Toggle */}
            <div className="inline-flex items-center gap-1 p-1 rounded-full bg-white/5 border border-white/10">
              <button
                onClick={() => setPricingMode("sito")}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  pricingMode === "sito"
                    ? "bg-white text-black"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Solo Sito
              </button>
              <button
                onClick={() => setPricingMode("sito+ads")}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  pricingMode === "sito+ads"
                    ? "bg-gradient-to-r from-blue-500 to-violet-500 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Sito + Ads
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-7xl mx-auto">
            {pricingPlans.map((plan, idx) => (
              <TiltCard
                key={idx}
                className={`relative p-6 rounded-2xl border transition-colors ${
                  plan.popular
                    ? "bg-gradient-to-b from-blue-600/10 to-transparent border-blue-500/30"
                    : "bg-white/[0.02] border-white/5 hover:border-white/10"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1 bg-gradient-to-r from-blue-500 to-violet-500 rounded-full text-xs font-semibold">
                      Piu&apos; Popolare
                    </span>
                  </div>
                )}

                <div className="mb-5">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-xs text-slate-500">{plan.description}</p>
                </div>

                <div className="mb-5">
                  <span className="text-4xl font-bold">
                    &euro;{plan.price}
                  </span>
                  <span className="text-slate-400 ml-1 text-sm">
                    {plan.period}
                  </span>
                </div>

                <ul className="space-y-2.5 mb-6">
                  {plan.features.map((feature, fidx) => (
                    <li
                      key={fidx}
                      className="flex items-start gap-2.5 text-slate-300"
                    >
                      <CheckIcon className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                  {pricingMode === "sito+ads" &&
                    plan.adsFeatures.map((feature, fidx) => (
                      <li
                        key={`ads-${fidx}`}
                        className="flex items-start gap-2.5 text-slate-300"
                      >
                        <CheckIcon className="w-4 h-4 text-violet-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                </ul>

                <Link
                  href="/auth"
                  className={`block w-full py-3 rounded-full font-semibold text-sm text-center transition-all ${
                    plan.popular
                      ? "bg-gradient-to-r from-blue-500 to-violet-500 text-white hover:opacity-90"
                      : "bg-white/5 border border-white/10 hover:bg-white/10"
                  }`}
                >
                  {plan.cta}
                </Link>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* ===== TESTIMONIALS ===== */}
      <section className="py-24 lg:py-32 bg-white/[0.01]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
              Amato dai clienti
            </h2>
            <p className="text-lg text-slate-400">
              Business di tutta Italia hanno gia&apos; scelto E-quipe per
              crescere online.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, idx) => (
              <TiltCard
                key={idx}
                className="p-6 lg:p-8 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex gap-1 mb-6">
                  {[...Array(5)].map((_, i) => (
                    <StarIcon
                      key={i}
                      className="w-5 h-5 text-amber-400 fill-amber-400"
                    />
                  ))}
                </div>
                <p className="text-slate-300 mb-6 leading-relaxed">
                  &ldquo;{testimonial.quote}&rdquo;
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center font-semibold text-sm">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-medium">{testimonial.author}</p>
                    <p className="text-sm text-slate-400">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FAQ ACCORDION ===== */}
      <section className="py-24 lg:py-32">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tight mb-6">
              Domande frequenti
            </h2>
            <p className="text-lg text-slate-400">
              Tutto quello che devi sapere su E-quipe.
            </p>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-white/[0.02] transition-colors"
                >
                  <span className="font-medium pr-4">{faq.q}</span>
                  <ChevronDownIcon
                    className={`w-5 h-5 text-slate-400 flex-shrink-0 transition-transform duration-300 ${
                      openFaq === idx ? "rotate-180" : ""
                    }`}
                  />
                </button>
                <AnimatePresence>
                  {openFaq === idx && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-5 text-slate-400 leading-relaxed text-sm">
                        {faq.a}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section className="py-24 lg:py-32">
        <div className="max-w-5xl mx-auto px-6">
          <div className="relative p-12 lg:p-20 rounded-3xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-violet-600 to-purple-700" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(255,255,255,0.1),transparent_50%)]" />

            <div className="relative text-center">
              <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold mb-6">
                Pronto a crescere online?
              </h2>
              <p className="text-xl text-white/80 mb-10 max-w-2xl mx-auto">
                Sito + Ads: tutto quello che serve per il tuo business.
                <br />
                Inizia oggi, risultati domani.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <MagneticButton
                  href="/auth"
                  className="group px-8 py-4 bg-white text-blue-600 rounded-full font-semibold text-lg hover:bg-slate-100 transition-all flex items-center gap-2"
                >
                  Crea il Tuo Sito
                  <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </MagneticButton>
                <MagneticButton
                  href="mailto:info@e-quipe.com"
                  asAnchor
                  className="px-8 py-4 bg-white/10 border border-white/20 rounded-full font-semibold text-lg hover:bg-white/20 transition-all flex items-center gap-2"
                >
                  <EnvelopeIcon className="w-5 h-5" />
                  Contattaci
                </MagneticButton>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="py-16 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-5 gap-8 mb-12">
            {/* Brand */}
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center mb-4">
                <Image src="/e-quipe-logo.png" alt="E-quipe" width={120} height={36} className="h-8 w-auto" />
              </Link>
              <p className="text-slate-400 text-sm max-w-sm mb-4">
                E-quipe S.r.l.s — La piattaforma AI che crea il tuo sito web e
                gestisce le tue campagne Ads per farti crescere online.
              </p>
              <div className="flex items-center gap-3">
                {["Instagram", "LinkedIn", "Facebook", "TikTok", "YouTube"].map(
                  (social) => (
                    <a
                      key={social}
                      href="#"
                      className="w-9 h-9 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/10 transition-all text-xs font-medium"
                      aria-label={social}
                    >
                      {social[0]}
                    </a>
                  )
                )}
              </div>
            </div>

            {/* Prodotto */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">Prodotto</h4>
              <ul className="space-y-2.5 text-slate-400 text-sm">
                <li>
                  <a
                    href="#features"
                    className="hover:text-white transition-colors"
                  >
                    Funzionalita&apos;
                  </a>
                </li>
                <li>
                  <a
                    href="#how-it-works"
                    className="hover:text-white transition-colors"
                  >
                    Come Funziona
                  </a>
                </li>
                <li>
                  <a
                    href="#pricing"
                    className="hover:text-white transition-colors"
                  >
                    Prezzi
                  </a>
                </li>
                <li>
                  <Link
                    href="/dashboard"
                    className="hover:text-white transition-colors"
                  >
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>

            {/* Servizi Ads */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">Servizi Ads</h4>
              <ul className="space-y-2.5 text-slate-400 text-sm">
                <li>
                  <a
                    href="#ads-service"
                    className="hover:text-white transition-colors"
                  >
                    Meta Ads
                  </a>
                </li>
                <li>
                  <a
                    href="#ads-service"
                    className="hover:text-white transition-colors"
                  >
                    Google Ads
                  </a>
                </li>
                <li>
                  <a
                    href="#ads-service"
                    className="hover:text-white transition-colors"
                  >
                    Contenuti AI
                  </a>
                </li>
              </ul>
            </div>

            {/* Supporto */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">Supporto</h4>
              <ul className="space-y-2.5 text-slate-400 text-sm">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Contatti
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    FAQ
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Termini di Servizio
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-500 text-sm">
              &copy; 2026 E-quipe S.r.l.s. Tutti i diritti riservati.
            </p>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <a href="#" className="hover:text-white transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Termini
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Cookie
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* ===== CSS KEYFRAMES ===== */}
      <style jsx>{`
        .hero-orb-1 {
          top: 10%;
          left: 15%;
          animation: orb-drift-1 12s ease-in-out infinite;
        }
        .hero-orb-2 {
          bottom: 20%;
          right: 20%;
          animation: orb-drift-2 15s ease-in-out infinite;
        }
        .hero-orb-3 {
          top: 40%;
          left: 50%;
          animation: orb-drift-3 18s ease-in-out infinite;
        }
        .hero-orb-4 {
          top: 60%;
          right: 10%;
          animation: orb-drift-4 14s ease-in-out infinite;
        }
        @keyframes orb-drift-1 {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
          }
          25% {
            transform: translate(60px, -40px) scale(1.1);
          }
          50% {
            transform: translate(-30px, 50px) scale(0.95);
          }
          75% {
            transform: translate(40px, 20px) scale(1.05);
          }
        }
        @keyframes orb-drift-2 {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(-50px, 30px) scale(1.08);
          }
          66% {
            transform: translate(40px, -40px) scale(0.92);
          }
        }
        @keyframes orb-drift-3 {
          0%,
          100% {
            transform: translate(-50%, 0) scale(1);
          }
          25% {
            transform: translate(-45%, 40px) scale(1.15);
          }
          50% {
            transform: translate(-55%, -30px) scale(0.9);
          }
          75% {
            transform: translate(-48%, 20px) scale(1.05);
          }
        }
        @keyframes orb-drift-4 {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
          }
          50% {
            transform: translate(-30px, -40px) scale(1.1);
          }
        }
        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 20px;
          height: 20px;
          background: linear-gradient(135deg, #8b5cf6, #6366f1);
          border-radius: 50%;
          cursor: pointer;
          border: 2px solid rgba(255, 255, 255, 0.2);
        }
        input[type="range"]::-moz-range-thumb {
          width: 20px;
          height: 20px;
          background: linear-gradient(135deg, #8b5cf6, #6366f1);
          border-radius: 50%;
          cursor: pointer;
          border: 2px solid rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}
