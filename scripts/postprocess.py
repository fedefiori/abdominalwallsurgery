#!/usr/bin/env python3
"""Post-processing: pulizia shortcode Divi, regole anti-doppione (punto 4),
risposte dirette e FAQ (risposte verbatim dal testo del chirurgo)."""
import json, re
from pathlib import Path

PAGES = Path('/app/backend/data/pages')
HUB = 'https://www.federicofiori.com'
DIA = 'https://www.diastasiedintorni.it'
SC_RE = re.compile(r'\[/?et_pb_[^\]]*\]')
TAG_RE = re.compile(r'<[^>]+>')

def txt(html):
    return re.sub(r'\s+', ' ', TAG_RE.sub('', html or '')).strip()

def wc(s):
    return len(txt(s).split())

def trim_words(s, lo, hi):
    """Tronca a confine di frase tra lo e hi parole."""
    words = s.split()
    if len(words) <= hi:
        return s
    cut = ' '.join(words[:hi])
    m = list(re.finditer(r'[.!?](?:\s|$)', cut))
    for mm in reversed(m):
        cand = cut[:mm.end()].strip()
        if len(cand.split()) >= lo:
            return cand
    return ' '.join(words[:hi]) + '…'

def clean_shortcodes(blocks):
    out = []
    for b in blocks:
        b = dict(b)
        if 'html' in b:
            b['html'] = SC_RE.sub('', b['html'])
        if 'text' in b:
            b['text'] = SC_RE.sub('', b['text'])
        if 'items' in b:
            b['items'] = [SC_RE.sub('', i) for i in b['items']]
        if b['type'] == 'p' and wc(b.get('html', '')) == 0:
            continue
        if b['type'] in ('h2', 'h3') and not b.get('text', '').strip():
            continue
        if b['type'] == 'ul' and not [i for i in b['items'] if wc(i)]:
            continue
        out.append(b)
    return out

def find_para(blocks, keyword):
    kw = keyword.lower()
    for b in blocks:
        if b['type'] == 'p' and kw in txt(b.get('html', '')).lower():
            return txt(b['html'])
        if b['type'] == 'ul':
            for i in b['items']:
                if kw in txt(i).lower():
                    return txt(i)
    return None

def faq_from(page_blocks, spec):
    faq = []
    for q, kw in spec:
        a = find_para(page_blocks, kw)
        if a:
            faq.append({'q': q, 'a': trim_words(a, 40, 90)})
    return faq

def direct_answer(blocks, lo=40, hi=70):
    for b in blocks:
        if b['type'] == 'p' and wc(b.get('html', '')) >= lo:
            return trim_words(txt(b['html']), lo, hi)
    for b in blocks:
        if b['type'] == 'p' and wc(b.get('html', '')) >= 15:
            return txt(b['html'])
    return ''

