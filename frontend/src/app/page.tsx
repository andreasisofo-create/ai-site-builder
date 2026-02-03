"use client";

import Link from "next/link";
import { useState } from "react";
import { 
  SparklesIcon, 
  RocketIcon, 
  PaletteIcon, 
  GlobeIcon,
  ChevronDownIcon,
  CheckIcon,
  ArrowRightIcon,
  ZapIcon,
  ShieldIcon,
  ClockIcon
} from "lucide-react";

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 border-b border-white/10 backdrop-blur-xl bg-slate-950/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold">AI Site Builder</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-slate-400 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-slate-400 hover:text-white transition-colors">How It Works</a>
            <a href="#pricing" className="text-slate-400 hover:text-white transition-colors">Pricing</a>
            <a href="#faq" className="text-slate-400 hover:text-white transition-colors">FAQ</a>
          </div>
          <Link 
            href="/dashboard" 
            className="px-6 py-2.5 bg-white text-slate-950 rounded-full font-semibold hover:bg-slate-200 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm mb-8">
            <SparklesIcon className="w-4 h-4" />
            <span>Powered by Kimi AI 2.5</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Your ideas go in.
            <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Your site comes out.
            </span>
          </h1>
          
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            Create stunning, professional websites in minutes with our AI-powered builder. 
            No coding required. Just describe what you want and watch the magic happen.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link 
              href="/dashboard"
              className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full font-semibold text-lg hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              <RocketIcon className="w-5 h-5" />
              Create Your Site Free
            </Link>
            <a 
              href="#how-it-works"
              className="px-8 py-4 border border-white/20 rounded-full font-semibold text-lg hover:bg-white/5 transition-colors flex items-center gap-2"
            >
              See How It Works
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto mt-20 pt-10 border-t border-white/10">
            <div>
              <div className="text-3xl font-bold text-white">60s</div>
              <div className="text-slate-500">Average Build Time</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">€200</div>
              <div className="text-slate-500">Starting Price</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">100%</div>
              <div className="text-slate-500">Yours to Keep</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-24 bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Built for high standards.
            </h2>
            <p className="text-xl text-slate-400">
              More than just a good-looking site.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<ZapIcon className="w-8 h-8" />}
              title="AI-Powered Design"
              description="Our advanced AI understands your vision and creates stunning, tailored designs that match your brand perfectly."
            />
            <FeatureCard 
              icon={<ClockIcon className="w-8 h-8" />}
              title="Lightning Fast"
              description="Get your complete website in under 60 seconds. No waiting, no hassle. Just instant results."
            />
            <FeatureCard 
              icon={<PaletteIcon className="w-8 h-8" />}
              title="Fully Customizable"
              description="Every element is editable. Change colors, text, images, and layouts with our intuitive editor."
            />
            <FeatureCard 
              icon={<ShieldIcon className="w-8 h-8" />}
              title="Secure & Reliable"
              description="Enterprise-grade security with SSL certificates, DDoS protection, and 99.9% uptime guarantee."
            />
            <FeatureCard 
              icon={<GlobeIcon className="w-8 h-8" />}
              title="Free Domain Included"
              description="Get a free subdomain or connect your own custom domain. We handle all the technical setup."
            />
            <FeatureCard 
              icon={<CheckIcon className="w-8 h-8" />}
              title="No Hidden Fees"
              description="Pay once, own forever. No monthly subscriptions, no recurring charges. Your site is 100% yours."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              How to create a website with AI.
            </h2>
            <p className="text-xl text-slate-400">
              Four simple steps to your dream website.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            <StepCard 
              number="1"
              title="Describe Your Vision"
              description="Tell our AI about your business, your style, and what you need. The more details, the better."
            />
            <StepCard 
              number="2"
              title="AI Generates Your Site"
              description="Our Kimi-powered engine creates a complete website with stunning design in under 60 seconds."
            />
            <StepCard 
              number="3"
              title="Refine & Customize"
              description="Make adjustments with our visual editor or chat with AI to modify any element instantly."
            />
            <StepCard 
              number="4"
              title="Publish & Go Live"
              description="Choose your domain, connect it, and launch your site to the world. It's that simple."
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative z-10 py-24 bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Simple, transparent pricing.
            </h2>
            <p className="text-xl text-slate-400">
              Pay once. Own forever. No hidden fees.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Plan */}
            <div className="p-8 rounded-2xl border border-white/10 bg-slate-900/50">
              <div className="text-sm font-medium text-slate-400 mb-2">Starter</div>
              <div className="text-4xl font-bold mb-1">Free</div>
              <div className="text-slate-500 mb-6">Build your site</div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Create up to 3 projects
                </li>
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  AI preview & editing
                </li>
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Basic templates
                </li>
              </ul>
              <button className="w-full py-3 border border-white/20 rounded-full font-semibold hover:bg-white/5 transition-colors">
                Start Free
              </button>
            </div>

            {/* Homepage Plan */}
            <div className="p-8 rounded-2xl border-2 border-indigo-500 bg-gradient-to-b from-indigo-500/10 to-transparent relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-indigo-500 rounded-full text-sm font-medium">
                Most Popular
              </div>
              <div className="text-sm font-medium text-indigo-400 mb-2">Homepage</div>
              <div className="text-4xl font-bold mb-1">€200</div>
              <div className="text-slate-500 mb-6">One-time payment</div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  1 Professional Homepage
                </li>
                <li className="flex items-center gap-3">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Custom Domain
                </li>
                <li className="flex items-center gap-3">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  SSL Certificate
                </li>
                <li className="flex items-center gap-3">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Hosting Included
                </li>
                <li className="flex items-center gap-3">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Unlimited Edits (30 days)
                </li>
              </ul>
              <Link 
                href="/dashboard"
                className="w-full py-3 bg-indigo-600 rounded-full font-semibold hover:bg-indigo-500 transition-colors text-center block"
              >
                Get Started
              </Link>
            </div>

            {/* Extra Pages */}
            <div className="p-8 rounded-2xl border border-white/10 bg-slate-900/50">
              <div className="text-sm font-medium text-slate-400 mb-2">Extra Pages</div>
              <div className="text-4xl font-bold mb-1">€70</div>
              <div className="text-slate-500 mb-6">Per additional page</div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  About, Services, Contact
                </li>
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Gallery, Portfolio, Blog
                </li>
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  AI-generated content
                </li>
                <li className="flex items-center gap-3 text-slate-400">
                  <CheckIcon className="w-5 h-5 text-indigo-500" />
                  Matching design
                </li>
              </ul>
              <button className="w-full py-3 border border-white/20 rounded-full font-semibold hover:bg-white/5 transition-colors">
                Add Pages
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="relative z-10 py-24">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Frequently asked questions.
            </h2>
          </div>

          <div className="space-y-4">
            <FaqItem 
              question="What is AI Site Builder?"
              answer="AI Site Builder is a revolutionary tool that uses advanced AI (Kimi 2.5) to create professional websites in minutes. You simply describe your business and vision, and our AI generates a complete, customized website ready to publish."
              isOpen={openFaq === 0}
              onClick={() => toggleFaq(0)}
            />
            <FaqItem 
              question="How long does it take to create a website?"
              answer="Most websites are generated in under 60 seconds. After that, you can spend as much time as you want refining and customizing until it's perfect."
              isOpen={openFaq === 1}
              onClick={() => toggleFaq(1)}
            />
            <FaqItem 
              question="Do I need coding skills?"
              answer="Absolutely not! Our platform is designed for everyone. The AI handles all the technical aspects, and our visual editor makes customization simple and intuitive."
              isOpen={openFaq === 2}
              onClick={() => toggleFaq(2)}
            />
            <FaqItem 
              question="Can I use my own domain?"
              answer="Yes! You can connect any custom domain you own, or get a free subdomain (yoursite.ourdomain.com). We handle all the technical DNS configuration for you."
              isOpen={openFaq === 3}
              onClick={() => toggleFaq(3)}
            />
            <FaqItem 
              question="What do I get for €200?"
              answer="You get a complete, professional homepage with custom design, hosting, SSL certificate, and your chosen domain. You own the site 100% with no recurring fees. Additional pages are €70 each."
              isOpen={openFaq === 4}
              onClick={() => toggleFaq(4)}
            />
            <FaqItem 
              question="Can I edit my site after publishing?"
              answer="Yes! You have 30 days of unlimited edits included. After that, you can still make changes anytime through our editor or contact us for assistance."
              isOpen={openFaq === 5}
              onClick={() => toggleFaq(5)}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24">
        <div className="max-w-4xl mx-auto px-6">
          <div className="p-12 md:p-16 rounded-3xl bg-gradient-to-br from-indigo-600 to-purple-700 text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Ready to create your site?
            </h2>
            <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
              Join thousands of businesses who've transformed their online presence with AI Site Builder.
            </p>
            <Link 
              href="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 rounded-full font-bold text-lg hover:bg-slate-100 transition-colors"
            >
              Start Building Free
              <ArrowRightIcon className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-12 border-t border-white/10">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold">AI Site Builder</span>
            </div>
            <div className="text-slate-500 text-sm">
              © 2026 AI Site Builder. All rights reserved.
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-slate-400 hover:text-white transition-colors">Privacy</a>
              <a href="#" className="text-slate-400 hover:text-white transition-colors">Terms</a>
              <a href="#" className="text-slate-400 hover:text-white transition-colors">Contact</a>
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
      <div className="w-14 h-14 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-4 group-hover:scale-110 transition-transform">
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
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-2xl font-bold mx-auto mb-4">
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
