"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/i18n";

export default function TermsPage() {
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
          {en ? "Terms of Service" : "Termini di Servizio"}
        </h1>
        <p className="text-[#64748B] mb-12">
          {en ? "Last updated: February 2026" : "Ultimo aggiornamento: Febbraio 2026"}
        </p>

        <div className="space-y-10 text-[#1E293B] leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "1. Definitions" : "1. Definizioni"}</h2>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">&ldquo;Service&rdquo;</strong>: the e-quipe.app platform, including all AI-powered website generation features and ad campaign management</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Owner&rdquo;</strong> or <strong className="text-[#1E293B]">&ldquo;We&rdquo;</strong>: E-quipe S.r.l.s., VAT 17629021001, with registered office in Rome</li>
                  <li><strong className="text-[#1E293B]">&ldquo;User&rdquo;</strong> or <strong className="text-[#1E293B]">&ldquo;You&rdquo;</strong>: any natural or legal person who accesses or uses the Service</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Generated Site&rdquo;</strong>: any website created through the platform using artificial intelligence</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Account&rdquo;</strong>: the set of credentials and data associated with the User&apos;s registration on the platform</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">&ldquo;Servizio&rdquo;</strong>: la piattaforma e-quipe.app, incluse tutte le funzionalità di generazione siti web tramite intelligenza artificiale e gestione campagne pubblicitarie</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Titolare&rdquo;</strong> o <strong className="text-[#1E293B]">&ldquo;Noi&rdquo;</strong>: E-quipe S.r.l.s., P.IVA 17629021001, con sede legale in Roma</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Utente&rdquo;</strong> o <strong className="text-[#1E293B]">&ldquo;Tu&rdquo;</strong>: qualsiasi persona fisica o giuridica che accede o utilizza il Servizio</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Sito Generato&rdquo;</strong>: qualsiasi sito web creato attraverso la piattaforma tramite l&apos;uso dell&apos;intelligenza artificiale</li>
                  <li><strong className="text-[#1E293B]">&ldquo;Account&rdquo;</strong>: l&apos;insieme di credenziali e dati associati alla registrazione dell&apos;Utente sulla piattaforma</li>
                </>
              )}
            </ul>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "2. Service description" : "2. Descrizione del servizio"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "E-quipe is a SaaS platform that allows users to generate professional websites using artificial intelligence. The user selects a template, provides information about their business, and the system automatically generates a complete website with animations, text, and optimized graphics."
                : "E-quipe è una piattaforma SaaS che consente agli utenti di generare siti web professionali tramite intelligenza artificiale. L'utente seleziona un template, fornisce le informazioni sulla propria attività, e il sistema genera automaticamente un sito web completo con animazioni, testi e grafica ottimizzati."
              }
            </p>
            <p className="text-[#64748B] mt-3">
              {en
                ? "The platform also includes tools for managing online advertising campaigns (Google Ads, Meta Ads) with AI-assisted optimization."
                : "La piattaforma include inoltre strumenti per la gestione di campagne pubblicitarie online (Google Ads, Meta Ads) con ottimizzazione assistita dall'intelligenza artificiale."
              }
            </p>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "3. Registration and account" : "3. Registrazione e account"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "To use the Service, you must create an account by providing truthful and up-to-date information. The user is responsible for the confidentiality of their login credentials and all activities performed through their account."
                : "Per utilizzare il Servizio è necessario creare un account fornendo informazioni veritiere e aggiornate. L'utente è responsabile della riservatezza delle proprie credenziali di accesso e di tutte le attività svolte tramite il proprio account."
              }
            </p>
            <p className="text-[#64748B] mt-3">
              {en
                ? "You can register via email and password or via Google OAuth authentication. Each user may have only one account. E-quipe reserves the right to suspend or close accounts that violate these terms."
                : "È possibile registrarsi tramite email e password oppure tramite autenticazione Google OAuth. Ogni utente può disporre di un solo account. E-quipe si riserva il diritto di sospendere o chiudere account che violino i presenti termini."
              }
            </p>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "4. Plans and payments" : "4. Piani e pagamenti"}</h2>
            <p className="text-[#64748B] mb-4">
              {en ? "The Service is offered through the following subscription plans:" : "Il Servizio è offerto attraverso i seguenti piani di abbonamento:"}
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li><strong className="text-[#1E293B]">Starter:</strong> basic website generation features</li>
                  <li><strong className="text-[#1E293B]">Business:</strong> advanced features, more templates and customization</li>
                  <li><strong className="text-[#1E293B]">Growth:</strong> includes ad campaign management and advanced analytics</li>
                  <li><strong className="text-[#1E293B]">Premium:</strong> full access to all features, priority support</li>
                </>
              ) : (
                <>
                  <li><strong className="text-[#1E293B]">Starter:</strong> funzionalità base per la generazione di siti web</li>
                  <li><strong className="text-[#1E293B]">Business:</strong> funzionalità avanzate, più template e personalizzazione</li>
                  <li><strong className="text-[#1E293B]">Growth:</strong> include gestione campagne pubblicitarie e analytics avanzati</li>
                  <li><strong className="text-[#1E293B]">Premium:</strong> accesso completo a tutte le funzionalità, supporto prioritario</li>
                </>
              )}
            </ul>
            <p className="text-[#64748B] mt-4">
              {en
                ? "Payments are processed through Stripe and/or Revolut. Prices are listed in Euros (EUR) and include VAT where applicable. The subscription automatically renews at expiration, unless cancelled by the user at least 24 hours before the renewal date."
                : "I pagamenti vengono elaborati tramite Stripe e/o Revolut. I prezzi sono indicati in Euro (EUR) e si intendono IVA inclusa ove applicabile. L'abbonamento si rinnova automaticamente alla scadenza, salvo disdetta da parte dell'utente con almeno 24 ore di anticipo rispetto alla data di rinnovo."
              }
            </p>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "5. Free trial" : "5. Prova gratuita"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <>E-quipe offers a <strong className="text-[#1E293B]">14-day</strong> free trial for new users. During the free trial, the user has access to the features included in the selected plan. At the end of the trial period, the subscription will activate automatically only if the user has provided a valid payment method. Otherwise, access to premium features will be suspended.</>
                : <>E-quipe offre un periodo di prova gratuita di <strong className="text-[#1E293B]">14 giorni</strong> per i nuovi utenti. Durante la prova gratuita, l&apos;utente ha accesso alle funzionalità previste dal piano selezionato. Al termine del periodo di prova, l&apos;abbonamento si attiverà automaticamente solo se l&apos;utente ha fornito un metodo di pagamento valido. In caso contrario, l&apos;accesso alle funzionalità premium sarà sospeso.</>
              }
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "6. Advertising budget" : "6. Budget pubblicitario"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <>The budget for advertising campaigns (Google Ads, Meta Ads, and other platforms) is entirely <strong className="text-[#1E293B]">at the client&apos;s expense</strong> and is managed directly on the connected advertising platforms. This budget is separate and distinct from the E-quipe platform subscription cost. E-quipe is not responsible for the direct management of advertising funds but provides optimization and monitoring tools.</>
                : <>Il budget destinato alle campagne pubblicitarie (Google Ads, Meta Ads e altre piattaforme) è interamente <strong className="text-[#1E293B]">a carico del cliente</strong> e viene gestito direttamente sulle piattaforme pubblicitarie collegate. Tale budget è separato e distinto dal costo dell&apos;abbonamento alla piattaforma E-quipe. E-quipe non è responsabile per la gestione diretta dei fondi pubblicitari, ma fornisce strumenti di ottimizzazione e monitoraggio.</>
              }
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "7. Intellectual property" : "7. Proprietà intellettuale"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <><strong className="text-[#1E293B]">User-generated content:</strong> the user retains full intellectual property of websites generated through the platform, including text, layouts, and custom configurations. The user is free to use, modify, and distribute their generated sites without limitations.</>
                : <><strong className="text-[#1E293B]">Contenuti generati dall&apos;utente:</strong> l&apos;utente mantiene la piena proprietà intellettuale dei siti web generati attraverso la piattaforma, inclusi testi, layout e configurazioni personalizzate. L&apos;utente è libero di utilizzare, modificare e distribuire i propri siti generati senza limitazioni.</>
              }
            </p>
            <p className="text-[#64748B] mt-3">
              {en
                ? <><strong className="text-[#1E293B]">E-quipe platform:</strong> the platform, its source code, base templates, AI generation engine, graphic components, and the E-quipe brand remain the exclusive property of E-quipe S.r.l.s. The user does not acquire any rights to these elements, except for the limited license granted as part of the active subscription.</>
                : <><strong className="text-[#1E293B]">Piattaforma E-quipe:</strong> la piattaforma, il suo codice sorgente, i template base, il motore di generazione AI, i componenti grafici e il marchio E-quipe restano di proprietà esclusiva di E-quipe S.r.l.s. L&apos;utente non acquisisce alcun diritto su tali elementi, fatta eccezione per la licenza d&apos;uso limitata concessa nell&apos;ambito dell&apos;abbonamento attivo.</>
              }
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "8. Acceptable use" : "8. Uso accettabile"}</h2>
            <p className="text-[#64748B] mb-4">{en ? "The user agrees not to use the Service to:" : "L'utente si impegna a non utilizzare il Servizio per:"}</p>
            <ul className="list-disc list-inside space-y-2 text-[#64748B]">
              {en ? (
                <>
                  <li>Create illegal, defamatory, discriminatory content or content that incites violence</li>
                  <li>Violate third-party intellectual property rights</li>
                  <li>Distribute malware, viruses, or malicious code</li>
                  <li>Attempt to access unauthorized systems or data</li>
                  <li>Use the service for phishing, spam, or fraud activities</li>
                  <li>Intentionally overload the platform&apos;s servers or infrastructure</li>
                  <li>Resell access to the Service without written authorization</li>
                </>
              ) : (
                <>
                  <li>Creare contenuti illegali, diffamatori, discriminatori o che incitino alla violenza</li>
                  <li>Violare diritti di proprietà intellettuale di terzi</li>
                  <li>Distribuire malware, virus o codice dannoso</li>
                  <li>Tentare di accedere a sistemi o dati non autorizzati</li>
                  <li>Utilizzare il servizio per attività di phishing, spam o frode</li>
                  <li>Sovraccaricare intenzionalmente i server o l&apos;infrastruttura della piattaforma</li>
                  <li>Rivendere l&apos;accesso al Servizio senza autorizzazione scritta</li>
                </>
              )}
            </ul>
            <p className="text-[#64748B] mt-4">
              {en
                ? "Violation of these rules may result in immediate account suspension without notice and without right to a refund."
                : "La violazione di queste regole può comportare la sospensione immediata dell'account senza preavviso e senza diritto a rimborso."
              }
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "9. Limitation of liability" : "9. Limitazione di responsabilità"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "The Service is provided \"as is\" and \"as available\". E-quipe is committed to ensuring the continuity and quality of the service but cannot guarantee the absence of interruptions, errors, or malfunctions."
                : "Il Servizio viene fornito \"così com'è\" e \"come disponibile\". E-quipe si impegna a garantire la continuità e la qualità del servizio, ma non può garantire l'assenza di interruzioni, errori o malfunzionamenti."
              }
            </p>
            <p className="text-[#64748B] mt-3">
              {en
                ? "In no event shall E-quipe be liable for indirect, incidental, special, or consequential damages arising from the use or inability to use the Service. E-quipe's total liability to the user shall in no case exceed the total amount paid by the user in the 12 months preceding the event giving rise to the liability."
                : "In nessun caso E-quipe sarà responsabile per danni indiretti, incidentali, speciali o consequenziali derivanti dall'uso o dall'impossibilità di uso del Servizio. La responsabilità complessiva di E-quipe nei confronti dell'utente non potrà in nessun caso superare l'importo totale pagato dall'utente nei 12 mesi precedenti l'evento che ha dato origine alla responsabilità."
              }
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "10. Termination" : "10. Risoluzione"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <>The user may withdraw from the contract and delete their account at any time through the platform settings or by contacting support at <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>.</>
                : <>L&apos;utente può recedere dal contratto e cancellare il proprio account in qualsiasi momento tramite le impostazioni della piattaforma o contattando il supporto all&apos;indirizzo <a href="mailto:info@e-quipe.com" className="text-[#4F46E5] hover:underline">info@e-quipe.com</a>.</>
              }
            </p>
            <p className="text-[#64748B] mt-3">
              {en
                ? "E-quipe reserves the right to terminate the contract and suspend the user's account in case of violation of these terms, with immediate effect and after notification via email. In case of termination, the user will have the opportunity to export their generated sites within 30 days of the closure notification."
                : "E-quipe si riserva il diritto di risolvere il contratto e sospendere l'account dell'utente in caso di violazione dei presenti termini, con effetto immediato e previa comunicazione via email. In caso di risoluzione, l'utente avrà la possibilità di esportare i propri siti generati entro 30 giorni dalla comunicazione di chiusura."
              }
            </p>
          </section>

          {/* 11 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "11. Governing law and jurisdiction" : "11. Legge applicabile e foro competente"}</h2>
            <p className="text-[#64748B]">
              {en
                ? <>These Terms of Service are governed by <strong className="text-[#1E293B]">Italian law</strong>. For any dispute arising from the interpretation or execution of these terms, the <strong className="text-[#1E293B]">Court of Rome</strong> shall have exclusive jurisdiction, except where the law provides for a mandatory forum for consumer protection.</>
                : <>I presenti Termini di Servizio sono regolati dalla <strong className="text-[#1E293B]">legge italiana</strong>. Per qualsiasi controversia derivante dall&apos;interpretazione o dall&apos;esecuzione dei presenti termini, sarà competente in via esclusiva il <strong className="text-[#1E293B]">Foro di Roma</strong>, salvo i casi in cui la legge preveda un foro inderogabile a tutela del consumatore.</>
              }
            </p>
          </section>

          {/* 12 */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">{en ? "12. Contact" : "12. Contatti"}</h2>
            <p className="text-[#64748B]">
              {en
                ? "For any questions regarding these Terms of Service:"
                : "Per qualsiasi domanda relativa ai presenti Termini di Servizio:"
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
          <Link href="/cookies" className="hover:text-[#4F46E5] transition-colors">Cookie Policy</Link>
        </div>
      </div>
    </main>
  );
}
