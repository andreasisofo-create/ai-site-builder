import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cookie Policy - E-quipe",
  description: "Informativa sull'utilizzo dei cookie su e-quipe.app",
};

export default function CookiesPage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-3xl mx-auto px-6 py-20">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-[#4F46E5] hover:text-[#4338CA] transition-colors mb-12"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Torna alla home
        </Link>

        <h1 className="text-4xl font-bold text-[#1E293B] mb-4">
          Cookie Policy
        </h1>
        <p className="text-[#64748B] mb-12">
          Ultimo aggiornamento: Febbraio 2026
        </p>

        <div className="space-y-10 text-[#1E293B] leading-relaxed">
          {/* 1. Cosa sono i cookie */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Cosa sono i cookie</h2>
            <p className="text-[#64748B]">
              I cookie sono piccoli file di testo che vengono memorizzati sul tuo dispositivo
              (computer, tablet o smartphone) quando visiti un sito web. Vengono utilizzati per
              far funzionare i siti in modo efficiente, migliorare l&apos;esperienza di navigazione
              e fornire informazioni ai proprietari del sito.
            </p>
          </section>

          {/* 2. Cookie utilizzati */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Cookie utilizzati su e-quipe.app</h2>

            {/* Cookie tecnici */}
            <div className="mt-6 p-6 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <h3 className="text-lg font-semibold text-[#1E293B] mb-3">Cookie tecnici (necessari)</h3>
              <p className="text-[#64748B] mb-4">
                Questi cookie sono essenziali per il funzionamento della piattaforma e non possono
                essere disattivati. Non richiedono il tuo consenso.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E2E8F0]">
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Cookie</th>
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Finalit&agrave;</th>
                      <th className="text-left py-2 font-semibold text-[#1E293B]">Durata</th>
                    </tr>
                  </thead>
                  <tbody className="text-[#64748B]">
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">session_token</td>
                      <td className="py-2 pr-4">Autenticazione e sessione utente</td>
                      <td className="py-2">Sessione</td>
                    </tr>
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">auth_token</td>
                      <td className="py-2 pr-4">Token JWT per l&apos;accesso autenticato</td>
                      <td className="py-2">7 giorni</td>
                    </tr>
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">csrf_token</td>
                      <td className="py-2 pr-4">Protezione da attacchi CSRF</td>
                      <td className="py-2">Sessione</td>
                    </tr>
                    <tr>
                      <td className="py-2 pr-4 font-mono text-xs">cookie_consent</td>
                      <td className="py-2 pr-4">Memorizzazione delle preferenze cookie</td>
                      <td className="py-2">12 mesi</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Cookie analitici */}
            <div className="mt-6 p-6 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <h3 className="text-lg font-semibold text-[#1E293B] mb-3">Cookie analitici (previo consenso)</h3>
              <p className="text-[#64748B] mb-4">
                Questi cookie ci permettono di analizzare l&apos;utilizzo della piattaforma in forma
                aggregata e anonimizzata, per migliorare le funzionalit&agrave; e l&apos;esperienza utente.
                Vengono installati solo dopo aver ottenuto il tuo consenso.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E2E8F0]">
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Cookie</th>
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Fornitore</th>
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Finalit&agrave;</th>
                      <th className="text-left py-2 font-semibold text-[#1E293B]">Durata</th>
                    </tr>
                  </thead>
                  <tbody className="text-[#64748B]">
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">_ga</td>
                      <td className="py-2 pr-4">Google Analytics</td>
                      <td className="py-2 pr-4">Identificazione utenti unici</td>
                      <td className="py-2">24 mesi</td>
                    </tr>
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">_ga_*</td>
                      <td className="py-2 pr-4">Google Analytics</td>
                      <td className="py-2 pr-4">Stato della sessione</td>
                      <td className="py-2">24 mesi</td>
                    </tr>
                    <tr>
                      <td className="py-2 pr-4 font-mono text-xs">_gid</td>
                      <td className="py-2 pr-4">Google Analytics</td>
                      <td className="py-2 pr-4">Identificazione sessione</td>
                      <td className="py-2">24 ore</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* 3. Come gestire i cookie */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Come gestire i cookie</h2>
            <p className="text-[#64748B] mb-4">
              Puoi gestire le tue preferenze sui cookie in qualsiasi momento. Oltre al banner di
              consenso mostrato al primo accesso, puoi configurare il tuo browser per rifiutare
              i cookie o eliminare quelli gi&agrave; memorizzati.
            </p>
            <p className="text-[#64748B] mb-4">
              Ecco le istruzioni per i browser pi&ugrave; comuni:
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li>
                <strong className="text-[#1E293B]">Google Chrome:</strong> Impostazioni &rarr; Privacy e sicurezza &rarr; Cookie e altri dati dei siti
              </li>
              <li>
                <strong className="text-[#1E293B]">Mozilla Firefox:</strong> Impostazioni &rarr; Privacy e sicurezza &rarr; Cookie e dati dei siti web
              </li>
              <li>
                <strong className="text-[#1E293B]">Safari:</strong> Preferenze &rarr; Privacy &rarr; Gestisci dati siti web
              </li>
              <li>
                <strong className="text-[#1E293B]">Microsoft Edge:</strong> Impostazioni &rarr; Cookie e autorizzazioni sito &rarr; Cookie e dati del sito
              </li>
            </ul>
            <p className="text-[#64748B] mt-4">
              <strong className="text-[#1E293B]">Nota:</strong> la disattivazione dei cookie tecnici potrebbe
              compromettere il funzionamento della piattaforma e impedirti di utilizzare alcune funzionalit&agrave;.
            </p>
          </section>

          {/* 4. Cookie di terze parti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Cookie di terze parti</h2>
            <p className="text-[#64748B]">
              Alcuni cookie possono essere impostati da servizi di terze parti che compaiono sulle
              nostre pagine. Non abbiamo il controllo su questi cookie. Per maggiori informazioni,
              consulta le informative privacy dei rispettivi fornitori:
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B] mt-4">
              <li>
                <a href="https://policies.google.com/privacy" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">
                  Google Analytics - Informativa Privacy
                </a>
              </li>
              <li>
                <a href="https://vercel.com/legal/privacy-policy" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">
                  Vercel - Privacy Policy
                </a>
              </li>
            </ul>
          </section>

          {/* 5. Aggiornamenti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Aggiornamenti alla presente policy</h2>
            <p className="text-[#64748B]">
              Ci riserviamo il diritto di aggiornare la presente Cookie Policy in qualsiasi momento
              per riflettere modifiche alle nostre pratiche o per adeguamenti normativi. Le modifiche
              saranno pubblicate su questa pagina con indicazione della nuova data di aggiornamento.
              In caso di modifiche sostanziali, verr&agrave; richiesto nuovamente il consenso tramite
              il banner dei cookie.
            </p>
          </section>

          {/* 6. Contatti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Contatti</h2>
            <p className="text-[#64748B]">
              Per qualsiasi domanda relativa alla presente Cookie Policy:
            </p>
            <div className="mt-4 p-6 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <p className="font-semibold text-[#1E293B]">E-quipe S.r.l.s.</p>
              <p className="text-[#64748B] mt-1">P.IVA: 17629021001</p>
              <p className="text-[#64748B]">Sede legale: Roma, Italia</p>
              <p className="text-[#64748B]">
                Email:{" "}
                <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>
              </p>
            </div>
          </section>
        </div>

        <div className="mt-16 pt-8 border-t border-[#E2E8F0] flex gap-6 text-sm text-[#64748B]">
          <Link href="/privacy" className="hover:text-[#4F46E5] transition-colors">Informativa sulla Privacy</Link>
          <Link href="/terms" className="hover:text-[#4F46E5] transition-colors">Termini di Servizio</Link>
        </div>
      </div>
    </main>
  );
}
