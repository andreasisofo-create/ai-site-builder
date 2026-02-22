/**
 * rallyCarDatabase.js — Elenco iscritti ufficiale Rally di Roma Capitale 2025
 *
 * Fonte: Elenco_iscritti_entry_list_erc_rom_2025_ver_c_25_june.pdf (FIA approvato)
 * 103 equipaggi — ERC1/RC2, ERC3/RC3, ERC4/RC4, RC5, RGT, NAT
 */

export const PARTECIPANTI_2025 = [
  // ── ERC1 / RC2 / Rally2 ────────────────────────────────────────────────────
  { numero: 1,  pilota: 'Roope Korhonen',       copilota: 'Anssi Viinikka',        nazione: 'FIN', auto: 'Toyota GR Yaris Rally2',       team: 'Team MRF Tyres',                      categoria: 'ERC1/RC2' },
  { numero: 2,  pilota: 'Efren Llarena',         copilota: 'Sara Fernandez',         nazione: 'ESP', auto: 'Toyota GR Yaris Rally2',       team: 'Efren Llarena',                       categoria: 'ERC1/RC2' },
  { numero: 3,  pilota: 'Emil Lindholm',         copilota: 'Reeta Hämäläinen',       nazione: 'FIN', auto: 'Škoda Fabia RS Rally2',        team: 'J2X Rally Team',                      categoria: 'ERC1/RC2' },
  { numero: 4,  pilota: 'Miko Marczyk',          copilota: 'Szymon Gospodarczyk',    nazione: 'POL', auto: 'Škoda Fabia RS Rally2',        team: 'Miko Marczyk',                        categoria: 'ERC1/RC2' },
  { numero: 5,  pilota: 'Mads Østberg',          copilota: 'Torstein Eriksen',       nazione: 'NOR', auto: 'Citroën C3 Rally2',           team: 'TRT Rally Team',                      categoria: 'ERC1/RC2' },
  { numero: 6,  pilota: 'Andrea Mabellini',      copilota: 'Virginia Lenzi',         nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Andrea Mabellini',                    categoria: 'ERC1/RC2' },
  { numero: 7,  pilota: 'Jon Armstrong',         copilota: 'Shane Byrne',            nazione: 'IRL', auto: 'Ford Fiesta Mk II Rally2',     team: 'M-Sport Ford World Rally Team',       categoria: 'ERC1/RC2' },
  { numero: 8,  pilota: 'Mille Johansson',       copilota: 'Johan Gronvall',         nazione: 'SWE', auto: 'Škoda Fabia Evo Rally2',       team: 'Mille Johansson',                     categoria: 'ERC1/RC2' },
  { numero: 9,  pilota: 'Simone Tempestini',     copilota: 'Sergiu Itu',             nazione: 'ROU', auto: 'Škoda Fabia RS Rally2',        team: 'Team MRF Tyres',                      categoria: 'ERC1/RC2' },
  { numero: 10, pilota: 'Jakub Matulka',         copilota: 'Damian Syty',            nazione: 'POL', auto: 'Škoda Fabia RS Rally2',        team: 'Jakub Matulka',                       categoria: 'ERC1/RC2' },
  { numero: 11, pilota: 'Jos Verstappen',        copilota: 'Renaud Jamoul',          nazione: 'NED', auto: 'Škoda Fabia RS Rally2',        team: 'Jos Verstappen',                      categoria: 'ERC1/RC2' },
  { numero: 12, pilota: 'Norbert Herczig',       copilota: 'Ramon Ferencz',          nazione: 'HUN', auto: 'Škoda Fabia RS Rally2',        team: 'Proformance Service Kft',             categoria: 'ERC1/RC2' },
  { numero: 14, pilota: 'Simon Wagner',          copilota: 'Hanna Ostlender',        nazione: 'AUT', auto: 'Hyundai i20 N Rally2',         team: 'Kowax DST Racing',                    categoria: 'ERC1/RC2' },
  { numero: 15, pilota: 'Roberto Blach',         copilota: 'Mauro Barreiro',         nazione: 'ESP', auto: 'Škoda Fabia RS Rally2',        team: 'Roberto Blach',                       categoria: 'ERC1/RC2' },
  { numero: 16, pilota: 'Max McRae',             copilota: 'Cameron Fair',           nazione: 'GBR', auto: 'Citroën C3 Rally2',           team: 'MRF Tyres Dealer Team',               categoria: 'ERC1/RC2' },
  { numero: 18, pilota: 'Philip Allen',          copilota: 'Craig Drew',             nazione: 'GBR', auto: 'Škoda Fabia RS Rally2',        team: 'Philip Allen',                        categoria: 'ERC1/RC2' },
  { numero: 19, pilota: 'Martin Vlček',          copilota: 'Jakub Kunst',            nazione: 'CZE', auto: 'Hyundai i20 N Rally2',         team: 'Kowax DST Racing',                    categoria: 'ERC1/RC2' },
  { numero: 20, pilota: 'András Hadik',          copilota: 'István Juhász',          nazione: 'HUN', auto: 'Ford Fiesta Mk II Rally2',     team: 'B-A Promotion Kft.',                  categoria: 'ERC1/RC2' },
  { numero: 21, pilota: 'Dominik Stříteský',    copilota: 'Igor Bacigál',            nazione: 'CZE', auto: 'Škoda Fabia RS Rally2',        team: 'Auto Podbabská Škoda PSG ACCR Team', categoria: 'ERC1/RC2' },
  { numero: 22, pilota: 'Jan Solans',            copilota: 'Rodrigo Sanjuan',        nazione: 'ESP', auto: 'Toyota GR Yaris Rally2',       team: 'Team MRF Tyres',                      categoria: 'ERC1/RC2' },
  { numero: 23, pilota: 'Giandomenico Basso',    copilota: 'Lorenzo Granai',         nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Giandomenico Basso',                  categoria: 'ERC1/RC2' },
  { numero: 24, pilota: 'Andrea Crugnola',       copilota: 'Pietro Ometto',          nazione: 'ITA', auto: 'Citroën C3 Rally2',           team: 'F.P.F. Sport',                        categoria: 'ERC1/RC2' },
  { numero: 25, pilota: 'Bostjan Avbelj',        copilota: 'Elia De Guio',           nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Bostjan Avbelj',                      categoria: 'ERC1/RC2' },
  { numero: 26, pilota: 'Fabio Andolfi',         copilota: 'Marco Menchini',         nazione: 'ITA', auto: 'Toyota GR Yaris Rally2',       team: 'T-Racing Srl',                        categoria: 'ERC1/RC2' },
  { numero: 27, pilota: 'Marco Signor',          copilota: 'Daniele Michi',          nazione: 'ITA', auto: 'Toyota GR Yaris Rally2',       team: 'Marco Signor',                        categoria: 'ERC1/RC2' },
  { numero: 28, pilota: "Roberto Daprà",         copilota: 'Luca Guglielmetti',      nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: "Roberto Daprà",                       categoria: 'ERC1/RC2' },
  { numero: 29, pilota: 'Simone Campedelli',     copilota: 'Tania Canton',           nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Simone Campedelli',                   categoria: 'ERC1/RC2' },
  { numero: 30, pilota: 'Benjamin Korhola',      copilota: 'Kristian Temonen',       nazione: 'FIN', auto: 'Toyota GR Yaris Rally2',       team: 'Team MRF Tyres',                      categoria: 'ERC1/RC2' },
  { numero: 31, pilota: 'Antonio Rusce',         copilota: 'Gabriele Zanni',         nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Antonio Rusce',                       categoria: 'ERC1/RC2' },
  { numero: 32, pilota: 'Davide Porta',          copilota: 'Andrea Quistini',        nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Davide Porta',                        categoria: 'ERC1/RC2' },
  { numero: 33, pilota: 'Vittorio Ceccato',      copilota: 'Paolo Garavaldi',        nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Vittorio Ceccato',                    categoria: 'ERC1/RC2' },
  { numero: 34, pilota: 'Rachele Somaschini',    copilota: 'Giulia Zanchetta',       nazione: 'ITA', auto: 'Citroën C3 Rally2',           team: 'Rachele Somaschini',                  categoria: 'ERC1/RC2' },
  { numero: 35, pilota: 'Dariusz Biedrzyński',  copilota: 'Rafal Fiołek',            nazione: 'POL', auto: 'Hyundai i20 N Rally2',         team: 'Kowax DST Racing',                    categoria: 'ERC1/RC2' },
  { numero: 36, pilota: 'Jarosław Kołtun',      copilota: 'Ireneusz Pleskot',        nazione: 'POL', auto: 'Škoda Fabia RS Rally2',        team: 'J2X Rally Team',                      categoria: 'ERC1/RC2' },
  { numero: 37, pilota: 'Zoltan Laszlo',         copilota: 'György Kocsis',          nazione: 'HUN', auto: 'Škoda Fabia RS Rally2',        team: 'Topp-Cars Rally Team',                categoria: 'ERC1/RC2' },
  { numero: 38, pilota: 'Piotr Krotoszyński',   copilota: 'Marcin Szeja',            nazione: 'POL', auto: 'Škoda Fabia Evo Rally2',       team: 'Turán Motorsport',                    categoria: 'ERC1/RC2' },
  { numero: 39, pilota: 'David Tomek',           copilota: 'Vítězslav Baďura',       nazione: 'CZE', auto: 'Škoda Fabia Evo Rally2',       team: 'Top Trans Highway S.R.O.',            categoria: 'ERC1/RC2' },
  { numero: 40, pilota: 'Eamonn Boland',         copilota: 'MJ Whelan',              nazione: 'IRL', auto: 'Ford Fiesta Mk II Rally2',     team: 'Eamonn Boland',                       categoria: 'ERC1/RC2' },

  // ── ERC3 / RC3 / Rally3 ────────────────────────────────────────────────────
  { numero: 41, pilota: 'Tymek Abramowski',      copilota: 'Jakub Wróbel',           nazione: 'POL', auto: 'Ford Fiesta Rally3',           team: 'Tymek Abramowski',                    categoria: 'ERC3/RC3' },
  { numero: 42, pilota: 'Tristan Charpentier',   copilota: 'Florian Barral',         nazione: 'FRA', auto: 'Ford Fiesta Rally3',           team: 'Tristan Charpentier',                 categoria: 'ERC3/RC3' },
  { numero: 43, pilota: 'Igor Widłak',           copilota: 'Daniel Dymurski',        nazione: 'POL', auto: 'Ford Fiesta Rally3',           team: 'Grupa PGS RT',                        categoria: 'ERC3/RC3' },
  { numero: 44, pilota: 'Błażej Gazda',          copilota: 'Michał Jurgała',         nazione: 'POL', auto: 'Renault Clio Rally3',          team: 'Blazej Gazda',                        categoria: 'ERC3/RC3' },
  { numero: 45, pilota: 'Hubert Kowalczyk',      copilota: 'Jaroslaw Hryniuk',       nazione: 'POL', auto: 'Renault Clio Rally3',          team: 'Hubert Kowalczyk',                    categoria: 'ERC3/RC3' },
  { numero: 46, pilota: 'Adrian Rzeznik',        copilota: 'Kamil Kozdroń',          nazione: 'POL', auto: 'Ford Fiesta Rally3',           team: 'Adrian Rzeznik',                      categoria: 'ERC3/RC3' },
  { numero: 47, pilota: 'Casey Jay Coleman',     copilota: 'Killian McArdle',        nazione: 'IRL', auto: 'Ford Fiesta Rally3',           team: 'Casey Jay Coleman',                   categoria: 'ERC3/RC3' },
  { numero: 48, pilota: 'Martin Ravenščak',      copilota: 'Dora Ravenščak',         nazione: 'CRO', auto: 'Ford Fiesta Rally3',           team: 'Iksport Racing',                      categoria: 'ERC3/RC3' },
  { numero: 50, pilota: 'Sebastian Butyński',    copilota: 'Łukasz Jastrzębski',     nazione: 'POL', auto: 'Renault Clio Rally3',          team: 'Sebastian Butyński',                  categoria: 'ERC3/RC3' },
  { numero: 51, pilota: 'Adam Grahn',            copilota: 'Christoffer Bäck',       nazione: 'SWE', auto: 'Ford Fiesta Rally3',           team: 'Adam Grahn',                          categoria: 'ERC3/RC3' },
  { numero: 52, pilota: 'Taylor Gill',           copilota: 'Daniel Brkic',           nazione: 'AUS', auto: 'Ford Fiesta Rally3',           team: 'KMS Racing X VL',                     categoria: 'ERC3/RC3' },

  // ── ERC4 / RC4 / Rally4 ────────────────────────────────────────────────────
  { numero: 53, pilota: 'Calle Carlberg',        copilota: 'Jørgen Eriksen',         nazione: 'SWE', auto: 'Opel Corsa Rally4',            team: 'ADAC Opel Rally Junior Team',         categoria: 'ERC4/RC4' },
  { numero: 54, pilota: 'Ioan Lloyd',            copilota: 'Sion Williams',          nazione: 'GBR', auto: 'Peugeot 208 Rally4',           team: 'Ioan Lloyd',                          categoria: 'ERC4/RC4' },
  { numero: 55, pilota: 'Sergi Pérez',           copilota: 'Axel Coronado',          nazione: 'ESP', auto: 'Peugeot 208 Rally4',           team: 'Sec. Esp. RACC Motorsport',           categoria: 'ERC4/RC4' },
  { numero: 56, pilota: 'Jaspar Vaher',          copilota: 'Sander Pruul',           nazione: 'EST', auto: 'Lancia Ypsilon Rally4',        team: 'Team Estonia Autosport',              categoria: 'ERC4/RC4' },
  { numero: 57, pilota: 'Aoife Raftery',         copilota: 'Hannah McKillop',        nazione: 'IRL', auto: 'Peugeot 208 Rally4',           team: 'HRT Racing Kft.',                     categoria: 'ERC4/RC4' },
  { numero: 58, pilota: 'Tuukka Kauppinen',      copilota: 'Veli-Pekka Karttunen',   nazione: 'FIN', auto: 'Lancia Ypsilon Rally4',        team: 'Tuukka Kauppinen',                    categoria: 'ERC4/RC4' },
  { numero: 59, pilota: 'Keelan Grogan',         copilota: 'Ayrton Sherlock',        nazione: 'IRL', auto: 'Peugeot 208 Rally4',           team: 'Motorsport Ireland Rally Academy',    categoria: 'ERC4/RC4' },
  { numero: 70, pilota: 'Craig Rahill',          copilota: 'Conor Smith',            nazione: 'IRL', auto: 'Peugeot 208 Rally4',           team: 'Motorsport Ireland Rally Academy',    categoria: 'ERC4/RC4' },
  { numero: 71, pilota: 'Leevi Lassila',         copilota: 'Antti Linnaketo',        nazione: 'FIN', auto: 'Opel Corsa Rally4',            team: 'Iksport Racing',                      categoria: 'ERC4/RC4' },
  { numero: 72, pilota: 'Luca Pröglhöf',         copilota: 'Christina Ettel',        nazione: 'AUT', auto: 'Opel Corsa Rally4',            team: 'ADAC Opel Rally Junior Team',         categoria: 'ERC4/RC4' },
  { numero: 73, pilota: 'Tommaso Sandrin',       copilota: 'Andrea Dal Maso',        nazione: 'ITA', auto: 'Peugeot 208 Rally4',           team: 'Tommaso Sandrin',                     categoria: 'ERC4/RC4' },
  { numero: 74, pilota: 'Kevin Lempu',           copilota: 'Fredi Kostikov',         nazione: 'EST', auto: 'Ford Fiesta Rally4',           team: 'Team Estonia Autosport',              categoria: 'ERC4/RC4' },
  { numero: 75, pilota: 'Francesco Dei Ceci',    copilota: 'Nicolò Lazzarini',       nazione: 'ITA', auto: 'Peugeot 208 Rally4',           team: 'Francesco Dei Ceci',                  categoria: 'ERC4/RC4' },
  { numero: 76, pilota: 'Kevin Saraiva',         copilota: 'Beatriz Pinto',          nazione: 'POR', auto: 'Peugeot 208 Rally4',           team: 'Kevin Saraiva',                       categoria: 'ERC4/RC4' },
  { numero: 77, pilota: 'Yohan Surroca',         copilota: 'Pierre Blot',            nazione: 'SUI', auto: 'Peugeot 208 Rally4',           team: 'Yohan Surroca',                       categoria: 'ERC4/RC4' },
  { numero: 78, pilota: 'Davide Pesavento',      copilota: 'Alessandro Michelet',    nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Davide Pesavento',                    categoria: 'ERC4/RC4' },
  { numero: 79, pilota: 'Gianandrea Pisani',     copilota: 'Nicola Biagi',           nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Gianandrea Pisani',                   categoria: 'ERC4/RC4' },
  { numero: 80, pilota: 'Giorgio Cogni',         copilota: 'Daiana Darderi',         nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Giorgio Cogni',                       categoria: 'ERC4/RC4' },
  { numero: 81, pilota: 'Gabriel Di Pietro',     copilota: 'Andrea Dresti',          nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Gabriel Di Pietro',                   categoria: 'ERC4/RC4' },
  { numero: 82, pilota: 'Nicolò Ardizzone',      copilota: 'Valentina Pasini',       nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Nicolò Ardizzone',                    categoria: 'ERC4/RC4' },
  { numero: 83, pilota: 'Michael Rendina',       copilota: 'Alice Caprile',          nazione: 'ITA', auto: 'Renault Clio Rally4',          team: 'Motorsport Italia Spa',               categoria: 'ERC4/RC4' },
  { numero: 84, pilota: 'Federico Francia',      copilota: 'Chiara Lombardi',        nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Federico Francia',                    categoria: 'ERC4/RC4' },
  { numero: 85, pilota: 'Denis Vigliaturo',      copilota: 'Ermanno Corradini',      nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Denis Vigliaturo',                    categoria: 'ERC4/RC4' },
  { numero: 86, pilota: 'Michael Lengauer',      copilota: 'Jürgen Rausch',          nazione: 'AUT', auto: 'Lancia Ypsilon Rally4',        team: 'Michael Lengauer',                    categoria: 'ERC4/RC4' },
  { numero: 87, pilota: 'Andrea Mazzocchi',      copilota: 'Nicolò Gonella',         nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Andrea Mazzocchi',                    categoria: 'ERC4/RC4' },
  { numero: 88, pilota: 'Emanuele Fiore',        copilota: "Pietro D'Agostino",      nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Emanuele Fiore',                      categoria: 'ERC4/RC4' },
  { numero: 89, pilota: 'Emanuele Rosso',        copilota: 'Federico Capilli',       nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Emanuele Rosso',                      categoria: 'ERC4/RC4' },
  { numero: 90, pilota: 'Edoardo De Antoni',     copilota: 'Martina Musiari',        nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Edoardo De Antoni',                   categoria: 'ERC4/RC4' },
  { numero: 91, pilota: 'Dariusz Poloński',      copilota: 'Łukasz Sitek',           nazione: 'POL', auto: 'Lancia Ypsilon Rally4',        team: 'Dariusz Poloński',                    categoria: 'ERC4/RC4' },
  { numero: 92, pilota: 'Adam Sroka',            copilota: 'Paweł Pochroń',          nazione: 'POL', auto: 'Lancia Ypsilon Rally4',        team: 'Adam Sroka',                          categoria: 'ERC4/RC4' },
  { numero: 93, pilota: 'Mauro Porzia',          copilota: 'Arianna Genaro',         nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Mauro Porzia',                        categoria: 'ERC4/RC4' },
  { numero: 94, pilota: 'Giuseppe Piumatti',     copilota: 'Sonia Piumatti',         nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Giuseppe Piumatti',                   categoria: 'ERC4/RC4' },
  { numero: 96, pilota: 'Catherine Radulescu',   copilota: 'Bogdan Minea',           nazione: 'ROU', auto: 'Renault Clio Rally4',          team: 'Catherine Radulescu',                 categoria: 'ERC4/RC4' },

  // ── RC5 / Rally5 ──────────────────────────────────────────────────────────
  { numero: 95,  pilota: 'Ciprian Lupu',         copilota: 'Vlad Colceriu',          nazione: 'ROU', auto: 'Renault Clio RS Line',         team: 'Ciprian Lupu',                        categoria: 'RC5' },
  { numero: 114, pilota: 'Ludwig Zigliani',      copilota: 'Sara Montavoci',         nazione: 'ITA', auto: 'Renault Clio RS Line',         team: 'Ludwig Zigliani',                     categoria: 'RC5' },
  { numero: 115, pilota: 'Nazan Zorlu',          copilota: 'Ozhan Ciplak',           nazione: 'TUR', auto: 'Renault Clio RS Line',         team: 'Nazan Zorlu',                         categoria: 'RC5' },

  // ── RC2 nazionali ─────────────────────────────────────────────────────────
  { numero: 97,  pilota: 'Ivan Ferrarotti',      copilota: 'Fabio Grimaldi',         nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Ivan Ferrarotti',                     categoria: 'RC2' },
  { numero: 98,  pilota: 'Marco Pollara',        copilota: 'Giuseppe Princiotto',    nazione: 'ITA', auto: 'Škoda Fabia RS Rally2',        team: 'Marco Pollara',                       categoria: 'RC2' },
  { numero: 99,  pilota: 'Liberato Sulpizio',    copilota: 'Manuel Fenoli',          nazione: 'ITA', auto: 'Hyundai i20 N Rally2',         team: 'Liberato Sulpizio',                   categoria: 'RC2' },
  { numero: 100, pilota: 'Fabio Angelucci',      copilota: 'Massimo Cambria',        nazione: 'ITA', auto: 'Toyota GR Yaris Rally2',       team: 'Fabio Angelucci',                     categoria: 'RC2' },
  { numero: 101, pilota: 'Sara Carra',           copilota: 'Federica Mauri',         nazione: 'ITA', auto: 'Škoda Fabia Rally2',           team: 'Sara Carra',                          categoria: 'RC2' },
  { numero: 102, pilota: 'Andre Nucita',         copilota: 'Sergio Eguia',           nazione: 'ITA', auto: 'Citroën C3 Rally2',           team: 'DMAX Swiss',                          categoria: 'RC2' },
  { numero: 103, pilota: 'Thomas Pahlitzsch',    copilota: 'Stefan Grundmann',       nazione: 'GER', auto: 'Volkswagen Polo GTI Rally2',   team: 'Thomas Pahlitzsch',                   categoria: 'RC2' },
  { numero: 104, pilota: 'Cristian Milano',      copilota: 'Nicolò Cottellero',      nazione: 'ITA', auto: 'Škoda Fabia Rally2',           team: 'Cristian Milano',                     categoria: 'RC2' },

  // ── RC3 nazionali ─────────────────────────────────────────────────────────
  { numero: 106, pilota: 'Hsuan Lee',            copilota: 'Tsungyu Hsieh',          nazione: 'TPE', auto: 'Renault Clio Rally3',          team: 'Hsuan Lee',                           categoria: 'RC3' },

  // ── RC4 nazionali ─────────────────────────────────────────────────────────
  { numero: 107, pilota: 'Simone Di Giovanni',   copilota: 'Andrea Colapietro',      nazione: 'ITA', auto: 'Peugeot 208 Rally4',           team: 'Simone Di Giovanni',                  categoria: 'RC4' },
  { numero: 108, pilota: 'Daniele Campanaro',    copilota: 'Andrea Musolesi',        nazione: 'ITA', auto: 'Peugeot 208 Rally4',           team: 'Daniele Campanaro',                   categoria: 'RC4' },
  { numero: 109, pilota: 'Patrik Hallberg',      copilota: 'John Stigh',             nazione: 'SWE', auto: 'Peugeot 208 Rally4',           team: 'Patrik Hallberg',                     categoria: 'RC4' },
  { numero: 110, pilota: 'Tom Heindrichs',       copilota: 'Jonas Schmitz',          nazione: 'BEL', auto: 'Opel Corsa Rally4',            team: 'AMC Sankt Vith',                      categoria: 'RC4' },
  { numero: 111, pilota: 'Giovanni Ceccato',     copilota: 'Enrico Bracchi',         nazione: 'ITA', auto: 'Peugeot 208 Rally4',           team: 'Giovanni Ceccato',                    categoria: 'RC4' },
  { numero: 112, pilota: 'Pierluigi Maurino',    copilota: 'Samuele Perino',         nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Pierluigi Maurino',                   categoria: 'RC4' },
  { numero: 113, pilota: 'Asia Vidori',          copilota: 'Andrea Sarah Tardito',   nazione: 'ITA', auto: 'Lancia Ypsilon Rally4',        team: 'Asia Vidori',                         categoria: 'RC4' },

  // ── RGT / NAT ─────────────────────────────────────────────────────────────
  { numero: 105, pilota: 'Gianfranco Belletti',  copilota: 'Marco Del Torre',        nazione: 'ITA', auto: 'Abarth 124 Rally',             team: 'Officina Tome Srl',                   categoria: 'RGT' },
  { numero: 116, pilota: 'Roberto Gobbin',       copilota: 'Ismaele Barra',          nazione: 'ITA', auto: 'Abarth 124 Rally',             team: 'Roberto Gobbin',                      categoria: 'NAT' },
];

// ── Lookup rapido per numero di gara ─────────────────────────────────────────
const BY_NUMBER = Object.fromEntries(PARTECIPANTI_2025.map(p => [p.numero, p]));

/**
 * Cerca un partecipante per numero di gara.
 */
export function getByNumber(numero) {
  return BY_NUMBER[numero] || null;
}

/**
 * Cerca partecipanti per nome (pilota o copilota), case-insensitive.
 */
export function searchByName(query) {
  const q = query.toLowerCase()
    .replace(/[àáâãäå]/g, 'a').replace(/[èéêë]/g, 'e')
    .replace(/[ìíîï]/g, 'i').replace(/[òóôõö]/g, 'o').replace(/[ùúûü]/g, 'u');
  return PARTECIPANTI_2025.filter(p =>
    p.pilota.toLowerCase().includes(q) || p.copilota.toLowerCase().includes(q)
  );
}

/**
 * Contesto compatto per il Vision Agent (analisi foto).
 */
export function getPartecipantiContext() {
  const lines = PARTECIPANTI_2025.map(p =>
    `#${p.numero} ${p.pilota}/${p.copilota} (${p.nazione}) | ${p.auto} | ${p.team} | ${p.categoria}`
  );
  return `ISCRITTI RALLY DI ROMA CAPITALE 2025 (${PARTECIPANTI_2025.length} equipaggi):\n` + lines.join('\n');
}

/**
 * Contesto per domande chat su piloti/numeri specifici.
 */
export function getPilotiChatContext(query) {
  const q = query.toLowerCase();

  // Cerca per numero specifico
  const numMatch = q.match(/\b(\d{1,3})\b/);
  if (numMatch) {
    const p = getByNumber(parseInt(numMatch[1]));
    if (p) return `#${p.numero}: ${p.pilota} / ${p.copilota} (${p.nazione}) — ${p.auto} — Team: ${p.team} — Cat: ${p.categoria}`;
  }

  // Cerca per nome
  const trovati = searchByName(q);
  if (trovati.length > 0) {
    return trovati.map(p =>
      `#${p.numero} ${p.pilota} / ${p.copilota} (${p.nazione}) — ${p.auto} — ${p.team} [${p.categoria}]`
    ).join('\n');
  }

  // Lista ERC1 principali
  if (/piloti|equipaggi|iscritti|partecipanti|chi.*gareggia|chi.*corre|lista|startlist/.test(q)) {
    const top = PARTECIPANTI_2025.filter(p => p.categoria === 'ERC1/RC2').slice(0, 20);
    return `ERC1/RC2 top 2025:\n` + top.map(p => `#${p.numero} ${p.pilota} (${p.auto})`).join('\n');
  }

  return '';
}
