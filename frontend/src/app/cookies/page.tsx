"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/i18n";

export default function CookiesPage() {
  const { language } = useLanguage();
  const en = language === "en";

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
          {en ? "Back to home" : "Torna alla home"}
        </Link>

        <h1 className="text-4xl font-bold text-[#1E293B] mb-4">
          Cookie Policy
        </h1>
        <p className="text-[#64748B] mb-12">
          {en ? "Last updated: February 2026" : "Ultimo aggiornamento: Febbraio 2026"}
        </p>

        <div className="space-y-10 text-[#1E293B] leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "1. What are cookies" : "1. Cosa sono i cookie"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "Cookies are small text files stored on your device (computer, tablet, or smartphone) when you visit a website. They are used to make websites work efficiently, improve the browsing experience, and provide information to site owners."
                : "I cookie sono piccoli file di testo che vengono memorizzati sul tuo dispositivo (computer, tablet o smartphone) quando visiti un sito web. Vengono utilizzati per far funzionare i siti in modo efficiente, migliorare l'esperienza di navigazione e fornire informazioni ai proprietari del sito."
              }
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "2. Cookies used on e-quipe.app" : "2. Cookie utilizzati su e-quipe.app"}</h2>

            {/* Technical cookies */}
            <div className="mt-6 p-6 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <h3 className="text-lg font-semibold text-[#1E293B] mb-3">{en ? "Technical cookies (necessary)" : "Cookie tecnici (necessari)"}</h3>
              <p className="text-[#64748B] mb-4">
                {en
                  ? "These cookies are essential for the platform to function and cannot be disabled. They do not require your consent."
                  : "Questi cookie sono essenziali per il funzionamento della piattaforma e non possono essere disattivati. Non richiedono il tuo consenso."
                }
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E2E8F0]">
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Cookie</th>
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">{en ? "Purpose" : "Finalità"}</th>
                      <th className="text-left py-2 font-semibold text-[#1E293B]">{en ? "Duration" : "Durata"}</th>
                    </tr>
                  </thead>
                  <tbody className="text-[#64748B]">
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">session_token</td>
                      <td className="py-2 pr-4">{en ? "Authentication and user session" : "Autenticazione e sessione utente"}</td>
                      <td className="py-2">{en ? "Session" : "Sessione"}</td>
                    </tr>
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">auth_token</td>
                      <td className="py-2 pr-4">{en ? "JWT token for authenticated access" : "Token JWT per l'accesso autenticato"}</td>
                      <td className="py-2">{en ? "7 days" : "7 giorni"}</td>
                    </tr>
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">csrf_token</td>
                      <td className="py-2 pr-4">{en ? "Protection against CSRF attacks" : "Protezione da attacchi CSRF"}</td>
                      <td className="py-2">{en ? "Session" : "Sessione"}</td>
                    </tr>
                    <tr>
                      <td className="py-2 pr-4 font-mono text-xs">cookie_consent</td>
                      <td className="py-2 pr-4">{en ? "Storage of cookie preferences" : "Memorizzazione delle preferenze cookie"}</td>
                      <td className="py-2">{en ? "12 months" : "12 mesi"}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Analytics cookies */}
            <div className="mt-6 p-6 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <h3 className="text-lg font-semibold text-[#1E293B] mb-3">{en ? "Analytics cookies (with consent)" : "Cookie analitici (previo consenso)"}</h3>
              <p className="text-[#64748B] mb-4">
                {en
                  ? "These cookies allow us to analyze platform usage in aggregate and anonymized form, to improve features and user experience. They are only installed after obtaining your consent."
                  : "Questi cookie ci permettono di analizzare l'utilizzo della piattaforma in forma aggregata e anonimizzata, per migliorare le funzionalità e l'esperienza utente. Vengono installati solo dopo aver ottenuto il tuo consenso."
                }
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E2E8F0]">
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">Cookie</th>
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">{en ? "Provider" : "Fornitore"}</th>
                      <th className="text-left py-2 pr-4 font-semibold text-[#1E293B]">{en ? "Purpose" : "Finalità"}</th>
                      <th className="text-left py-2 font-semibold text-[#1E293B]">{en ? "Duration" : "Durata"}</th>
                    </tr>
                  </thead>
                  <tbody className="text-[#64748B]">
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">_ga</td>
                      <td className="py-2 pr-4">Google Analytics</td>
                      <td className="py-2 pr-4">{en ? "Unique user identification" : "Identificazione utenti unici"}</td>
                      <td className="py-2">{en ? "24 months" : "24 mesi"}</td>
                    </tr>
                    <tr className="border-b border-[#E2E8F0]/50">
                      <td className="py-2 pr-4 font-mono text-xs">_ga_*</td>
                      <td className="py-2 pr-4">Google Analytics</td>
                      <td className="py-2 pr-4">{en ? "Session state" : "Stato della sessione"}</td>
                      <td className="py-2">{en ? "24 months" : "24 mesi"}</td>
                    </tr>
                    <tr>
                      <td className="py-2 pr-4 font-mono text-xs">_gid</td>
                      <td className="py-2 pr-4">Google Analytics</td>
                      <td className="py-2 pr-4">{en ? "Session identification" : "Identificazione sessione"}</td>
                      <td className="py-2">{en ? "24 hours" : "24 ore"}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "3. How to manage cookies" : "3. Come gestire i cookie"}</h2>
            <p className="text-[#64748B] mb-4">
              {en
                ? "You can manage your cookie preferences at any time. In addition to the consent banner shown on first access, you can configure your browser to reject cookies or delete those already stored."
                : "Puoi gestire le tue preferenze sui cookie in qualsiasi momento. Oltre al banner di consenso mostrato al primo accesso, puoi configurare il tuo browser per rifiutare i cookie o eliminare quelli già memorizzati."
              }
            </p>
            <p className="text-[#64748B] mb-4">
              {en ? "Here are the instructions for the most common browsers:" : "Ecco le istruzioni per i browser più comuni:"}
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Google Chrome:</strong> Settings &rarr; Privacy and security &rarr; Cookies and other site data</li>
                  <li><strong className="text-[#1E293B]">Mozilla Firefox:</strong> Settings &rarr; Privacy & Security &rarr; Cookies and Site Data</li>
                  <li><strong className="text-[#1E293B]">Safari:</strong> Preferences &rarr; Privacy &rarr; Manage Website Data</li>
                  <li><strong className="text-[#1E293B]">Microsoft Edge:</strong> Settings &rarr; Cookies and site permissions &rarr; Cookies and site data</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Google Chrome:</strong> Impostazioni &rarr; Privacy e sicurezza &rarr; Cookie e altri dati dei siti</li>
                  <li><strong className="text-[#1E293B]">Mozilla Firefox:</strong> Impostazioni &rarr; Privacy e sicurezza &rarr; Cookie e dati dei siti web</li>
                  <li><strong className="text-[#1E293B]">Safari:</strong> Preferenze &rarr; Privacy &rarr; Gestisci dati siti web</li>
                  <li><strong className="text-[#1E293B]">Microsoft Edge:</strong> Impostazioni &rarr; Cookie e autorizzazioni sito &rarr; Cookie e dati del sito</li>
                </>
              )}
            </ul>
            <p className="text-[#64748B] mt-4">
              {en
                ? <><strong className="text-[#1E293B]">Note:</strong> disabling technical cookies may compromise the platform&apos;s functionality and prevent you from using certain features.</>
                : <><strong className="text-[#1E293B]">Nota:</strong> la disattivazione dei cookie tecnici potrebbe compromettere il funzionamento della piattaforma e impedirti di utilizzare alcune funzionalità.</>
              }
            </p>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "4. Third-party cookies" : "4. Cookie di terze parti"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "Some cookies may be set by third-party services that appear on our pages. We do not control these cookies. For more information, please consult the privacy policies of the respective providers:"
                : "Alcuni cookie possono essere impostati da servizi di terze parti che compaiono sulle nostre pagine. Non abbiamo il controllo su questi cookie. Per maggiori informazioni, consulta le informative privacy dei rispettivi fornitori:"
              }
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B] mt-4">
              <li>
                <a href="https://policies.google.com/privacy" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">
                  {en ? "Google Analytics - Privacy Policy" : "Google Analytics - Informativa Privacy"}
                </a>
              </li>
              <li>
                <a href="https://vercel.com/legal/privacy-policy" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">
                  Vercel - Privacy Policy
                </a>
              </li>
            </ul>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "5. Updates to this policy" : "5. Aggiornamenti alla presente policy"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "We reserve the right to update this Cookie Policy at any time to reflect changes to our practices or for regulatory compliance. Changes will be published on this page with the new update date. In case of substantial changes, consent will be requested again via the cookie banner."
                : "Ci riserviamo il diritto di aggiornare la presente Cookie Policy in qualsiasi momento per riflettere modifiche alle nostre pratiche o per adeguamenti normativi. Le modifiche saranno pubblicate su questa pagina con indicazione della nuova data di aggiornamento. In caso di modifiche sostanziali, verrà richiesto nuovamente il consenso tramite il banner dei cookie."
              }
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "6. Contact" : "6. Contatti"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "For any questions regarding this Cookie Policy:"
                : "Per qualsiasi domanda relativa alla presente Cookie Policy:"
              }
            </p>
            <div className="mt-4 p-6 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <p className="font-semibold text-[#1E293B]">E-quipe S.r.l.s.</p>
              <p className="text-[#64748B] mt-1">{en ? "VAT: 17629021001" : "P.IVA: 17629021001"}</p>
              <p className="text-[#64748B]">{en ? "Registered office: Rome, Italy" : "Sede legale: Roma, Italia"}</p>
              <p className="text-[#64748B]">
                Email:{" "}
                <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>
              </p>
            </div>
          </section>
        </div>

        <div className="mt-16 pt-8 border-t border-[#E2E8F0] flex gap-6 text-sm text-[#64748B]">
          <Link href="/privacy" className="hover:text-[#4F46E5] transition-colors">{en ? "Privacy Policy" : "Informativa sulla Privacy"}</Link>
          <Link href="/terms" className="hover:text-[#4F46E5] transition-colors">{en ? "Terms of Service" : "Termini di Servizio"}</Link>
        </div>
      </div>
    </main>
  );
}