# ---------------------------------------------------------------- diastasi (a)
DIASTASI_H1 = 'La diastasi dei muscoli retti in chirurgia della parete'
DIASTASI_BLOCKS = [
    {'type': 'p', 'html': f'<a href="{DIA}">Tutto il percorso della diastasi dei retti — sintomi, misurazione, riabilitazione, intervento e risultati — è trattato su diastasiedintorni.it</a>, il sito verticale della rete dedicato a questo argomento. In questa pagina la diastasi è descritta solo per quello che conta nella chirurgia della parete addominale.'},
    {'type': 'h2', 'text': "Che cos'è la diastasi dei muscoli retti"},
    {'type': 'p', 'html': "La diastasi dei muscoli retti è l'allontanamento dei due muscoli retti dell'addome sulla linea alba, la fascia fibrosa che li unisce sulla linea mediana. Non è una lesione della fascia e non è un'ernia: la parete resta continua, ma è assottigliata e cede sotto pressione."},
    {'type': 'h2', 'text': "Perché la diastasi compare in questo sito"},
    {'type': 'p', 'html': "La diastasi si associa spesso a ernia ombelicale o a piccoli difetti della linea mediana. Quando i due problemi coesistono la scelta tecnica cambia: non basta chiudere il difetto erniario, va ricostruita l'intera linea mediana, altrimenti la riparazione resta esposta alla recidiva."},
    {'type': 'h2', 'text': "Che cosa cambia nell'indicazione chirurgica"},
    {'type': 'p', 'html': "Nella valutazione chirurgica contano la dimensione del difetto erniario associato, la qualità della linea alba residua e la presenza di eccesso cutaneo. Da questi tre elementi dipendono la via d'accesso, il piano di posizionamento della protesi e l'eventuale necessità di un rimodellamento cutaneo. Un difetto piccolo con linea alba solida può essere trattato in modo diverso da una diastasi ampia con ernia ombelicale e cute in eccesso, che richiede una ricostruzione completa della linea mediana."},
    {'type': 'h2', 'text': 'I limiti di questa pagina'},
    {'type': 'p', 'html': f"La valutazione morfo-funzionale della diastasi e il percorso riabilitativo non sono trattati in questo sito. Per la misurazione, i sintomi, la riabilitazione e i risultati dell'intervento il riferimento è la <a href=\"{DIA}\">diastasi dei muscoli retti trattata su diastasiedintorni.it</a>."},
]

# ---------------------------------------------------------------- FAQ config
FAQ_SPEC = {
    'anatomia-della-parete-addominale-e-abdominal-core': [
        ("Quali sono i muscoli principali della parete addominale?", 'principali muscoli della parete addominale'),
        ("Che cos'è l'abdominal core?", 'core'),
        ("Che cos'è la linea alba?", 'linea alba'),
        ("Perché l'anatomia conta per capire ernie e laparoceli?", 'difetti della parete addominale'),
    ],
    'la-terapia-chirurgica': [
        ("Quali vie di accesso esistono per riparare un difetto della parete?", 'via aperta'),
        ("Che cos'è la tecnica di Rives-Stoppa?", 'Rives'),
        ("In che cosa consiste la separazione dei componenti?", 'component separation'),
        ("Quali vantaggi offre la chirurgia robotica della parete?", 'robotica'),
    ],
    'radiologia': [
        ("A che cosa serve l'ecografia della parete addominale?", 'imaging di primo approccio'),
        ("Quali limiti ha l'ecografia nella parete addominale?", 'operatore-dipendente'),
        ("Quando serve la TC nella valutazione della parete?", 'tomografia'),
    ],
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': [
        ("Che cos'è una protesi in chirurgia della parete?", 'costituite da'),
        ("Quali piani di posizionamento esistono per la protesi?", 'posizionamento'),
        ("Come si sceglie il piano di posizionamento della protesi?", 'piano'),
    ],
    'le-complicanze-chirurgiche-la-vac-therapy': [
        ("Quali complicanze può avere la chirurgia della parete?", 'può essere aperta'),
        ("Quali complicanze di ferita si possono verificare?", 'Complicanze di ferita'),
        ("Che cos'è la VAC therapy?", 'VAC-therapy'),
    ],
    'sintomi-e-complicanze': [
        ("Quali sintomi provoca un'ernia della parete addominale?", 'sintom'),
        ("Che cos'è un'ernia incarcerata?", 'incarcerat'),
        ("Quando un'ernia diventa un'urgenza?", 'strangolat'),
    ],
    'difetti-della-parete-addominale-e-classificazione': [
        ("Come si classificano le ernie della parete addominale?", 'classificazioni'),
        ("Che cosa misura la classificazione EHS?", 'EHS'),
        ("Quali sono le sedi dei difetti della parete addominale?", 'sedi'),
    ],
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': [
        ("Quali fattori alterano la guarigione prima dell'intervento?", 'fumo'),
        ("Come incide il peso sull'esito della chirurgia della parete?", 'peso'),
        ("Perché si prepara il paziente prima dell'intervento?", 'intervento'),
    ],
    'la-diastasi-dei-muscoli-retti': [
        ("La diastasi dei retti è un'ernia?", 'Non è una lesione della fascia'),
        ("Perché la diastasi conta nella chirurgia della parete?", 'si associa spesso a ernia ombelicale'),
        ("Dove trovo il percorso completo della diastasi?", 'diastasiedintorni'),
    ],
    'chi-sono': [
        ("Chi è il dott. Federico Fiori?", 'Chirurgia Generale'),
        ("Dove opera il dott. Federico Fiori?", 'Divisione di Chirurgia'),
    ],
    'contatti': [
        ("Dove si trova lo studio del dott. Federico Fiori?", 'Galleria del corso'),
    ],
}

