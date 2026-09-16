#!/usr/bin/env python3
"""Contenuti richiesti dall'hub: chi-sono (700-900 parole), home (700-900),
contatti + Fi Multicare, mappa statica. Fatti solo dal materiale esistente."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PAGES = Path('/app/backend/data/pages')
MEDIA = Path('/app/backend/static/media')
HUB = 'https://www.federicofiori.com'
PORTRAIT = 'https://www.federicofiori.com/media/og-federico-fiori.jpg?v=2'

# ---------------------------------------------------------------- mappa statica
def make_map():
    W, H = 1200, 675
    im = Image.new('RGB', (W, H), '#161B21')
    d = ImageDraw.Draw(im)
    # reticolo secondario
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill='#1E252D', width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill='#1E252D', width=1)
    # strade
    streets_h = [140, 300, 470, 590]
    streets_v = [180, 420, 700, 950]
    for y in streets_h:
        d.line([(0, y), (W, y)], fill='#2C3742', width=6)
    for x in streets_v:
        d.line([(x, 0), (x, H)], fill='#2C3742', width=6)
    # corso principale (Galleria del Corso)
    d.line([(0, 300), (W, 300)], fill='#3A4754', width=10)
    d.line([(700, 0), (700, H)], fill='#3A4754', width=10)
    try:
        f_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
        f_sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
    except Exception:
        f_big = f_sm = ImageFont.load_default()
    # pin
    px, py = 700, 300
    d.ellipse([px - 46, py - 46, px + 46, py + 46], outline='#0B81E1', width=3)
    d.ellipse([px - 26, py - 26, px + 26, py + 26], fill='#0B81E1')
    d.ellipse([px - 9, py - 9, px + 9, py + 9], fill='#04121D')
    d.text((px + 58, py - 58), 'Fi Multicare', font=f_big, fill='#EEF4FA')
    d.text((px + 58, py - 16), 'Galleria del Corso 4, 20122 Milano', font=f_sm, fill='#9BAAB9')
    d.text((24, H - 48), 'Mappa schematica — posizione indicativa', font=f_sm, fill='#55636F')
    im.save(MEDIA / 'mappa-fi-multicare.webp', 'WEBP', quality=85)
    print('mappa ok', (MEDIA / 'mappa-fi-multicare.webp').stat().st_size, 'bytes')

make_map()

# ---------------------------------------------------------------- chi-sono
chi = {
    'h1': 'Dott. Federico Fiori — chirurgo della parete addominale',
    'answer': ("Il dott. Federico Fiori è un chirurgo generale che si occupa in modo specifico dei difetti "
               "della parete addominale: ernie, laparoceli e diastasi dei muscoli retti. È responsabile della "
               "Struttura Semplice di Chirurgia della Parete Addominale dell'ASST Santi Paolo e Carlo di Milano "
               "e riceve su appuntamento presso Fi Multicare, in Galleria del Corso 4 a Milano."),
    'blocks': [
        {'type': 'img', 'src': PORTRAIT, 'alt': 'Il dott. Federico Fiori, chirurgo della parete addominale',
         'caption': 'Il dott. Federico Fiori, responsabile della Chirurgia della Parete Addominale a Milano.',
         'kind': 'photo', 'width': 1200, 'height': 630},
        {'type': 'h2', 'text': 'Di che cosa mi occupo in chirurgia della parete?'},
        {'type': 'p', 'html': "Mi occupo dei difetti della parete addominale anteriore: ernie primitive, ernie incisionali (laparoceli) e diastasi dei muscoli retti, con particolare attenzione alle riparazioni complesse, ai disastri di parete e alle recidive dopo precedenti interventi."},
        {'type': 'p', 'html': "Sono Dirigente Medico di Chirurgia Generale presso l'ASST Santi Paolo e Carlo di Milano ed esperto di chirurgia mininvasiva e robotica della parete addominale: alla chirurgia addominale mi dedico da oltre vent'anni, con centinaia di interventi laparoscopici all'attivo. Dal 1996 mi occupo anche di chirurgia plastica ricostruttiva del tronco, competenza che uso ogni giorno nel ripristino funzionale ed estetico della parete."},
        {'type': 'p', 'html': "Sono titolare dell'ambulatorio di Chirurgia della Parete e di un Incarico di Alta Specializzazione per il trattamento delle patologie complesse della parete addominale con tecniche mininvasive e tradizionali. Nel gennaio 2019 ho pubblicato sul <i>Journal of Laparoendoscopic &amp; Advanced Surgical Techniques</i> la TESAR, una tecnica endoscopica originale per il trattamento mininvasivo dei laparoceli e delle ernie ventrali (J Laparoendosc Adv Surg Tech A. 2019. DOI: 10.1089/lap.2018.0807. PMID: 30807248)."},
        {'type': 'h2', 'text': 'Dove opero e dove ricevo?'},
        {'type': 'p', 'html': "Opero presso la Divisione di Chirurgia d'Urgenza – Chirurgia Generale e Robotica dell'ASST Santi Paolo e Carlo, Polo Ospedaliero San Carlo Borromeo di Milano, dove da oltre quindici anni svolgo funzione di Capoturno Chirurgo con ruolo di Trauma Leader e autonomia gestionale e chirurgica nei casi di politrauma maggiore."},
        {'type': 'p', 'html': "Ricevo su appuntamento presso <strong>Fi Multicare — Centro Medico Multidisciplinare</strong>, Galleria del Corso 4, 20122 Milano. Telefono <a href=\"tel:+390276021568\">02 7602 1568</a>, e-mail <a href=\"mailto:info@fimulticare.it\">info@fimulticare.it</a>. Tutti i riferimenti sono nella <a href=\"/contatti/\">pagina dei contatti</a>."},
        {'type': 'h2', 'text': 'Come scelgo la tecnica per ogni Paziente?'},
        {'type': 'p', 'html': "La tecnica si sceglie sul singolo Paziente, non sull'abitudine: contano la sede e la dimensione del difetto, la qualità della linea alba e dei muscoli, la storia chirurgica precedente e le condizioni generali. Per questo la valutazione in ambulatorio comprende sempre l'esame clinico e, quando serve, la <a href=\"/radiologia/\">diagnostica per immagini della parete</a>."},
        {'type': 'p', 'html': "A seconda del quadro propongo la via aperta, laparoscopica, robotica o endoscopica, con la protesi e il <a href=\"/le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/\">piano di posizionamento</a> più adatti al caso: le tecniche sono descritte nella pagina della <a href=\"/la-terapia-chirurgica/\">terapia chirurgica</a>. Quando il quadro clinico lo richiede, il percorso inizia con la <a href=\"/preabilitazione-dei-pazienti-all-intervento-chirurgico/\">pre-abilitazione</a>."},
        {'type': 'h2', 'text': 'Che cosa insegno e dove?'},
        {'type': 'p', 'html': "Ho presentato la tecnica TESAR e i suoi risultati come relatore a congressi nazionali e internazionali di chirurgia della parete — fra cui EHS, ACOI, ISHAWS e AWR Europe — e in videocorsi dedicati alla riparazione dei difetti della linea mediana. La formazione continua fa parte del lavoro: i congressi si inseguono, la casistica cresce e la tecnica si aggiorna."},
        {'type': 'p', 'html': "Le pubblicazioni principali sulla parete addominale: <i>Totally Endoscopic Sublay Anterior Repair for Ventral and Incisional Hernias</i>, J Laparoendosc Adv Surg Tech A, 2019, DOI: 10.1089/lap.2018.0807, PMID: 30807248; <i>Surgical treatment of diastasis recti: the importance of an overall view of the problem</i>, Hernia, 2020, DOI: 10.1007/s10029-020-02252-0, PMID: 32564225."},
        {'type': 'h2', 'text': 'Dove trovo il curriculum completo?'},
        {'type': 'p', 'html': f"Curriculum completo, titoli, congressi, pubblicazioni e galleria dei risultati non si duplicano su questo sito: sono pubblicati sull'hub della rete, alla pagina <a href=\"{HUB}/curriculum\">curriculum del dott. Federico Fiori su federicofiori.com</a>."},
    ],
    'faq': [
        {'q': 'Chi è il dott. Federico Fiori?',
         'a': "Il dott. Federico Fiori è un chirurgo generale, Dirigente Medico presso l'ASST Santi Paolo e Carlo di Milano, dove è responsabile della Struttura Semplice di Chirurgia della Parete Addominale. Si occupa di ernie, laparoceli e diastasi dei muscoli retti con tecniche aperte, laparoscopiche, robotiche ed endoscopiche."},
        {'q': 'Dove riceve il dott. Federico Fiori?',
         'a': "Il dott. Fiori riceve su appuntamento presso Fi Multicare — Centro Medico Multidisciplinare, Galleria del Corso 4, 20122 Milano. Per prenotare: telefono 02 7602 1568, e-mail info@fimulticare.it."},
        {'q': "Che cos'è la tecnica TESAR?",
         'a': "La TESAR (Totally Endoscopic Sublay Anterior Repair) è una tecnica endoscopica mininvasiva per la riparazione dei difetti della linea mediana, pubblicata dal dott. Fiori nel 2019 sul Journal of Laparoendoscopic & Advanced Surgical Techniques (DOI: 10.1089/lap.2018.0807). La descrizione completa è sull'hub federicofiori.com."},
        {'q': 'Dove trovo curriculum e pubblicazioni complete?',
         'a': "Il curriculum completo, l'elenco dei congressi e tutte le pubblicazioni del dott. Fiori sono pubblicati sull'hub della rete, federicofiori.com, alla pagina Curriculum. Su questo sito resta solo il profilo legato alla chirurgia della parete addominale."},
    ],
}

f = PAGES / 'chi-sono.json'
page = json.load(open(f))
page['it'].update(chi)
json.dump(page, open(f, 'w'), ensure_ascii=False, indent=1)
w = sum(len((b.get('html') or b.get('text', '')).split()) for b in chi['blocks'])
print('chi-sono parole (blocchi):', w)

# ---------------------------------------------------------------- home
home_new = [
    {'type': 'h2', 'text': 'Di che cosa si occupa questo sito?'},
    {'type': 'p', 'html': "Questo sito è il verticale italiano sulla chirurgia della parete addominale del dott. Federico Fiori: spiega l'anatomia della parete, la classificazione dei difetti, i sintomi, gli esami e le tecniche di riparazione, con il testo clinico del chirurgo e gli articoli divulgativi della rete editoriale di federicofiori.com."},
    {'type': 'h3', 'text': 'Ernie e difetti primitivi della parete'},
    {'type': 'p', 'html': "L'ernia è la fuoriuscita di viscere o tessuto attraverso un punto di debolezza della parete addominale: epigastrica, ombelicale o di Spigelio. Sedi, sigle e dimensioni sono nella pagina della <a href=\"/difetti-della-parete-addominale-e-classificazione/\">classificazione dei difetti della parete</a>."},
    {'type': 'h3', 'text': "Laparocele: l'ernia sulla cicatrice"},
    {'type': 'p', 'html': "Il laparocele, o ernia incisionale, è il difetto che compare su una cicatrice di un precedente intervento addominale. Come si riconosce e quando diventa urgente è spiegato nella pagina dei <a href=\"/sintomi-e-complicanze/\">sintomi e delle complicanze</a>."},
    {'type': 'h3', 'text': "La pre-abilitazione prima dell'intervento"},
    {'type': 'p', 'html': "La pre-abilitazione è la preparazione clinica delle settimane che precedono l'intervento: peso, glicemia, fumo, nutrizione ed esercizio. Il percorso è descritto nella pagina della <a href=\"/preabilitazione-dei-pazienti-all-intervento-chirurgico/\">pre-abilitazione dei Pazienti</a>."},
    {'type': 'h2', 'text': "Come si arriva all'intervento?"},
    {'type': 'ul', 'ordered': True, 'items': [
        "La <strong>valutazione specialistica</strong> in ambulatorio, con l'esame clinico della parete: si prenota dalla pagina dei <a href=\"/contatti/\">contatti</a>.",
        "La <strong>diagnostica per immagini</strong> — ecografia, TC o risonanza — quando serve misurare il difetto: gli esami sono descritti nella pagina di <a href=\"/radiologia/\">radiologia della parete</a>.",
        "La <strong>pre-abilitazione</strong>, se il quadro lo richiede, per arrivare all'intervento nelle migliori condizioni.",
        "L'<strong>intervento</strong> con la tecnica scelta sul singolo Paziente: le tecniche sono nella pagina della <a href=\"/la-terapia-chirurgica/\">terapia chirurgica</a>.",
    ]},
]
home_faq = [
    {'q': 'Di che cosa si occupa questo sito?',
     'a': "Il sito si occupa dei difetti della parete addominale — ernie, laparoceli e diastasi dei muscoli retti — e della loro cura chirurgica: anatomia, classificazione, sintomi, esami diagnostici, protesi e tecniche di riparazione. I contenuti clinici sono del dott. Federico Fiori; gli articoli divulgativi arrivano dalla redazione di federicofiori.com."},
    {'q': 'Chi è il dott. Federico Fiori?',
     'a': "Il dott. Federico Fiori è un chirurgo generale, responsabile della Struttura Semplice di Chirurgia della Parete Addominale dell'ASST Santi Paolo e Carlo di Milano. Il profilo completo è nella pagina Chi sono; il curriculum è sull'hub federicofiori.com."},
    {'q': 'Dove si riceve?',
     'a': "Si riceve su appuntamento presso Fi Multicare — Centro Medico Multidisciplinare, Galleria del Corso 4, 20122 Milano. Telefono 02 7602 1568, e-mail info@fimulticare.it."},
    {'q': "Che cos'è un laparocele?",
     'a': "Il laparocele, o ernia incisionale, è un difetto della parete addominale che compare su una cicatrice di un precedente intervento chirurgico: i tessuti cedono e una parte del contenuto addominale sporge attraverso il difetto. Si classifica per sede e dimensione e la sua cura è chirurgica."},
]
f = PAGES / 'home.json'
page = json.load(open(f))
it = page['it']
blocks = [b for b in it['blocks'] if not (b['type'] == 'h2' and b.get('text') == 'Contenuti')]
blocks = [b for b in blocks if not (b['type'] == 'ul' and any('anatomia' in i for i in b.get('items', [])))]
it['blocks'] = blocks + home_new
it['faq'] = home_faq
json.dump(page, open(f, 'w'), ensure_ascii=False, indent=1)
import re
def wc_all(p):
    t = 0
    for b in p['it']['blocks']:
        t += len(re.sub(r'<[^>]+>', ' ', b.get('html', '') or b.get('text', '')).split())
        t += sum(len(re.sub(r'<[^>]+>', ' ', i).split()) for i in b.get('items', []))
    t += len(p['it'].get('answer', '').split())
    t += sum(len(x['q'].split()) + len(x['a'].split()) for x in p['it'].get('faq', []))
    return t
print('home parole totali (blocchi+answer+faq):', wc_all(page))
print('chi-sono parole totali:', wc_all(json.load(open(PAGES / 'chi-sono.json'))))

# ---------------------------------------------------------------- contatti
cont_blocks_add = [
    {'type': 'h2', 'text': 'Dove riceve'},
    {'type': 'p', 'html': "Il dott. Federico Fiori riceve presso <strong>Fi Multicare — Centro Medico Multidisciplinare</strong>, Galleria del Corso 4, 20122 Milano. Le visite sono su appuntamento."},
    {'type': 'p', 'html': "Telefono <a href=\"tel:+390276021568\">02 7602 1568</a> · E-mail <a href=\"mailto:info@fimulticare.it\">info@fimulticare.it</a> · Sito del centro: <a href=\"https://www.fimulticare.it/\">fimulticare.it</a>"},
    {'type': 'img', 'src': '/api/media/mappa-fi-multicare.webp',
     'alt': 'Mappa schematica della zona di Galleria del Corso 4 a Milano, sede di Fi Multicare',
     'caption': 'Fi Multicare, Galleria del Corso 4, 20122 Milano — posizione indicativa.',
     'kind': 'schema', 'width': 1200, 'height': 675},
]
cont_faq = [
    {'q': 'Come si prenota una visita?',
     'a': "La visita si prenota contattando Fi Multicare — Centro Medico Multidisciplinare: telefono 02 7602 1568 oppure e-mail info@fimulticare.it. Le visite sono su appuntamento; la sede è in Galleria del Corso 4, 20122 Milano."},
    {'q': 'Dove si trova lo studio?',
     'a': "Lo studio è presso Fi Multicare — Centro Medico Multidisciplinare, Galleria del Corso 4, 20122 Milano, in pieno centro, a pochi passi da Piazza San Babila."},
    {'q': 'Quali documenti portare alla prima visita?',
     'a': "Alla prima visita è utile portare un documento di identità, il codice fiscale o la tessera sanitaria, gli esami già eseguiti (ecografie, TC o risonanze della parete addominale) e la documentazione degli eventuali interventi chirurgici precedenti."},
]
f = PAGES / 'contatti.json'
page = json.load(open(f))
page['it']['blocks'] = page['it']['blocks'] + cont_blocks_add
page['it']['faq'] = cont_faq
json.dump(page, open(f, 'w'), ensure_ascii=False, indent=1)
print('contatti aggiornato')
