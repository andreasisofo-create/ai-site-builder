/**
 * knowledge.js — Knowledge base completa del Rally di Roma Capitale
 *
 * Fonti: rallydiromacapitale.it, eWRC, fiaerc.com, acisport.it
 * Ultimo aggiornamento: febbraio 2026
 */

// ─── Informazioni generali evento ───────────────────────────────────────────
export const EVENT_INFO = {
  nome: 'Rally di Roma Capitale',
  edizione_corrente: '13ª edizione 2026',
  campionati: [
    'FIA European Rally Championship (ERC)',
    'Campionato Italiano Assoluto Rally Sparco (CIAR)',
  ],
  date: '3-5 luglio 2026',
  date_dettaglio: {
    inizio: 'Venerdì 4 luglio 2026',
    fine: 'Domenica 6 luglio 2026',
  },
  sito_ufficiale: 'https://www.rallydiromacapitale.it',
  email_contatto: 'info@rallydiromacapitale.it',
  telefono: ['06 5214260', '331 805 8801'],
  organizzatore: 'Motorsport Italia S.p.A.',
  direttore: 'Max Rendina',
  indirizzo_organizzatore: 'Via Charles Lenormant, 156, Roma 00119',
  patrocinio: 'Ministero per lo Sport e i Giovani, Roma Capitale, Regione Lazio, ACI Sport',
  social: {
    instagram: 'https://www.instagram.com/rallydiromacapitale',
    facebook: 'https://www.facebook.com/rallydiromacapitale',
    youtube: 'https://www.youtube.com/@RallydiRomaCapitale',
  },
  descrizione:
    'Il Rally di Roma Capitale è un rally su asfalto che dal 2013 porta le auto da competizione ' +
    'nel centro di Roma e nella regione Lazio. Nato come evento nazionale, è entrato nel FIA ' +
    'European Rally Championship (ERC) nel 2017, riportando l\'Italia nel campionato continentale. ' +
    'L\'evento è gratuito per gli spettatori e offre tre giorni di competizione con oltre 900 km ' +
    'di percorso. Nel 2026 è candidato all\'osservazione FIA/WRC Promoter per un\'eventuale ' +
    'inclusione nel calendario WRC 2027.',
  ingresso: 'GRATUITO per tutti gli spettatori',
  impatto_tv: 'Oltre 9 milioni di spettatori nei collegamenti TV e streaming nell\'edizione 2025',
  novita_2026: [
    'HQ, Sala Stampa e Parco Assistenza si spostano da Fiuggi a Roma (prima volta nella storia)',
    'Percorso e logistica completamente ridisegnati con nuove prove speciali',
    'Candidatura ufficiale all\'osservazione FIA/WRC Promoter per il WRC 2027',
    'Accreditamento FIA Environmental Programme 3 stelle (sostenibilità)',
    'Proseguono i progetti sociali: "La strada non è un videogioco" e collaborazioni con associazioni locali',
  ],
};