KIND = {
    'home': 'home',
    'chi-sono': 'profile',
    'contatti': 'contact',
    'privacy-policy': 'legal',
    'cookie-policy': 'legal',
    'anatomia-della-parete-addominale-e-abdominal-core': 'clinical',
    'la-terapia-chirurgica': 'clinical-procedure',
    'radiologia': 'clinical',
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': 'clinical-procedure',
    'le-complicanze-chirurgiche-la-vac-therapy': 'clinical',
    'sintomi-e-complicanze': 'clinical-condition',
    'difetti-della-parete-addominale-e-classificazione': 'classifications',
    'la-diastasi-dei-muscoli-retti': 'clinical-condition',
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': 'clinical',
}

ANSWER_OVERRIDE = {
    'home': "La chirurgia della parete addominale è la branca della chirurgia generale che ripara i difetti della parete: ernie, laparoceli e diastasi dei muscoli retti. Questo sito, a cura del dott. Federico Fiori, spiega anatomia, classificazioni, sintomi, esami e tecniche di riparazione.",
    'contatti': "Per contattare il dott. Federico Fiori, chirurgo della parete addominale: sede in Galleria del Corso 4, 20122 Milano; telefono 02 76021568; e-mail fedefiori@tiscali.it. È possibile richiedere una valutazione per ernie, laparoceli e altri difetti della parete.",
    'privacy-policy': "Questa pagina è l'informativa privacy di chirurgiadellaparete.it: descrive il titolare del trattamento, le finalità e le basi giuridiche del trattamento dei dati personali, i destinatari, i tempi di conservazione e i diritti che l'interessato può esercitare.",
    'cookie-policy': "Questa pagina è la cookie policy di chirurgiadellaparete.it: elenca le tipologie di cookie utilizzate dal sito, le loro finalità e durata, e spiega come l'utente può gestire, modificare o revocare il consenso all'uso dei cookie.",
    'la-diastasi-dei-muscoli-retti': "La diastasi dei muscoli retti è l'allontanamento dei due muscoli retti sulla linea alba: non è una lesione della fascia né un'ernia. Conta in chirurgia della parete perché si associa spesso a ernia ombelicale e cambia la scelta tecnica dell'intervento.",
}

