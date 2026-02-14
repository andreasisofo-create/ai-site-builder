"""
Professional Reference Site HTML Templates.
Used to inject quality examples into AI generation prompts.
Each reference is a condensed but complete section set showing
Awwwards/Dribbble-level design quality using Tailwind CSS + CSS variables.
"""

from typing import Dict, Optional

# Each reference is ~120-180 lines of high-quality HTML showing
# hero + services + about + contact sections with professional design

REFERENCE_SITES: Dict[str, str] = {}

REFERENCE_SITES["restaurant"] = """
<!-- REFERENCE: Restaurant Site (Awwwards Quality) -->
<section class="relative min-h-screen flex items-center overflow-hidden" style="background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-bg-alt) 100%)">
  <div class="absolute inset-0 opacity-5" style="background-image: radial-gradient(var(--color-primary) 1px, transparent 1px); background-size: 40px 40px;"></div>
  <div class="relative max-w-7xl mx-auto px-6 grid grid-cols-2 gap-16 items-center">
    <div class="space-y-8">
      <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[var(--color-primary)]/20 text-sm" style="color: var(--color-primary)">
        <span>★</span> Dal 1985
      </div>
      <h1 class="text-6xl font-heading font-bold leading-[1.1] tracking-tight" style="color: var(--color-text)" data-animate="text-split">
        Dove il Tempo<br>si Ferma
      </h1>
      <p class="text-xl leading-relaxed max-w-md" style="color: var(--color-text-muted)">
        Un viaggio sensoriale tra i sapori autentici della tradizione, reinterpretati con creativita contemporanea.
      </p>
      <div class="flex items-center gap-4">
        <a href="#prenota" class="px-8 py-4 rounded-xl font-semibold text-white text-lg shadow-xl hover:shadow-2xl hover:scale-105 transition-all" style="background: linear-gradient(135deg, var(--color-primary), var(--color-secondary))" data-animate="magnetic">
          Prenota un Tavolo
        </a>
        <a href="#menu" class="px-8 py-4 rounded-xl font-semibold border-2 hover:scale-105 transition-all" style="border-color: var(--color-primary); color: var(--color-primary)">
          Scopri il Menu
        </a>
      </div>
    </div>
    <div class="relative">
      <div class="absolute -inset-4 rounded-3xl opacity-20 blur-3xl" style="background: var(--color-primary)"></div>
      <img src="hero.webp" alt="Piatto signature" class="relative rounded-3xl shadow-2xl w-full aspect-[4/5] object-cover" />
      <div class="absolute -bottom-6 -left-6 px-6 py-4 rounded-2xl shadow-xl backdrop-blur-sm" style="background: var(--color-bg)">
        <div class="text-3xl font-bold" style="color: var(--color-primary)" data-counter>847</div>
        <div class="text-sm" style="color: var(--color-text-muted)">Recensioni 5 stelle</div>
      </div>
    </div>
  </div>
</section>

<section class="py-32" style="background: var(--color-bg-alt)">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center max-w-2xl mx-auto mb-20">
      <h2 class="text-5xl font-heading font-bold mb-6" style="color: var(--color-text)" data-animate="text-split">Il Menu dell'Anima</h2>
      <p class="text-lg" style="color: var(--color-text-muted)">Ogni piatto racconta una storia di passione e territorio</p>
    </div>
    <div class="grid grid-cols-3 gap-8" data-animate="stagger">
      <div class="group p-8 rounded-2xl border transition-all duration-500 hover:shadow-2xl hover:-translate-y-2" style="background: var(--color-bg); border-color: rgba(0,0,0,0.05)">
        <div class="text-5xl mb-6">🍝</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Primi della Tradizione</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Pasta fresca fatta a mano ogni mattina, con ragù che sobbollono per 8 ore e sughi che profumano di nonna.</p>
        <div class="mt-6 flex items-center gap-2 font-semibold opacity-0 group-hover:opacity-100 transition-opacity" style="color: var(--color-primary)">
          Scopri <span>→</span>
        </div>
      </div>
      <div class="group p-8 rounded-2xl border transition-all duration-500 hover:shadow-2xl hover:-translate-y-2" style="background: var(--color-bg); border-color: rgba(0,0,0,0.05)">
        <div class="text-5xl mb-6">🥩</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Secondi d'Autore</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Carni selezionate dai migliori allevatori locali, cotte alla brace con legna di quercia centenaria.</p>
        <div class="mt-6 flex items-center gap-2 font-semibold opacity-0 group-hover:opacity-100 transition-opacity" style="color: var(--color-primary)">
          Scopri <span>→</span>
        </div>
      </div>
      <div class="group p-8 rounded-2xl border transition-all duration-500 hover:shadow-2xl hover:-translate-y-2" style="background: var(--color-bg); border-color: rgba(0,0,0,0.05)">
        <div class="text-5xl mb-6">🍰</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Dolci Tentazioni</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Dessert artigianali che chiudono il cerchio: dal tiramisu decostruito alla panna cotta al passion fruit.</p>
        <div class="mt-6 flex items-center gap-2 font-semibold opacity-0 group-hover:opacity-100 transition-opacity" style="color: var(--color-primary)">
          Scopri <span>→</span>
        </div>
      </div>
    </div>
  </div>
</section>
"""

