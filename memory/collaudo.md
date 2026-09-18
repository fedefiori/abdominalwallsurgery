# COLLAUDO 4 — punti 13-14 hub + design (18/09/2026, pomeriggio)

## Punto 13 — /chi-sono/ cambia bersaglio
- title: "Chirurgia della parete addominale a Milano: come opero" (54)
- description: "Come affronto ernie, laparoceli e difetti complessi della parete addominale:
  criteri di scelta della tecnica, dove opero e dove ricevo a Milano." (144, testo esatto dell'hub)
- H1: "Come opero i difetti della parete addominale" (nome NON nell'H1)
- H2 (domande, come prescritto): Di che cosa mi occupo in chirurgia della parete? /
  Come scelgo la tecnica per ogni Paziente? / Dove opero e dove ricevo? / Che cosa insegno e dove? /
  Dove trovo il curriculum completo?
- 705 parole (600-800 richieste). Formula di definizione del Dottore applicata:
  "Medico Chirurgo - Specialista in Chirurgia Generale, con alta specializzazione in chirurgia
  della parete addominale e in chirurgia plastica". Zero occorrenze di "chirurgo della parete"
  riferite alla persona. "chi sono" assente da title/description/H1.

## Punto 14 — riquadro d'autore
Componente AuthorBox su tutte le pagine cliniche e tutti gli articoli, prima di "Leggi anche":
ritratto 72px circolare, nome, qualifica, ruolo esteso, "Scrive e revisiona i contenuti di questo
sito.", link Curriculum hub + Dove ricevo, data di ultima modifica del contenuto. Presente anche
nel prerender dei crawler. JSON-LD: author e reviewedBy = @id hub su pagine e articoli;
Person.jobTitle come lista [qualifica, ruolo] (regola punto 8). Screenshot: /tmp/j_authorbox.png
(pagina clinica), /tmp/j_articolo_box.png (articolo).

## jobTitle punto 8
Person.jobTitle nel JSON-LD: ["Medico Chirurgo - Specialista in Chirurgia Generale",
"Responsabile della Unità Operativa di Chirurgia della Parete Addominale"].

## Design (richiesta utente, stesso turno)
- Font: corpo Literata 18px/1.75 (contratto), titoli Inter Tight e etichette Azeret Mono (hub).
- Sfondi piu' dinamici: ciclo a 4 superfici con contrasto maggiore (grafite / acciaio / blu
  profondo / acciaio chiaro), filetti laterali alternati, figure degli schemi a lato del testo
  (destra/sinistra alternate) su desktop, barra di progresso di lettura in alto, micro-movimento
  sulle figure al passaggio del mouse, alone in parallasse. Tutto sospeso con prefers-reduced-motion.
- Verifiche browser: chi-sono, terapia (author box + figure laterali), articolo (author box +
  Su questo sito), zero errori console.

# COLLAUDO 3 — giro hub 2 (18/09/2026)
Host: https://chirurgia-test.preview.emergentagent.com

## Punto 1 — recapiti
grep -ri tiscali su tutti i contenuti e il codice: 0 occorrenze.
Telefono ovunque "+39 02 76021568" (link tel:+390276021568), e-mail studio info@fimulticare.it,
contatto diretto rete info@federicofiori.com. Indirizzo identico nelle tre occorrenze:
"Galleria del Corso 4, 20122 Milano".

