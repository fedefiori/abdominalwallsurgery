#!/usr/bin/env python3
"""Giro 2 hub: recapiti, risposte dirette, titoli in minuscolo, refusi,
percentuali senza fonte, qualifica Unita' Operativa, H2-domande, diastasi,
diapositive radiologia, ancore descrittive, link contatti."""
import json, re, glob
from pathlib import Path

PAGES = Path('/app/backend/data/pages')
TAG = re.compile(r'<[^>]+>')

def txt(h):
    return re.sub(r'\s+', ' ', TAG.sub('', h or '')).strip()

def wc(s):
    return len(txt(s).split())

# ---------------------------------------------------------------- costanti
QUALIFICA_BREVE = "Unità Operativa di Chirurgia della Parete Addominale"
TEL = "+39 02 76021568"
EMAIL_STUDIO = "info@fimulticare.it"

ANSWERS = {
    'radiologia': "Nella chirurgia della parete l'imaging serve a due cose: misurare il difetto prima di operare e riconoscere le complicanze dopo. L'ecografia è l'esame di primo livello, disponibile e ripetibile; la TC serve quando il difetto è ampio o recidivo e va pianificato; la risonanza si riserva ai casi in cui contano i tessuti molli.",
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': "La pre-abilitazione è la preparazione clinica delle settimane che precedono l'intervento sulla parete: peso, glicemia, fumo, nutrizione ed esercizio fisico. Serve perché la recidiva resta il problema principale di questa chirurgia, e arrivare all'operazione nelle migliori condizioni riduce le complicanze e migliora la guarigione.",
    'la-diastasi-dei-muscoli-retti': "In chirurgia della parete la diastasi dei retti conta perché spesso si associa a un'ernia ombelicale: allora non basta chiudere il difetto, va ricostruita la linea mediana. Questa pagina spiega solo che cosa cambia nell'indicazione chirurgica; il percorso completo è su diastasiedintorni.it.",
    'anatomia-della-parete-addominale-e-abdominal-core': "La parete addominale anteriore è formata da cute, grasso, fasce, quattro coppie di muscoli e peritoneo, con la linea alba al centro. Conoscere questi strati è la base per capire dove si aprono ernie e laparoceli, come si classificano e in quale piano si posiziona la rete che li ripara.",
    'la-terapia-chirurgica': "La riparazione di un difetto della parete si costruisce su tre scelte: la via di accesso (aperta, laparoscopica, robotica o endoscopica), il tipo di protesi e il piano in cui viene posizionata. Questa pagina descrive le tecniche principali, dai capisaldi come Rives-Stoppa alle separazioni dei componenti.",
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': "La protesi è una rete che rinforza la parete addominale dopo la chiusura del difetto. Il risultato dipende dal materiale, ma ancora di più dal piano di posizionamento: onlay sopra la fascia, sublay dietro i muscoli, preperitoneale o intraperitoneale. Questa pagina descrive materiali e piani.",
    'le-complicanze-chirurgiche-la-vac-therapy': "Le complicanze di ferita — sieromi, infezioni, deiscenze — sono lo scoglio principale della chirurgia della parete. La VAC therapy è una medicazione a pressione negativa che avvicina i margini della ferita e drena gli essudati in un sistema chiuso, favorendo la guarigione per seconda intenzione.",
    'sintomi-e-complicanze': "Un'ernia della parete si riconosce dal rigonfiamento che compare in piedi o sotto sforzo e rientra da sdraiati. Dolore improvviso, irriducibilità e arrossamento sono invece segni di allarme: indicano incarceramento o strangolamento e richiedono una valutazione chirurgica urgente.",
    'difetti-della-parete-addominale-e-classificazione': "I difetti della parete addominale si classificano per sede, dimensione e origine: primitivi se nascono su una parete integra, incisionali (laparoceli) se compaiono su una cicatrice. La classificazione EHS assegna a ogni ernia una sigla di zona e una classe di misura e guida la scelta tecnica.",
    'contatti': "Il dott. Federico Fiori riceve su appuntamento presso Fi Multicare — Centro Medico Multidisciplinare, Galleria del Corso 4, 20122 Milano: telefono +39 02 76021568, e-mail info@fimulticare.it. Per il contatto diretto della rete: info@federicofiori.com. La valutazione riguarda ernie, laparoceli e gli altri difetti della parete.",
}