REFERENCE_SITES["saas"] = """
<!-- REFERENCE: SaaS Landing Page (Awwwards Quality) -->
<section class="relative min-h-screen flex items-center overflow-hidden" style="background: var(--color-bg)">
  <div class="absolute inset-0">
    <div class="absolute top-20 left-20 w-72 h-72 rounded-full blur-3xl opacity-20" style="background: var(--color-primary)"></div>
    <div class="absolute bottom-20 right-20 w-96 h-96 rounded-full blur-3xl opacity-10" style="background: var(--color-accent)"></div>
  </div>
  <div class="relative max-w-7xl mx-auto px-6 text-center">
    <div class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border mb-8 text-sm" style="border-color: var(--color-primary); color: var(--color-primary); background: rgba(124,58,237,0.05)">
      ⚡ Novita 2026
    </div>
    <h1 class="text-7xl font-heading font-extrabold leading-[1.05] tracking-tight max-w-4xl mx-auto" style="color: var(--color-text)" data-animate="text-split">
      Meno Caos.<br>Piu Risultati.
    </h1>
    <p class="text-xl mt-8 max-w-2xl mx-auto leading-relaxed" style="color: var(--color-text-muted)">
      La piattaforma che trasforma il modo in cui lavori. Automatizza, collabora e scala — tutto in un unico posto.
    </p>
    <div class="flex items-center justify-center gap-4 mt-12">
      <a href="#start" class="px-10 py-5 rounded-2xl font-bold text-white text-lg shadow-2xl hover:shadow-3xl hover:scale-105 transition-all" style="background: linear-gradient(135deg, var(--color-primary), var(--color-secondary))" data-animate="magnetic">
        Inizia Gratis →
      </a>
      <a href="#demo" class="px-10 py-5 rounded-2xl font-bold border-2 hover:scale-105 transition-all" style="border-color: var(--color-text); color: var(--color-text)">
        Guarda la Demo
      </a>
    </div>
    <div class="flex items-center justify-center gap-8 mt-8 text-sm" style="color: var(--color-text-muted)">
      <span>✓ Setup in 2 minuti</span>
      <span>✓ Nessuna carta richiesta</span>
      <span>✓ 14 giorni gratis</span>
    </div>
  </div>
</section>

<section class="py-32" style="background: var(--color-bg-alt)">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center max-w-2xl mx-auto mb-20">
      <h2 class="text-5xl font-heading font-bold mb-6" style="color: var(--color-text)" data-animate="text-split">Tutto Quello che Serve</h2>
      <p class="text-lg" style="color: var(--color-text-muted)">Strumenti potenti, interfaccia semplice. Progettato per team che vogliono fare di piu.</p>
    </div>
    <div class="grid grid-cols-3 gap-6" data-animate="stagger">
      <div class="group relative p-8 rounded-2xl overflow-hidden transition-all duration-500 hover:-translate-y-2" style="background: var(--color-bg); box-shadow: 0 4px 24px rgba(0,0,0,0.06)">
        <div class="absolute top-0 left-0 w-full h-1 opacity-0 group-hover:opacity-100 transition-opacity" style="background: linear-gradient(90deg, var(--color-primary), var(--color-accent))"></div>
        <div class="w-14 h-14 rounded-xl flex items-center justify-center text-2xl mb-6" style="background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)); opacity: 0.1">
        </div>
        <div class="text-4xl mb-4">⚡</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Automazione Intelligente</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Workflow che si adattano al tuo modo di lavorare. L'AI impara dai tuoi pattern e suggerisce ottimizzazioni.</p>
      </div>
      <div class="group relative p-8 rounded-2xl overflow-hidden transition-all duration-500 hover:-translate-y-2" style="background: var(--color-bg); box-shadow: 0 4px 24px rgba(0,0,0,0.06)">
        <div class="absolute top-0 left-0 w-full h-1 opacity-0 group-hover:opacity-100 transition-opacity" style="background: linear-gradient(90deg, var(--color-primary), var(--color-accent))"></div>
        <div class="text-4xl mb-4">🎯</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Analytics in Tempo Reale</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Dashboard che raccontano storie, non solo numeri. Vedi l'impatto di ogni decisione in millisecondi.</p>
      </div>
      <div class="group relative p-8 rounded-2xl overflow-hidden transition-all duration-500 hover:-translate-y-2" style="background: var(--color-bg); box-shadow: 0 4px 24px rgba(0,0,0,0.06)">
        <div class="absolute top-0 left-0 w-full h-1 opacity-0 group-hover:opacity-100 transition-opacity" style="background: linear-gradient(90deg, var(--color-primary), var(--color-accent))"></div>
        <div class="text-4xl mb-4">🔒</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Sicurezza Enterprise</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Crittografia end-to-end, SSO, audit trail completo. I tuoi dati protetti come in una cassaforte digitale.</p>
      </div>
    </div>
  </div>
</section>
"""