// ─── Programma dettagliato 2026 ──────────────────────────────────────────────
export const PROGRAMMA = {
  date_confermate: true,
  periodo: '4-6 luglio 2026 (con apertura venerdì 4)',
  struttura: 'Tre giorni — cerimonia apertura + 2 tappe competitive',
  km_prove_speciali: '140-160 km totali di prove speciali su asfalto',
  power_stage: 'Jenne – Monastero 2 (ultima prova, ~7 km)',
  shakedown: 'Al Parco Assistenza di Roma prima della cerimonia',

  giorni: {
    venerdi: {
      data: 'Venerdì 4 luglio 2026',
      tipo: 'Cerimonia apertura + Prova Spettacolo',
      orari: [
        { ora: '18:00', evento: 'Roma Parade Start — Bocca della Verità' },
        { ora: '19:00', evento: 'Apertura VIP Lounge in via delle Terme di Tito (Colle Oppio)' },
        { ora: '20:05', evento: 'PS "Colosseo – ACI Roma" — prova spettacolo serale nelle vie intorno al Colosseo' },
      ],
    },
    sabato: {
      data: 'Sabato 5 luglio 2026',
      tipo: 'Prima tappa — strade di montagna Frusinate',
      orari: [
        { ora: '08:30', evento: 'PS Vico nel Lazio – Collepardo Pozzo d\'Antullo 1' },
        { ora: '09:40', evento: 'PS Torre di Cicerone 1' },
        { ora: '11:10', evento: 'PS Santopadre 1' },
        { ora: '13:35', evento: 'Rientro al paddock (Fiuggi)' },
        { ora: '14:45', evento: 'PS Vico nel Lazio – Collepardo Pozzo d\'Antullo 2' },
        { ora: '~16:00', evento: 'PS Torre di Cicerone 2' },
        { ora: '~17:15', evento: 'PS Santopadre 2' },
        { ora: '19:20', evento: 'Arrivo al paddock' },
      ],
    },
    domenica: {
      data: 'Domenica 6 luglio 2026',
      tipo: 'Seconda tappa + Power Stage + Podio',
      orari: [
        { ora: '08:25', evento: 'PS Guarcino – Altipiani 1' },
        { ora: '09:20', evento: 'PS Canterano – Subiaco 1' },
        { ora: '11:05', evento: 'PS Jenne – Monastero 1' },
        { ora: '12:30', evento: 'Arrivo al paddock' },
        { ora: '13:45', evento: 'PS Guarcino – Altipiani 2' },
        { ora: '14:40', evento: 'PS Canterano – Subiaco 2' },
        { ora: '17:05', evento: 'POWER STAGE — Jenne – Monastero 2' },
        { ora: '18:30', evento: 'Cerimonia del Podio a Fiuggi, Corso Nuova Italia' },
      ],
    },
  },

  prove_speciali: [
    'Colosseo – ACI Roma (PS serale venerdì)',
    'Vico nel Lazio – Collepardo Pozzo d\'Antullo',
    'Torre di Cicerone',
    'Santopadre',
    'Guarcino – Altipiani',
    'Canterano – Subiaco',
    'Jenne – Monastero (Power Stage)',
  ],

  nota: 'Il programma definitivo potrebbe subire modifiche. Orari ufficiali su rallydiromacapitale.it.',
};

