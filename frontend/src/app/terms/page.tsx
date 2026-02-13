import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Termini di Servizio - E-quipe",
  description: "Termini e condizioni di utilizzo della piattaforma e-quipe.app",
};

export default function TermsPage() {
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
          Termini di Servizio
        </h1>
        <p className="text-[#64748B] mb-12">
          Ultimo aggiornamento: Febbraio 2026
        </p>

        <div className="space-y-10 text-[#1E293B] leading-relaxed">
          {/* 1. Definizioni */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Definizioni</h2>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">&ldquo;Servizio&rdquo;</strong>: la piattaforma e-quipe.app, incluse tutte le funzionalit&agrave; di generazione siti web tramite intelligenza artificiale e gestione campagne pubblicitarie</li>
              <li><strong className="text-[#1E293B]">&ldquo;Titolare&rdquo;</strong> o <strong className="text-[#1E293B]">&ldquo;Noi&rdquo;</strong>: E-quipe S.r.l.s., P.IVA 17629021001, con sede legale in Roma</li>
              <li><strong className="text-[#1E293B]">&ldquo;Utente&rdquo;</strong> o <strong className="text-[#1E293B]">&ldquo;Tu&rdquo;</strong>: qualsiasi persona fisica o giuridica che accede o utilizza il Servizio</li>
              <li><strong className="text-[#1E293B]">&ldquo;Sito Generato&rdquo;</strong>: qualsiasi sito web creato attraverso la piattaforma tramite l&apos;uso dell&apos;intelligenza artificiale</li>
              <li><strong className="text-[#1E293B]">&ldquo;Account&rdquo;</strong>: l&apos;insieme di credenziali e dati associati alla registrazione dell&apos;Utente sulla piattaforma</li>
            </ul>
          </section>

          {/* 2. Descrizione del servizio */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Descrizione del servizio</h2>
            <p className="text-[#64748B]">
              E-quipe &egrave; una piattaforma SaaS che consente agli utenti di generare siti web
              professionali tramite intelligenza artificiale. L&apos;utente seleziona un template,
              fornisce le informazioni sulla propria attivit&agrave;, e il sistema genera automaticamente
              un sito web completo con animazioni, testi e grafica ottimizzati.
            </p>
            <p className="text-[#64748B] mt-3">
              La piattaforma include inoltre strumenti per la gestione di campagne pubblicitarie
              online (Google Ads, Meta Ads) con ottimizzazione assistita dall&apos;intelligenza artificiale.
            </p>
          </section>

          {/* 3. Registrazione e account */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Registrazione e account</h2>
            <p className="text-[#64748B]">
              Per utilizzare il Servizio &egrave; necessario creare un account fornendo informazioni
              veritiere e aggiornate. L&apos;utente &egrave; responsabile della riservatezza delle proprie
              credenziali di accesso e di tutte le attivit&agrave; svolte tramite il proprio account.
            </p>
            <p className="text-[#64748B] mt-3">
              &Egrave; possibile registrarsi tramite email e password oppure tramite autenticazione
              Google OAuth. Ogni utente pu&ograve; disporre di un solo account. E-quipe si riserva
              il diritto di sospendere o chiudere account che violino i presenti termini.
            </p>
          </section>

          {/* 4. Piani e pagamenti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Piani e pagamenti</h2>
            <p className="text-[#64748B] mb-4">
              Il Servizio &egrave; offerto attraverso i seguenti piani di abbonamento:
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">Starter:</strong> funzionalit&agrave; base per la generazione di siti web</li>
              <li><strong className="text-[#1E293B]">Business:</strong> funzionalit&agrave; avanzate, pi&ugrave; template e personalizzazione</li>
              <li><strong className="text-[#1E293B]">Growth:</strong> include gestione campagne pubblicitarie e analytics avanzati</li>
              <li><strong className="text-[#1E293B]">Premium:</strong> accesso completo a tutte le funzionalit&agrave;, supporto prioritario</li>
            </ul>
            <p className="text-[#64748B] mt-4">
              I pagamenti vengono elaborati tramite Stripe e/o Revolut. I prezzi sono indicati
              in Euro (EUR) e si intendono IVA inclusa ove applicabile. L&apos;abbonamento si rinnova
              automaticamente alla scadenza, salvo disdetta da parte dell&apos;utente con almeno 24 ore
              di anticipo rispetto alla data di rinnovo.
            </p>
          </section>

          {/* 5. Prova gratuita */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Prova gratuita</h2>
            <p className="text-[#64748B]">
              E-quipe offre un periodo di prova gratuita di <strong className="text-[#1E293B]">14 giorni</strong> per
              i nuovi utenti. Durante la prova gratuita, l&apos;utente ha accesso alle funzionalit&agrave;
              previste dal piano selezionato. Al termine del periodo di prova, l&apos;abbonamento si
              attiver&agrave; automaticamente solo se l&apos;utente ha fornito un metodo di pagamento valido.
              In caso contrario, l&apos;accesso alle funzionalit&agrave; premium sar&agrave; sospeso.
            </p>
          </section>

          {/* 6. Budget pubblicitario */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Budget pubblicitario</h2>
            <p className="text-[#64748B]">
              Il budget destinato alle campagne pubblicitarie (Google Ads, Meta Ads e altre piattaforme)
              &egrave; interamente <strong className="text-[#1E293B]">a carico del cliente</strong> e viene gestito
              direttamente sulle piattaforme pubblicitarie collegate. Tale budget &egrave; separato e
              distinto dal costo dell&apos;abbonamento alla piattaforma E-quipe. E-quipe non &egrave;
              responsabile per la gestione diretta dei fondi pubblicitari, ma fornisce strumenti di
              ottimizzazione e monitoraggio.
            </p>
          </section>

          {/* 7. Proprietà intellettuale */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Propriet&agrave; intellettuale</h2>
            <p className="text-[#64748B]">
              <strong className="text-[#1E293B]">Contenuti generati dall&apos;utente:</strong> l&apos;utente
              mantiene la piena propriet&agrave; intellettuale dei siti web generati attraverso la
              piattaforma, inclusi testi, layout e configurazioni personalizzate. L&apos;utente &egrave;
              libero di utilizzare, modificare e distribuire i propri siti generati senza limitazioni.
            </p>
            <p className="text-[#64748B] mt-3">
              <strong className="text-[#1E293B]">Piattaforma E-quipe:</strong> la piattaforma, il suo
              codice sorgente, i template base, il motore di generazione AI, i componenti grafici e
              il marchio E-quipe restano di propriet&agrave; esclusiva di E-quipe S.r.l.s. L&apos;utente
              non acquisisce alcun diritto su tali elementi, fatta eccezione per la licenza d&apos;uso
              limitata concessa nell&apos;ambito dell&apos;abbonamento attivo.
            </p>
          </section>

          {/* 8. Uso accettabile */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Uso accettabile</h2>
            <p className="text-[#64748B] mb-4">L&apos;utente si impegna a non utilizzare il Servizio per:</p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li>Creare contenuti illegali, diffamatori, discriminatori o che incitino alla violenza</li>
              <li>Violare diritti di propriet&agrave; intellettuale di terzi</li>
              <li>Distribuire malware, virus o codice dannoso</li>
              <li>Tentare di accedere a sistemi o dati non autorizzati</li>
              <li>Utilizzare il servizio per attivit&agrave; di phishing, spam o frode</li>
              <li>Sovraccaricare intenzionalmente i server o l&apos;infrastruttura della piattaforma</li>
              <li>Rivendere l&apos;accesso al Servizio senza autorizzazione scritta</li>
            </ul>
            <p className="text-[#64748B] mt-4">
              La violazione di queste regole pu&ograve; comportare la sospensione immediata
              dell&apos;account senza preavviso e senza diritto a rimborso.
            </p>
          </section>

          {/* 9. Limitazione di responsabilità */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Limitazione di responsabilit&agrave;</h2>
            <p className="text-[#64748B]">
              Il Servizio viene fornito &ldquo;cos&igrave; com&apos;&egrave;&rdquo; e &ldquo;come disponibile&rdquo;.
              E-quipe si impegna a garantire la continuit&agrave; e la qualit&agrave; del servizio,
              ma non pu&ograve; garantire l&apos;assenza di interruzioni, errori o malfunzionamenti.
            </p>
            <p className="text-[#64748B] mt-3">
              In nessun caso E-quipe sar&agrave; responsabile per danni indiretti, incidentali, speciali
              o consequenziali derivanti dall&apos;uso o dall&apos;impossibilit&agrave; di uso del Servizio.
              La responsabilit&agrave; complessiva di E-quipe nei confronti dell&apos;utente non potr&agrave;
              in nessun caso superare l&apos;importo totale pagato dall&apos;utente nei 12 mesi precedenti
              l&apos;evento che ha dato origine alla responsabilit&agrave;.
            </p>
          </section>

          {/* 10. Risoluzione */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Risoluzione</h2>
            <p className="text-[#64748B]">
              L&apos;utente pu&ograve; recedere dal contratto e cancellare il proprio account in qualsiasi
              momento tramite le impostazioni della piattaforma o contattando il supporto
              all&apos;indirizzo <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>.
            </p>
            <p className="text-[#64748B] mt-3">
              E-quipe si riserva il diritto di risolvere il contratto e sospendere l&apos;account
              dell&apos;utente in caso di violazione dei presenti termini, con effetto immediato e
              previa comunicazione via email. In caso di risoluzione, l&apos;utente avr&agrave; la
              possibilit&agrave; di esportare i propri siti generati entro 30 giorni dalla comunicazione
              di chiusura.
            </p>
          </section>

          {/* 11. Foro competente */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">11. Legge applicabile e foro competente</h2>
            <p className="text-[#64748B]">
              I presenti Termini di Servizio sono regolati dalla <strong className="text-[#1E293B]">legge italiana</strong>.
              Per qualsiasi controversia derivante dall&apos;interpretazione o dall&apos;esecuzione dei
              presenti termini, sar&agrave; competente in via esclusiva il <strong className="text-[#1E293B]">Foro di Roma</strong>,
              salvo i casi in cui la legge preveda un foro inderogabile a tutela del consumatore.
            </p>
          </section>

          {/* 12. Contatti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">12. Contatti</h2>
            <p className="text-[#64748B]">
              Per qualsiasi domanda relativa ai presenti Termini di Servizio:
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
          <Link href="/cookies" className="hover:text-[#4F46E5] transition-colors">Cookie Policy</Link>
        </div>
      </div>
    </main>
  );
}