REFERENCE_SITES["business"] = """
<!-- REFERENCE: Business/Corporate Site (Awwwards Quality) -->
<section class="relative min-h-screen flex items-center" style="background: var(--color-bg)">
  <div class="absolute top-0 right-0 w-1/2 h-full opacity-5" style="background-image: url('data:image/svg+xml,...'); background-size: 60px 60px;"></div>
  <div class="max-w-7xl mx-auto px-6 grid grid-cols-2 gap-20 items-center">
    <div class="space-y-8">
      <h1 class="text-6xl font-heading font-bold leading-[1.1]" style="color: var(--color-text)" data-animate="text-split">
        Costruiamo<br>il Domani
      </h1>
      <p class="text-xl leading-relaxed max-w-lg" style="color: var(--color-text-muted)">
        Strategia, innovazione e risultati concreti. Dal 2005 trasformiamo le sfide in opportunita per aziende visionarie.
      </p>
      <a href="#contatti" class="inline-flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-white shadow-xl hover:shadow-2xl hover:scale-105 transition-all" style="background: linear-gradient(135deg, var(--color-primary), var(--color-secondary))" data-animate="magnetic">
        Parliamo del Tuo Progetto <span>→</span>
      </a>
      <div class="flex items-center gap-12 pt-8 border-t" style="border-color: rgba(0,0,0,0.08)">
        <div>
          <div class="text-3xl font-bold" style="color: var(--color-primary)" data-counter>347</div>
          <div class="text-sm mt-1" style="color: var(--color-text-muted)">Progetti Completati</div>
        </div>
        <div>
          <div class="text-3xl font-bold" style="color: var(--color-primary)" data-counter>98.7</div>
          <div class="text-sm mt-1" style="color: var(--color-text-muted)">% Clienti Soddisfatti</div>
        </div>
        <div>
          <div class="text-3xl font-bold" style="color: var(--color-primary)" data-counter>19</div>
          <div class="text-sm mt-1" style="color: var(--color-text-muted)">Anni di Esperienza</div>
        </div>
      </div>
    </div>
    <div class="relative">
      <div class="absolute -inset-8 rounded-3xl rotate-3 opacity-10" style="background: var(--color-primary)"></div>
      <img src="hero.webp" alt="Team" class="relative rounded-3xl shadow-2xl w-full" />
    </div>
  </div>
</section>

<section class="py-32" style="background: var(--color-bg-alt)">
  <div class="max-w-7xl mx-auto px-6">
    <div class="max-w-2xl mb-20">
      <h2 class="text-5xl font-heading font-bold mb-6" style="color: var(--color-text)" data-animate="text-split">Il Metodo che Funziona</h2>
      <p class="text-lg" style="color: var(--color-text-muted)">Un approccio collaudato che ha generato risultati straordinari per centinaia di aziende.</p>
    </div>
    <div class="grid grid-cols-3 gap-8" data-animate="stagger">
      <div class="group p-8 rounded-2xl border transition-all duration-500 hover:shadow-2xl hover:-translate-y-2" style="background: var(--color-bg); border-color: rgba(0,0,0,0.05)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold text-white mb-6" style="background: var(--color-primary)">01</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Analisi Strategica</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Radiografiamo il tuo business, il mercato e i competitor per trovare l'angolo vincente.</p>
      </div>
      <div class="group p-8 rounded-2xl border transition-all duration-500 hover:shadow-2xl hover:-translate-y-2" style="background: var(--color-bg); border-color: rgba(0,0,0,0.05)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold text-white mb-6" style="background: var(--color-primary)">02</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Esecuzione Fulminante</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">Sprint settimanali, deliverable concreti, zero sprechi. Ogni giorno il tuo progetto avanza.</p>
      </div>
      <div class="group p-8 rounded-2xl border transition-all duration-500 hover:shadow-2xl hover:-translate-y-2" style="background: var(--color-bg); border-color: rgba(0,0,0,0.05)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold text-white mb-6" style="background: var(--color-primary)">03</div>
        <h3 class="text-xl font-bold mb-3" style="color: var(--color-text)">Crescita Misurabile</h3>
        <p class="leading-relaxed" style="color: var(--color-text-muted)">KPI chiari, report trasparenti, ROI documentato. Sai sempre esattamente dove vanno i tuoi investimenti.</p>
      </div>
    </div>
  </div>
</section>
"""