// ─── Location, mappe e logistica ─────────────────────────────────────────────
export const LOCATION = {
  hq_2026: {
    luogo: 'Roma (novità assoluta 2026 — in precedenza era a Fiuggi)',
    dettaglio: 'Rally HQ, Sala Stampa e Parco Assistenza per la prima volta nel cuore di Roma',
  },

  // Coordinate GPS luoghi chiave per invio posizione Telegram
  luoghi_gps: {
    bocca_della_verita: {
      nome: 'Bocca della Verità — Partenza Parade',
      lat: 41.8883,
      lon: 12.4813,
      maps: 'https://maps.google.com/?q=41.8883,12.4813',
      descrizione: 'Piazza Bocca della Verità — partenza Roma Parade (venerdì ore 18:00)',
    },
    colosseo: {
      nome: 'Colosseo — Prova Speciale Serale',
      lat: 41.8902,
      lon: 12.4922,
      maps: 'https://maps.google.com/?q=41.8902,12.4922',
      descrizione: 'Area Colosseo — PS serale "Colosseo – ACI Roma" (venerdì ore 20:05)',
    },
    colle_oppio: {
      nome: 'Colle Oppio — Area Spettatori Roma',
      lat: 41.8886,
      lon: 12.4947,
      maps: 'https://maps.google.com/?q=41.8886,12.4947',
      descrizione: 'Parco del Colle Oppio — area spettatori con stand, bar e intrattenimento',
    },
    fiuggi: {
      nome: 'Fiuggi — Podio e Village',
      lat: 41.8003,
      lon: 13.2217,
      maps: 'https://maps.google.com/?q=41.8003,13.2217',
      descrizione: 'Fiuggi, Corso Nuova Italia — cerimonia podio (domenica ore 18:30) e Village',
    },
    vico_nel_lazio: {
      nome: 'Vico nel Lazio — PS sabato',
      lat: 41.7497,
      lon: 13.2672,
      maps: 'https://maps.google.com/?q=41.7497,13.2672',
      descrizione: 'Punto spettatori prova speciale Vico nel Lazio – Collepardo',
    },
    jenne: {
      nome: 'Jenne — Power Stage domenica',
      lat: 41.8722,
      lon: 13.1622,
      maps: 'https://maps.google.com/?q=41.8722,13.1622',
      descrizione: 'Jenne — Power Stage finale (domenica ore 17:05)',
    },
  },

  aree_spettatori: {
    roma_colle_oppio: {
      nome: 'Roma — Colle Oppio',
      descrizione: 'Area aperta al pubblico con pista di gara, stand espositivi, cocktail bar. Famiglie benvenute.',
      ps_serale: 'Prova Speciale Colosseo (venerdì sera) — spettacolo unico nel suo genere',
      accesso: 'Gratuito',
    },
    fiuggi_village: {
      nome: 'Fiuggi — Village e Paddock',
      descrizione: 'Village con intrattenimento, stand gastronomici, musica e area paddock.',
      accesso: 'Gratuito',
      podio: 'Cerimonia di premiazione finale in Corso Nuova Italia',
    },
    zone_montagna: {
      nome: 'Province Roma e Frosinone — Punti Spettatori PS',
      descrizione: 'Zone spettatori lungo le prove speciali. Mappe ufficiali pubblicate sul sito prima dell\'evento.',
      sicurezza: 'Rispettare sempre le indicazioni del personale di sicurezza. Non accedere a zone proibite.',
    },
  },

  come_arrivare: {
    aereo: {
      aeroporto: 'Fiumicino – Leonardo da Vinci (FCO), ~26 km da Roma',
      opzioni: [
        'Leonardo Express: Fiumicino → Roma Termini in ~32 min, 14€, no fermate',
        'FL1 regionale: ogni 15 min, Fiumicino → Roma Tiburtina in ~48 min, 8€',
        'Taxi: tariffa fissa 48€ verso centro Roma, 55€ verso Tiburtina',
        'Bus: ATRAL, COTRAL, Terravision con partenze regolari',
      ],
      nota_bambini: 'Bambini sotto 4 anni gratis sul treno. Un bambino 4-12 anni gratis per ogni adulto sul Leonardo Express.',
    },
    treno: {
      stazioni: [
        'Roma Termini — nodo principale, metro A e B, biglietterie, servizi completi',
        'Roma Tiburtina — alta velocità, metro B, terminal bus lunga percorrenza',
      ],
      da_fiuggi: 'Da Roma Termini: treno per Frosinone poi bus/taxi per Fiuggi (~1h30 totale)',
    },
    autobus: {
      info: 'Stazione Tiburtina: terminal pullman nazionali e internazionali',
      raccomandazione: 'Usare mezzi pubblici per raggiungere Roma — traffico intenso durante l\'evento',
    },
    auto: [
      'Da Roma Nord: A1 Autostrada del Sole direzione Napoli, uscita Frosinone o Anagni-Fiuggi',
      'Per zone Frusinate: SS215 o SS6 Casilina',
      'Arrivare almeno 2 ore prima — strade chiuse nelle zone di gara',
      'Seguire segnaletica ufficiale dell\'evento',
    ],
  },

  parcheggio: {
    disponibilita: 'Aree parcheggio dedicate nelle zone gara — gratuiti',
    consiglio: 'Arrivare presto, parcheggi si riempiono rapidamente',
    sostenibilita: 'Preferire car sharing o mezzi pubblici in linea con la politica green del rally',
  },

  accessibilita: {
    famiglie: 'Sì — area Colle Oppio a Roma e Village Fiuggi pensati per famiglie con bambini',
    disabili: 'Aree accessibili disponibili — contattare organizzazione per assistenza specifica',
    email: 'info@rallydiromacapitale.it',
    telefono: '06 5214260',
  },
};

// ─── Biglietti e accesso ──────────────────────────────────────────────────────
export const BIGLIETTI = {
  ingresso_base: 'GRATUITO',
  dettaglio:
    'L\'accesso è sempre gratuito, sia a Roma che sulle prove speciali nella zona del Frusinate e a Fiuggi. ' +
    'Non è necessario acquistare biglietti per le zone pubbliche.',
  aree_gratuite: [
    'Roma — Colle Oppio (area gara + PS serale Colosseo)',
    'Punti spettatori lungo tutte le prove speciali',
    'Fiuggi — Village e Paddock (durante orari di apertura)',
    'Cerimonia del Podio',
  ],
  vip_hospitality: {
    disponibilita: 'Pacchetti VIP/Hospitality disponibili su richiesta',
    cosa_include: 'VIP Lounge, accesso zone riservate, catering, paddock walk',
    lounge_venerdi: 'VIP Lounge in via delle Terme di Tito (Colle Oppio) aperta dalle 19:00',
    contatto_email: 'info@rallydiromacapitale.it',
    contatto_tel: '06 5214260',
  },
  consigli_visitatori: [
    'Arriva almeno 2 ore prima delle prove per trovare buona posizione',
    'Porta acqua e protezione solare — luglio a Roma fa caldo',
    'Rispetta le zone di sicurezza indicate dal personale',
    'Porta via i rifiuti — il rally ha politica green con 3 stelle FIA',
    'Ideale per tutta la famiglia',
  ],
  sito_ufficiale: 'https://www.rallydiromacapitale.it',
};