TITLES = {
    'home': ("Chirurgia della parete addominale | dott. Federico Fiori",
             "Ernie, laparoceli e difetti della parete addominale: diagnosi, classificazione e chirurgia ricostruttiva a Milano con il dott. Federico Fiori. Info e contatti."),
    'anatomia-della-parete-addominale-e-abdominal-core': ("Anatomia della parete addominale e abdominal core | Fiori",
             "Muscoli retti, obliqui, trasverso e linea alba: l'anatomia della parete addominale spiegata in dettaglio per capire ernie, laparoceli e la loro riparazione."),
    'la-terapia-chirurgica': ("La terapia chirurgica dei difetti della parete addominale",
             "Tecniche di riparazione di ernie e laparoceli della parete: Rives-Stoppa, TAR, separazione dei componenti, chirurgia robotica, endoscopica e mininvasiva."),
    'chi-sono': ("Chi sono | dott. Federico Fiori, chirurgo della parete",
             "Il dott. Federico Fiori, chirurgo generale a Milano, responsabile della Unità Operativa di Chirurgia della Parete Addominale di ASST Santi Paolo e Carlo."),
    'radiologia': ("Radiologia della parete addominale: ecografia, TC e RM",
             "Ecografia, TC e risonanza magnetica nella valutazione dei difetti della parete addominale: che cosa mostra ciascun esame, i limiti e quando è indispensabile."),
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': ("Protesi in chirurgia della parete e piano di posizionamento",
             "Tipi di protesi per ernie e laparoceli e i piani di posizionamento: sottocutaneo onlay, retromuscolare sublay, preperitoneale e intraperitoneale IPOM."),
    'le-complicanze-chirurgiche-la-vac-therapy': ("Complicanze chirurgiche e VAC therapy della parete",
             "Sieromi, infezioni e deiscenze dopo chirurgia della parete addominale: come si riconoscono, come si trattano e quale ruolo ha la VAC therapy nella guarigione."),
    'sintomi-e-complicanze': ("Sintomi dei difetti di parete: riferimento clinico",
             "Sintomi delle ernie e dei laparoceli per tipo di difetto, segni di allarme di incarceramento e strangolamento e quando l'urgenza cambia la strategia chirurgica."),
    'difetti-della-parete-addominale-e-classificazione': ("Classificazione EHS dei difetti di parete: sedi, sigle e misure",
             "La classificazione della European Hernia Society per le ernie della parete addominale: sedi anatomiche M1-L4, dimensioni del difetto e definizioni cliniche."),
    'la-diastasi-dei-muscoli-retti': ("Diastasi dei retti associata a ernia: cosa cambia in chirurgia",
             "Quando la diastasi dei retti si associa a un'ernia ombelicale l'indicazione cambia: va ricostruita la linea mediana. Il percorso completo è su diastasiedintorni.it."),
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': ("Preabilitazione prima dell'intervento sulla parete",
             "Come prepararsi all'intervento sulla parete addominale: controllo di peso e glicemia, stop del fumo, nutrizione ed esercizio fisico prima della chirurgia."),
    'contatti': ("Contatti | chirurgia della parete addominale a Milano",
             "Il dott. Federico Fiori riceve presso Fi Multicare, Galleria del Corso 4, 20122 Milano: telefono +39 02 76021568, e-mail info@fimulticare.it, su appuntamento."),
    'privacy-policy': ("Privacy policy | chirurgia della parete addominale",
             "Informativa privacy del sito chirurgiadellaparete.it: titolare del trattamento, finalità e basi giuridiche, tempi di conservazione e diritti dell'interessato."),
    'cookie-policy': ("Cookie policy | chirurgia della parete addominale Milano",
             "Cookie policy del sito chirurgiadellaparete.it: tipologie di cookie utilizzati, finalità, base giuridica, durata del consenso e come gestirlo o revocarlo."),
}

