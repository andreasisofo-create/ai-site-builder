"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/i18n";

export default function PrivacyPage() {
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
          {en ? "Privacy Policy" : "Informativa sulla Privacy"}
        </h1>
        <p className="text-[#64748B] mb-12">
          {en ? "Last updated: February 2026" : "Ultimo aggiornamento: Febbraio 2026"}
        </p>

        <div className="space-y-10 text-[#1E293B] leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "1. Data Controller" : "1. Titolare del trattamento"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <>The data controller is <strong className="text-[#1E293B]">E-quipe S.r.l.s.</strong>, with registered office in Rome, Italy. VAT: 17629021001.</>
                : <>Il titolare del trattamento dei dati personali è <strong className="text-[#1E293B]">E-quipe S.r.l.s.</strong>, con sede legale in Roma, P.IVA 17629021001.</>
              }
            </p>
            <p className="text-[#64748B] mt-3">
              {en
                ? <>For any request regarding the processing of your personal data, you can contact us at: <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a></>
                : <>Per qualsiasi richiesta relativa al trattamento dei tuoi dati personali, puoi contattarci all&apos;indirizzo email: <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a></>
              }
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "2. Personal data collected" : "2. Dati personali raccolti"}</h2>
            <p className="text-[#64748B] mb-4">
              {en
                ? "In the context of providing the e-quipe.app service, we collect the following categories of personal data:"
                : "Nell'ambito dell'erogazione del servizio e-quipe.app, raccogliamo le seguenti categorie di dati personali:"
              }
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Identification data:</strong> first name, last name, email address</li>
                  <li><strong className="text-[#1E293B]">Authentication data:</strong> login credentials (encrypted passwords), Google OAuth access data</li>
                  <li><strong className="text-[#1E293B]">Browsing data:</strong> IP address, browser type, pages visited, access times, platform interaction data</li>
                  <li><strong className="text-[#1E293B]">Service data:</strong> generated websites, inserted content, style preferences and selected templates</li>
                  <li><strong className="text-[#1E293B]">Payment data:</strong> managed directly by payment processors (Stripe/Revolut); we do not store complete credit card data</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Dati identificativi:</strong> nome, cognome, indirizzo email</li>
                  <li><strong className="text-[#1E293B]">Dati di autenticazione:</strong> credenziali di accesso (password in forma criptata), dati di accesso tramite Google OAuth</li>
                  <li><strong className="text-[#1E293B]">Dati di navigazione:</strong> indirizzo IP, tipo di browser, pagine visitate, orari di accesso, dati di interazione con la piattaforma</li>
                  <li><strong className="text-[#1E293B]">Dati relativi al servizio:</strong> siti web generati, contenuti inseriti, preferenze di stile e template selezionati</li>
                  <li><strong className="text-[#1E293B]">Dati di pagamento:</strong> gestiti direttamente dai processori di pagamento (Stripe/Revolut); non memorizziamo dati completi delle carte di credito</li>
                </>
              )}
            </ul>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "3. Purpose of processing" : "3. Finalità del trattamento"}</h2>
            <p className="text-[#64748B] mb-4">{en ? "Your personal data is processed for the following purposes:" : "I tuoi dati personali vengono trattati per le seguenti finalità:"}</p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Service delivery:</strong> account creation and management, AI-powered website generation, ad campaign management</li>
                  <li><strong className="text-[#1E293B]">Service communications:</strong> sending emails related to your account, update notifications, technical support</li>
                  <li><strong className="text-[#1E293B]">Service improvement:</strong> aggregate and anonymized analysis to improve platform features</li>
                  <li><strong className="text-[#1E293B]">Legal compliance:</strong> tax, accounting, and regulatory obligations</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Erogazione del servizio:</strong> creazione e gestione dell&apos;account, generazione di siti web tramite intelligenza artificiale, gestione delle campagne pubblicitarie</li>
                  <li><strong className="text-[#1E293B]">Comunicazioni di servizio:</strong> invio di email relative al tuo account, notifiche di aggiornamento, assistenza tecnica</li>
                  <li><strong className="text-[#1E293B]">Miglioramento del servizio:</strong> analisi aggregate e anonimizzate per migliorare le funzionalità della piattaforma</li>
                  <li><strong className="text-[#1E293B]">Adempimenti di legge:</strong> obblighi fiscali, contabili e normativi</li>
                </>
              )}
            </ul>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "4. Legal basis for processing" : "4. Base giuridica del trattamento"}</h2>
            <p className="text-[#64748B] mb-4">
              {en
                ? "The processing of your personal data is based on the following legal bases under EU Regulation 2016/679 (GDPR):"
                : "Il trattamento dei tuoi dati personali si fonda sulle seguenti basi giuridiche ai sensi del Regolamento UE 2016/679 (GDPR):"
              }
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Contract performance</strong> (Art. 6.1.b GDPR): processing is necessary for the provision of the requested service</li>
                  <li><strong className="text-[#1E293B]">Consent</strong> (Art. 6.1.a GDPR): for sending promotional communications and for analytics cookies</li>
                  <li><strong className="text-[#1E293B]">Legitimate interest</strong> (Art. 6.1.f GDPR): for platform security and service improvement</li>
                  <li><strong className="text-[#1E293B]">Legal obligation</strong> (Art. 6.1.c GDPR): for tax and regulatory compliance</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Esecuzione del contratto</strong> (Art. 6.1.b GDPR): il trattamento è necessario per l&apos;erogazione del servizio richiesto</li>
                  <li><strong className="text-[#1E293B]">Consenso</strong> (Art. 6.1.a GDPR): per l&apos;invio di comunicazioni promozionali e per i cookie analitici</li>
                  <li><strong className="text-[#1E293B]">Legittimo interesse</strong> (Art. 6.1.f GDPR): per la sicurezza della piattaforma e il miglioramento del servizio</li>
                  <li><strong className="text-[#1E293B]">Obbligo legale</strong> (Art. 6.1.c GDPR): per gli adempimenti fiscali e normativi</li>
                </>
              )}
            </ul>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "5. Third-party sharing" : "5. Condivisione con terze parti"}</h2>
            <p className="text-[#64748B] mb-4">
              {en
                ? "Your data may be shared with the following service providers, acting as data processors:"
                : "I tuoi dati possono essere condivisi con i seguenti fornitori di servizi, che agiscono in qualità di responsabili del trattamento:"
              }
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Vercel Inc.</strong> (USA) &mdash; frontend platform hosting</li>
                  <li><strong className="text-[#1E293B]">Render Services Inc.</strong> (USA) &mdash; backend services and database hosting</li>
                  <li><strong className="text-[#1E293B]">Moonshot AI</strong> (Kimi K2.5) &mdash; AI-powered content and website generation</li>
                  <li><strong className="text-[#1E293B]">Google LLC</strong> &mdash; Google Analytics for traffic analysis, Google OAuth for authentication</li>
                  <li><strong className="text-[#1E293B]">Resend Inc.</strong> (USA) &mdash; transactional email service</li>
                  <li><strong className="text-[#1E293B]">Stripe / Revolut</strong> &mdash; payment processing</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Vercel Inc.</strong> (USA) &mdash; hosting della piattaforma frontend</li>
                  <li><strong className="text-[#1E293B]">Render Services Inc.</strong> (USA) &mdash; hosting dei servizi backend e database</li>
                  <li><strong className="text-[#1E293B]">Moonshot AI</strong> (Kimi K2.5) &mdash; generazione di contenuti e siti web tramite intelligenza artificiale</li>
                  <li><strong className="text-[#1E293B]">Google LLC</strong> &mdash; Google Analytics per l&apos;analisi del traffico, Google OAuth per l&apos;autenticazione</li>
                  <li><strong className="text-[#1E293B]">Resend Inc.</strong> (USA) &mdash; servizio di invio email transazionali</li>
                  <li><strong className="text-[#1E293B]">Stripe / Revolut</strong> &mdash; elaborazione dei pagamenti</li>
                </>
              )}
            </ul>
            <p className="text-[#64748B] mt-4">
              {en
                ? "For data transfers to the USA, we rely on the safeguards provided by the EU-US Data Privacy Framework and/or the Standard Contractual Clauses approved by the European Commission."
                : "Per i trasferimenti di dati verso gli USA, ci avvaliamo delle garanzie previste dal EU-US Data Privacy Framework e/o dalle Clausole Contrattuali Standard approvate dalla Commissione Europea."
              }
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "6. User rights" : "6. Diritti dell'utente"}</h2>
            <p className="text-[#64748B] mb-4">
              {en ? "Under Articles 15-22 of the GDPR, you have the right to:" : "Ai sensi degli articoli 15-22 del GDPR, hai il diritto di:"}
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Access:</strong> obtain confirmation of processing and access your data</li>
                  <li><strong className="text-[#1E293B]">Rectification:</strong> request correction of inaccurate data or completion of incomplete data</li>
                  <li><strong className="text-[#1E293B]">Erasure:</strong> request deletion of your personal data (&ldquo;right to be forgotten&rdquo;)</li>
                  <li><strong className="text-[#1E293B]">Restriction:</strong> request restriction of processing in certain cases</li>
                  <li><strong className="text-[#1E293B]">Portability:</strong> receive your data in a structured, machine-readable format</li>
                  <li><strong className="text-[#1E293B]">Objection:</strong> object to processing based on legitimate interest</li>
                  <li><strong className="text-[#1E293B]">Consent withdrawal:</strong> withdraw consent at any time</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Accesso:</strong> ottenere conferma dell&apos;esistenza di un trattamento e accedere ai tuoi dati</li>
                  <li><strong className="text-[#1E293B]">Rettifica:</strong> chiedere la correzione di dati inesatti o l&apos;integrazione di dati incompleti</li>
                  <li><strong className="text-[#1E293B]">Cancellazione:</strong> richiedere la cancellazione dei tuoi dati personali (&ldquo;diritto all&apos;oblio&rdquo;)</li>
                  <li><strong className="text-[#1E293B]">Limitazione:</strong> chiedere la limitazione del trattamento in determinati casi</li>
                  <li><strong className="text-[#1E293B]">Portabilità:</strong> ricevere i tuoi dati in un formato strutturato e leggibile da dispositivo automatico</li>
                  <li><strong className="text-[#1E293B]">Opposizione:</strong> opporti al trattamento basato sul legittimo interesse</li>
                  <li><strong className="text-[#1E293B]">Revoca del consenso:</strong> revocare in qualsiasi momento il consenso prestato</li>
                </>
              )}
            </ul>
            <p className="text-[#64748B] mt-4">
              {en ? (
                <>To exercise your rights, send a request to{" "}
                  <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>.
                  You also have the right to lodge a complaint with the <strong className="text-[#1E293B]">Italian Data Protection Authority</strong>{" "}
                  (<a href="https://www.garanteprivacy.it" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">www.garanteprivacy.it</a>).
                </>
              ) : (
                <>Per esercitare i tuoi diritti, invia una richiesta a{" "}
                  <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>.
                  Hai inoltre il diritto di proporre reclamo al <strong className="text-[#1E293B]">Garante per la protezione dei dati personali</strong>{" "}
                  (<a href="https://www.garanteprivacy.it" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">www.garanteprivacy.it</a>).
                </>
              )}
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "7. Data retention" : "7. Conservazione dei dati"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <>Your personal data is retained for the duration of the contractual relationship and, subsequently, for a maximum period of <strong className="text-[#1E293B]">10 years</strong> from the end of the relationship, in compliance with tax and accounting legal obligations. Browsing data and access logs are retained for a maximum of 24 months. At the end of retention periods, data is deleted or irreversibly anonymized.</>
                : <>I tuoi dati personali sono conservati per la durata del rapporto contrattuale e, successivamente, per un periodo massimo di <strong className="text-[#1E293B]">10 anni</strong> dalla cessazione del rapporto, in conformità con gli obblighi di legge in materia fiscale e contabile. I dati di navigazione e i log di accesso sono conservati per un massimo di 24 mesi. Al termine dei periodi di conservazione, i dati vengono cancellati o anonimizzati in modo irreversibile.</>
              }
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "8. Security measures" : "8. Misure di sicurezza"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "We adopt adequate technical and organizational measures to protect your personal data, including: encryption of data in transit (HTTPS/TLS), password hashing, need-based access to data, regular backups, and continuous monitoring of system security."
                : "Adottiamo misure tecniche e organizzative adeguate per proteggere i tuoi dati personali, tra cui: crittografia dei dati in transito (HTTPS/TLS), hashing delle password, accesso limitato ai dati su base di necessità, backup periodici e monitoraggio continuo della sicurezza dei sistemi."
              }
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "9. Changes to this policy" : "9. Modifiche alla presente informativa"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "We reserve the right to update this policy at any time. Changes will be published on this page with an indication of the last update date. We encourage you to periodically review this page to stay informed about how your data is processed."
                : "Ci riserviamo il diritto di aggiornare la presente informativa in qualsiasi momento. Le modifiche saranno pubblicate su questa pagina con indicazione della data di ultimo aggiornamento. Ti invitiamo a consultare periodicamente questa pagina per restare informato sulle modalità di trattamento dei tuoi dati."
              }
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "10. Contact" : "10. Contatti"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "For any questions or requests regarding this policy or the processing of your personal data:"
                : "Per qualsiasi domanda o richiesta relativa alla presente informativa o al trattamento dei tuoi dati personali:"
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
          <Link href="/terms" className="hover:text-[#4F46E5] transition-colors">{en ? "Terms of Service" : "Termini di Servizio"}</Link>
          <Link href="/cookies" className="hover:text-[#4F46E5] transition-colors">Cookie Policy</Link>
        </div>
      </div>
    </main>
  );
}
