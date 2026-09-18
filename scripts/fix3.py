#!/usr/bin/env python3
"""Giro 3: /chi-sono/ cambia bersaglio (come opero), formula di definizione
del Dottore, e pulizia dei riferimenti alla persona."""
import json, re, glob
from pathlib import Path

PAGES = Path('/app/backend/data/pages')
HUB = 'https://www.federicofiori.com'

DEFINIZIONE = ("Medico Chirurgo - Specialista in Chirurgia Generale, con alta specializzazione "
               "in chirurgia della parete addominale e in chirurgia plastica")
RUOLO_ESTESO = ("Responsabile della Unità Operativa di Chirurgia della Parete Addominale - "
                "ASST Santi Paolo e Carlo, PO San Carlo Borromeo, Milano")

# ---------------------------------------------------------------- chi-sono: nuovo bersaglio
f = PAGES / 'chi-sono.json'
p = json.load(open(f))
it = p['it']
it['metaTitle'] = 'Chirurgia della parete addominale a Milano: come opero'
it['metaDescription'] = ('Come affronto ernie, laparoceli e difetti complessi della parete '
                         'addominale: criteri di scelta della tecnica, dove opero e dove ricevo a Milano.')
it['h1'] = 'Come opero i difetti della parete addominale'
it['answer'] = (f"Sono il dott. Federico Fiori, {DEFINIZIONE}. In questa pagina racconto come opero "
                "i difetti della parete addominale: i criteri con cui scelgo la tecnica per ogni "
                "Paziente, dove opero in ASST a Milano e dove ricevo, presso Fi Multicare in "
                "Galleria del Corso 4.")
ritratto = {'type': 'img', 'src': '/api/media/ritratto-dottor-fiori.webp',
            'alt': 'Il dott. Federico Fiori in camice operatorio, ritratto ufficiale',
            'caption': 'Il dott. Federico Fiori, ' + RUOLO_ESTESO.split(' - ')[0] + ', a Milano.',
            'kind': 'photo', 'width': 820, 'height': 1000}