REFERENCE_SITES["portfolio"] = """
<!-- REFERENCE: Portfolio Site (Awwwards Quality) -->
<section class="relative min-h-screen flex items-center" style="background: var(--color-bg)">
  <div class="max-w-7xl mx-auto px-6">
    <div class="max-w-3xl">
      <p class="text-lg mb-4 font-medium" style="color: var(--color-primary)">Designer & Creative Director</p>
      <h1 class="text-8xl font-heading font-extrabold leading-[0.95] tracking-tight" style="color: var(--color-text)" data-animate="text-split">
        Creo Mondi<br>Visivi
      </h1>
      <p class="text-xl mt-8 max-w-xl leading-relaxed" style="color: var(--color-text-muted)">
        Ogni progetto e un universo. Trasformo idee astratte in esperienze digitali che le persone ricordano.
      </p>
      <a href="#lavori" class="inline-flex items-center gap-3 mt-10 px-8 py-4 rounded-xl font-semibold text-white shadow-xl hover:scale-105 transition-all" style="background: var(--color-primary)" data-animate="magnetic">
        Vedi i Lavori →
      </a>
    </div>
  </div>
</section>
"""


def get_reference_for_category(category_label: str) -> str:
    """Get the most relevant reference HTML for a business category."""
    category_lower = category_label.lower()

    # Direct matches
    if category_lower in REFERENCE_SITES:
        return REFERENCE_SITES[category_lower]

    # Category mapping
    mapping = {
        "restaurant": "restaurant",
        "ristorante": "restaurant",
        "food": "restaurant",
        "bar": "restaurant",
        "cafe": "restaurant",
        "saas": "saas",
        "tech": "saas",
        "startup": "saas",
        "software": "saas",
        "app": "saas",
        "business": "business",
        "corporate": "business",
        "consulting": "business",
        "agency": "business",
        "agenzia": "business",
        "portfolio": "portfolio",
        "creative": "portfolio",
        "designer": "portfolio",
        "photographer": "portfolio",
        "fotografo": "portfolio",
        "ecommerce": "saas",  # SaaS-style works for ecommerce too
        "shop": "saas",
        "blog": "portfolio",  # Portfolio-style works for blogs
        "event": "business",  # Business-style works for events
        "evento": "business",
    }

    for keyword, ref_key in mapping.items():
        if keyword in category_lower:
            return REFERENCE_SITES[ref_key]

    # Default to business (most versatile)
    return REFERENCE_SITES["business"]