H2_Q = {
    'anatomia-della-parete-addominale-e-abdominal-core': {
        'Muscolo retto dell\u2019addome': "Che cos'è il muscolo retto dell'addome?",
        'Muscolo obliquo esterno dell\u2019addome': "Che cos'è il muscolo obliquo esterno dell'addome?",
        'Muscolo obliquo interno dell\u2019addome': "Che cos'è il muscolo obliquo interno dell'addome?",
        'Il muscolo trasverso dell\u2019addome': "Che cos'è il muscolo trasverso dell'addome?",
        'Muscolo quadrato dei lombi': "Che cos'è il muscolo quadrato dei lombi?",
        'Muscoli del pavimento pelvico': 'Quali sono i muscoli del pavimento pelvico?',
        'Muscoli dell\u2019anca': "Quali muscoli dell'anca completano l'abdominal core?",
        'Muscoli paravertebrali': 'Che cosa sono i muscoli paravertebrali?',
        'Diaframma': 'Che ruolo ha il diaframma nella pressione addominale?',
    },
    'contatti': {
        'Richiedi maggiori informazioni': 'Come richiedere maggiori informazioni?',
        'Dove riceve': 'Dove si trova lo studio?',
    },
    'la-diastasi-dei-muscoli-retti': {
        'Che cos\'è la diastasi dei muscoli retti': "Che cos'è la diastasi dei retti?",
        'Perché la diastasi compare in questo sito': 'Perché la diastasi conta in chirurgia della parete?',
        'Che cosa cambia nell\'indicazione chirurgica': "Quando la diastasi cambia l'intervento sull'ernia?",
        'I limiti di questa pagina': 'Quali sono i limiti di questa pagina?',
    },
}

# h2 di servizio nei contatti -> paragrafi con etichetta in grassetto
CONTATTI_DEMOTE = {'Indirizzo', 'E-mail', 'Telefono', 'Seguici su Facebook', 'Seguici su Youtube'}

ANCHOR_FIX = {
    ('anatomia-della-parete-addominale-e-abdominal-core', 'le-protesi'): 'i piani di posizionamento della protesi',
    ('anatomia-della-parete-addominale-e-abdominal-core', 'la-terapia-chirurgica'): 'la terapia chirurgica della parete',
    ('sintomi-e-complicanze', 'la-terapia-chirurgica'): "l'intervento chirurgico sulla parete",
    ('sintomi-e-complicanze', 'difetti-della-parete'): 'la classificazione dei difetti di parete',
    ('sintomi-e-complicanze', 'radiologia'): 'la diagnostica per immagini della parete',
    ('difetti-della-parete-addominale-e-classificazione', 'la-terapia-chirurgica'): "l'intervento di riparazione",
    ('difetti-della-parete-addominale-e-classificazione', 'le-protesi'): 'la rete protesica e il suo piano',
    ('la-terapia-chirurgica', 'le-protesi'): 'le protesi della parete addominale',
    ('la-terapia-chirurgica', 'preabilitazione'): "la pre-abilitazione prima dell'intervento",
    ('radiologia', 'difetti-della-parete'): 'la classificazione dei difetti di parete',
    ('radiologia', 'la-terapia-chirurgica'): 'la terapia chirurgica della parete',
    ('le-complicanze-chirurgiche-la-vac-therapy', 'la-terapia-chirurgica'): 'la terapia chirurgica della parete',
    ('le-complicanze-chirurgiche-la-vac-therapy', 'sintomi-e-complicanze'): "i sintomi che precedono l'intervento",
    ('preabilitazione-dei-pazienti-all-intervento-chirurgico', 'la-terapia-chirurgica'): 'la terapia chirurgica della parete',
    ('preabilitazione-dei-pazienti-all-intervento-chirurgico', 'contatti'): 'i contatti per la valutazione specialistica',
}

