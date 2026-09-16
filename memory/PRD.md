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
  Design "acciaio e rame" punto 11: tema scuro base + chiaro ritarato, Space Grotesk/Literata/IBM Plex Mono,
  framer-motion, lenis, hero con masked line reveal, marquee, indice appiccicoso, grana, data-testid ovunque.
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