// ─── Storia e albo d'oro ──────────────────────────────────────────────────────
export const STORIA = {
  prima_edizione: 2013,
  ingresso_erc: 2017,
  descrizione:
    'Il Rally di Roma Capitale è nato nel 2013 come gara nazionale. Nel 2017 è entrato ' +
    'nel FIA European Rally Championship, riportando l\'Italia nel continentale dopo 4 anni. ' +
    'Da allora è cresciuto costantemente fino a diventare uno degli eventi più seguiti dell\'ERC.',

  albo_oro: [
    { anno: 2025, pilota: 'Giandomenico Basso – Lorenzo Granai', auto: 'Škoda Fabia RS Rally2', tempo: '2:04:11.2', note: '3ª vittoria di Basso a Roma. Penalità di 20s a Crugnola. 103 partenti. Oltre 9M spettatori TV.' },
    { anno: 2024, pilota: 'Andrea Crugnola – Pietro Elia Ometto', auto: 'Citroën C3 Rally2', tempo: '1:53:10.9', note: 'Crugnola precede Campedelli e Llarena.' },
    { anno: 2023, pilota: 'Andrea Crugnola – Pietro Elia Ometto', auto: 'Citroën C3 Rally2', tempo: '1:52:35.2', note: '91 equipaggi al via, 69 al traguardo. Basso 2°, Paddon 3°.' },
    { anno: 2022, pilota: 'Damiano De Tommaso – Giorgia Ascalone', auto: 'Škoda Fabia Rally2 evo', tempo: '1:52:37.5', note: 'Campedelli 2°, Bonato 3°.' },
    { anno: 2021, pilota: 'Giandomenico Basso – Lorenzo Granai', auto: 'Škoda Fabia Rally2 evo', tempo: '1:54:06.6', note: 'Crugnola 2°, Herczig 3°.' },
    { anno: 2020, pilota: 'Alexey Lukyanuk – Dmitriy Eremeev', auto: 'Citroën C3 R5', tempo: '1:58:57.0', note: 'Gara in pandemia. Basso 2°, Oliver Solberg 3°.' },
    { anno: 2019, pilota: 'Giandomenico Basso – Lorenzo Granai', auto: 'Škoda Fabia R5', tempo: '1:57:32.0', note: 'Vittoria in volata su Campedelli e Crugnola.' },
    { anno: 2018, pilota: 'Alexey Lukyanuk – Alexey Arnautov', auto: 'Ford Fiesta R5', tempo: '1:48:03.5', note: 'Il russo domina. Basso 2°, Grzyb 3°.' },
    { anno: 2017, pilota: 'Bryan Bouffier – Xavier Panseri', auto: 'Ford Fiesta R5', tempo: '2:02:16.0', note: '1ª edizione ERC. Bouffier batte Kajetanowicz e Magalhães.' },
    { anno: 2016, pilota: 'Umberto Scandola – Guido D\'Amore', auto: 'Škoda Fabia R5', tempo: '1:34:26.1', note: 'Gara nazionale. Andreucci 2°, Basso 3°.' },
    { anno: 2015, pilota: 'Umberto Scandola – Guido D\'Amore', auto: 'Škoda Fabia R5', tempo: '1:37:36.2', note: 'Basso 2°, Andreucci 3°.' },
    { anno: 2014, pilota: 'Tonino Di Cosimo – Mario Papa', auto: 'Ford Focus RS WRC \'07', tempo: '25:12.9', note: 'TRAGEDIA: gara sospesa dopo PS3. Il pilota Emanuele Garosci colpito da infarto, deceduto. Classifica congelata.' },
    { anno: 2013, pilota: 'Dedo (Maurizio Davide) – Matteo Chiarcossi', auto: 'Ford Focus RS WRC \'08', tempo: '59:36.9', note: '1ª edizione in assoluto. Andreucci 2°, Beltrami 3°.' },
  ],

  curiosita: [
    'Giandomenico Basso è il pilota più vincente con 3 vittorie (2019, 2021, 2025)',
    'Umberto Scandola ha vinto le prime due edizioni consecutive (2015-2016)',
    'Il 2014 è l\'unica edizione sospesa per tragedia — in memoria di Emanuele Garosci',
    'Nel 2017 il rally entra nell\'ERC con la vittoria del francese Bryan Bouffier',
    'L\'edizione 2025 ha superato 9 milioni di spettatori TV e streaming',
    'La PS serale al Colosseo è una delle prove più iconiche del rallismo europeo',
    'L\'evento è completamente gratuito per gli spettatori fin dalla prima edizione',
  ],
};