REFUSI = [
    ('superpecialistica', 'superspecialistica'),
    ('affontare', 'affrontare'),
]

def global_hygiene(s):
    s = s.replace('\xa0', ' ')
    s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    s = re.sub(r' {2,}', ' ', s)
    for k, v in REFUSI:
        s = s.replace(k, v)
    s = s.replace('fedefiori@tiscali.it', EMAIL_STUDIO)
    s = re.sub(r'02 7602 1568|02 76021568', TEL, s)
    s = s.replace('Struttura Semplice di Chirurgia della Parete Addominale', QUALIFICA_BREVE)
    s = s.replace('Struttura Semplice', 'Unità Operativa')
    s = re.sub(r'(?<=[a-z] )(Anatomia|Fisiopatologia)(?=,| )', lambda m: m.group(1).lower(), s)
    return s

for f in sorted(PAGES.glob('*.json')):
    slug = f.stem
    p = json.load(open(f))
    it = p['it']
    for b in it['blocks']:
        if 'html' in b: b['html'] = global_hygiene(b['html'])
        if 'text' in b: b['text'] = global_hygiene(b['text'])
        if 'items' in b: b['items'] = [global_hygiene(x) for x in b['items']]
        if b.get('caption'): b['caption'] = global_hygiene(b['caption'])
        if b.get('alt'): b['alt'] = global_hygiene(b['alt'])
    if it.get('answer'): it['answer'] = global_hygiene(it['answer'])
    for fq in it.get('faq') or []:
        fq['q'] = global_hygiene(fq['q']); fq['a'] = global_hygiene(fq['a'])

    # risposte dirette nuove (mai identiche al primo paragrafo)
    if slug in ANSWERS:
        it['answer'] = ANSWERS[slug]
    # titoli e description
    if slug in TITLES:
        it['metaTitle'], it['metaDescription'] = TITLES[slug]
    # h1 in minuscolo di rete (tranne sigle e nomi propri)
    h1 = it.get('h1', '')
    it['h1'] = re.sub(r'\be Classificazione\b', 'e classificazione', h1)

    # H2 -> domande
    qmap = H2_Q.get(slug, {})
    for b in it['blocks']:
        if b['type'] == 'h2' and b.get('text') in qmap:
            b['text'] = qmap[b['text']]
        if slug == 'contatti' and b['type'] == 'h2' and b.get('text') in CONTATTI_DEMOTE:
            b['type'], b['html'] = 'p', f"<strong>{b['text']}</strong>"
            b.pop('text', None)

    # ancore descrittive
    for b in it['blocks']:
        for key in ('html',):
            if key not in b: continue
            for (sl, href_part), phrase in ANCHOR_FIX.items():
                if sl != slug: continue
                pat = re.compile(r'(<a href="[^"]*' + re.escape(href_part) + r'[^"]*">)[^<]{1,40}(</a>)')
                def repl(m):
                    inner = TAG.sub('', m.group(0))
                    inner_txt = m.group(0)[len(m.group(1)):-len(m.group(2))]
                    return m.group(1) + (phrase if len(inner_txt.split()) <= 2 else inner_txt) + m.group(2)
                b[key] = pat.sub(repl, b[key])

    json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)
    print('fix base:', slug)