it['blocks'] = [
    ritratto,
    {'type': 'h2', 'text': 'Di che cosa mi occupo in chirurgia della parete?'},
    {'type': 'p', 'html': "Mi occupo dei difetti della parete addominale anteriore: ernie primitive, ernie incisionali (laparoceli) e diastasi dei muscoli retti, con particolare attenzione alle riparazioni complesse, ai disastri di parete e alle recidive dopo precedenti interventi."},
    {'type': 'p', 'html': "Sono Dirigente Medico di Chirurgia Generale presso l'ASST Santi Paolo e Carlo di Milano e ricopro il ruolo di " + RUOLO_ESTESO + ". Alla chirurgia addominale mi dedico da oltre vent'anni, con centinaia di interventi laparoscopici all'attivo; dal 1996 mi occupo anche di chirurgia plastica ricostruttiva del tronco, che impiega ogni giorno nel ripristino funzionale ed estetico della parete."},
    {'type': 'p', 'html': "Sono titolare dell'ambulatorio di Chirurgia della Parete. Nel gennaio 2019 ho pubblicato sul <i>Journal of Laparoendoscopic &amp; Advanced Surgical Techniques</i> la TESAR, una tecnica endoscopica originale per il trattamento mininvasivo dei laparoceli e delle ernie ventrali (J Laparoendosc Adv Surg Tech A. 2019. DOI: 10.1089/lap.2018.0807. PMID: 30807248)."},
    {'type': 'h2', 'text': 'Come scelgo la tecnica per ogni Paziente?'},
    {'type': 'p', 'html': "Scelgo la tecnica sul singolo Paziente, non sull'abitudine: contano la sede e la dimensione del difetto, la qualità della linea alba e dei muscoli, la storia chirurgica precedente e le condizioni generali. Per questo la valutazione in ambulatorio comprende sempre l'esame clinico e, quando serve, la <a href=\"/radiologia/\">diagnostica per immagini della parete addominale</a>."},
    {'type': 'p', 'html': "A seconda del quadro, la scelta ricade sulla via aperta, laparoscopica, robotica o endoscopica, con la protesi e il <a href=\"/le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/\">piano di posizionamento della rete</a> più adatti al caso: le tecniche sono descritte nella pagina della <a href=\"/la-terapia-chirurgica/\">terapia chirurgica della parete</a>. Quando il quadro clinico lo richiede, il percorso inizia con la <a href=\"/preabilitazione-dei-pazienti-all-intervento-chirurgico/\">pre-abilitazione prima dell'intervento</a>."},
    {'type': 'h2', 'text': 'Dove opero e dove ricevo?'},
    {'type': 'p', 'html': "Opero presso la Divisione di Chirurgia d'Urgenza – Chirurgia Generale e Robotica dell'ASST Santi Paolo e Carlo, Polo Ospedaliero San Carlo Borromeo di Milano, dove da oltre quindici anni svolgo funzione di Capoturno Chirurgo con ruolo di Trauma Leader."},
    {'type': 'p', 'html': "Ricevo su appuntamento presso <strong>Fi Multicare — Centro Medico Multidisciplinare</strong>, Galleria del Corso 4, 20122 Milano. Telefono <a href=\"tel:+390276021568\">+39 02 76021568</a>, e-mail <a href=\"mailto:info@fimulticare.it\">info@fimulticare.it</a>. Tutti i riferimenti sono nella <a href=\"/contatti/\">pagina dei contatti dello studio</a>."},
    {'type': 'h2', 'text': 'Che cosa insegno e dove?'},
    {'type': 'p', 'html': "Ho presentato la tecnica TESAR e i suoi risultati come relatore a congressi nazionali e internazionali di chirurgia della parete — fra cui EHS, ACOI, ISHAWS e AWR Europe — e in videocorsi dedicati alla riparazione dei difetti della linea mediana."},
    {'type': 'h2', 'text': 'Dove trovo il curriculum completo?'},
    {'type': 'p', 'html': f"Curriculum completo, titoli, congressi, pubblicazioni e galleria dei risultati non si duplicano su questo sito: sono pubblicati sull'hub della rete, alla pagina <a href=\"{HUB}/curriculum\">curriculum completo del dott. Federico Fiori</a>. Chi sono, nel senso anagrafico e professionale, lo racconta l'hub; qui racconto come opero."},
]
for fq in it.get('faq', []):
    if fq['q'].startswith('Chi è'):
        fq['a'] = (f"Il dott. Federico Fiori è {DEFINIZIONE}. È {RUOLO_ESTESO}. "
                   "Si occupa di ernie, laparoceli e diastasi dei muscoli retti con tecniche aperte, laparoscopiche, robotiche ed endoscopiche.")
    if '02 7602' in fq['a']:
        fq['a'] = fq['a'].replace('02 7602 1568', '+39 02 76021568')
json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- "chirurgo della parete" mai per la persona
fixed = []
for path in glob.glob(str(PAGES / '*.json')):
    s = open(path).read()
    n = s
    n = n.replace('chirurgo della parete addominale a cura del dott. Federico Fiori', 'cura del dott. Federico Fiori')
    n = n.replace('chirurgo della parete addominale', 'chirurgo generale')
    n = n.replace('chirurgo della parete', 'chirurgo generale')
    if n != s:
        open(path, 'w').write(n)
        fixed.append(path.split('/')[-1])
print('ripulite le occorrenze su:', fixed)

import re as _re
pp = json.load(open(f))
w = sum(len(_re.sub(r'<[^>]+>', ' ', b.get('html', '') or b.get('text', '')).split()) for b in pp['it']['blocks'])
w += len(pp['it']['answer'].split()) + sum(len(x['q'].split()) + len(x['a'].split()) for x in pp['it']['faq'])
print('chi-sono parole totali:', w)
print('title:', pp['it']['metaTitle'], len(pp['it']['metaTitle']))
print('desc:', pp['it']['metaDescription'], len(pp['it']['metaDescription']))
print('h1:', pp['it']['h1'])
