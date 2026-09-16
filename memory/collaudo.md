# COLLAUDO 2 — giro di correzioni hub (16/09/2026, ore 20)
Host: https://chirurgia-test.preview.emergentagent.com (noindex attivo fuori dominio)

## 1. Guasto bloccante home e /articoli — RISOLTO
Causa vera: doppia rotta React Router `/articoli` + `/articoli/` (duplicate path in react-router v7
-> render silenzioso nullo) e lettura di `site.articlesIndex` prima del caricamento della config.
Fix: rotte duplicate eliminate (la barra finale si normalizza dentro i componenti), guardie su
config non ancora caricata. Verificato in browser reale (Playwright):
- home: H1 nel DOM, footer presente, 0 errori console (1920 e 390)
- /articoli: 3 card, 0 errori console (1920 e 390)
- /articoli/{tesar, laparocele, ernia-recidiva}: H1 presente, 0 errori console
Nota: la sotto-agente "testing_agent" non esiste in questo ambiente; la verifica e' stata fatta
in browser reale con cattura di console e pageerror.

## 2. Colore — blu #0B81E1 su grigio acciaio (sostituisce acciaio e rame)
Variabili esatte da specifica (ink #161B21, surface #1E252D, line #2C3742, text #EEF4FA,
muted #9BAAB9, accent #0B81E1, accent-soft #4FB0F5, deep #08243B); chiaro ritarato
(#F2F5F8/#FFFFFF/#D5DEE7/#0C161F/#55636F/#0A63AE). Un solo pulsante pieno per schermata,
marquee tornata striscia tecnica con dettagli blu (niente campiture piene). Fondi mobili:
alone blu radiale con parallasse lento (4% dello scroll) + griglia 1px + grana; tutto sospeso
con prefers-reduced-motion. Conferma: `grep -ciE '#E4762C|#B85A18|#C08A45|#E8935A|#E07B39' index.css` -> 0
Tipografia ripristinata: Space Grotesk / Literata 18px/1.75 max 68ch / IBM Plex Mono;
h2 a 2.75rem sopra, 0.8rem sotto.

## 3. Immagini — FOTO vs SCHEMI
49/49 classificate: FOTO max 320px h (200px mobile), max 560px w, cover, raggio 10px, hairline;
SCHEMI max 420px contain su --surface; coppie consecutive a due colonne; didascalia visibile
12.5px su tutte; width/height dichiarati; lazy tranne la prima; lightbox sobria con Esc
(verificata in browser: apertura=1, dopo Esc=0). Campione reso su /la-terapia-chirurgica/:
252x320 (nat 500), 273x320 (nat 500), 680x330 (nat 800), 292x320, 348x320 — mai oltre il nativo.
Pesi: ipom 34KB, ecografia 24KB, chirurgia-01 137KB, vac-01 20KB, tar-3 34KB, protesi-01 40KB
(tutte <=150KB).

## 4. Footer a quattro blocchi
Chi opera (con link curriculum hub) / Dove riceve (Fi Multicare, Galleria del Corso 4, 20122
Milano, tel:+390276021568, info@fimulticare.it, visite su appuntamento, fimulticare.it) /
La rete (abdominalwallsurgery.com RIMOSSO, federico-fiori.it presente) / Legale e servizio
(privacy, cookie, sitemap, torna su) + riga finale divulgativa. Verificato: 4 sezioni nel DOM.

## 5. Fi Multicare
Footer + sezione "Dove riceve" in /contatti/ con mappa statica webp (9KB, no iframe) +
3 FAQ + JSON-LD: MedicalClinic una sola volta (@id /contatti/#clinic), Person con
workLocation -> @id clinica e affiliation -> ASST (blocco completo verificato nel prerender).
Nessun orario inventato (rimosso openingHours).

## 6. /chi-sono/ — profilo
736 parole (700-900), H1 "Dott. Federico Fiori — chirurgo della parete addominale", 5 H2-domande
come da elenco, risposta diretta 64 parole, foto dal dominio hub sotto la risposta, congressi e
pubblicazioni solo citati con DOI/PMID (10.1089/lap.2018.0807, 10.1007/s10029-020-02252-0),
rimando a /curriculum, 4 FAQ + FAQPage. Tolti capacita' linguistiche/tecnologie e liste congressi.

## 7-8. Forma del testo e H2-domande
Igiene applicata a tutte le pagine: nbsp e doppi spazi rimossi, corsivi ereditati tolti,
concatenazioni minuscole-Maiuscole separate ("d'UrgenzaChirurgia" -> corretta), accenti con
apostrofo corretti (puo'->può ecc.), Paziente maiuscolo, paragrafi >110 parole spezzati a frase.
H2 con punto di domanda: anatomia 4, chi-sono 5, difetti 6, terapia 14, protesi 4, radiologia 2,
sintomi 4, vac 2, preabilitazione 2 (testo sotto invariato).

## 9. Link interni
Inline nel corpo (ancore descrittive) + blocco "Leggi anche" (campo related) su ogni pagina
clinica; i 3 articoli dell'hub linkati dalle pagine affini (TESAR da terapia; laparocele da
difetti/sintomi; ernia recidiva da protesi/diastasi). Conteggi per pagina nella tabella sotto.

## 10. Redirects barra finale
`curl -s .../api/seo/routes`: paths=19; redirects con 13 "/slug" -> "https://.../slug/"
assoluti + "/home" e "/home/" -> "/". (output incollato sopra in questa sessione)

## 11. Tabelle
EHS sedi M1-M5/L1-L4 + dimensioni (primaria <2/2-4/>4 cm; incisionale W1<4, W2 4-10, W3>10 cm)
con fonte Muysoms et al., Hernia 2009;13(4):407-414, DOI 10.1007/s10029-009-0518-x;
protesi: materiali (6 righe) + piani (4 righe); radiologia: esame/mostra/quando. Scorrevoli
su telefono (min-width + overflow-x).

## 12. Home — 709 parole
Risposta diretta, "Di che cosa si occupa questo sito?" con 3 percorsi linkati,
"Come si arriva all'intervento?" in 4 passi linkati, ultimi articoli dal canale, 4 FAQ + FAQPage.
Un solo H1. Prima schermata dichiara l'ambito in 3 righe.

## 13. Diastasi
Corpo 268 parole (250-350), rimando a diastasiedintorni.it come PRIMO link del testo, 3 immagini
conservate. (461 parole totali contando answer+FAQ richieste dalle regole AEO.)

## 14. Cookie tecnici
Paragrafo __emg_vid/__emg_sid presente in cookie-policy e privacy-policy
(grep su /api/pages/cookie-policy -> 1, /api/pages/privacy-policy -> 1).

## Tabella riepilogo (parole incluse answer+FAQ | h2? | link int. | tabelle | faq)
```
/                                                     709  2  3  0  4
/anatomia-della-parete-addominale-e-abdominal-core/  3105  4  5  0  4
/chi-sono/                                            736  5  8  0  4
/contatti/                                            273  0  3  0  3
/cookie-policy/                                      2089  0  0  0  0
/difetti-della-parete-addominale-e-classificazione/   977  6  6  2  2
/la-diastasi-dei-muscoli-retti/                       461  0  5  0  3
/la-terapia-chirurgica/                              2659 14  8  0  4
/le-complicanze-chirurgiche-la-vac-therapy/          1006  2  4  0  2
/le-protesi-...-posizionamento-della-protesi/        1421  4  6  2  3
/preabilitazione-dei-pazienti-all-intervento.../      785  2  4  0  3
/privacy-policy/                                     3112  0  1  0  0
/radiologia/                                         1199  2  6  1  2
/sintomi-e-complicanze/                              1008  4  5  0  3
```
Screenshot acquisiti: home 1920 scuro+chiaro, /articoli 1920+390, chi-sono 1920 scuro+chiaro,
terapia 1920 (coppie immagini, TOC, link), articolo 1920, 404.
