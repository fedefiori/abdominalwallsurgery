# COLLAUDO chirurgiadellaparete.it — 15/09/2026
Host di prova: https://chirurgia-test.preview.emergentagent.com (su host non finale tutte le pagine portano `noindex`, come da contratto)

## 1. Contenuti: le 14 pagine (indirizzo | HTTP | parole | immagini | len title | len description)
```
200 /                                                219 parole  1 img   t=56 d=159
200 /anatomia-della-parete-addominale-e-abdominal-core/   2743    5 img   t=57 d=156
200 /la-terapia-chirurgica/                          2399   17 img   t=57 d=153
200 /chi-sono/                                       1275    0 img   t=54 d=160
200 /radiologia/                                     1015    9 img   t=54 d=157
200 /le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/  1009 5 img t=59 d=150
200 /le-complicanze-chirurgiche-la-vac-therapy/       819    2 img   t=50 d=158
200 /sintomi-e-complicanze/                           755    2 img   t=57 d=155
200 /difetti-della-parete-addominale-e-classificazione/ 758  5 img   t=53 d=159
200 /la-diastasi-dei-muscoli-retti/                   268    3 img   t=52 d=158
200 /preabilitazione-dei-pazienti-all-intervento-chirurgico/ 642 0 img t=50 d=154
200 /contatti/                                         89    0 img   t=53 d=157
200 /privacy-policy/                                 3028    0 img   t=50 d=158
200 /cookie-policy/                                  2006    0 img   t=56 d=154
```
Totale estratto dal WordPress PRIMA delle riduzioni del punto 4: 18.248 parole / 49 immagini
(contratto: 18.251 — differenza di 3 parole dovuta all'unione di token spezzati da tag inline Divi).
Dopo il punto 4 (diastasi 250-350, TESAR in sintesi, chi-sono senza congressi/titoli): 17.025 parole.
Riduzioni solo dove il contratto lo prescrive (punto 4 a/d/e). Immagini: 49/49 scaricate, webp, max 1600px, 0 file oltre 150 KB, alt presente su tutte (generato descrittivo in italiano dove mancava: elenco in /app/scripts/migrate.py ALT_GENERATI).

## 2. Articoli (catalogo hub LIVE)
```
$ curl -s https://www.federicofiori.com/api/blog/syndication/parete | head -c 300
{"site":"parete","label":"chirurgiadellaparete.it","lang":"it","articlePath":"/articoli/","hubUrl":"https://www.federicofiori.com","total":3,"pending":3,"items":[{"id":"96583b75-...
```
Articoli importati (upsert su groupId, sections sovrascritte a ogni sync, sync all'avvio + ogni ora):
- tecnica-tesar-riparazione-endoscopica-sublay-anteriore
- laparocele-dopo-intervento-addominale-quando-operare
- ernia-ombelicale-recidiva-come-prevenirla

Sonde (esempio reale; lo slug `chirurgia-test` del contratto non esiste nel catalogo attuale):
```
$ curl -s .../api/blog/posts/it/laparocele-dopo-intervento-addominale-quando-operare | head -c 150
{"post":{"id":"cf8b5e5d-...","groupId":"...","lang":"it","title":"Laparocele dopo un intervento addominale: cosa fare e quando...
HTTP 200, content-type application/json ✓ — lingua sbagliata: 404 ✓
$ curl -s -o /dev/null -w "%{http_code}" .../articoli/laparocele-dopo-intervento-addominale-quando-operare
200
```

## 3. SEO machine
```
$ curl -s .../api/seo/routes | head -c 400
{"paths":["/","/404","/anatomia-della-parete-addominale-e-abdominal-core/","/articoli","/articoli/ernia-ombelicale-recidiva-come-prevenirla","/articoli/laparocele-dopo-intervento-addominale-quando-operare","/articoli/tecnica-tesar-riparazione-endoscopica-sublay-anteriore","/chi-sono/",...]}
$ curl -s ".../api/seo/prerender?path=/chi-sono/&absolute=true" | grep canonical
<link rel="canonical" href="https://www.chirurgiadellaparete.it/chi-sono/" />
   + JSON-LD ProfilePage + Person (stesso @id dell'hub) + BreadcrumbList; noindex su host non finale ✓
$ curl -s ".../api/seo/prerender?path=/articoli/tecnica-tesar-...&absolute=true" | grep -E "canonical|alternate"
canonical = ESATTAMENTE il campo canonical del catalogo ✓
hreflang en -> https://www.federicofiori.com/en/articles/tesar-technique-... (translation.url dell'hub, invariato) ✓
$ curl -s .../api/seo/sitemap.xml | grep -c "<url>"   -> 18 (14 pagine + /articoli + 3 articoli, lastmod veri)
$ curl -s .../api/seo/robots.txt   -> Allow: /, allow-list bot AI, Disallow solo /api/stats/, Sitemap + llms.txt ✓ (nessun Disallow: /)
$ curl -s .../api/seo/llms.txt | head -c 400  -> generato dai dati ✓
```
hreflang sulle 14 pagine: ASSENTI di proposito — la chiave `en` di ogni pagina è vuota, quindi la pagina inglese non esiste (né URL, né sitemap, né hreflang).

## 4. Statistiche
```
$ curl -s -o /dev/null -w "%{http_code}" .../api/stats/summary          -> 401
$ curl -s -H "X-Network-Token: ***" .../api/stats/summary | head -c 200
{"site":"www.chirurgiadellaparete.it","days":30,"visits":0,"visitors":0,"pageviews":0,"topPages":[],...}
```
Token in backend/.env (NETWORK_STATS_TOKEN) e in /app/memory/test_credentials.md.

## 5. Grafica
Screenshot acquisiti: home 1920 scuro, home 1920 chiaro, pagina clinica lunga 1920 scuro+chiaro, articolo 1920 scuro, home 390 scuro + menu mobile, 404. Nessuno sbordamento orizzontale a 390px. Temi: scuro base + chiaro ritarato (rame #B85A18 AA su bianco).

## Note per il chirurgo (frasi migliorabili, testo NON toccato)
- /la-terapia-chirurgica/: "molto molto complessi" (doppione) e "Viene quindi posizionato un drenaggio" (concordanza).
- /preabilitazione.../: "Controllo dell'peso" (refuso nel testo originale).
- /chi-sono/: il testo WP originale conteneva shortcode Divi residui ([et_pb_...]) stampati come testo: rimossi perché markup tecnico, non parole cliniche.

## Da fare in produzione (fuori da questa app)
- Worker Cloudflare davanti al dominio: legge /api/seo/routes, /api/seo/prerender, sitemap/robots/llms dal backend (gli endpoint sono pronti e calcolati dai dati).
- DNS: lo configura il cliente, per ultimo.
- Video anatomia home: predisposto lo spazio hero (SVG animato); serve il file video definitivo.