# ---------------------------------------------------------------- preabilitazione: percentuali senza fonte
f = PAGES / 'preabilitazione-dei-pazienti-all-intervento-chirurgico.json'
p = json.load(open(f))
bl = p['it']['blocks']
for i, b in enumerate(bl):
    h = b.get('html', '')
    if 'Circa il 24' in h or 'circa il 24' in h:
        bl[i] = {'type': 'p', 'html': "I tassi di recidiva dopo chirurgia riparativa di un difetto primitivo della parete addominale anteriore sono un elemento da conoscere e considerare. La recidiva resta il problema principale di questa chirurgia, con differenze ampie fra le casistiche: è per questo che la preparazione all'intervento conta quanto la tecnica."}
    elif 'tra il 10 e il 60' in h:
        bl[i] = {'type': 'p', 'html': "Anche nella riparazione dell'ernia incisionale la recidiva resta l'esito da temere di più: la pre-abilitazione serve ad abbassarne il rischio prima dell'intervento."}
p['it']['blocks'] = bl
json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)
print('preabilitazione: percentuali senza fonte riformulate')

# ---------------------------------------------------------------- radiologia: via le due diapositive, frase sobria
f = PAGES / 'radiologia.json'
p = json.load(open(f))
bl = p['it']['blocks']
before = len([b for b in bl if b['type'] == 'img'])
bl = [b for b in bl if not (b['type'] == 'img' and b['src'].split('/')[-1] in (
    'ecografia-parete-addominale.webp', 'tc-e-rm-nella-valutazione-della-parete-addominale.webp'))]
for i, b in enumerate(bl):
    if b['type'] == 'p' and 'operatore-dipendente' in b.get('html', ''):
        bl.insert(i + 1, {'type': 'p', 'html': "L'affidabilità dell'ecografia dipende dall'operatore: va eseguita da chi conosce la parete addominale."})
        break
p['it']['blocks'] = bl
json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)
print(f'radiologia: immagini {before} -> {len([b for b in bl if b["type"]=="img"])}')

# ---------------------------------------------------------------- diastasi: via le FAQ (pagina breve 250-350)
f = PAGES / 'la-diastasi-dei-muscoli-retti.json'
p = json.load(open(f))
p['it']['faq'] = []
json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)
print('diastasi: faq rimosse, corpo invariato')

# ---------------------------------------------------------------- contatti: link interni nel corpo
f = PAGES / 'contatti.json'
p = json.load(open(f))
bl = p['it']['blocks']
link_p = {'type': 'p', 'html': 'Prima della visita può essere utile leggere come funziona la <a href="/preabilitazione-dei-pazienti-all-intervento-chirurgico/">pre-abilitazione prima dell\u2019intervento</a>, la descrizione della <a href="/la-terapia-chirurgica/">terapia chirurgica della parete</a> e il profilo del <a href="/chi-sono/">dott. Federico Fiori</a>.'}
if not any('preabilitazione-dei-pazienti' in b.get('html', '') for b in bl):
    bl.append(link_p)
p['it']['blocks'] = bl
json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)
print('contatti: 3 link interni aggiunti')

# ---------------------------------------------------------------- report finale
print()
print('=== report ===')
for f in sorted(PAGES.glob('*.json')):
    p = json.load(open(f)); it = p['it']; bl = it['blocks']
    w = sum(wc(b.get('html', '') or b.get('text', '')) + sum(wc(x) for x in b.get('items', [])) for b in bl)
    w += len(it.get('answer', '').split()) + sum(len(x['q'].split()) + len(x['a'].split()) for x in it.get('faq', []))
    h2 = [b for b in bl if b['type'] == 'h2']
    q = len([b for b in h2 if '?' in b.get('text', '')])
    links = sum(b.get('html', '').count('href="/') for b in bl) + len(it.get('related', []))
    tabs = len([b for b in bl if b['type'] == 'table'])
    t, d = it['metaTitle'], it['metaDescription']
    print(f"{p['path'][:52]:54s} w={w:5d} h2={len(h2):2d} q={q:2d} link={links:2d} tab={tabs} faq={len(it.get('faq',[]))} t={len(t)} d={len(d)}")
EOF = None