for f in sorted(PAGES.glob('*.json')):
    slug = f.stem
    page = json.load(open(f))
    it = page['it']
    blocks = clean_shortcodes(it['blocks'])

    if slug == 'la-diastasi-dei-muscoli-retti':
        imgs = [b for b in blocks if b['type'] == 'img'][:3]
        new = list(DIASTASI_BLOCKS)
        # inserisci le 3 immagini conservate
        if imgs:
            new.insert(2, imgs[0])
            if len(imgs) > 1: new.insert(5, imgs[1])
            if len(imgs) > 2: new.append(imgs[2])
        blocks = new
        it['h1'] = DIASTASI_H1

    elif slug == 'sintomi-e-complicanze':
        blocks.insert(1, {'type': 'plainBox', 'html':
            f"Questa pagina è il riferimento clinico su sintomi e complicanze dei difetti della parete addominale; la versione per il Paziente, divulgativa, è l'articolo <a href=\"{HUB}/articoli/sintomi-complicanze-difetti-parete-addominale\">Sintomi e complicanze dei difetti della parete addominale</a> pubblicato su federicofiori.com."})

    elif slug == 'difetti-della-parete-addominale-e-classificazione':
        blocks.insert(1, {'type': 'plainBox', 'html':
            f"Per gli acronimi e le sigle usati in questa pagina il riferimento è il <a href=\"{HUB}/glossario-acronimi-chirurgia-parete-addominale\">glossario degli acronimi della chirurgia della parete addominale</a> su federicofiori.com; la versione divulgativa di questo argomento è l'articolo <a href=\"{HUB}/articoli/difetti-parete-addominale-classificazione\">Difetti della parete addominale e classificazione</a>."})

    elif slug == 'la-terapia-chirurgica':
        out, skip = [], set()
        for i, b in enumerate(blocks):
            t = txt(b.get('html', '') or b.get('text', ''))
            if i in skip:
                continue
            if b['type'] == 'p' and ('TESAR, o Totally Endoscopic' in t or 'La tecnica TESAR coinvolge' in t or 'I risultati della TESAR' in t):
                if 'TESAR, o Totally Endoscopic' in t:
                    out.append({'type': 'p', 'html':
                        f"La <strong>TESAR</strong> (Totally Endoscopic Sublay Anterior Repair), presentata dal nostro gruppo nel 2018 e pubblicata nel 2019, è la tecnica endoscopica per via anteriore con protesi in piano sublay retromuscolare sviluppata per i difetti della linea mediana. La descrizione completa della tecnica, i dati scientifici pubblicati e i risultati sono la fonte canonica su federicofiori.com: <a href=\"{HUB}/tecnica-tesar\">la tecnica TESAR</a>."})
                continue
            out.append(b)
        blocks = out

    elif slug == 'chi-sono':
        out, dropping = [], False
        for b in blocks:
            t = (b.get('text') or txt(b.get('html', '')))
            if b['type'] == 'p' and 'TITOLI DI STUDIO' in t:
                dropping = 'skip1'; continue
            if dropping == 'skip1' and b['type'] == 'ul':
                dropping = False; continue
            dropping = False
            if b['type'] == 'h2' and ('Congressi e Convegni' in t or 'qualità di Esperto o Relatore' in t or 'pubblicazioni' in t.lower()):
                dropping = 'skipul'; continue
            if dropping == 'skipul' and b['type'] == 'ul':
                dropping = False; continue
            dropping = False
            out.append(b)
        out.append({'type': 'plainBox', 'html':
            f"Curriculum completo, titoli, congressi, pubblicazioni e galleria dei risultati sono pubblicati sull'hub della rete: <a href=\"{HUB}/curriculum\">il curriculum del dott. Federico Fiori su federicofiori.com</a>."})
        blocks = [b for b in out if not (b['type'] in ('p',) and wc(b.get('html', '')) == 0)]

    elif slug == 'contatti':
        out = []
        seen = set()
        for b in blocks:
            t = txt(b.get('html', '') or b.get('text', '')).strip()
            if b['type'] == 'p' and t in ('Nome', 'Cognome', 'Telefono', 'Indirizzo E-mail', 'Messaggio', 'Invia', '* Campi obbligatori.', ''):
                continue
            if b['type'] == 'p' and t.startswith('Trattamento Dati'):
                continue
            if b['type'] == 'p' and t.startswith('Gli eventuali dati personali'):
                if 'privacy-note' in seen:
                    continue
                seen.add('privacy-note')
            out.append(b)
        blocks = out

    it['blocks'] = blocks
    it['kind'] = KIND.get(slug, 'clinical')
    it['answer'] = ANSWER_OVERRIDE.get(slug) or direct_answer(blocks)
    it['faq'] = faq_from(blocks, FAQ_SPEC.get(slug, []))
    words = sum(wc(b.get('html', '') or b.get('text', '')) + sum(wc(i) for i in b.get('items', [])) for b in blocks)
    imgs = len([b for b in blocks if b['type'] == 'img'])
    json.dump(page, open(f, 'w'), ensure_ascii=False, indent=1)
    print(f"{slug:70s} parole={words:5d} img={imgs} faq={len(it['faq'])} answer={wc(it['answer'])}w")