## Punto 2 — risposte dirette riscritte (diverse dal corpo, 40-70 parole)
- /radiologia/ (testo fornito dall'hub): "Nella chirurgia della parete l'imaging serve a due cose:
  misurare il difetto prima di operare e riconoscere le complicanze dopo. L'ecografia è l'esame di
  primo livello, disponibile e ripetibile; la TC serve quando il difetto è ampio o recidivo e va
  pianificato; la risonanza si riserva ai casi in cui contano i tessuti molli."
- /preabilitazione…/: "La pre-abilitazione è la preparazione clinica delle settimane che precedono
  l'intervento sulla parete: peso, glicemia, fumo, nutrizione ed esercizio fisico. Serve perché la
  recidiva resta il problema principale di questa chirurgia, e arrivare all'operazione nelle migliori
  condizioni riduce le complicanze e migliora la guarigione."
- /la-diastasi…/: "In chirurgia della parete la diastasi dei retti conta perché spesso si associa a
  un'ernia ombelicale: allora non basta chiudere il difetto, va ricostruita la linea mediana. Questa
  pagina spiega solo che cosa cambia nell'indicazione chirurgica; il percorso completo è su
  diastasiedintorni.it."
Riscritte di conseguenza anche anatomia, terapia, protesi, VAC, sintomi, difetti, contatti (prima
ripetevano il primo paragrafo).

## Punto 3 — titoli in minuscolo di rete
I due title contesi cambiati come richiesto ("Sintomi dei difetti di parete: riferimento clinico",
"Classificazione EHS dei difetti di parete: sedi, sigle e misure", "Diastasi dei retti associata a
ernia: cosa cambia in chirurgia", "Chi sono | dott. Federico Fiori, chirurgo della parete"); tutte
le pagine passate alla forma minuscola. Le due lunghezze >60 (63 e 62) sono i title esatti dell'hub.

## Punto 4 — studio nodo condiviso
Il JSON-LD di /contatti/ incorpora il MedicalClinic con @id dell'hub
(https://www.federicofiori.com/contatti#fi-multicare), Person.workLocation -> quell'@id.
Nota: /api/seo/entity dell'hub oggi NON espone ancora clinicId/clinic (verificato 18/09): il blocco
e' costruito con i dati dichiarati nel brief e con l'@id definitivo; appena l'endpoint li espone,
il sito li prende cosi' come arrivano senza riscrivere nulla (fallback automatico gia' predisposto).

## Punto 5 — diapositive lilla
Radiologia: rimosse ecografia-parete-addominale.webp e tc-e-rm-nella-valutazione-della-parete-addominale.webp
(9 -> 7 immagini), tabella esame/mostra/quando gia' presente, aggiunta la frase sobria
"L'affidabilità dell'ecografia dipende dall'operatore: va eseguita da chi conosce la parete addominale."
Screenshot: /tmp/i_radiologia.png.

## Punto 6 — refusi
superpecialistica->superspecialistica, affontare->affrontare, "ernie ,valutando" corretta,
spazi prima della punteggiatura rimossi, nbsp/doppi spazi, maiuscole enfatiche (anatomia,
fisiopatologia) in minuscolo. Applicato a tutte e 14 le pagine.

## Punto 7 — percentuali senza fonte
Rimosse da /preabilitazione…/ e riformulate con la frase dell'hub. CIFRE PER CUI SERVE LA FONTE
(da chiedere al Dottore): recidiva difetto primitivo senza mesh ~24%, con mesh oltre 7%, ernia
incisionale tra 10 e 60% a 2 anni.

## Punto 8 — qualifica
"Unità Operativa" ovunque: footer, hero, chi-sono, jobTitle (dall'entity hub), meta description.
Zero occorrenze di "Struttura Semplice".

## Punto 9 — H2 domande
Anatomia 13/13, terapia 14/14, difetti 6/6, sintomi 4/4, protesi 4/4, chi-sono 5/5, diastasi 4/4,
contatti 2/2, radiologia 2/2, VAC 2/2, preabilitazione 2/2, home 2/2, /articoli 2 (in pagina).

## Punto 10 — link
Ogni pagina: 3+ link interni con ancore descrittive (le ancore di una parola sono state riscritte)
+ "Leggi anche". Ogni articolo: blocco "Su questo sito" con 3 link alle pagine affini + ritorno
all'indice (screenshot /tmp/i_articolo_rel.png). /articoli: sotto ogni voce sintesi 12-18 parole
+ link alla pagina del sito collegata. /contatti/: link a pre-abilitazione, terapia, chi sono.

## Punto 11 — diastasi
313 parole totali (corpo 268, nel range 250-350 richiesto), definizione non ripetuta, primo link
del testo a diastasiedintorni.it. FAQ rimosse dalla pagina per restare nel range.

## Punto 12 — tipografia
Corpo ripristinato a Literata 18px/1.75, misura 68-72ch; titoli Space Grotesk, etichette IBM Plex
Mono (il set concordato del contratto). Tema chiaro: link #0A63AE (5,9:1), didascalie #55636F.

## Extra utente (stesso turno)
- Ritratto ufficiale del Dottore caricato: editato in bianco e nero con virata blu-acciaio
  (duotone coerente con la palette), 820x1000, 29KB, in home e in chi-sono.
- Sfondi piu' contrastati: ciclo a 4 superfici (grafite / acciaio / blu profondo / acciaio chiaro);
  tema chiaro con tre toni diversi (bianco / azzurro tenue / caldo tenue).

## Bug trovato e risolto in questa verifica
Articolo: crash "startsWith of undefined" sul blocco Su questo sito (formato tupla vs oggetto):
normalizzato in Related. Riverificato in browser: blocco presente, 0 errori console.

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
