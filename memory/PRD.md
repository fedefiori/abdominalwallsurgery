# PRD — chirurgiadellaparete.it (verticale parete, rete federicofiori.com)

## Problem statement (originale, sintesi)
Costruire il verticale italiano sulla chirurgia della parete addominale (ernie, laparoceli, pre-abilitazione)
ereditando le 14 pagine del WordPress esistente senza perdere contenuti, seguendo il contratto di rete
collaudato su diastasiedintorni.it e diastasisandbeyond.com. La stessa app deve diventare il gemello
inglese (abdominalwallsurgery.com) cambiando SOLO SITE_KEY, SITE_LANG, SITE_DOMAIN.

## Architettura
- Backend FastAPI (`/app/backend/server.py` + `siteconfig.py` + `seo_render.py`):
  - contenuti pagine in JSON strutturati `/app/backend/data/pages/{slug}.json` (chiavi `it` compilate, `en` vuote=null);
  - sync articoli dall'hub `GET {HUB}/api/blog/syndication/{SITE_KEY}`: catalogo completo, upsert su groupId,
    sections sovrascritte, ritirati → redirect 301 verso /articoli (collezione `retired_redirects`); sync all'avvio + ogni ora;
  - sonda `GET /api/blog/posts/{lang}/{slug}` → 200 JSON `{"post": {...}}`;
  - `GET /api/seo/routes`, `/api/seo/prerender?path=&absolute=`, `/api/seo/sitemap.xml`, `/api/seo/robots.txt`, `/api/seo/llms.txt`;
  - `GET /api/stats/summary?days=30` protetto da `X-Network-Token` (o `?token=`), `POST /api/stats/track` (beacon, nessun dato personale: vid = hash giornaliero ip+ua);
  - `GET /api/media/{file}.webp` (49 immagini ricompresse ≤150KB, cache immutable).
