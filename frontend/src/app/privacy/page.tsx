import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Informativa sulla Privacy - E-quipe",
  description: "Informativa sulla privacy di E-quipe S.r.l.s. ai sensi del Regolamento UE 2016/679 (GDPR)",
};

export default function PrivacyPage() {
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
          Informativa sulla Privacy
        </h1>
        <p className="text-[#64748B] mb-12">
          Ultimo aggiornamento: Febbraio 2026
        </p>

        <div className="space-y-10 text-[#1E293B] leading-relaxed">
          {/* 1. Titolare del trattamento */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Titolare del trattamento</h2>
            <p className="text-[#64748B]">
              Il titolare del trattamento dei dati personali è <strong className="text-[#1E293B]">E-quipe S.r.l.s.</strong>,
              con sede legale in Roma, P.IVA 17629021001.
            </p>
            <p className="text-[#64748B] mt-3">
              Per qualsiasi richiesta relativa al trattamento dei tuoi dati personali, puoi contattarci
              all&apos;indirizzo email: <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>
            </p>
          </section>

          {/* 2. Dati raccolti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Dati personali raccolti</h2>
            <p className="text-[#64748B] mb-4">
              Nell&apos;ambito dell&apos;erogazione del servizio e-quipe.app, raccogliamo le seguenti
              categorie di dati personali:
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">Dati identificativi:</strong> nome, cognome, indirizzo email</li>
              <li><strong className="text-[#1E293B]">Dati di autenticazione:</strong> credenziali di accesso (password in forma criptata), dati di accesso tramite Google OAuth</li>
              <li><strong className="text-[#1E293B]">Dati di navigazione:</strong> indirizzo IP, tipo di browser, pagine visitate, orari di accesso, dati di interazione con la piattaforma</li>
              <li><strong className="text-[#1E293B]">Dati relativi al servizio:</strong> siti web generati, contenuti inseriti, preferenze di stile e template selezionati</li>
              <li><strong className="text-[#1E293B]">Dati di pagamento:</strong> gestiti direttamente dai processori di pagamento (Stripe/Revolut); non memorizziamo dati completi delle carte di credito</li>
            </ul>
          </section>

          {/* 3. Finalità del trattamento */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Finalit&agrave; del trattamento</h2>
            <p className="text-[#64748B] mb-4">I tuoi dati personali vengono trattati per le seguenti finalit&agrave;:</p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">Erogazione del servizio:</strong> creazione e gestione dell&apos;account, generazione di siti web tramite intelligenza artificiale, gestione delle campagne pubblicitarie</li>
              <li><strong className="text-[#1E293B]">Comunicazioni di servizio:</strong> invio di email relative al tuo account, notifiche di aggiornamento, assistenza tecnica</li>
              <li><strong className="text-[#1E293B]">Miglioramento del servizio:</strong> analisi aggregate e anonimizzate per migliorare le funzionalit&agrave; della piattaforma</li>
              <li><strong className="text-[#1E293B]">Adempimenti di legge:</strong> obblighi fiscali, contabili e normativi</li>
            </ul>
          </section>

          {/* 4. Base giuridica */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Base giuridica del trattamento</h2>
            <p className="text-[#64748B] mb-4">
              Il trattamento dei tuoi dati personali si fonda sulle seguenti basi giuridiche ai sensi
              del Regolamento UE 2016/679 (GDPR):
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">Esecuzione del contratto</strong> (Art. 6.1.b GDPR): il trattamento &egrave; necessario per l&apos;erogazione del servizio richiesto</li>
              <li><strong className="text-[#1E293B]">Consenso</strong> (Art. 6.1.a GDPR): per l&apos;invio di comunicazioni promozionali e per i cookie analitici</li>
              <li><strong className="text-[#1E293B]">Legittimo interesse</strong> (Art. 6.1.f GDPR): per la sicurezza della piattaforma e il miglioramento del servizio</li>
              <li><strong className="text-[#1E293B]">Obbligo legale</strong> (Art. 6.1.c GDPR): per gli adempimenti fiscali e normativi</li>
            </ul>
          </section>

          {/* 5. Terze parti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Condivisione con terze parti</h2>
            <p className="text-[#64748B] mb-4">
              I tuoi dati possono essere condivisi con i seguenti fornitori di servizi, che agiscono
              in qualit&agrave; di responsabili del trattamento:
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">Vercel Inc.</strong> (USA) &mdash; hosting della piattaforma frontend</li>
              <li><strong className="text-[#1E293B]">Render Services Inc.</strong> (USA) &mdash; hosting dei servizi backend e database</li>
              <li><strong className="text-[#1E293B]">Moonshot AI</strong> (Kimi K2.5) &mdash; generazione di contenuti e siti web tramite intelligenza artificiale</li>
              <li><strong className="text-[#1E293B]">Google LLC</strong> &mdash; Google Analytics per l&apos;analisi del traffico, Google OAuth per l&apos;autenticazione</li>
              <li><strong className="text-[#1E293B]">Resend Inc.</strong> (USA) &mdash; servizio di invio email transazionali</li>
              <li><strong className="text-[#1E293B]">Stripe / Revolut</strong> &mdash; elaborazione dei pagamenti</li>
            </ul>
            <p className="text-[#64748B] mt-4">
              Per i trasferimenti di dati verso gli USA, ci avvaliamo delle garanzie previste dal
              EU-US Data Privacy Framework e/o dalle Clausole Contrattuali Standard approvate dalla
              Commissione Europea.
            </p>
          </section>

          {/* 6. Diritti dell'utente */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Diritti dell&apos;utente</h2>
            <p className="text-[#64748B] mb-4">
              Ai sensi degli articoli 15-22 del GDPR, hai il diritto di:
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              <li><strong className="text-[#1E293B]">Accesso:</strong> ottenere conferma dell&apos;esistenza di un trattamento e accedere ai tuoi dati</li>
              <li><strong className="text-[#1E293B]">Rettifica:</strong> chiedere la correzione di dati inesatti o l&apos;integrazione di dati incompleti</li>
              <li><strong className="text-[#1E293B]">Cancellazione:</strong> richiedere la cancellazione dei tuoi dati personali (&ldquo;diritto all&apos;oblio&rdquo;)</li>
              <li><strong className="text-[#1E293B]">Limitazione:</strong> chiedere la limitazione del trattamento in determinati casi</li>
              <li><strong className="text-[#1E293B]">Portabilit&agrave;:</strong> ricevere i tuoi dati in un formato strutturato e leggibile da dispositivo automatico</li>
              <li><strong className="text-[#1E293B]">Opposizione:</strong> opporti al trattamento basato sul legittimo interesse</li>
              <li><strong className="text-[#1E293B]">Revoca del consenso:</strong> revocare in qualsiasi momento il consenso prestato</li>
            </ul>
            <p className="text-[#64748B] mt-4">
              Per esercitare i tuoi diritti, invia una richiesta a{" "}
              <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>.
              Hai inoltre il diritto di proporre reclamo al <strong className="text-[#1E293B]">Garante per la protezione dei dati personali</strong>{" "}
              (<a href="https://www.garanteprivacy.it" className="text-[#4F46E5] hover:underline" target="_blank" rel="noopener noreferrer">www.garanteprivacy.it</a>).
            </p>
          </section>

          {/* 7. Conservazione dati */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Conservazione dei dati</h2>
            <p className="text-[#64748B]">
              I tuoi dati personali sono conservati per la durata del rapporto contrattuale e,
              successivamente, per un periodo massimo di <strong className="text-[#1E293B]">10 anni</strong> dalla
              cessazione del rapporto, in conformit&agrave; con gli obblighi di legge in materia fiscale
              e contabile. I dati di navigazione e i log di accesso sono conservati per un massimo
              di 24 mesi. Al termine dei periodi di conservazione, i dati vengono cancellati o
              anonimizzati in modo irreversibile.
            </p>
          </section>

          {/* 8. Sicurezza */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Misure di sicurezza</h2>
            <p className="text-[#64748B]">
              Adottiamo misure tecniche e organizzative adeguate per proteggere i tuoi dati personali,
              tra cui: crittografia dei dati in transito (HTTPS/TLS), hashing delle password,
              accesso limitato ai dati su base di necessit&agrave;, backup periodici e monitoraggio
              continuo della sicurezza dei sistemi.
            </p>
          </section>

          {/* 9. Modifiche */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Modifiche alla presente informativa</h2>
            <p className="text-[#64748B]">
              Ci riserviamo il diritto di aggiornare la presente informativa in qualsiasi momento.
              Le modifiche saranno pubblicate su questa pagina con indicazione della data di ultimo
              aggiornamento. Ti invitiamo a consultare periodicamente questa pagina per restare
              informato sulle modalit&agrave; di trattamento dei tuoi dati.
            </p>
          </section>

          {/* 10. Contatti */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Contatti</h2>
            <p className="text-[#64748B]">
              Per qualsiasi domanda o richiesta relativa alla presente informativa o al trattamento
              dei tuoi dati personali:
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
          <Link href="/terms" className="hover:text-[#4F46E5] transition-colors">Termini di Servizio</Link>
          <Link href="/cookies" className="hover:text-[#4F46E5] transition-colors">Cookie Policy</Link>
        </div>
      </div>
    </main>
  );
}