// ─── Risposte fisse ───────────────────────────────────────────────────────────
export const RISPOSTE_FISSE = {
  saluto_it:
    'Ciao! Sono Cesare, l\'assistente ufficiale del Rally di Roma Capitale 2026. ' +
    'Posso aiutarti con date, programma, dove vedere le prove, biglietti e come arrivare. ' +
    'Cosa vuoi sapere?',
  saluto_en:
    'Hello! I\'m Cesare, the official Rally di Roma Capitale 2026 assistant. ' +
    'I can help you with dates, schedule, spectator areas, tickets and how to get there. ' +
    'What would you like to know?',
  non_so:
    'Non ho questa informazione. Contatta l\'organizzazione: ' +
    'info@rallydiromacapitale.it oppure 06 5214260',
  non_so_en:
    'I don\'t have this information. Contact the organization: ' +
    'info@rallydiromacapitale.it or +39 06 5214260',
};

// ─── Funzione ricerca contesto ─────────────────────────────────────────────
/**
 * Cerca keyword nella query e restituisce il contesto rilevante dalla knowledge base.
 * @param {string} query
 * @returns {string}
 */
export function getKnowledgeContext(query) {
  const q = query.toLowerCase();
  const sezioni = [];

  // Programma / date / orari / prove speciali
  if (/quando|programma|orario|schedule|date|giorno|weekend|shakedown|ps|prova speciale|luglio|july|colosseo|vico|jenne|santopadre|guarcino|canterano|torre di cicerone|power stage/.test(q)) {
    sezioni.push(`PROGRAMMA DETTAGLIATO 2026:\n${JSON.stringify(PROGRAMMA, null, 2)}`);
  }

  // Biglietti / prezzi / costo / gratuito
  if (/bigliett|ticket|prezzo|prezzi|costo|acquist|euro|gratuito|gratis|free|vip|hospitality/.test(q)) {
    sezioni.push(`BIGLIETTI E ACCESSO:\n${JSON.stringify(BIGLIETTI, null, 2)}`);
  }

  // Location / dove / come arrivare / parcheggio / mappe / spettatori
  if (/dove|location|posto|luogo|arrivare|parcheggio|parking|treno|aereo|fiumicino|auto|bus|navetta|colle oppio|fiuggi|bocca della verità|spettator|mappa|indicazioni/.test(q)) {
    sezioni.push(`LOCATION, MAPPE E TRASPORTI:\n${JSON.stringify(LOCATION, null, 2)}`);
  }

  // Storia / albo d'oro / edizioni passate / vincitori
  if (/storia|storico|vincitor|albo|passate|edizioni|anni|2013|2014|2015|2016|2017|2018|2019|2020|2021|2022|2023|2024|2025|basso|crugnola|scandola|bouffier|lukyanuk/.test(q)) {
    sezioni.push(`STORIA E ALBO D'ORO:\n${JSON.stringify(STORIA, null, 2)}`);
  }

  // Info generali / cos'è / novità / wrc / erc
  if (/cos.è|what is|evento|rally|erc|campionato|championship|storia|history|wrc|novit|2026|rendina|motorsport italia/.test(q)) {
    sezioni.push(`INFO EVENTO 2026:\n${JSON.stringify(EVENT_INFO, null, 2)}`);
  }

  // Contatti
  if (/contatt|email|telefono|phone|organizzaz|info@/.test(q)) {
    sezioni.push(
      `CONTATTI:\nEmail: ${EVENT_INFO.email_contatto}\n` +
      `Telefono: ${EVENT_INFO.telefono.join(' / ')}\n` +
      `Sito: ${EVENT_INFO.sito_ufficiale}\n` +
      `Organizzatore: ${EVENT_INFO.organizzatore} (dir. ${EVENT_INFO.direttore})`
    );
  }

  // Fallback info base
  if (sezioni.length === 0) {
    sezioni.push(
      `INFO BASE:\nDate: ${EVENT_INFO.date}\nIngresso: ${BIGLIETTI.ingresso_base}\n` +
      `Sito: ${EVENT_INFO.sito_ufficiale}\nEmail: ${EVENT_INFO.email_contatto}`
    );
  }

  return sezioni.join('\n\n---\n\n');
}
