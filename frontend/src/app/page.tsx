"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useEffect, useRef, useCallback } from "react";
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
import { useLanguage, translations } from "@/lib/i18n";
import LanguageSwitcher from "@/components/LanguageSwitcher";

// Rendered MP4 video component — visible neon glow device mockup
function RenderedVideo({
  src,
  accentColor = "#8b5cf6",
  label,
  className = "",
}: {
  src: string;
  accentColor?: string;
  label?: string;
  className?: string;
}) {
  return (
    <div className={`relative group ${className}`}>
      {/* Visible glow behind the box */}
      <div
        className="absolute -inset-4 rounded-3xl blur-2xl opacity-60 group-hover:opacity-80 transition-opacity duration-700 pointer-events-none"
        style={{ background: `radial-gradient(ellipse at center, ${accentColor}55 0%, ${accentColor}20 40%, transparent 70%)` }}
      />

      {/* Label badge */}
      {label && (
        <div className="absolute -top-5 left-1/2 -translate-x-1/2 z-20">
          <span
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold text-white border backdrop-blur-sm"
            style={{
              background: `linear-gradient(135deg, ${accentColor}cc, ${accentColor}88)`,
              borderColor: `${accentColor}66`,
              boxShadow: `0 0 20px ${accentColor}44`,
            }}
          >
            <VideoCameraIcon className="w-3.5 h-3.5" />
            {label}
          </span>
        </div>
      )}

      {/* Solid visible gradient border */}
      <div
        className="relative rounded-2xl p-[2px] transition-transform duration-500 ease-out group-hover:scale-[1.02]"
        style={{
          background: `linear-gradient(135deg, ${accentColor}, #3b82f6, #06b6d4, ${accentColor})`,
          backgroundSize: '300% 300%',
          animation: 'gradient-shift 4s ease infinite',
        }}
      >
        {/* Browser chrome frame */}
        <div className="relative rounded-2xl overflow-hidden bg-[#0c1222]">
          {/* Top bar */}
          <div className="flex items-center gap-3 px-4 py-2.5 bg-[#0f1729] border-b border-white/10">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
              <span className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
              <span className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
            </div>
            <div className="flex-1 mx-2">
              <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-[#080e1a]/70 border border-white/10">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: accentColor, boxShadow: `0 0 6px ${accentColor}` }} />
                <span className="text-[10px] text-slate-400 font-mono truncate">e-quipe.app</span>
              </div>
            </div>
          </div>

          {/* Video content */}
          <video
            src={src}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-auto"
          />
        </div>
      </div>

      {/* Bottom neon glow reflection */}
      <div
        className="absolute -bottom-6 left-[5%] right-[5%] h-12 blur-2xl opacity-60 rounded-full pointer-events-none"
        style={{ background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)` }}
      />
    </div>
  );
}

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

// Floating geometric shapes — visible animated background decoration
function FloatingShapes({ variant = "default" }: { variant?: "default" | "alt" }) {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {variant === "default" ? (
        <>
          <div className="absolute top-[15%] left-[8%] w-20 h-20 border border-violet-500/20 rounded-xl floating-shape-1 shadow-[0_0_30px_rgba(139,92,246,0.1)]" />
          <div className="absolute top-[60%] right-[12%] w-14 h-14 border border-blue-500/20 rounded-full floating-shape-2 shadow-[0_0_20px_rgba(59,130,246,0.1)]" />
          <div className="absolute bottom-[20%] left-[15%] w-8 h-8 bg-blue-500/10 rounded-sm floating-shape-3 rotate-45" />
          <div className="absolute top-[35%] right-[5%] w-32 h-[2px] bg-gradient-to-r from-transparent via-violet-500/20 to-transparent floating-shape-1" />
          <div className="absolute top-[80%] left-[40%] w-6 h-6 border border-cyan-500/15 rounded-full floating-shape-2" />
        </>
      ) : (
        <>
          <div className="absolute top-[25%] right-[10%] w-16 h-16 border border-purple-500/20 rounded-full floating-shape-2 shadow-[0_0_25px_rgba(168,85,247,0.1)]" />
          <div className="absolute bottom-[30%] left-[5%] w-18 h-18 border border-blue-500/15 rounded-lg floating-shape-3 rotate-12" />
          <div className="absolute top-[70%] right-[18%] w-5 h-5 bg-emerald-500/15 rounded-full floating-shape-1" />
          <div className="absolute top-[10%] left-[20%] w-32 h-[2px] bg-gradient-to-r from-transparent via-violet-500/20 to-transparent floating-shape-2" />
          <div className="absolute bottom-[10%] right-[30%] w-10 h-10 border border-pink-500/15 rounded-lg floating-shape-1 rotate-45" />
        </>
      )}
    </div>
  );
}

// Dot grid pattern overlay — visible
function DotGrid() {
  return (
    <div
      className="absolute inset-0 pointer-events-none opacity-[0.07]"
      style={{
        backgroundImage: "radial-gradient(circle, rgba(139,92,246,0.5) 1px, transparent 1px)",
        backgroundSize: "40px 40px",
      }}
    />
  );
}

// ==================== MAIN PAGE ====================

export default function LandingPage() {
  const { language, t } = useLanguage();
  const tx = translations[language];

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
  const businessLabels = tx.earnings.businessTypes;
  const roiMultipliers: Record<string, { roi: number; clients: number; label: string }> = {
    ristorante: { roi: 3.2, clients: 0.04, label: businessLabels.ristorante },
    studio: { roi: 2.8, clients: 0.025, label: businessLabels.studio },
    ecommerce: { roi: 3.5, clients: 0.035, label: businessLabels.ecommerce },
    servizi: { roi: 3.0, clients: 0.03, label: businessLabels.servizi },
  };

  const currentRoi = roiMultipliers[roiBusiness] || roiMultipliers.ristorante;
  const estimatedClients = Math.round(roiBudget * currentRoi.clients);
  const estimatedRoi = Math.round(roiBudget * currentRoi.roi);
  const estimatedRevenue = estimatedRoi - roiBudget;

  // ==================== DATA (i18n) ====================

  const stepIcons = [ChatBubbleBottomCenterTextIcon, SparklesIcon, PaintBrushIcon, RocketLaunchIcon];
  const steps = tx.howItWorks.steps.map((s, i) => ({ icon: stepIcons[i], title: s.title, description: s.description }));

  const featureIcons = [SparklesIcon, SwatchIcon, CursorArrowRaysIcon, BoltIcon, DevicePhoneMobileIcon, GlobeAltIcon, CodeBracketIcon, Square3Stack3DIcon];
  const featureLarge = [true, true, false, false, false, false, false, false];
  const features = tx.features.items.map((f, i) => ({ icon: featureIcons[i], title: f.title, description: f.description, large: featureLarge[i] }));

  const adsIcons = [MegaphoneIcon, ChartBarIcon, VideoCameraIcon];
  const adsGradients = ["from-blue-500/20 to-cyan-500/20", "from-violet-500/20 to-purple-500/20", "from-purple-500/20 to-pink-500/20"];
  const adsIconColors = ["text-blue-400", "text-violet-400", "text-purple-400"];
  const adsColumns = tx.ads.columns.map((c, i) => ({ icon: adsIcons[i], title: c.title, subtitle: c.subtitle, items: [...c.items], gradient: adsGradients[i], iconColor: adsIconColors[i] }));

  const tlIcons = [SparklesIcon, RocketLaunchIcon, ChartBarIcon, TrophyIcon];
  const tlColors = ["from-blue-500 to-cyan-500", "from-violet-500 to-purple-500", "from-purple-500 to-pink-500", "from-amber-500 to-orange-500"];
  const timelineMilestones = tx.timeline.milestones.map((m, i) => ({ time: m.time, title: m.title, icon: tlIcons[i], color: tlColors[i] }));

  const planPopular = [false, true, false, false];
  const pricingPlans = tx.pricing.plans.map((p, i) => ({ ...p, features: [...p.features], adsFeatures: [...p.adsFeatures], popular: planPopular[i] }));

  const avatars = ["MR", "LB", "GV"];
  const testimonials = tx.testimonials.items.map((t, i) => ({ quote: t.quote, author: t.author, role: t.role, avatar: avatars[i] }));

  const faqs = tx.faq.items.map((f) => ({ q: f.q, a: f.a }));

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-[#0c1222] text-white overflow-x-hidden relative">
      {/* ===== NOISE TEXTURE OVERLAY — Premium depth ===== */}
      <div className="fixed inset-0 pointer-events-none z-[70] opacity-[0.02]"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")` }}
      />

      {/* ===== CURSOR GLOW ===== */}
      <div
        className="pointer-events-none fixed inset-0 z-[60] hidden lg:block"
        style={{
          background: `radial-gradient(500px circle at ${cursorPos.x}px ${cursorPos.y}px, rgba(139,92,246,0.12), rgba(59,130,246,0.06) 40%, transparent 70%)`,
        }}
      />

      {/* ===== NAVIGATION ===== */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? "bg-[#0c1222]/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20"
            : "bg-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link href="/" className="flex items-center">
              <Image src="/e-quipe-logo.png" alt="E-quipe" width={140} height={40} className="h-9 w-auto" />
            </Link>

            <div className="hidden lg:flex items-center gap-8">
              <a href="#features" className="text-sm text-slate-300 hover:text-white transition-colors">{t("nav.features")}</a>
              <a href="#how-it-works" className="text-sm text-slate-300 hover:text-white transition-colors">{t("nav.howItWorks")}</a>
              <a href="#ads-service" className="text-sm text-slate-300 hover:text-white transition-colors">{t("nav.adsService")}</a>
              <a href="#pricing" className="text-sm text-slate-300 hover:text-white transition-colors">{t("nav.pricing")}</a>
              <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white transition-colors">{t("nav.dashboard")}</Link>
            </div>

            <div className="hidden lg:flex items-center gap-4">
              <LanguageSwitcher />
              <Link href="/auth" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">{t("nav.login")}</Link>
              <Link href="/auth" className="px-6 py-2.5 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full text-sm font-bold shadow-[0_0_20px_rgba(139,92,246,0.4)] hover:shadow-[0_0_35px_rgba(139,92,246,0.6)] hover:-translate-y-0.5 transition-all duration-300">{t("nav.cta")}</Link>
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
              className="lg:hidden bg-[#0c1222]/95 backdrop-blur-xl border-b border-white/5 overflow-hidden"
            >
              <div className="px-6 py-4 space-y-4">
                <a href="#features" className="block text-slate-300 hover:text-white py-2" onClick={() => setMobileMenuOpen(false)}>{t("nav.features")}</a>
                <a href="#how-it-works" className="block text-slate-300 hover:text-white py-2" onClick={() => setMobileMenuOpen(false)}>{t("nav.howItWorks")}</a>
                <a href="#ads-service" className="block text-slate-300 hover:text-white py-2" onClick={() => setMobileMenuOpen(false)}>{t("nav.adsService")}</a>
                <a href="#pricing" className="block text-slate-300 hover:text-white py-2" onClick={() => setMobileMenuOpen(false)}>{t("nav.pricing")}</a>
                <Link href="/dashboard" className="block text-slate-300 hover:text-white py-2" onClick={() => setMobileMenuOpen(false)}>{t("nav.dashboard")}</Link>
                <hr className="border-white/10" />
                <div className="flex items-center gap-3 py-2"><LanguageSwitcher /></div>
                <Link href="/auth" className="block text-slate-300 hover:text-white py-2">{t("nav.login")}</Link>
                <Link href="/auth" className="block w-full py-3 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full font-semibold text-center">{t("nav.cta")}</Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ===== HERO SECTION ===== */}
      <section className="relative min-h-screen flex items-center pt-20">
        {/* Animated gradient mesh background — stronger */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="hero-orb hero-orb-1 absolute w-[800px] h-[800px] bg-blue-600/30 rounded-full blur-[128px]" />
          <div className="hero-orb hero-orb-2 absolute w-[600px] h-[600px] bg-violet-600/25 rounded-full blur-[100px]" />
          <div className="hero-orb hero-orb-3 absolute w-[700px] h-[700px] bg-purple-600/20 rounded-full blur-[120px]" />
          <div className="hero-orb hero-orb-4 absolute w-[500px] h-[500px] bg-cyan-500/15 rounded-full blur-[100px]" />
        </div>
        {/* Visible grid pattern — like Vercel/Linear */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.12]"
          style={{
            backgroundImage: `linear-gradient(rgba(139,92,246,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.3) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
        {/* Radial fade to hide grid edges */}
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_30%,#0c1222_80%)]" />
        <FloatingShapes />

        <div className="relative max-w-7xl mx-auto px-6 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
                  <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-sm text-slate-300">{t("hero.badge")}</span>
                </div>
              </motion.div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-black uppercase leading-[1.1] tracking-tight mb-6">
                <motion.span
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
                  className="inline-block"
                >
                  {t("hero.titleLine1")}
                </motion.span>
                <br />
                <motion.span
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.25, ease: "easeOut" }}
                  className="inline-block bg-gradient-to-r from-blue-400 via-violet-400 to-purple-400 bg-[length:200%_auto] bg-clip-text text-transparent animate-text-shimmer"
                >
                  {t("hero.titleLine2")}
                </motion.span>
                <br />
                <motion.span
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
                  className="inline-block"
                >
                  {t("hero.titleLine3")}
                </motion.span>
              </h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.55, ease: "easeOut" }}
                className="text-lg lg:text-xl text-slate-400 max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed"
              >
                {t("hero.description")}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.65, ease: "easeOut" }}
                className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start"
              >
                <MagneticButton
                  href="/auth"
                  className="group w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full font-bold text-lg shadow-[0_0_30px_rgba(139,92,246,0.5)] hover:shadow-[0_0_50px_rgba(139,92,246,0.7)] hover:-translate-y-1 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  {t("hero.ctaPrimary")}
                  <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </MagneticButton>
                <MagneticButton
                  href="#ads-service"
                  asAnchor
                  className="group w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 rounded-full font-semibold text-lg hover:bg-white/10 transition-all flex items-center justify-center gap-2"
                >
                  {t("hero.ctaSecondary")}
                  <ChevronDownIcon className="w-5 h-5 group-hover:translate-y-0.5 transition-transform" />
                </MagneticButton>
              </motion.div>

              {/* Trust Badges */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="flex flex-wrap items-center justify-center lg:justify-start gap-6 mt-12 pt-8 border-t border-white/10"
              >
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">{t("hero.trustNoCode")}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">{t("hero.trustSetup")}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm">{t("hero.trustAds")}</span>
                </div>
              </motion.div>
            </div>

            {/* Right Visual - Single main video */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
              className="relative"
            >
              <div className="transform -rotate-2 hover:rotate-0 transition-transform duration-500">
                <RenderedVideo src="/videos/hero.mp4" accentColor="#8b5cf6" label="Live Preview" />
              </div>

              {/* Floating accent cards */}
              <div className="absolute -bottom-4 -left-4 p-3 rounded-xl bg-[#0f1729]/90 backdrop-blur-xl border border-white/10 shadow-xl hidden sm:block">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <CheckIcon className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{t("hero.floatingPublished")}</p>
                    <p className="text-xs text-slate-400">{t("hero.floatingPublishedSub")}</p>
                  </div>
                </div>
              </div>

              <div className="absolute -top-4 -right-4 p-3 rounded-xl bg-[#0f1729]/90 backdrop-blur-xl border border-white/10 shadow-xl hidden sm:block">
                <div className="flex items-center gap-2">
                  <SparklesIcon className="w-5 h-5 text-violet-400" />
                  <span className="text-sm font-medium">{t("hero.floatingAI")}</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* ===== 3 SMALL VIDEO DEMOS IN A ROW ===== */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
            className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto"
          >
            {[
              { src: "/videos/process.mp4", label: "AI Builder", accent: "#7c3aed", offset: "" },
              { src: "/videos/features.mp4", label: "Templates", accent: "#3b82f6", offset: "md:-translate-y-4" },
              { src: "/videos/ads.mp4", label: "Ads Manager", accent: "#06b6d4", offset: "" },
            ].map((video, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.0 + idx * 0.15 }}
                className={`${video.offset}`}
              >
                <div className={`transform ${idx % 2 === 0 ? 'rotate-2' : '-rotate-2'} hover:rotate-0 transition-transform duration-500`}>
                  <RenderedVideo src={video.src} accentColor={video.accent} label={video.label} />
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ===== LOGO MARQUEE — SOCIAL PROOF ===== */}
      <section className="py-12 border-y border-white/5 relative overflow-hidden bg-[#080e1a]">
        <div className="absolute inset-0 bg-gradient-to-r from-[#0c1222] via-transparent to-[#0c1222] z-10 pointer-events-none" />
        <p className="text-center text-xs font-medium text-slate-400 tracking-[0.2em] uppercase mb-8">
          {language === "en" ? "Trusted by businesses worldwide" : "Scelto da aziende in tutto il mondo"}
        </p>
        <div className="flex items-center gap-16 animate-marquee whitespace-nowrap">
          {[...Array(2)].map((_, setIdx) => (
            <div key={setIdx} className="flex items-center gap-16 shrink-0">
              {["Meta", "Google", "Shopify", "Stripe", "Vercel", "Next.js", "TailwindCSS", "Framer"].map((brand, i) => (
                <span key={i} className="text-xl font-bold text-white/20 hover:text-white/50 transition-colors duration-300 cursor-default select-none">
                  {brand}
                </span>
              ))}
            </div>
          ))}
        </div>
      </section>

      {/* ===== QUICK STATS STRIP ===== */}
      <section className="py-20 relative overflow-hidden bg-blue-600">
        <div className="max-w-5xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { value: t("quickStats.creationTime"), label: t("quickStats.creationTimeLabel") },
              { value: t("quickStats.templates"), label: t("quickStats.templatesLabel") },
              { value: t("quickStats.animations"), label: t("quickStats.animationsLabel") },
              { value: t("quickStats.monitoring"), label: t("quickStats.monitoringLabel") },
            ].map((stat, idx) => (
              <div key={idx} className="relative group">
                <div className="relative p-6 rounded-2xl bg-white/20 border border-blue-700/30 hover:bg-white/25 transition-all duration-300 hover:scale-105">
                  <p className="text-3xl md:text-4xl font-black text-[#0c1222]">
                    {stat.value}
                  </p>
                  <p className="text-sm text-blue-950 mt-2 font-medium">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Stats Video */}
          <div className="mt-12 max-w-sm mx-auto">
            <div className="transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/stats.mp4" accentColor="#1e40af" label="Stats" />
            </div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== COME FUNZIONA ===== */}
      <section id="how-it-works" className="py-24 lg:py-32 relative" ref={stepsRef}>
        <div className="absolute inset-0 bg-gradient-to-b from-violet-950/20 via-transparent to-blue-950/20 pointer-events-none" />
        <FloatingShapes variant="alt" />
        <div className="max-w-7xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={stepsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6"
            >
              {t("howItWorks.title")}
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {t("howItWorks.titleHighlight")}
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={stepsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-slate-400"
            >
              {t("howItWorks.subtitle")}
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
                <div className="relative z-10 w-24 h-24 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 border-2 border-violet-500/30 flex items-center justify-center mx-auto mb-6 shadow-[0_0_30px_rgba(139,92,246,0.2)]">
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

          {/* Process Video — compact */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={stepsInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.6 }}
            className="mt-16 max-w-sm mx-auto"
          >
            <div className="transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/process.mp4" accentColor="#7c3aed" label={language === "en" ? "How It Works" : "Come Funziona"} />
            </div>
          </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ===== SITE BUILDER FEATURES (BENTO GRID) ===== */}
      <section
        id="features"
        className="py-24 lg:py-32 relative bg-blue-600"
        ref={featuresRef}
      >
        <div className="max-w-7xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={featuresInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6 text-[#0c1222]"
            >
              {t("features.title")}
              {t("features.titleHighlight")}
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={featuresInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-blue-100"
            >
              {t("features.subtitle")}
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
                  className="h-full p-6 lg:p-8 rounded-2xl bg-white/15 border border-blue-800/20 hover:bg-white/20 transition-all duration-300"
                >
                  <div className="w-12 h-12 rounded-xl bg-blue-800/30 border border-blue-800/20 flex items-center justify-center mb-5">
                    <feature.icon className="w-6 h-6 text-blue-200" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3 text-[#0c1222]">
                    {feature.title}
                  </h3>
                  <p className="text-blue-950 leading-relaxed text-sm">
                    {feature.description}
                  </p>
                </TiltCard>
              </motion.div>
            ))}
          </div>

          {/* Features Video — compact */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.5 }}
            className="mt-16 max-w-sm mx-auto"
          >
            <div className="transform -rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/features.mp4" accentColor="#1e40af" label="Features Demo" />
            </div>
          </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ===== ADS SERVICE SECTION ===== */}
      <section id="ads-service" className="py-24 lg:py-32 relative" ref={adsRef}>
        <FloatingShapes variant="alt" />
        <div className="max-w-7xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={adsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 mb-6">
                <MegaphoneIcon className="w-4 h-4 text-violet-400" />
                <span className="text-sm text-violet-300">{t("ads.badge")}</span>
              </span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={adsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6"
            >
              {t("ads.title")}
              <br />
              <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                {t("ads.titleHighlight")}
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={adsInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg text-slate-400"
            >
              {t("ads.subtitle")}
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
                <TiltCard className="h-full p-6 lg:p-8 rounded-2xl bg-white/[0.05] border border-white/5 hover:border-white/10 transition-colors">
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${col.gradient} border border-white/5 flex items-center justify-center mb-6`}
                  >
                    <col.icon className={`w-7 h-7 ${col.iconColor}`} />
                  </div>
                  <h3 className="text-xl font-semibold mb-1">{col.title}</h3>
                  <p className="text-sm text-slate-400 mb-5">{col.subtitle}</p>
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
              {t("ads.flowTitle")}
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl bg-blue-500/5 border border-blue-500/20 text-center">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                  <SparklesIcon className="w-5 h-5 text-blue-400" />
                </div>
                <p className="font-semibold text-sm mb-1">{t("ads.flowStep1Title")}</p>
                <p className="text-xs text-slate-400">{t("ads.flowStep1Sub")}</p>
              </div>
              <div className="p-5 rounded-xl bg-violet-500/5 border border-violet-500/20 text-center relative">
                <div className="hidden md:block absolute left-0 top-1/2 -translate-x-full -translate-y-1/2 text-slate-600">
                  <ArrowRightIcon className="w-4 h-4" />
                </div>
                <div className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center mx-auto mb-3">
                  <ShieldCheckIcon className="w-5 h-5 text-violet-400" />
                </div>
                <p className="font-semibold text-sm mb-1">{t("ads.flowStep2Title")}</p>
                <p className="text-xs text-slate-400">{t("ads.flowStep2Sub")}</p>
              </div>
              <div className="p-5 rounded-xl bg-purple-500/5 border border-purple-500/20 text-center relative">
                <div className="hidden md:block absolute left-0 top-1/2 -translate-x-full -translate-y-1/2 text-slate-600">
                  <ArrowRightIcon className="w-4 h-4" />
                </div>
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-3">
                  <ChartBarIcon className="w-5 h-5 text-purple-400" />
                </div>
                <p className="font-semibold text-sm mb-1">{t("ads.flowStep3Title")}</p>
                <p className="text-xs text-slate-400">{t("ads.flowStep3Sub")}</p>
              </div>
            </div>

            <div className="mt-8 flex justify-center">
              <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                <ShieldCheckIcon className="w-5 h-5 text-emerald-400" />
                <span className="text-sm text-emerald-300">
                  {t("ads.complianceBadge")}
                </span>
              </div>
            </div>

            {/* Ads Video — compact */}
            <div className="mt-12 max-w-sm mx-auto">
              <div className="transform rotate-2 hover:rotate-0 transition-transform duration-500">
                <RenderedVideo src="/videos/ads.mp4" accentColor="#10b981" label="Ads Manager" />
              </div>
            </div>
          </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ===== BEFORE/AFTER TIMELINE ===== */}
      <section className="py-24 lg:py-32 bg-blue-600 relative" ref={timelineRef}>
        <div className="max-w-7xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={timelineInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6 text-[#0c1222]"
            >
              {t("timeline.title")}
              {t("timeline.titleHighlight")}
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={timelineInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-blue-100"
            >
              {t("timeline.subtitle")}
            </motion.p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-16 left-[12.5%] right-[12.5%] h-0.5 bg-[#0c1222]/20" />

            {timelineMilestones.map((milestone, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 40 }}
                animate={timelineInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: idx * 0.2 }}
                className="relative text-center"
              >
                <div
                  className="relative z-10 w-32 h-32 rounded-2xl bg-white/20 border border-blue-800/20 p-[1px] mx-auto mb-6"
                >
                  <div className="w-full h-full rounded-2xl bg-blue-700/40 flex items-center justify-center">
                    <milestone.icon className="w-12 h-12 text-[#0c1222]" />
                  </div>
                </div>
                <p className="text-xs text-blue-950 uppercase tracking-wider font-semibold mb-2">
                  {milestone.time}
                </p>
                <h3 className="text-lg font-semibold text-[#0c1222]">{milestone.title}</h3>
              </motion.div>
            ))}
          </div>

          {/* Timeline Video */}
          <div className="mt-12 max-w-sm mx-auto">
            <div className="transform -rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/timeline.mp4" accentColor="#1e40af" label="Timeline" />
            </div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== ROI CALCULATOR ===== */}
      <section className="py-24 lg:py-32" ref={roiRef}>
        <div className="max-w-4xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={roiInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
                <CalculatorIcon className="w-4 h-4 text-emerald-400" />
                <span className="text-sm text-emerald-300">
                  {t("earnings.badge")}
                </span>
              </span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={roiInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6"
            >
              {t("earnings.title")}
              <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                {t("earnings.titleHighlight")}
              </span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={roiInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg text-slate-400"
            >
              {t("earnings.subtitle")}
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={roiInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="p-8 lg:p-10 rounded-2xl bg-white/[0.05] border border-white/10"
          >
            <div className="grid md:grid-cols-2 gap-10">
              {/* Inputs */}
              <div className="space-y-8">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-3">
                    {t("earnings.budgetLabel")}
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
                    {t("earnings.businessTypeLabel")}
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
                    {t("earnings.estimatedClientsLabel")}
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
                  <p className="text-sm text-slate-400 mb-1">{t("earnings.estimatedRevenueLabel")}</p>
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
                    {t("earnings.estimatedProfitLabel")}
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

                <p className="text-xs text-slate-400 text-center">
                  {t("earnings.disclaimer")}
                </p>
              </div>
            </div>
          </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ===== FAI DA TE vs CON E-QUIPE ===== */}
      <section className="py-24 lg:py-32 bg-blue-600" ref={comparisonRef}>
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={comparisonInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6 text-[#0c1222]"
            >
              {t("comparison.title")}
              <span className="text-red-800">
                {t("comparison.titleVs")}
              </span>
              {t("comparison.titleBrand")}
            </motion.h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Fai da Te */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={comparisonInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="p-8 rounded-2xl bg-white/15 border border-blue-800/20"
            >
              <h3 className="text-xl font-bold text-red-800 mb-6">{t("comparison.diy.title")}</h3>
              <ul className="space-y-4">
                {tx.comparison.diy.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <XMarkIcon className="w-5 h-5 text-red-800 flex-shrink-0 mt-0.5" />
                    <span className="text-[#0c1222] text-sm">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8 pt-6 border-t border-blue-800/20">
                <p className="text-sm text-blue-950">{t("comparison.diy.totalLabel")}</p>
                <p className="text-2xl font-bold text-red-800">
                  {t("comparison.diy.totalValue")}
                </p>
              </div>
            </motion.div>

            {/* Con E-quipe */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={comparisonInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="p-8 rounded-2xl bg-white/20 border border-blue-800/20 relative"
            >
              <div className="absolute -top-3 right-6">
                <span className="px-3 py-1 bg-[#0c1222] rounded-full text-xs font-bold text-white">
                  {t("comparison.equipe.saveBadge")}
                </span>
              </div>
              <h3 className="text-xl font-bold text-emerald-900 mb-6">
                {t("comparison.equipe.title")}
              </h3>
              <ul className="space-y-4">
                {tx.comparison.equipe.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckIcon className="w-5 h-5 text-emerald-900 flex-shrink-0 mt-0.5" />
                    <span className="text-[#0c1222] text-sm">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8 pt-6 border-t border-blue-800/20">
                <p className="text-sm text-blue-950">{t("comparison.equipe.totalLabel")}</p>
                <motion.p
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={
                    comparisonInView
                      ? { opacity: 1, scale: 1 }
                      : {}
                  }
                  transition={{ duration: 0.6, delay: 0.8 }}
                  className="text-2xl font-bold text-emerald-900"
                >
                  {t("comparison.equipe.totalValue")}
                </motion.p>
              </div>
            </motion.div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== STATS / NUMBERS ===== */}
      <section className="py-24 relative overflow-hidden" ref={statsRef}>
        <div className="max-w-5xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { value: <>{stat1}+</>, label: t("stats.sitesGenerated") },
              { value: stat2, label: t("stats.activeCampaigns") },
              { value: <>&euro;{stat3}M+</>, label: t("stats.revenueGenerated") },
              { value: "4.8/5", label: t("stats.clientRating") },
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 40, scale: 0.9 }}
                animate={statsInView ? { opacity: 1, y: 0, scale: 1 } : {}}
                transition={{ duration: 0.6, delay: idx * 0.12, ease: "easeOut" }}
                className="text-center relative group"
              >
                <div className="relative p-8 rounded-2xl bg-white/[0.06] border border-white/10 hover:bg-white/[0.08] transition-all duration-500 hover:scale-105 hover:shadow-lg">
                  <p className="text-4xl lg:text-6xl font-black text-white">
                    {stat.value}
                  </p>
                  <p className="text-sm text-slate-300 mt-3 font-medium">{stat.label}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Stats Video */}
          <div className="mt-12 max-w-sm mx-auto">
            <div className="transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/stats.mp4" accentColor="#8b5cf6" label="Stats" />
            </div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== PRICING SECTION ===== */}
      <section id="pricing" className="py-24 lg:py-32 relative">
        <DotGrid />
        <FloatingShapes variant="alt" />
        <div className="max-w-7xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6">
              {t("pricing.title")}
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                {t("pricing.titleHighlight")}
              </span>
            </h2>
            <p className="text-lg text-slate-400 mb-8">
              {t("pricing.subtitle")}
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
                {t("pricing.toggleSite")}
              </button>
              <button
                onClick={() => setPricingMode("sito+ads")}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  pricingMode === "sito+ads"
                    ? "bg-gradient-to-r from-blue-500 to-violet-500 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {t("pricing.toggleSiteAds")}
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-7xl mx-auto">
            {pricingPlans.map((plan, idx) => (
              <div key={idx} className={`relative ${plan.popular ? "pricing-popular-card" : ""}`}>
                {/* Animated glow border for popular plan */}
                {plan.popular && (
                  <div className="absolute -inset-[1px] rounded-2xl pricing-glow-gradient opacity-60" />
                )}
                {/* Background glow for popular plan */}
                {plan.popular && (
                  <div className="absolute -inset-4 rounded-3xl bg-violet-500/[0.08] blur-2xl pointer-events-none" />
                )}
              <TiltCard
                className={`relative p-6 rounded-2xl border transition-colors ${
                  plan.popular
                    ? "bg-gradient-to-b from-blue-600/10 via-violet-600/5 to-transparent border-blue-500/40 shadow-[0_0_40px_rgba(139,92,246,0.15)]"
                    : "bg-white/[0.06] border-white/10 hover:border-violet-500/30 hover:shadow-[0_0_30px_rgba(139,92,246,0.1)]"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 z-10">
                    <span className="px-4 py-1.5 bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500 rounded-full text-xs font-bold shadow-lg shadow-violet-500/30 pricing-badge-pulse">
                      {t("pricing.mostPopular")}
                    </span>
                  </div>
                )}

                <div className="mb-5">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-xs text-slate-400">{plan.description}</p>
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
              </div>
            ))}
          </div>

          {/* Pricing Video */}
          <div className="mt-12 max-w-sm mx-auto">
            <div className="transform -rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/pricing.mp4" accentColor="#8b5cf6" label="Pricing" />
            </div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== TESTIMONIALS ===== */}
      <section className="py-24 lg:py-32 relative bg-blue-600">
        <div className="max-w-7xl mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6 text-[#0c1222]">
              {t("testimonials.title")}
            </h2>
            <p className="text-lg text-blue-100">
              {t("testimonials.subtitle")}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, idx) => (
              <TiltCard
                key={idx}
                className="p-6 lg:p-8 rounded-2xl bg-white/15 border border-blue-800/20 hover:bg-white/20 transition-all duration-300"
              >
                <div className="flex gap-1 mb-6">
                  {[...Array(5)].map((_, i) => (
                    <StarIcon
                      key={i}
                      className="w-5 h-5 text-amber-400 fill-amber-400"
                    />
                  ))}
                </div>
                <p className="text-[#0c1222] mb-6 leading-relaxed">
                  &ldquo;{testimonial.quote}&rdquo;
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-[#0c1222] flex items-center justify-center font-semibold text-sm text-white">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-medium text-[#0c1222]">{testimonial.author}</p>
                    <p className="text-sm text-blue-950">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>

          {/* Testimonials Video */}
          <div className="mt-12 max-w-sm mx-auto">
            <div className="transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <RenderedVideo src="/videos/testimonials.mp4" accentColor="#1e40af" label="Testimonials" />
            </div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== FAQ ACCORDION ===== */}
      <section className="py-24 lg:py-32">
        <div className="max-w-3xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6">
              {t("faq.title")}
            </h2>
            <p className="text-lg text-slate-400">
              {t("faq.subtitle")}
            </p>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-white/5 bg-white/[0.05] overflow-hidden"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-white/[0.05] transition-colors"
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
          </motion.div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section className="py-24 lg:py-32">
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
          <div className="relative p-12 lg:p-20 rounded-3xl overflow-hidden shadow-[0_0_80px_rgba(59,130,246,0.3)]">
            <div className="absolute inset-0 bg-blue-600" />
            {/* Grid pattern overlay */}
            <div
              className="absolute inset-0 pointer-events-none opacity-[0.08]"
              style={{
                backgroundImage: `linear-gradient(rgba(0,0,0,0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.2) 1px, transparent 1px)`,
                backgroundSize: '40px 40px',
              }}
            />

            <div className="relative text-center">
              <h2 className="text-4xl lg:text-6xl font-black uppercase tracking-tight mb-6 text-[#0c1222]">
                {t("cta.title")}
              </h2>
              <p className="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
                {t("cta.description")}
                <br />
                {t("cta.descriptionLine2")}
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <MagneticButton
                  href="/auth"
                  className="group px-8 py-4 bg-[#0c1222] text-white rounded-full font-semibold text-lg shadow-[0_0_20px_rgba(12,18,34,0.3)] hover:shadow-[0_0_30px_rgba(12,18,34,0.5)] hover:-translate-y-0.5 transition-all flex items-center gap-2"
                >
                  {t("cta.ctaPrimary")}
                  <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </MagneticButton>
                <MagneticButton
                  href="mailto:info@e-quipe.com"
                  asAnchor
                  className="px-8 py-4 bg-white/15 border border-blue-800/20 rounded-full font-semibold text-lg text-[#0c1222] hover:bg-white/25 transition-all flex items-center gap-2"
                >
                  <EnvelopeIcon className="w-5 h-5" />
                  {t("cta.ctaSecondary")}
                </MagneticButton>
              </div>
            </div>
          </div>
          </motion.div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="py-16 border-t border-white/8 bg-[#080e1a]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-5 gap-8 mb-12">
            {/* Brand */}
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center mb-4">
                <Image src="/e-quipe-logo.png" alt="E-quipe" width={120} height={36} className="h-8 w-auto" />
              </Link>
              <p className="text-slate-400 text-sm max-w-sm mb-4">
                {t("footer.brandDescription")}
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
              <h4 className="font-semibold mb-4 text-sm">{t("footer.productTitle")}</h4>
              <ul className="space-y-2.5 text-slate-400 text-sm">
                <li>
                  <a href="#features" className="hover:text-white transition-colors">
                    {t("footer.productFeatures")}
                  </a>
                </li>
                <li>
                  <a href="#how-it-works" className="hover:text-white transition-colors">
                    {t("footer.productHowItWorks")}
                  </a>
                </li>
                <li>
                  <a href="#pricing" className="hover:text-white transition-colors">
                    {t("footer.productPricing")}
                  </a>
                </li>
                <li>
                  <Link href="/dashboard" className="hover:text-white transition-colors">
                    {t("footer.productDashboard")}
                  </Link>
                </li>
              </ul>
            </div>

            {/* Servizi Ads */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">{t("footer.adsTitle")}</h4>
              <ul className="space-y-2.5 text-slate-400 text-sm">
                <li>
                  <a href="#ads-service" className="hover:text-white transition-colors">
                    {t("footer.adsMetaAds")}
                  </a>
                </li>
                <li>
                  <a href="#ads-service" className="hover:text-white transition-colors">
                    {t("footer.adsGoogleAds")}
                  </a>
                </li>
                <li>
                  <a href="#ads-service" className="hover:text-white transition-colors">
                    {t("footer.adsAIContent")}
                  </a>
                </li>
              </ul>
            </div>

            {/* Supporto */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">{t("footer.supportTitle")}</h4>
              <ul className="space-y-2.5 text-slate-400 text-sm">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    {t("footer.supportContact")}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    {t("footer.supportFAQ")}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    {t("footer.supportPrivacy")}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    {t("footer.supportTerms")}
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-400 text-sm">
              {t("footer.copyright")}
            </p>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <a href="#" className="hover:text-white transition-colors">
                {t("footer.footerPrivacy")}
              </a>
              <a href="#" className="hover:text-white transition-colors">
                {t("footer.footerTerms")}
              </a>
              <a href="#" className="hover:text-white transition-colors">
                {t("footer.footerCookies")}
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* ===== CSS KEYFRAMES ===== */}
      <style jsx>{`
        @keyframes gradient-shift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes marquee-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee-scroll 25s linear infinite;
        }
        .animate-marquee:hover {
          animation-play-state: paused;
        }
        @keyframes text-shimmer {
          0% { background-position: 0% center; }
          100% { background-position: 200% center; }
        }
        .animate-text-shimmer {
          animation: text-shimmer 6s linear infinite;
        }
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
        .floating-shape-1 {
          animation: float-drift-1 16s ease-in-out infinite;
        }
        .floating-shape-2 {
          animation: float-drift-2 20s ease-in-out infinite;
        }
        .floating-shape-3 {
          animation: float-drift-3 14s ease-in-out infinite;
        }
        @keyframes float-drift-1 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(15px, -20px) rotate(5deg); }
          50% { transform: translate(-10px, 15px) rotate(-3deg); }
          75% { transform: translate(20px, 10px) rotate(8deg); }
        }
        @keyframes float-drift-2 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          33% { transform: translate(-20px, 10px) rotate(-5deg); }
          66% { transform: translate(15px, -15px) rotate(4deg); }
        }
        @keyframes float-drift-3 {
          0%, 100% { transform: translate(0, 0) rotate(45deg); }
          50% { transform: translate(10px, -25px) rotate(50deg); }
        }
        .pricing-glow-gradient {
          background: linear-gradient(135deg, #3b82f6, #8b5cf6, #a855f7, #3b82f6);
          background-size: 300% 300%;
          animation: gradient-shift 4s ease infinite;
        }
        .pricing-badge-pulse {
          animation: badge-pulse 2s ease-in-out infinite;
        }
        @keyframes badge-pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4); }
          50% { box-shadow: 0 0 16px 4px rgba(139, 92, 246, 0.2); }
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
