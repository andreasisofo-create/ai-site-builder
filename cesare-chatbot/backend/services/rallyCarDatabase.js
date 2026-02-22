/**
 * rallyCarDatabase.js — Agente Database Auto Rally di Roma Capitale
 *
 * Contiene i dati verificati dei partecipanti all'edizione 2025.
 * Usato dal Photo Agent per arricchire il riconoscimento delle auto.
 */

/**
 * Partecipanti confermati Rally di Roma Capitale 2025 (FIA ERC Stop 5 + CIAR Sparco)
 * Fonte: foto ufficiali Red Bull Content Pool + risultati ERC 2025
 */
export const PARTECIPANTI_2025 = [
  // ── ERC ──────────────────────────────────────────────────────────────────
  { numero: 1,  pilota: 'Andrea Crugnola',       copilota: 'Pietro Ometto',          auto: 'Škoda Fabia RS Rally2', team: 'Movisport / Shell Helix',     nazione: '🇮🇹' },
  { numero: 4,  pilota: 'Giandomenico Basso',    copilota: 'Lorenzo Granai',         auto: 'Hyundai i20 N Rally2',  team: 'Hyundai Rally Team Italia',   nazione: '🇮🇹', note: 'Vincitore 2025' },
  { numero: 5,  pilota: 'Miko Marczyk',          copilota: 'Szymon Gospodarczyk',    auto: 'Škoda Fabia RS Rally2', team: 'ORLEN Team / Škoda Auto PL',   nazione: '🇵🇱' },
  { numero: 7,  pilota: 'Simone Campedelli',     copilota: 'Tania Canton',           auto: 'Škoda Fabia RS Rally2', team: 'TRT World Rally Team',         nazione: '🇮🇹' },
  { numero: 8,  pilota: 'Fabio Andolfi',         copilota: 'Simone Scattolin',       auto: 'Škoda Fabia RS Rally2', team: 'Movisport',                    nazione: '🇮🇹' },
  { numero: 10, pilota: 'Efrén Llarena',         copilota: 'Sara Fernández',         auto: 'Škoda Fabia RS Rally2', team: 'Rallye Team Spain',            nazione: '🇪🇸' },
  { numero: 11, pilota: 'Jon Armstrong',         copilota: 'Brian Hoy',              auto: 'Škoda Fabia RS Rally2', team: 'FP World Rally Team',          nazione: '🇬🇧' },
  { numero: 21, pilota: 'Mads Østberg',          copilota: 'Jonas Andersson',        auto: 'Citroën C3 Rally2',     team: 'Toksport WRT',                 nazione: '🇳🇴' },
  { numero: 29, pilota: 'Pepe López',            copilota: 'Borja Rozada',           auto: 'Škoda Fabia RS Rally2', team: 'Rallye Team Spain',            nazione: '🇪🇸' },
  // ── CIAR Sparco ──────────────────────────────────────────────────────────
  { numero: 3,  pilota: 'Umberto Scandola',      copilota: 'Guido D\'Amore',         auto: 'Škoda Fabia RS Rally2', team: 'Friulmotor',                   nazione: '🇮🇹' },
  { numero: 6,  pilota: 'Andrea Mabellini',      copilota: 'Virginia Lenzi',         auto: 'Hyundai i20 N Rally2',  team: 'TRT World Rally Team',         nazione: '🇮🇹' },
  { numero: 9,  pilota: 'Roberto Daprà',         copilota: 'Luca Guglielmetti',      auto: 'Škoda Fabia RS Rally2', team: 'Movisport',                    nazione: '🇮🇹' },
];

/**
 * Restituisce la stringa contestuale con tutti i partecipanti,
 * da iniettare nel prompt del Vision Agent.
 */
export function getPartecipantiContext() {
  const righe = PARTECIPANTI_2025.map(p =>
    `  #${p.numero} ${p.nazione} ${p.pilota} / ${p.copilota} — ${p.auto} — ${p.team}${p.note ? ` (${p.note})` : ''}`
  ).join('\n');

  return `PARTECIPANTI CONFERMATI RALLY DI ROMA CAPITALE 2025 (ERC + CIAR Sparco):\n${righe}`;
}

/**
 * Cerca un partecipante per numero di gara.
 * @param {number|string} numero
 */
export function cercaPerNumero(numero) {
  return PARTECIPANTI_2025.find(p => p.numero === parseInt(numero)) || null;
}
