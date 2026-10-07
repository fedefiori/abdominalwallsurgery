// ============================================================================
// chirurgiadellaparete.it — MAPPA 301 per il Worker Cloudflare (06/10/2026)
// Da incollare nel worker di questo dominio (file di partenza in archivio hub:
// worker-chirurgiadellaparete.js.txt) PRIMA del cambio DNS, non dopo.
//
// Mappa completa delle 12 pagine del vecchio WordPress:
//   /                                                               -> / (200 diretto, stessa rotta)
//   /anatomia-della-parete-addominale-e-abdominal-core/             -> stessa rotta (200)
//   /difetti-della-parete-addominale-e-classificazione/             -> stessa rotta (200)
//   /sintomi-e-complicanze/                                         -> stessa rotta (200)
//   /radiologia/                                                    -> stessa rotta (200)
//   /preabilitazione-dei-pazienti-all-intervento-chirurgico/        -> stessa rotta (200)
//   /la-terapia-chirurgica/                                         -> stessa rotta (200)
//   /le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/ -> stessa rotta (200)
//   /le-complicanze-chirurgiche-la-vac-therapy/                     -> stessa rotta (200)
//   /contatti/                                                      -> stessa rotta (200)
//   /la-diastasi-dei-muscoli-retti/  -> https://www.diastasiedintorni.it/cose-una-diastasi/
//   /chi-sono/                       -> https://www.federicofiori.com/curriculum
//
// Le 10 rotte invariate NON vanno nel REDIRECTS: un 301 su se stesso sarebbe un
// loop; l'indirizzo risponde 200 col contenuto nuovo e il segnale si conserva.
// Nel REDIRECTS vanno solo le due uscite dal dominio e le normalizzazioni.
// ============================================================================

const REDIRECTS = {
  // Le due pagine che escono dal dominio di proposito (contratto hub 04/10/2026):
  // la diastasi e' del verticale dedicato, il curriculum e' dell'hub.
  '/la-diastasi-dei-muscoli-retti/': 'https://www.diastasiedintorni.it/cose-una-diastasi/',
  '/chi-sono/': 'https://www.federicofiori.com/curriculum',
  // Normalizzazioni di rete (gia' attese dal template Worker dell'hub):
  '/home': '/',
  '/home/': '/',
  // Articolo TESAR ritirato dal feed hub il 27/09/2026 (ritiro morbido):
  '/articoli/tecnica-tesar-riparazione-endoscopica-sublay-anteriore': '/articoli',
};

// ============================================================================
// CONTRATTO ORIGINE (deployment Emergent di questo sito)
// Il Worker del dominio vero instrada cosi' (pattern gia' in uso sugli altri 4 siti):
//   crawler UA (Googlebot, GPTBot, PerplexityBot, ...) -> GET
//     {ORIGIN}/api/seo/prerender?path=<path>&absolute=true   (HTML completo, 200)
//   /sitemap.xml -> {ORIGIN}/api/sitemap.xml   (text/xml, generato a ogni richiesta)
//   /robots.txt  -> {ORIGIN}/api/robots.txt    (allow-list 24 bot AI)
//   /llms.txt    -> {ORIGIN}/api/llms.txt
//   indirizzo inesistente -> 404 con HTML da
//     {ORIGIN}/api/seo/prerender?path=/404&absolute=true     (lo status 404 lo mette il Worker)
//   /api/*       -> passthrough al backend (form contatti, statistiche, feed pagine)
//   tutto il resto -> SPA statica (guscio React)
// La mappa redirect completa e sempre aggiornata (bare->slash incluse) e' servita
// in tempo reale da: {ORIGIN}/api/seo/routes  (JSON: paths + redirects + robots + sitemap)
// ============================================================================