- Frontend React (`/app/frontend/src`): SPA con le 14 rotte ereditate + `/articoli` + `/articoli/:slug` + `/404`.
  Crawler serviti dal Worker via prerender; il client imposta title/description/canonical/noindex.
  Design palette logo (nero/carbone + blu logo #3C83E1, distinta dal navy hub): tema scuro base + chiaro,
  font identici all'hub (Inter Tight titoli / Manrope corpo / Azeret Mono etichette), logo FP in header e
  favicon, aurora animata di sfondo, framer-motion, lenis, hero con masked line reveal, marquee,
  indice appiccicoso, grana, data-testid ovunque.
- DB MongoDB: `articles`, `pageviews`, `retired_redirects`.

## User personas
- Paziente/caregiver italiano che cerca informazioni cliniche su ernie/laparoceli.
- Crawler e motori generativi (AEO/GEO): prerender, JSON-LD, llms.txt, risposte dirette, FAQ.

## Requisiti core (statici, dal contratto)
14 URL identici con slash finale; articoli senza slash; canonical per regola; hreflang solo se il gemello esiste;
niente doppioni (punto 4 a-e); testo del chirurgo mai riscritto; immagini hub degli articoli usate così come sono;
robots.txt mai Disallow:/; noindex fuori dominio; stats di rete protette; llms.txt dai dati.

## Implementato (15/09/2026)
- Migrazione completa: 14 pagine, 18.248 parole estratte (contratto 18.251), 49/49 immagini webp con alt.
- Punto 4 applicato: diastasi ridotta a 268 parole con rimando primo link a diastasiedintorni.it;
  TESAR in sintesi 5 righe + link hub /tecnica-tesar; chi-sono senza congressi/titoli + rimando /curriculum;
  sintomi e classificazioni con plainBox dichiarativi e link hub; glossario hub linkato per gli acronimi.
- SEO: title 50-60 e description 150-160 su 14/14 pagine; JSON-LD per kind (MedicalWebPage, ProfilePage+Person
  con @id hub, MedicalBusiness con address/geo/openingHours, DefinedTermSet EHS, FAQPage, BreadcrumbList).
- Articoli: 3 articoli reali importati e serviti; canonical identico al catalogo; figure hub invariate.
- Collaudo completo in /app/memory/collaudo.md con output dei comandi.

## Backlog prioritizzato
- P0: Worker Cloudflare (legge i nostri endpoint SEO) + DNS finale — fuori da questa app, da fare col cliente.
- P0: secondo agente — compilare chiavi `en` nei JSON pagine per abdominalwallsurgery.com (meccanismo pronto:
  chiave vuota = pagina inesistente in quella lingua, niente URL/sitemap/hreflang).
- P1: video anatomia della parete in home (richiesto dall'utente; serve il file — ora c'è l'artwork SVG animato).
- P1: inviare il NETWORK_STATS_TOKEN al gestore dell'hub per l'aggregazione delle statistiche di rete.
- P2: redirect legacy aggiuntivi se emergono URL vecchi (infrastruttura `retired_redirects` già pronta).
- P2: validazione JSON-LD su validator.schema.org pagina per pagina in produzione.

## Prossimi task
1. Traduzione EN delle pagine (chiavi en) — una passata sola.
2. Asset video hero.
3. Aggancio Worker + go-live dominio.

## Figure generate con la ricetta hub (16/09/2026, notte)- Serie di 6 figure generate con gemini-3.1-flash-image-preview via EMERGENT_LLM_KEY
  (stile costante della ricetta hub, blu #0B81E1 su grigio acciaio, 1:1 o 4:3, <=150KB):
  strati-della-parete (home+anatomia), difetto-e-pressione (sintomi), piani-della-rete
  (protesi), vac-pressione-negativa (vac), gradini-preparazione (home+preabilitazione),
  respiro-diaframma (preabilitazione). Nessun testo/lettera nelle immagini (verificato a vista).
## Iterazione 19/09/2026 — fix bug utente (discendente "g" + maiuscole ereditate)
- H1 hero: la "g" di "Chirurgia" era clippata dal reveal (.mask-line overflow hidden): fix strutturale
  padding-bottom .12em + margin-bottom -.12em (spaziatura identica, discendenti interi).
- Maiuscole: h1 home e site_name ora "Chirurgia della parete addominale" (minuscolo normale);
  normalizzate le occorrenze generiche ereditate ("della Parete Addominale", "Core Addominale") in
  anatomia/sintomi; PRESERVATO il nome proprio "Unità Operativa di Chirurgia della Parete Addominale";
  FAQ home: "pagina Chi sono" -> "pagina Il dott. Fiori" (label nav aggiornata).
- Test: test_reports/iteration_8.json — entrambi i bug FIXED, 0 regressioni (palette/font congelati ok).

## Iterazione 19/09/2026 — COLLAUDO HUB (palette/font CONGELATI, solo struttura/SEO/tecnica)
- B1 JSON-LD nel DOM vivo: hook useJsonLd (Layout) -> GET /api/seo/jsonld?path= (server.py, stessi builder
  del prerender). Un solo script @graph per pagina: WebSite(+publisher), Person (@id autorevole hub
  /curriculum#federico-fiori, jobTitle=solo qualifica, hasOccupation=ruolo ASST con "dell'Unità",
  worksFor=#fi-multicare), MedicalClinic (#fi-multicare, geo verificate Nominatim 45.4645,9.1951) SOLO
  su /contatti/, MedicalWebPage (ABOUT_MAP per slug, primaryImageOfPage, lastReviewed=modified),
  FAQPage, BreadcrumbList; articoli: Article+publisher+isBasedOn (hubUrl vuoto nei 3 articoli: campo
  pronto, si popola quando l'hub lo fornisce).
- B2 FAQ: FaqView condiviso, risposte SEMPRE nel DOM, chiusura via CSS grid 0fr/1fr.
- B3 file reali in frontend/public: robots.txt (Sitemap -> /sitemap.xml), sitemap.xml (18 URL, www,
  barra sulle pagine, lastmod reali), llms.txt. Script rigenerabile: scripts/gen_static_seo.py.
- B4: 301 /slug -> /slug/ via middleware in craco.config.js (preview); produzione = Worker su
  /api/seo/routes. Link interni normalizzati con barra in tutti i JSON (scripts/collaudo19.py).
- B5: OG completi + twitter card ovunque (useSEO esteso + prerender og_meta); og-fallback.jpg (crema+
  logo+corallo) e og-home.jpg (poster hero) 1200x630 in public/og/.
- ALTI 7-14: hero/footer/AuthorBox con qualifica+ruolo e "dell'Unità"; card home h2->h3; firma+ultima
  revisione (rel=author, time datetime) sulle cliniche; blocco Fonti (link verificati: PMID 19495920,
  29330835, 37862616, 30807248, EHS, ISHAWS) su 5 pilastri; contatti riscritta (CTA tel/mailto,
  contactList lucide, Google Maps, via privacy-paragraph e mappa scura); video hero: muted via ref,
  mp4 134KB (era 1,86MB), source media min-width 768px; overflow 390px azzerato (halo/ticks off,
  aurora contenuta); safety net reduced-motion/no-JS.
- MEDI: nav una riga + dropdown Capitoli (9 voci, 12px); theme-color doppio light/dark; via riquadro WP
  in home + maiuscole normalizzate; nessun colore/font toccato (verificato in regressione).
- Test: test_reports/iteration_7.json — 100%, 0 bug. Note aperte: isBasedOn in attesa di hubUrl dall'hub.

## Iterazione 19/09/2026 — PALETTE VERSIONE 8 definitiva (scelta utente dai mockup numerati)
- PROCESSO: logo analizzato via PIL (#000000 69%, azzurro #9FBEE8 22%, medio #3675C8). Mockup numerati
  in /public/palette-v4.html (v1-v9 nei vari round). Scelta utente finale: VARIANTE 8 "Spezzato netto"
  (corallo acceso della v3 + home scura della v5 + azzurro del logo nei richiami).
- TOKEN V8: pagina carta #FBF4EF; hero/fasce/footer quasi-nero caldo #0C0A09 (testo #EDE4D8); striscia
  marquee CORALLO PIENO #E03E1A testo scuro; bottoni #C93412/#FFF3E8; link su chiaro #AE2F10; sezioni
  alternate bianco caldo #FFFDF8 / AZZURRO-GHIACCIO logo #E3EEFB / sabbia #F3E6DC; etichette/numeri:
  azzurro logo scuro #1B4F96 su chiaro, corallo #F5875A su scuro; link su scuro ghiaccio #9FBEE8.
  Dark: #0C0A09 fondo, accent #F5641F, link #FF9A66.
- HERO: fascia scura con video 3D dietro le scritte (opacity .5/.6, velo --deep, object-position 50% 16%),
  alone azzurro logo in deriva. Animazioni entrata a 0,4s (Reveal + MaskLines + hero). Fascia capitoli con
  bordi diagonali + texture che deriva. Numeri capitoli ghost corallo/ghiaccio alternati.
- IMMAGINI A FIANCO: Blocks.jsx ora affianca fino a 2 immagini per sezione (foto+schemi), lato alternato
  (min(46%,440px)). Libreria immagini usata al 97% (56/58); le 2 residue sono radiologiche, non forzate
  fuori contesto clinico. Pagine legali (privacy/cookie) senza immagini per scelta.
- Test: test_reports/iteration_6.json — 100%, 0 bug, contrasti AAA verificati, nessun overflow mobile,
  prerender SEO allineato ai token. Palette DEFINITIVA salvo nuova richiesta esplicita.

## Iterazione 19/09/2026 — PALETTE VERSIONE 3 "azzurro luminoso" (richiesta utente)
- V3: blu/azzurri CHIARI attinenti al logo ma mai navy-hub. Ghiaccio #F2F7FD, corpo ardesia #15293E,
  TITOLI IN COBALTO #0B4FBE (colore diverso dal corpo, ~7,9:1 AAA), accent #0B63E5, link #0A4CB0,
  fasce scure zaffiro #0D2E5E (più chiare del navy hub), rame #B4530A numeri/etichette, fasce alternate
  azzurro #E2EDFA e SABBIA #FAF3E9 ("spezzato": 4+ fondi diversi per pagina). Dark: notte #0A1826,
  titoli #8AB8F5, accent #5EA3F7.
- Motion/contrasti: fascia capitoli con BORDI DIAGONALI (clip-path polygon) + texture che deriva
  (pw-banddrift 70s, spenta con reduced-motion); aurora più presente su chiaro (opacity .8); video hero
  dietro le scritte (30%/44%); figure con entrata morbida allo scroll (animation-timeline: view(),
  progressive enhancement); testo affiancato a immagini più grandi (float alternati min(46%,440px)).
- Font: SEMPRE hub (Inter Tight/Manrope/Azeret Mono) — confermato di nuovo, non toccare.
- Storico versioni: v1 avorio/verde chirurgico/rame; v2 (superata) ghiaccio+Newsreader; v3 azzurro
  luminoso+cobalto (attuale). L'utente confronterà e deciderà.
- Test: test_reports/iteration_5.json — 100%, 0 bug, contrasti AAA verificati, prerender allineato.

## Iterazione 18/09/2026 — PALETTE VERSIONE 1 + font hub fissi + video hero come sfondo
- FONT: tornati DEFINITIVAMENTE a quelli dell'hub (Inter Tight / Manrope / Azeret Mono). Direttiva utente:
  "usa per tutte le versioni il font dell'hub, non cambiarlo mai più". Rimossi Newsreader/IBM Plex ovunque
  (index.css, index.html, seo_render.BASE_CSS).
- PALETTE VERSIONE 1 (di una serie numerata che l'utente valuterà): ZERO blu. Avorio caldo #F6F4EE, testo
  carbone caldo #201D18, verde chirurgico #0E6B52 / link #0A5240, fasce scure verde bottiglia #14332B
  (testo #EAF2ED, link #7FD4B4), rame #B4530A per numeri/etichette, fascia alternata sabbia #ECE8DD.
  Dark: #121A16 fondo, #1A241F superficie, accent #4FC49F. Contrasti AA verificati a runtime.
- VIDEO HERO: da riquadro laterale (tagliato) a SFONDO dell'hero home: .pw-hero-media absolute inset 0,
  object-position 50% 16% (in alto), dietro le scritte, opacity .30 light / .44 dark / .22 reduced-motion,
  velo ::after in gradiente --ink per la leggibilità. Rimosso il vecchio riquadro .pw-hero-portrait.
- Versionamento: le palette candidate si chiamano "Versione 1", "Versione 2"...; l'utente deciderà.
  Per una nuova versione: cambiare SOLO i token in :root e [data-theme="dark"] di index.css +
  BASE_CSS in seo_render.py + theme-color in index.html.
- Test: test_reports/iteration_4.json — 100%, 0 bug, 0 action items. Ex-404 media ora 200 stabili.

## Iterazione 18/09/2026 — INVERSIONE identità (specifica utente vincolante, misurata non stimata)
- PROBLEMA SOLLEVATO: sito troppo simile all'hub (entrambi scuri, stessi font). Diagnosi utente corretta:
  i valori precedenti erano stati scelti "a impressione". Ora palette SPECIFICA dell'utente, verificata
  con getComputedStyle.
- INVERSIONE: sito CHIARO di default (paper #F5F7FA) con fasce scure --deep #0B2C4A (capitoli home, box
  sintesi, footer). Dark theme solo come toggle: fondo #0E1A24 ardesia, accent #4FB0F5, signal #E08B4A.
- Palette storica: accent #0B81E1 (grafica/testo grande, 3,7:1), accent-ink #0A63AE (link/testo piccolo,
  5,7:1), signal #B4530A rame SOLO per numeri/etichette/dati. Variabili in UN SOLO punto: index.css
  (:root chiaro + [data-theme="dark"]). Allineato seo_render.BASE_CSS.
- Font NUOVI (via Inter Tight/Manrope/Azeret): Newsreader 600 titoli serif, IBM Plex Sans 400 18px/1.75
  corpo (max 68ch), IBM Plex Mono 500 11px uppercase .14em etichette. H1 clamp(2rem,4vw,3.25rem).
- Dettagli: filetto 3px accent su box sintesi; numeri sezioni mono in signal; tabelle th deep + zebra
  paper-2; immagini hairline 1px radius 10px; link SEMPRE sottolineati (offset 2px, hover ispessisce);
  focus-visible 2px accent + 2px offset.
- VIDEO HERO: /public/media/hero-loop-parete-addominale (.mp4 H.264 originale 1,9MB + .webm VP9 254KB
  transcodificato con imageio-ffmpeg + poster .webp). Doppia <source>: WebM per Chrome/Firefox, MP4 per
  Safari. Nel riquadro destro della hero home (sostituisce ritratto, che resta in /chi-sono/ e AuthorBox).
  NB: Chromium headless di Playwright NON decodifica H.264 → il WebM serve anche per i test.
- Verifiche: body #F5F7FA, h1 Newsreader, body IBM Plex Sans, 4 fondi distinti, zero Inter/Manrope nel
  CSS servito (gli 11 "Inter" trovati sono dell'overlay Emergent di preview, non del sito). Confronto
  screenshot hub (navy, sans gigante) vs sito (chiaro, serif, rame): inconfondibili.
- Test: test_reports/iteration_3.json — 100%, 0 bug. I 2 media 404 (gradini/strati) sono falsi positivi:
  rispondono 200 in modo consistente (verificato con curl ripetuti).

- Banca immagini: /app/backend/data/imagebank.json (titolo, soggetto, didascalia, alt, tag).
## Iterazione 18/09/2026 (richiesta utente: palette logo, logo integrato, fix testi)
- Palette DISTINTA dall'hub e attinente al logo FP (nero #000 / blu #3C83E1 / bianco): dark ink #0B0C0E
  (nero neutro, non navy), surface #14161A, band #10203A, band-light #22272E, accent #3C83E1; light theme
  ritarato (accent #2F6FC9). Secondo colore di alternazione: --silver #C3CCD6 (sostituisce il teal).
  Allineato anche seo_render.BASE_CSS. Logo analizzato via PIL dai colori esatti dell'allegato.
- Logo integrato: /app/backend/static/media/logo-chirurgia-della-parete.webp servito via /api/media;
  img 30px in header ([data-testid='brand-logo'], sostituisce il quadratino blu) + favicon
  /logo-chirurgia-della-parete.png (192px) in public/index.html; theme-color #0B0C0E.
- Testi: preabilitazione — "La corretta preparazione alla terapia chirurgica della parete addominale deve
  prevedere" (link interno preservato) e FAQ "ad un" → "a un"; siteconfig articles_title IT "Articoli di
  approfondimento" / EN "In-depth articles" (home: kicker "Dalla redazione" + h2 nuovo; /articoli/ H1+title).
- Test: test_reports/iteration_2.json — 100%, 0 errori console. I 2 media 404 segnalati erano transienti
  del restart: gradini-preparazione.webp e strati-della-parete.webp rispondono 200.

## Iterazione 18/09/2026 (richiesta utente: font hub, sfondi dinamici, chi-sono terza persona)
- Font pareggiati all'hub federicofiori.com (verificati dal bundle CSS hub): corpo Literata → Manrope
  400/500/600/700; Inter Tight e Azeret Mono confermati. Link Google Fonts in public/index.html aggiornato;
  fallback del prerender (seo_render.BASE_CSS) da Georgia serif a Manrope/sans. Body 16.5px.
- Sfondo dinamico discreto: componente Aurora (3 blob radiali blu/teal/acciaio, position fixed, deriva in
  loop 44-64s, opacity ridotta in light theme) + alone rinforzato nell'hero; tutto spento con
  prefers-reduced-motion. data-testid="bg-aurora".
- Sezioni alternate più distinte: ciclo trasparente/surface/blu profondo/acciaio chiaro (--band-light
  #303D4C dark, #E6ECF2 light — tolta la nuance crema fuori palette).
- Numerazioni colorate alternate: contatori a pillola per gli elenchi numerati (azure dispari / teal pari,
  --teal #35A89B) e numerali ghost dei capitoli home alternati azure/teal.
- /chi-sono/ riscritta in TERZA PERSONA (scelta utente): H1 "Il dott. Federico Fiori: profilo e chirurgia
  della parete addominale", H2-domande in terza persona, answer/meta aggiornati, tolte quantificazioni
  enfatiche ("centinaia di interventi", "originale"). Nav: "Chi sono" → "Il dott. Fiori". AuthorBox:
  "Dove ricevo" → "Dove riceve". Nessun testo autocelebrativo residuo (scansione su tutti i JSON).
- Test: test_reports/iteration_1.json — 100% backend/frontend, 0 bug, 0 errori console.
- NOTA preview URL valido: https://chirurgia-test.preview.emergentagent.com (da REACT_APP_BACKEND_URL).


## Iterazione 18/09/2026 (giro hub 3: punti 13-14)
- /chi-sono/ ritarghettizzata: "come opero" (title/H1/H2 come da hub, 705 parole, definizione
  ufficiale del Dottore, niente "chirurgo della parete" per la persona).
- AuthorBox (componente) su pagine cliniche e articoli + nel prerender; author/reviewedBy = @id hub;
  Person.jobTitle come lista [qualifica, ruolo].
- Design: corpo Literata, titoli Inter Tight + etichette Azeret Mono (hub); bande a contrasto
  maggiore; schemi a lato del testo alternati dx/sx; barra di progresso; micro-motion sulle figure.

## Iterazione 18/09/2026 (giro hub 2)
- Recapiti unificati (no tiscali; +39 02 76021568; info@fimulticare.it; info@federicofiori.com).
- Risposte dirette riscritte ovunque (mai uguali al corpo). Titoli in minuscolo di rete.
- Studio = nodo condiviso hub (clinicId federicofiori.com/contatti#fi-multicare; fallback finche
  /api/seo/entity non espone clinic/clinicId).
- Radiologia: via 2 diapositive lilla, frase sobria operatore-dipendente. Percentuali senza fonte
  riformulate in preabilitazione (elenco fonti da chiedere: 24% / 7% / 10-60%).
- Qualifica "Unità Operativa" ovunque. H2-domande completati (>=70% ovunque, di solito 100%).
- Articoli: blocco "Su questo sito" (3 link + indice); indice con sintesi 12-18 parole + link pagina.
- Diastasi 313 parole. Font: set concordato (Space Grotesk/Literata 18/1.75/IBM Plex Mono).
- Ritratto ufficiale in duotone acciaio (home + chi-sono). Sfondi a 4 superfici + 3 toni chiari.
- Bug risolto: crash Related su tuple (articoli).
- Figura sedi-dei-difetti (soggetto hub) generata e messa in apertura di /difetti-...-classificazione/.
- Hero home: ritratto del Dottore con titoli sotto — PROVVISORIO: usa l'immagine identita'
  ufficiale dell'hub (og-federico-fiori.jpg, card con testo); serve il file ritratto pulito
  dal Dottore (l'hub non espone un ritratto fotografico puro, solo foto congressi e la card og).
- chi-sono riscritta in TERZA PERSONA, tolto "Incarico di Alta Specializzazione" (superato
  dalla Struttura Semplice di cui e' responsabile). ~740 parole totali.
- Header: prima riga Home/Articoli/Chi sono/Contatti + striscia secondaria con tutti e 9 i
  contenuti (scrollabile su schermi stretti, nel burger menu su mobile).
- Sfondi: ciclo a 4 superfici (trasparente / surface / blu profondo / acciaio chiaro) con
  margini asimmetrici e filetti laterali alternati.
- Vecchie arte-* decorative cancellate (file e riferimenti); privacy e cookie SENZA immagini.
- Kicker home: "A cura del Dottor Federico Fiori" + riga titoli dall'entity hub (jobTitle + ASST).
- Sezioni contenuto con tre sfondi alternati (ink / surface / blu profondo #0E2A42),
  margini asimmetrici e filetti laterali alternati.

## Illustrazioni e ritmo visivo (16/09/2026, sera)
- 10 illustrazioni stilizzate generate in stile hub (blu notte + linee luminose su reticolo,
  webp 5-38KB) in /app/backend/static/media/arte-*.webp, inserite come blocchi schema con
  alt+didascalia in: home (2), sintomi, vac, preabilitazione, privacy, cookie.
  Generatore riproducibile: /app/scripts/make_art.py.
- Font dell'hub ripristinati su richiesta utente: Inter Tight / Manrope / Azeret Mono.
- Contenuti raggruppati in sezioni per h2 con sfondi alternati (trasparente / --surface /
  --band piu' chiara, radius 14px) in Blocks.jsx: ritmo dinamico senza cambiare il testo.

## Giro correzioni hub (16/09/2026) — CHIUSO
1. Guasto /articoli: causa = doppia rotta `/articoli` e `/articoli/` (react-router v7) + config non caricata; risolto e verificato in browser, 0 errori console su home/articoli/3 articoli a 1920 e 390.
2. Palette blu #0B81E1 su grigio acciaio (esatta da specifica), alone radiale con parallasse lento, niente campiture piene, un solo pulsante pieno per schermata. Font ripristinati Space Grotesk/Literata 18px/1.75/IBM Plex Mono.
3. Immagini FOTO (max 320px/200px mobile, cover, raggio 10px) vs SCHEMI (max 420px, contain), coppie a due colonne, didascalie, lightbox con Esc.
4. Footer a 4 blocchi (Chi opera / Dove riceve Fi Multicare / La rete senza abdominalwallsurgery.com / Legale) + disclaimer.
5. Fi Multicare: footer + sezione in /contatti/ con mappa statica + 3 FAQ + MedicalClinic JSON-LD una sola volta, Person workLocation/affiliation.
6. /chi-sono/ riscritto 736 parole con 5 H2-domande, foto, DOI/PMID.
7. Igiene testo (nbsp, corsivi, concatenazioni, accenti, Paziente, split paragrafi lunghi).
8. H2-domande su tutte le pagine cliniche; FAQ+FAQPage anche su home e contatti.
9. Link interni inline + blocco "Leggi anche" ovunque; articoli hub linkati dalle pagine affini.
10. routes.redirects pieno (13 slash-redirect + /home, /home/).
11. Tabelle EHS/protesi/radiologia con fonte DOI.
12. Home a 709 parole. 13. Diastasi 268 parole corpo, primo link a diastasiedintorni. 14. Cookie __emg_vid/__emg_sid in cookie+privacy.
Collaudo completo: /app/memory/collaudo.md.

## Design refresh (16/09/2026)
- Font dell'hub: Inter Tight (titoli), Manrope (testo), Azeret Mono (etichette).
- H1 home: "Chirurgia della Parete Addominale" (maiuscolo).
- DOPO il confronto varianti l'utente ha scelto la PALETTE ORIGINALE del contratto (rame #E4762C / grafite #070B0F / acciaio #7FA8C9): varianti ?v= rimosse, niente bande chiare.
- Grafica "profonda": reticolo tecnico fisso sul fondo, grana, spotlight radiale rame nell'hero, parola fantasma PARETE outline verticale, segni di taglio agli angoli, scanline animata sull'anatomia SVG, marquee pieno rame, banda capitoli con contorni topografici e numerali ghost outline 01-09 (hover = riempimento rame), testata delle pagine interne con cornice tecnica + barra rame + spotlight, 404 con numerale outline.
- Screenshot finali: /tmp/new_hero.png, new_chapters.png, new_pillar.png, new_mobile.png.

## Interventi contenuto 19/09/2026 (testo approvato utente) — CHIUSO, test iterazione_9 verde 32/32
- /chi-sono/ riscritta integralmente: H1 "Il dott. Federico Fiori: profilo e attività clinica",
  title "Dott. Federico Fiori - Chirurgia Generale e della parete | Milano", nuova meta description,
  "In sintesi" speakable, 5 H2, PMID 30807248 linkato (noopener, no nofollow), UNA sola menzione
  "approccio morfo-funzionale" come link hub; rimossa frase ambulatorio; "oltre trent'anni".
- Home: nuovo H2 "Perché la parete si valuta insieme alla forma dell'addome?" dopo
  "Come si arriva all'intervento?" e prima dei capitoli; titolo indice -> "I capitoli";
  FAQ "Dove si riceve?" -> "Dove riceve?"; FAQ allineate verbatim al testo pagina.
- /la-terapia-chirurgica/: nuovo H2 "La tecnica basta a definire il risultato?" prima delle FAQ
  (link hub approccio morfo-funzionale + MILA); corrette le 3 frasi corrotte dettate; FAQ verbatim;
  "Dottor" -> "dott." (Carrara, Costa, Manetti, Ramirez), discipline in minuscolo.
- Frasi corrotte trovate e corrette sulle altre pagine (stesso criterio ancora-su-parole-esistenti):
  difetti (2), le-complicanze (2). Report all'utente nel riepilogo.
- Immagini: gradini-preparazione.webp sostituita. Home -> chirurgo-sala-operatoria.webp;
  preabilitazione -> preabilitazione-parete.webp (entrambe AI Nano Banana, ricetta hub invariata,
  script /app/scripts/gen_two_images.py, registrate in imagebank.json).
- FAQ preabilitazione corrotte/troncate riscritte verbatim; "il paziente" -> "il Paziente".
- Curve banda capitoli piu' evidenti: .pw-band-deep::before stroke-opacity 0.07 -> 0.22, width 1.4
  (colori invariati). Menu: nav_about "Il dott. Federico Fiori". Kicker: "A cura del dott. Federico Fiori".
- llms.txt: riga /chi-sono/ aggiornata (automatica dai JSON) + identita' "dell'Unità" (replace in
  seo_render.llms_txt). ProfilePage: aggiunto lastReviewed. Sitemap lastmod: solo pagine toccate.
- H1 le-protesi: "chirurgia della parete" minuscolo (regola stile discipline).
- Nota nota: FAQ home "Dove riceve?" ha risposta contatti Fi Multicare non-verbatim dalla home
  (domanda mantenuta per richiesta esplicita utente).

## Rettifica /chi-sono/ (19/09/2026, sera) — CHIUSO
- H2 "Dove opera e dove riceve?": sostituiti i due paragrafi col testo utente — attivita'
  istituzionale ASST + attivita' libero-professionale presso Cliniche private in Milano;
  "Riceve appuntamento presso Fi Multicare..." (rimossi Capoturno/Trauma Leader).
- FAQ "Dove riceve il dott. Federico Fiori?" riallineata parola per parola al nuovo testo.

## Fix refuso + contatti gemelli (19/09/2026, sera 2) — CHIUSO
- /chi-sono/: "Riceve appuntamento" -> "Riceve su appuntamento" (blocco + FAQ).
- /contatti/: paragrafo studio allineato ("riceve su appuntamento presso Fi Multicare...") e
  aggiunto paragrafo con distinzione attivita' istituzionale ASST / libero-professionale presso
  Cliniche private in Milano (testo identico a /chi-sono/). FAQ riorganizzate:
  "Dove si trova lo studio e come si prenota?" (verbatim), "Dove opera il dott. Fiori?" (nuova,
  verbatim), documenti invariata. Voce related "Chi sono" -> "Il profilo del dott. Federico Fiori".

## Nuove regole maiuscole (19/09/2026, sera 3) — CHIUSO — REGOLE STILE PRECEDENTI SUPERATE
- L'utente ha SOSTITUITO la vecchia regola minuscole: da ora "Chirurgia della Parete addominale"
  (C e P maiuscole, addominale minuscolo), "Dott./Dottor" SEMPRE con iniziale maiuscola,
  "Chirurgia Generale" sempre maiuscolo. Valido su tutto il sito.
- Script di normalizzazione applicato a: data/pages/*.json, imagebank.json, seo_render.py,
  siteconfig.py, HomePage/Layout/AuthorBox.jsx. 117 occorrenze. Protetto il nome proprio
  "Unità Operativa di Chirurgia della Parete Addominale" (reparto, maiuscole ufficiali).
- Non toccati: hub_entity.json (cache hub), wp_pages_raw.json (dump), articoli sindacati dall'hub.
- FAQ verbatim re-verificate dopo la trasformazione: coerenza mantenuta su tutte le pagine.

## Rettifica maiuscole (19/09/2026, sera 4) — CHIUSO
- Correzione utente: la forma corretta e' "Chirurgia della Parete Addominale" (A maiuscola).
  33 occorrenze aggiornate. La shorthand "Chirurgia della Parete" resta con C/P maiuscole.
- REGOLE STILE VIGENTI (finali): "Chirurgia della Parete Addominale" / "Chirurgia della Parete"
  maiuscole; "Dott."/"Dottor" sempre maiuscolo; "Chirurgia Generale" sempre maiuscolo;
  uso anatomico "parete addominale" (es. "difetti della parete addominale") resta minuscolo;
  "Paziente" maiuscolo; nome reparto "Unità Operativa di Chirurgia della Parete Addominale".

## Giro 5 hub — 7 punti SEO/entita' (20/09/2026) — CHIUSO (18/18 rotte verificate)
1. @id centro: HUB_CLINIC_ID -> https://www.federicofiori.com/contatti#fi-multicare (fallback,
   worksFor, ogni riferimento). Cache hub_entity.json riallineata all'endpoint (deploy confermato).
2. Person: person_ld ora copia il nodo COSI' COM'E' dall'endpoint hub, cambia solo inLanguage.
   Rimossi override manuali (jobTitle/hasOccupation/worksFor/url e il branch contact). jobTitle
   ora e' la lista di due voci dell'hub. Rimossa costante HUB_HOSPITAL_ID inutilizzata.
3. llms.txt identita': qualifica + riga Incarico (dell'Unita') + riga Centro col nuovo @id.
4. Publisher: MedicalBusiness -> Organization, tolto medicalSpecialty, sameAs invariato.
5. Article: isBasedOn = URL articolo hub (/articoli/{slug}); cover .png -> .webp in clean_article
   (JSON-LD, og:image e frontend ereditano).
6. Firma in home: AuthorBox client (HomePage.jsx dopo FAQ) + prerender (esclusione 'home' rimossa).
7. Sitemap lastmod reali: diastasi 19/09 (link aggiunto), sintomi/radiologia/cookie 16/09
   (giro H2/FAQ/cookie), le altre gia' 19/09 per edit reali.
Extra: nodo Person (e WebSite nel prerender) aggiunto all'indice /articoli (mancava).

## Giro 6 hub — 2 rilievi (20/09/2026) — GIA' CHIUSI nel giro 5, dimostrato con output
- llms.txt: identita' e riga chi-sono risultavano vecchie al hub -> era una lettura in cache;
  l'output corrente e' gia' conforme (qualifica + Incarico + Centro; chi-sono col titolo nuovo;
  zero occorrenze "della Unita'"/titolo vecchio).
- Sitemap: le 5 pagine con lastmod 2023 erano gia' state riallineate (16/09 o 19/09);
  verificata coerenza lastmod = lastReviewed schema = data blocco firma (stesso campo modified).
- REGOLA RITIRATA dall'hub: "Dott."/"Chirurgia Generale"/"Chirurgia Plastica" maiuscoli sono
  la convenzione di rete (misurata su hub e diastasiedintorni.it): NON tornare mai indietro.

## Statistiche di rete (20/09/2026) — CHIUSO
- POST /api/stats/hit: sempre 202, filtro bot su user-agent (+ nessuna riga senza UA),
  scarta /api /admin /404 e percorsi con estensione; sid pseudonimo client (sessionStorage,
  TTL 30 min); ref classificato (diretto/interno/ricerca/social/AI/altri siti) e scartato;
  mai IP. Click tracciati con ev=click + label (contatti-telefono/email/whatsapp/menu/link
  via listener delegato). Una riga per pagina vista: guardia lastPath in lib/stats.js +
  timer 800ms con cleanup in StatsTracker (App.js). Vecchio /stats/track (hash IP) RIMOSSO,
  collection pageviews eliminata, Layout.jsx ripulito.
- GET /api/stats/summary?days=N: solo token di rete (X-Network-Token o ?token=), 401 altrimenti,
  rotta indipendente (nessuna area admin esiste). Campi esatti del contratto (site, days,
  from/to ISO con fuso, visits, people, prevVisits, prevPeople, today, pages top10, articles
  per slug hub, clicks con byLabel e contact=*, sources). Cache in memoria 5 min per il
  timeout di 8s dell'hub. Fix: datetime naive da pymongo normalizzati a UTC; classificatore
  per etichette di dominio (bug 't.co' vs 'chatgpt.com' risolto); 'interno' riconosce anche
  l'host di anteprima.
- NETWORK_STATS_TOKEN di rete in backend/.env (valore hub). stats_hits azzerata per il go-live.
- Collaudo: hit 202 / summary 401 senza token / 200 con token (header e query). Beacon
  verificato in browser reale: sid stabile, ref interno, titolo aggiornato, 1 hit per vista.

## Giro 7 hub — go-live readiness (26/09/2026) — CHIUSO
1. Meta robots host-dipendente (BLOCCANTE): CANONICAL_HOSTS in backend/.env
   (www.chirurgiadellaparete.it, chirurgiadellaparete.it). is_final_host legge la lista;
   host canonico -> "index, follow, max-snippet:-1, max-image-preview:large" esplicito
   (seo_render.robots_meta, usato da pagine/articoli/indice); ogni altro host -> noindex,nofollow.
   Lato client useSEO.js confronta location.hostname con la stessa coppia (canon + senza www).
2. Sitemap 2023: la causa erano file STATICI in frontend/public (sitemap.xml, llms.txt,
   robots.txt) che rispondevano al posto del backend. Eliminati; craco devServer ora proxia
   /sitemap.xml /robots.txt /llms.txt dal backend (in produzione ci pensa il Worker: MAI
   rimettere copie statiche in public/, finirebbero nel build di produzione stantie).
3. 404 veri: middleware craco "seo-files-and-real-404": percorsi sconosciuti (GET html/HEAD)
   -> 404 con guscio app; rotte note da /api/seo/routes (cache 60s) + /articoli/* + /404.
4. llms.txt: come punto 2, ora la root serve la versione viva (dell'Unita').
5. ProfilePage: dateModified/dateCreated come data-ora ISO con fuso Roma (rome_dt,
   ZoneInfo Europe/Rome); chi-sono.json ha "created": "2024-09-25T16:17:02" (data WP originale).

## Giro 8 hub — bloccanti A e B (26/09/2026) — CHIUSO
A. is_final_host ora legge PRIMA X-Forwarded-Host poi Host (ordine hub). Verificato:
   origine diretta con XFH canonico -> index, follow, max-snippet:-1, max-image-preview:large.
   PROVA INFRASTRUTTURA: la catena di anteprima Emergent (CF worker preview) SOVRASCRIVE
   X-Forwarded-Host con l'host di anteprima (probe sugli header in arrivo). Quindi via URL di
   anteprima il collaudo XFH mostra sempre noindex: e' la piattaforma, non l'app. In produzione
   il Worker della rete chiama l'origine con Host canonico e la catena lo propaga (come gia'
   per diastasiedintorni.it). Tutta l'HTML server-side passa da seo_prerender: regola unica.
B. Nuove rotte /api/robots.txt, /api/sitemap.xml, /api/llms.txt (doppio decorator con /seo/),
   metodi GET+HEAD espliciti (Starlette qui non auto-aggiunge HEAD: era il 405 misurato).
   Proxy craco alla radice ora gestisce anche HEAD con content-type giusto (text/plain x2,
   application/xml). Collaudo: 6/6 HEAD 200 con content-type corretti, corpi GET corretti.

## Giro 9 hub — disegno definitivo robots prerender (26/09/2026) — CHIUSO
- Convenuto con l'hub: /api/seo/prerender con absolute=true emette SEMPRE
  "index, follow, max-snippet:-1, max-image-preview:large" senza guardare intestazioni
  (quel percorso e' solo per il Worker dei crawler; le intestazioni possono essere
  riscritte dalla catena). La logica host resta sul rendering diretto (senza absolute)
  e lato client (useSEO.js): anteprime noindex. Canonical invariato sul dominio vero.
- Verificato: absolute=true -> index su home/chi-sono/articolo anche via anteprima;
  senza absolute -> noindex; DOM browser anteprima -> noindex.
- IN ATTESA: l'indirizzo origine *.emergent.host (Manage deployment -> Domain) serve
  all'hub per la variabile ORIGIN del Worker Cloudflare. Non leggibile da qui: compare
  nella scheda Domain dopo/alla prima pubblicazione. Il Dottore puo' copiarlo da li',
  oppure si preme Deploy e lo si legge subito dopo.

## Contatti "le due porte" (27/09/2026) — CONSEGNATO, con nota per l'hub sul provider
- Backend POST /api/contact: reason appuntamento->info@federicofiori.com / dottore->
  fedefiori@federicofiori.com (fallback appuntamento su reason mancante/inventato);
  salvataggio SEMPRE su db.contact_requests (con subject e notifyTo) prima dell'invio;
  oggetto "[Motivo] Nome — dal sito"; Reply-To = mittente (contact_email); honeypot
  anti-bot silenzioso; guardrail gate email del playbook integrato.
- Env: EMERGENT_EMAIL_KEY, EMAIL_FROM_NAME (Chirurgia della Parete Addominale - Dott.
  Federico Fiori), CONTACT_NOTIFY_EMAIL, CONTACT_DIRECT_EMAIL in backend/.env.
  MAIL_FROM NON configurabile: il From e' fissato dalla piattaforma (proxy gestito).
- NOTA CRITICA PER L'HUB: il proxy email della piattaforma RIFIUTA i due recapiti di
  rete ("undeliverable_recipient", 422): federicofiori.com ha MX self-hosted
  (mx.federicofiori.com) che non supera la verifica del provider. Pipeline OK
  (delivered@resend.dev -> 202). Un invio a fedefiori@ e' passato una volta (202),
  poi sempre 422: inaffidabile. Le richieste NON si perdono (DB), ma la notifica email
  richiede intervento lato hub/piattaforma (whitelist destinatari o setup del gemello).
- Frontend: ContactForm.jsx su /contatti/ (telefono primo sopra il modulo, due radio
  con nota che cambia, honeypot, conferma che ripete la nota, riga mailto diretta
  sempre visibile). Footer Layout: due righe etichetta+mailto + telefono nella colonna
  Chi opera. Prerender: stesse due righe + telefono nel footer di ogni pagina.
- contactPoint MedicalClinic: copia da entity.contactPoints se presente; l'endpoint hub
  oggi NON espone il campo (null) -> segnalato; appena pubblicato, basta un restart.
- robots.txt: Sitemap ora punta alla radice /sitemap.xml. emmagadda5@gmail.com: 0 occorrenze.

## Figure laterali piene in home (27/09/2026) — CHIUSO
- Richiesta: niente banda vuota a destra del testo; le figure la occupano.
- Blocks.jsx: prop wideFigures (solo home). Le sezioni che contengono una figura
  prendono classe pw-sect--wide: la banda si allarga a tutto lo shell
  (width: min(1200px,100vw) - 96px), il testo resta su 68ch e TUTTE le figure
  dentro le sezioni wide flottano a DESTRA a filo del bordo (clamp 380-500px).
  Pagine pilastro INVARIATE (hanno la TOC: li' il float resta nella colonna).
- Nuova figura AI "approccio-morfofunzionale.webp" (struttura+silhouette fuse,
  ricetta hub invariata) nel blocco "Perche' la parete si valuta insieme alla forma
  dell'addome?" in home; registrata in imagebank.json.
- Verificato: niente overflow a 390/1366/1920; mobile impila figura sopra il testo;
  chi-sono e pilastro intatti. Colori/font mai toccati (solo larghezze/margini).

## Giro 10 hub — cura 422 email + contactPoints + layout antivuoto (27/09/2026) — CHIUSO
- EMAIL: rimosso il proxy gestito della piattaforma (EMERGENT_EMAIL_KEY eliminata da .env);
  invio diretto Resend con la chiave del Dottore (RESEND_API_KEY, dominio federicofiori.com
  verificato nel suo account) e MAIL_FROM=info@federicofiori.com. From = "EMAIL_FROM_NAME
  <info@federicofiori.com>", Reply-To = chi ha scritto. Guardrail _assert_safe_email e
  salvataggio DB prima dell'invio INVARIATI. Collaudo: 2 invii REALI marcati TEST, entrambi
  Resend 200 OK con id (appuntamento 01a0e4ee-199b-7423-a66a-40f252d0946f,
  dottore 01a0e4ee-1a3d-76df-a4a7-0c6820aac94e).
- CONTACTPOINTS: l'hub ora espone entity.contactPoints (3 voci); cache hub_entity.json
  aggiornata al riavvio; CLINIC_FALLBACK rimosso da seo_render.py — unica fonte di rete =
  endpoint hub. I 3 contactPoint del nodo MedicalClinic su /contatti/ combaciano 1:1 con
  l'hub (diff stringa verificato) sia in /api/seo/jsonld sia nel prerender.
- LAYOUT ANTIVUOTO (richiesta utente, palette/font mai toccati): Blocks.jsx — la prima
  figura della sezione fluttua dall'ALTO e il testo la avvolge; la seconda figura fluttua
  nella sua posizione naturale SOLO se la sezione ha >1100 caratteri (fix del testo
  strozzato fra due immagini); foto singole inline a tutta colonna (pw-img-solo, cover,
  max 440px); figure laterali min(48%,470px) cover 4/3.1; home wide clamp(400px,40%,540px)
  4/3.4. Sezioni SENZA figure su pagine cliniche/home/chi-sono: illustrazione della pagina
  come fondo sfumato sul lato libero (pw-sect--bg, velo a scomparsa verso il testo,
  opacity .13 light / .18 dark) oppure cornice tecnica con angoli (pw-sect--framed) se la
  pagina non ha schemi (chi-sono: 5 cornici). Legali e contatti ESCLUSE dalle decorazioni.
- Honeypot contatti: aggiunto name="company" (trappola piu' efficace per bot da form).
- test_credentials.md riallineato al NETWORK_STATS_TOKEN reale di backend/.env.
- Test: test_reports/iteration_10.json — 16/16 pytest backend + 12 pagine frontend
  (1366/375, entrambi i temi), 0 bug, 0 errori console. File: backend/tests/test_iteration10.py.

## Rettifica etichette chi-sono (27/09/2026, sera) — CHIUSO
- Voce di menu nav_about IT: "Il Dott. Federico Fiori" -> "Dott. F. Fiori" (resta su una riga).
- H1 /chi-sono/: "Il Dott. Federico Fiori: profilo e attività clinica" -> "Dott. Federico Fiori:
  profilo e attività clinica" (senza "Il"). Breadcrumb, llms.txt e JSON-LD seguono l'h1 in
  automatico; metaTitle invariato. modified -> 2026-09-27T16:00:00 (lastmod sitemap reale).
- Verificato: API /api/pages/chi-sono e /api/site aggiornate; screenshot header+pagehead ok.

## Prerender /404 per il Worker (27/09/2026, sera 2) — CHIUSO
- Rilievo hub: /api/seo/prerender?path=/404 rispondeva 404 JSON; il Worker non aveva
  l'HTML della pagina 404 e ripiegava sul guscio della home.
- seo_render.prerender_404(site): HTML completo della 404 (title "404 — Pagina non
  trovata", H1 proprio, testo e CTA dalle stringhe ui, canonical su /404, OG completi,
  meta robots SEMPRE noindex,nofollow, JSON-LD minimale WebPage+WebSite, footer di rete).
- server.py: seo_prerender intercetta path /404 (anche /404/) prima del lookup e la
  consegna con 200 text/html — il codice 404 lo mette il Worker sull'indirizzo vero.
- Nota per l'hub: /api/seo/404 non e' mai esistito come rotta — il JSON visto era il
  404 generico FastAPI dei percorsi API sconosciuti; niente da rimuovere.
- Verificato: /404 -> 200 text/html (con e senza absolute), home e chi-sono 200,
  slug inesistente resta 404, /api/seo/routes elenca ancora /404.

## Pagina /video/ (28/09/2026, contratto hub) — CHIUSO
- Nuova pagina data/pages/video.json (kind "video", en=null): H1 "Video", risposta diretta e
  avviso contenuti verbatim hub, 3 gruppi H2 (reti/tecniche mininvasive/dopo l'intervento),
  9 video YouTube con didascalia di una riga + link interno (protesi/terapia/sintomi),
  chiusura con 2 link esterni (hub /video + canale @federicofiori2383, _blank noopener,
  MAI nofollow). Titoli iframe = titoli reali YouTube (oEmbed).
- REGOLA ZERO: nessun VideoObject, nessun ItemList di video su questo sito (verificato su
  TUTTE le pagine prerender + jsonld). Schema pagina = solito grafo (MedicalWebPage +
  BreadcrumbList + WebSite/Org/Person, isPartOf sito; about=MedicalProcedure parete).
- CARICAMENTO AL CLIC: Blocks.jsx VideoEmbed — all'apertura solo copertina i.ytimg.com
  (hqdefault) + pulsante play in palette + alt descrittivo; iframe creato SOLO al clic verso
  youtube-nocookie.com/embed con title, loading=lazy, allowfullscreen, NO autoplay.
  Verificato in browser con tracciamento richieste: 0 chiamate youtube.com prima del clic.
- PRERENDER: render_blocks caso 'video' -> figura con LINK youtube.com/watch + copertina
  img + didascalia + link interno (i crawler non cliccano). Nuovo menu_html(): il menu
  principale (Home/Articoli/Video/Dott. F. Fiori/Contatti, voci pagina solo se esistenti
  nella lingua) ora e' presente nel prerender di TUTTE le pagine (pagine, articoli,
  indice, 404) — prima non c'era alcun menu nel crawler HTML.
- Menu sito: voce "Video" dopo "Articoli" (Layout mainNav, desktop+mobile), condizionata a
  site.hasVideo (nuovo flag di /api/site). Fix di conseguenza: .pw-nav a white-space
  nowrap + gap fluido — il menu resta su UNA riga fino a 981px.
- Cookie policy: riga YouTube caricamento-al-clic nella sezione Esperienza (contenuti
  terze parti), verbatim hub. modified -> 2026-09-27 (sitemap reale).
- AuthorBox escluso su kind video (pagina curata ma struttura hub minimale). Decorate
  (sfondi sfumati/cornici) disattivate sulla pagina video (i video sono gia' i media).
- Sitemap: /video/ con lastmod 2026-09-27; routes: /video/ + redirect /video -> /video/.
- Collaudo: batteria backend 7/7 verde (API, routes, sitemap, prerender completo, zero
  VideoObject ovunque, menu in prerender x4, riga cookie) + browser (9 video/9 didascalie/
  9 link, clic -> nocookie, overflow 375=0, nav una riga 981-1366).

## Fix foto che coprono il testo + test palette azzurra (28/09/2026) — CHIUSO
- BUG segnalato dall'utente: nella pagina terapia chirurgica le figure laterali coprivano
  l'inizio delle righe di testo. Causa: le regole float `.pw-fig-side-* img` avevano la
  stessa specificita' di `.pw-img-photo img`/`.pw-img-schema img` (0,1,1) ma compaiono
  prima nel foglio -> vincevano max-width 560px/width:auto e l'immagine debordava dal
  float sul testo (visibile solo coi float a sinistra; a destra debordava verso il bordo).
- FIX: selettori float portati a specificita' (0,2,1) con prefisso .pw-content +
  max-width:100%. Verificato: 0 figure debordanti (controllo geometrico), testo sempre
  avvolto e leggibile, home wide invariata (regola (0,3,1) gia' vincente).
- TEST PALETTE (richiesta utente, NESSUN file modificato): simulazione runtime via
  add_style_tag — arancio corallo -> azzurro logo (--accent #3C83E1, --accent-soft
  #9FBEE8, --accent-btn #3675C8, --accent-ink #1B4F96, --signal-on-deep #9FBEE8) e scritte
  su azzurro bianche (marquee, bottoni solidi, pulsanti play). Screenshot prodotti:
  /tmp/azzurro_1_hero_v2.png, azzurro_2_sezioni.png, azzurro_3_video.png,
  azzurro_4_capitoli.png. NON coperti dalla simulazione: tema scuro (token [data-theme=dark]
  con arancio #F5641F) e le immagini OG statiche (og-fallback/og-home hanno corallo).
  Decisione utente in sospeso: se adottata, applicare i 5 token in index.css + BASE_CSS
  di seo_render.py + valutare rigenerazione OG.

## PALETTE VERSIONE 9 "Azzurro logo" DEFINITIVA (28/09/2026, scelta utente) — CHIUSO
- L'utente ha visto la simulazione runtime e ha scelto: l'arancio corallo esce di scena,
  sostituito ovunque dall'azzurro del logo. Token :root: --accent #3C83E1, --accent-soft
  #9FBEE8, --accent-btn #3675C8 (AA con bianco, ~4,6:1), --accent-ink #1B4F96 (~7:1),
  --signal-on-deep #9FBEE8. Tema SCURO incluso: --accent #3C83E1, --accent-soft/--signal/
  --accent-ink #9FBEE8, --accent-btn #3675C8. Sfondi INVARIATI (carta/ghiaccio/sabbia/
  quasi-nero caldo). Scritte su azzurro SEMPRE bianche: #FFF3E8 e #140B06 -> #FFFFFF
  (bottoni solidi, CTA contatti, pulsanti play video, striscia marquee e suoi punti).
- Allineato BASE_CSS di seo_render.py (prerender crawler). Immagini OG rigenerate con
  sostituzione cromatica PIL corallo->azzurro (og-fallback 23.953 px, og-home 989 px).
- LOGO piu' grande e leggibile: header 30px -> 46px (38px mobile), blocco brand con nome
  sopra "Dott. Federico Fiori" (colonna, nowrap); a <=480px nome 14px (altrimenti
  overflow 13px). Attributi width/height img aggiornati in Layout.jsx.
- Verifiche: token computed light/dark corretti, nav su UNA riga (38px a 1366),
  overflow 0 a 375/768/1366, hero/marquee/sezioni/video/dark a video tutti azzurri.
- REGOLA AGGIORNATA: la palette V9 azzurro-logo e' la DEFINITIVA (sostituisce V8).

## Logo orizzontale leggibile in header (28/09/2026) — CHIUSO
- Richiesta: "logo piu' grande, deve leggersi chirurgia della parete". La scritta nel logo
  quadrato e' il 3,5% dell'altezza immagine: nessun ingrandimento del chip l'avrebbe mai
  resa leggibile. Soluzione: lockup orizzontale composto con PIL dai PIXEL ORIGINALI del
  marchio (nessun ridisegno): monogramma FP a sinistra + banda testo ritagliata e divisa
  "CHIRURGIA" / "DELLA PARETE" su due righe (taglio agli spazi misurati x268/370),
  scalata 5,4x LANCZOS. File nuovo: static/media/logo-chirurgia-della-parete-orizz.webp
  (1723x600, 2,87:1, 16,5KB). Il quadrato originale resta per favicon/OG.
- Header: img lockup 60px desktop / 44px mobile; rimossa la scritta HTML duplicata del nome
  sito (ora la porta il logo); resta il sub "DOTT. FEDERICO FIORI" accanto; alt completo.
- Verifiche: scritta leggibile a 1366/768/375 (zoom di controllo), nav una riga (38px),
  overflow 0 ovunque.

## Layout fluido multi-schermo (30/09/2026, richiesta utente "15 pollici con molto spazio") — CHIUSO
- Radice tipografica fluida: html font-size clamp(16px, 0.45vw + 10px, 19px) — scala TUTTI
  i rem del sito (16px a <=1366, 17,2px a 1600, 18,6px a 1920, cap 19px). Body 18px ->
  1.125rem (18px a 1366 -> ~21px a 1920). Mobile invariato (16px).
- Contenitore fluido: --shell-w clamp(1200px, 82vw, 1520px) su .pw-shell e .pw-sect--wide
  (prima 1200px fisso). Figure laterali min(48%,540px) (era 470), home wide
  clamp(420px,40%,620px). Blocchi FAQ/firma home 820px -> 980px.
- Colori/font MAI toccati: solo dimensioni. Verificato: 7 pagine x 4 viewport
  (1920/1366/768/375) = 28 combinazioni, overflow SEMPRE 0, nessun arancio residuo
  (light+dark), menu una riga 981-1920, video click-to-play nocookie, TOC sticky,
  lightbox, form contatti. Test: test_reports/iteration_11.json — 100% frontend.
- Nota: warning React 'unique key prop' segnalato dal tester NON riproducibile
  (console pulita su home/articoli/terapia/video/chi-sono); tutte le .map hanno key.

## Correzioni pre-pubblicazione dall'hub (04/10/2026, audit di rete) — CHIUSO
- ROTTE RITIRATE (decisione hub, supera il contratto di settembre): /chi-sono/ e
  /la-diastasi-dei-muscoli-retti/ NON esistono piu' sul sito. JSON spostati in
  data/pages/_archivio/ (contenuto conservato). 301 esterni registrati in
  retired_redirects (letti dal Worker via /api/seo/routes): /chi-sono/ ->
  federicofiori.com/curriculum, /la-diastasi-dei-muscoli-retti/ ->
  diastasiedintorni.it/cose-una-diastasi/. Menu «Dott. F. Fiori» ora punta al curriculum
  canonico (link esterno nel mainNav, desktop+mobile). Tolte da KNOWN_SLUGS e nav_pages.
  Link interni aggiornati (home related, contatti related + inline).
- DICITURA RUOLO canonica carattere per carattere (senza "PO San Carlo Borromeo"): hero
  home, AuthorBox, firma prerender, llms.txt. Il worksFor del nodo Person hub contiene
  ancora "PO San Carlo Borromeo": e' il nome della Divisione copiato verbatim (regola di
  rete), NON la dicitura del ruolo. Telefono display ovunque "+39 02 7602 1568".
  NOTA PER L'HUB: l'endpoint /api/seo/entity espone il telefono come "+39 02 76021568"
  (senza spazio): i contactPoint si copiano verbatim da li' — allineare l'hub se serve.
- og:description <=125 con taglio a confine di frase (seo_render.og_description +
  useSEO.js): le description restano 150-160, le og corte. Verificato su tutte le pagine.
- Prerender: menu ora dentro <header><nav> (contratto: i bot devono vedere la
  navigazione). robots.txt: allow-list completa copiata da diastasisandbeyond.com
  (24 UA AI/motori) + Disallow solo /api/stats/ + llms.txt annunciato alla radice.
- Bug trovato e corretto: il guscio 404 del dev-server serviva public/index.html SENZA
  il bundle -> pagina bianca in anteprima su rotte sconosciute. Ora inietta
  /static/js/bundle.js: /chi-sono/ e indirizzi inventati mostrano la 404 del sito.
- Verifiche: batteria completa su tutte le pagine servite (0 tiscali/0240222182;
  dicitura ok; og<=125 decodificate; header>nav+robots+canonical+JSON-LD valido x3
  pagine; 0 hreflang verso abdominalwallsurgery; sitemap 16 URL senza le ritirate;
  llms aggiornato). DOI/PMID: tutti risolvono (Handle API 200; i 403 erano bot-block
  degli editori). pytest 15/15 (test chi-sono rimosso dalla regressione).
- APERTO (decisione del Dottore, segnalata non eseguita): H1 home = nome del sito
  ("Chirurgia della Parete Addominale") — coincide con l'argomento esatto del verticale;
  la regola hub vieta H1=nome sito. In attesa di parere.

## Deploy — tentativi e stato (06/10/2026)
- Health check deploy: PASS dopo correzione blocker (sync_articles: mai piu' delete al
  boot — feed giu'/vuoto = sync saltato; articoli ritirati = flag morbido 'retired',
  filtrato da tutte le letture; riammissione automatica se tornano nel feed).
- Tentativo 1 FALLITO in build_image: craco.config.js leggeva /app/backend/data/pages a
  build-time (ENOENT nel contesto Docker solo-frontend). Fix: try/catch con fallback
  ['/home'] (middleware slash-301 e' solo per l'anteprima). yarn build locale: OK 33s.
- Tentativo 2: in coda (job 22fdafad-ddf5-4386-b2ca-ee9bc6c3d2bf), esito in attesa.
- Utente ha confermato i 50 ECU del primo deploy. Promemoria go-live dominio vero:
  Worker con mappa 301 -> DNS -> collaudo 12 redirect -> Search Console/Bing.
  NON spegnere Aruba finche' i 301 non sono collaudati e le pagine indicizzate.

## DEPLOY COMPLETATO (06/10/2026)
- Produzione live: https://chirurgia-test.emergent.host (tutti i passaggi verdi nel pannello).
- Collaudo su produzione: home /video/ /contatti/ /la-terapia-chirurgica/ -> 200;
  prerender con robots index,follow + nav in <header> + canonical self + dicitura
  canonica; sitemap 200; /api/seo/routes con i 2 redirect 301 esterni (copia DB ok);
  validazione contatti 400 su payload invalido. Nessuna email reale inviata nei test.
- Il dominio vero chirurgiadellaparete.it NON e' ancora attivo: serve il passo hub
  (Worker + mappa 301 + DNS). Aruba resta acceso finche' i 301 non sono collaudati.

## Pacchetto go-live consegnato (07/10/2026)
- /app/scripts/worker-301-map.js: mappa REDIRECTS pronta da incollare nel Worker
  (2 uscite dal dominio + /home + articolo TESAR ritirato) + contratto origine per il
  Worker (prerender crawler, /sitemap.xml /robots.txt /llms.txt proxati da /api/*,
  404 via prerender /404). Le 10 rotte invariate NON vanno redirect-ate (loop).
- /app/scripts/collaudo-301.sh: batteria post-DNS one-shot (10 rotte 200 dirette,
  301 in un salto, file SEO radice, HTML completo per Googlebot/GPTBot/PerplexityBot,
  404 vero). Criterio: un solo salto per redirect.
- Rilevato e documentato: sull'URL di produzione Emergent /sitemap.xml|robots.txt|llms.txt
  alla radice rispondono col guscio SPA (in produzione non c'e' il middleware dev):
  sul dominio vero ci pensa il Worker col proxy sopra — i file veri sono sotto /api/.
- Verifica visiva produzione: home e /video/ renderizzate identiche all'anteprima.
- RESTA ESTERNO (non facibile da qui): Worker+DNS (hub, con il file consegnato),
  invio sitemap a Search Console/Bing (account del Dottore: sitemap
  https://www.chirurgiadellaparete.it/sitemap.xml), video hero (file dal Dottore),
  parere H1 home = nome sito (in attesa).
