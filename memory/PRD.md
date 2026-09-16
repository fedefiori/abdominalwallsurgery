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
4. Fissare la variante colore scelta dall'utente come default (attualmente default=1 Bronzo).

## Design refresh (16/09/2026)
- Font dell'hub: Inter Tight (titoli), Manrope (testo), Azeret Mono (etichette) — sostituiscono Space Grotesk/Literata/IBM Plex Mono.
- H1 home: "Chirurgia della Parete Addominale" (maiuscolo).
- Contrasto: striscia marquee piena in colore accento, banda "carta" calda per capitoli e articoli home, blocco risposta diretta con fondo tinta rame.
- 4 varianti colore selezionabili con ?v=1..4 (persistenza localStorage, picker visibile solo con ?v=):
  1 Bronzo (grafite caldo #C08A45 / carta osso) — default
  2 Rame chiaro (#E8935A / carta cipria)
  3 Ottone e petrolio (#D2A94E su verde petrolio #071216 / carta salvia)
  4 Carta e rame (base editoriale chiara #FAF5EC, banda cioccolato, rame scuro #A44A12)
- Screenshot varianti in /tmp/v1_bronzo.png, v2_rame_chiaro.png (+hero), v3_ottone_petrolio.png, v4_carta_rame.png (+hero).
