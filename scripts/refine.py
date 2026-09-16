#!/usr/bin/env python3
"""Giro di correzioni hub: forma del testo (non le parole), H2-domande,
tabelle dai dati della pagina, link interni, chi-sono, home, contatti, cookie."""
import json, re, copy
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

PAGES = Path('/app/backend/data/pages')
HUB = 'https://www.federicofiori.com'
DIA = 'https://www.diastasiedintorni.it'

CONCAT_RE = re.compile(r'([a-zà-ù])([A-ZÀ-Ù])')
ACCENTI = {"puo'": 'può', "piu'": 'più', "cosi'": 'così', "cioe'": 'cioè',
           "pero'": 'però', "qualita'": 'qualità', "nonche'": 'nonché',
           "attualita'": 'attualità', "dignostico": 'diagnostico'}

def hygiene(html):
    if not html:
        return html
    soup = BeautifulSoup(html, 'lxml')
    for t in soup.find_all(['em', 'i']):
        t.unwrap()
    for node in soup.find_all(string=True):
        s = str(node)
        s = s.replace('\xa0', ' ')
        s = CONCAT_RE.sub(r'\1 \2', s)
        for k, v in ACCENTI.items():
            s = s.replace(k, v)
        s = re.sub(r"\b([LD]) '(?=\w)", r"\1'", s)
        s = re.sub(r'\bpazienti\b', 'Pazienti', s)
        s = re.sub(r'\bpaziente\b', 'Paziente', s)
        s = re.sub(r' {2,}', ' ', s)
        node.replace_with(s)
    out = soup.decode()
    out = re.sub(r'^<html><body>|</body></html>$', '', out)
    return out.strip()

def plain_text(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html or '')).strip()

def wc(s):
    return len(plain_text(s).split())

def clean_block(b):
    b = copy.deepcopy(b)
    if 'html' in b:
        b['html'] = hygiene(b['html'])
    if 'text' in b:
        b['text'] = re.sub(r' {2,}', ' ', b['text'].replace('\xa0', ' ')).strip()
    if 'items' in b:
        b['items'] = [hygiene(i) for i in b['items']]
    if b.get('caption'):
        b['caption'] = hygiene(b['caption'])
    return b

def split_long(blocks):
    out = []
    for b in blocks:
        if b['type'] == 'p' and wc(b['html']) > 110:
            html = b['html']
            text_len = len(plain_text(html))
            best, best_d = None, 1e9
            for m in re.finditer(r'(?<=[.!?]) (?=[A-ZÀ-Ù])', html):
                d = abs(m.end() - len(html) / 2)
                if d < best_d:
                    best, best_d = m.end(), d
            if best:
                out.append({'type': 'p', 'html': html[:best].strip()})
                out.append({'type': 'p', 'html': html[best:].strip()})
                continue
        out.append(b)
    return out

SCHEMI = {'muscolo-retto-addome', 'muscolo-obliquo-addome', 'muscoli-paravertebrali',
          'riferimenti-anatomici-parete-addominale', 'abdominal-core',
          'difetti-parete-addominale', 'european-hernia-society-hernia-classification',
          'hernia-incisionali', 'incisional-hernia-classification-ehs', 'hernia-defect',
          'diastasi-muscoli-retti-addome-01', 'diastasi-muscoli-retti-addome-02',
          'diastasi-muscoli-retti-addome-03', 'ipom', 'tar-3',
          'anterior-component-separation', 'modifica-endoscopica',
          'complicazioni-delle-ernie', 'sintomatologia-01',
          'logo-chirurgia-della-parete', 'mappa-fi-multicare'}

def tag_images(blocks):
    for b in blocks:
        if b['type'] == 'img':
            stem = b['src'].split('/')[-1].replace('.webp', '')
            b['kind'] = 'schema' if stem in SCHEMI else 'photo'
            if not b.get('caption'):
                b['caption'] = plain_text(b.get('alt', ''))
    return blocks

def inject_link(blocks, keyword, href, anchor=None):
    """Primo paragrafo che contiene keyword: la avvolge in un link interno."""
    kw = keyword.lower()
    for b in blocks:
        if b['type'] != 'p':
            continue
        html = b['html']
        if 'href=' in html and kw in html.lower() and f'href="{href}"' in html:
            return True
        idx = html.lower().find(kw)
        if idx >= 0:
            # non dentro un tag
            before = html[:idx]
            if before.rfind('<') > before.rfind('>'):
                continue
            frag = html[idx:idx + len(keyword)]
            b['html'] = (html[:idx] + f'<a href="{href}">{anchor or frag}</a>' + html[idx + len(keyword):])
            return True
    return False

def table(headers, rows, caption=None, source=None):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    trs = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    html = f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'
    if caption:
        html += f'<p class="pw-table-caption">{caption}</p>'
    if source:
        html += f'<p class="pw-table-source">Fonte: {source}</p>'
    return {'type': 'table', 'html': html}

def rel(*items):
    return [{'label': l, 'href': h} for l, h in items]

P = lambda s: f'/{s}/'
ART = {
    'tesar': '/articoli/tecnica-tesar-riparazione-endoscopica-sublay-anteriore',
    'laparocele': '/articoli/laparocele-dopo-intervento-addominale-quando-operare',
    'recidiva': '/articoli/ernia-ombelicale-recidiva-come-prevenirla',
}

# ---------------------------------------------------------------- H2 -> domande
H2_MAP = {
    'anatomia-della-parete-addominale-e-abdominal-core': {
        0: None, 1: "Com'è fatta la parete addominale?", 46: "Che cos'è l'abdominal core?",
        107: 'Quali funzioni ha l\'abdominal core?', 118: 'Quali sono i riferimenti anatomici della parete addominale?'},
    'sintomi-e-complicanze': {
        0: None, 2: "Quali sintomi dà un'ernia della parete addominale?",
        11: "Che cos'è l'insufficienza muscolare della parete?",
        15: 'Che cosa succede se non si interviene?',
        28: "Quando un rigonfiamento diventa un'urgenza?"},
    'difetti-della-parete-addominale-e-classificazione': {
        0: None, 3: 'Quali sono i difetti della parete addominale anteriore?',
        6: 'Quali sono i difetti primitivi della parete?',
        18: 'Che cosa cambia fra ernia primaria e laparocele?',
        19: 'Come si classificano i difetti della parete addominale?',
        24: 'Come classifica la EHS le ernie incisionali?',
        27: "Che cos'è un disastro di parete?"},
    'la-terapia-chirurgica': {
        0: None, 2: 'Quali tecniche si usano oggi per la parete addominale?',
        15: "Che cos'è l'approccio posteriore intraperitoneale?",
        20: "Che cos'è l'approccio posteriore endo-laparoscopico?",
        25: "Che cos'è l'approccio posteriore extraperitoneale endoscopico?",
        30: "Che cos'è l'approccio anteriore?",
        32: "Che cos'è la protesi onlay, sovra-muscolare?",
        34: "Che cos'è la protesi sublay, retro-muscolare?",
        40: 'Che cosa cambia con la chirurgia robotica?',
        57: 'Quali sono i capisaldi della chirurgia di parete?',
        58: 'In che cosa consiste la riparazione secondo Rives e Stoppa?',
        67: "Che cos'è la TAR?",
        74: 'Quando serve la separazione delle componenti?',
        84: "Che cos'è la modifica endoscopica della separazione dei componenti?",
        93: 'Che cosa sono gli small bites nella sintesi della parete addominale?'},
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': {
        0: None, 2: 'Quali protesi si usano nella parete addominale?',
        5: 'Di quali materiali sono fatte le protesi?',
        25: 'Come si classificano le protesi?',
        31: 'In quale piano si posiziona la protesi?'},
    'radiologia': {
        0: None, 1: 'Quali esami servono prima di operare la parete?',
        30: 'Che cosa cerca il chirurgo nella TC e nella risonanza?'},
    'le-complicanze-chirurgiche-la-vac-therapy': {
        0: None, 1: 'Quali complicanze può avere la chirurgia della parete?',
        11: "Che cos'è la VAC therapy e quando si usa?"},
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': {
        0: None, 1: "Che cos'è la pre-abilitazione e a che cosa serve?"},
}

# ---------------------------------------------------------------- link interni inline
INLINE = {
    'anatomia-della-parete-addominale-e-abdominal-core': [
        ('classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('chirurgica', P('la-terapia-chirurgica')),
        ('protesi', P('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi'))],
    'sintomi-e-complicanze': [
        ('laparocele', ART['laparocele']),
        ('ernia ombelicale', ART['recidiva']),
        ('TC', P('radiologia')),
        ('intervento chirurgico', P('la-terapia-chirurgica'))],
    'difetti-della-parete-addominale-e-classificazione': [
        ('laparoceli', ART['laparocele']),
        ('anatomia', P('anatomia-della-parete-addominale-e-abdominal-core')),
        ('protesi', P('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi'))],
    'la-terapia-chirurgica': [
        ('TESAR', ART['tesar']),
        ('protesi', P('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi')),
        ('pre-abilitazione', P('preabilitazione-dei-pazienti-all-intervento-chirurgico')),
        ('VAC', P('le-complicanze-chirurgiche-la-vac-therapy'))],
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': [
        ('recidiva', ART['recidiva']),
        ('classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('complicanz', P('le-complicanze-chirurgiche-la-vac-therapy'))],
    'radiologia': [
        ('sintomi', P('sintomi-e-complicanze')),
        ('classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('chirurgica', P('la-terapia-chirurgica'))],
    'le-complicanze-chirurgiche-la-vac-therapy': [
        ('terapia chirurgica', P('la-terapia-chirurgica')),
        ('sintomi', P('sintomi-e-complicanze'))],
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': [
        ('intervento chirurgico', P('la-terapia-chirurgica')),
        ('specialista', P('contatti'))],
    'la-diastasi-dei-muscoli-retti': [
        ('ernia ombelicale', ART['recidiva']),
        ('difetto', P('difetti-della-parete-addominale-e-classificazione'))],
}

RELATED = {
    'anatomia-della-parete-addominale-e-abdominal-core': rel(
        ('Difetti della parete addominale e classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('La terapia chirurgica', P('la-terapia-chirurgica')),
        ('Le protesi e il piano di posizionamento', P('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi'))),
    'sintomi-e-complicanze': rel(
        ('Difetti della parete addominale e classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('Radiologia della parete addominale', P('radiologia')),
        ('La terapia chirurgica', P('la-terapia-chirurgica'))),
    'difetti-della-parete-addominale-e-classificazione': rel(
        ('Anatomia della parete addominale', P('anatomia-della-parete-addominale-e-abdominal-core')),
        ('Le protesi e il piano di posizionamento', P('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi')),
        ('Laparocele dopo un intervento addominale: quando operare (articolo)', ART['laparocele'])),
    'la-terapia-chirurgica': rel(
        ('Le protesi e il piano di posizionamento', P('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi')),
        ('La pre-abilitazione prima dell\u2019intervento', P('preabilitazione-dei-pazienti-all-intervento-chirurgico')),
        ('Le complicanze chirurgiche e la VAC therapy', P('le-complicanze-chirurgiche-la-vac-therapy')),
        ('La tecnica TESAR sull\u2019hub', f'{HUB}/tecnica-tesar')),
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': rel(
        ('La terapia chirurgica', P('la-terapia-chirurgica')),
        ('Difetti della parete addominale e classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('Le complicanze chirurgiche e la VAC therapy', P('le-complicanze-chirurgiche-la-vac-therapy'))),
    'radiologia': rel(
        ('Sintomi e complicanze', P('sintomi-e-complicanze')),
        ('Difetti della parete addominale e classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('La terapia chirurgica', P('la-terapia-chirurgica'))),
    'le-complicanze-chirurgiche-la-vac-therapy': rel(
        ('La terapia chirurgica', P('la-terapia-chirurgica')),
        ('Sintomi e complicanze', P('sintomi-e-complicanze'))),
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': rel(
        ('La terapia chirurgica', P('la-terapia-chirurgica')),
        ('Contatti e prenotazione della valutazione', P('contatti'))),
    'la-diastasi-dei-muscoli-retti': rel(
        ('Il percorso completo della diastasi su diastasiedintorni.it', DIA),
        ('Difetti della parete addominale e classificazione', P('difetti-della-parete-addominale-e-classificazione')),
        ('Ernia ombelicale recidiva: come prevenirla (articolo)', ART['recidiva'])),
    'chi-sono': rel(
        ('La terapia chirurgica', P('la-terapia-chirurgica')),
        ('Contatti e dove riceve', P('contatti')),
        ('Curriculum completo sull\u2019hub', f'{HUB}/curriculum')),
    'contatti': rel(
        ('Chi sono', P('chi-sono')),
        ('La terapia chirurgica', P('la-terapia-chirurgica')),
        ('La pre-abilitazione prima dell\u2019intervento', P('preabilitazione-dei-pazienti-all-intervento-chirurgico'))),
}

COOKIE_TXT = ('__emg_vid e __emg_sid — cookie tecnici di prima parte impiegati dalla piattaforma '
              'che ospita il sito per distinguere le sessioni e produrre statistiche aggregate di '
              'traffico. Non profilano e non vengono impiegati per finalità pubblicitarie. '
              'Durata: __emg_vid 12 mesi, __emg_sid fine sessione.')

report = {}
for f in sorted(PAGES.glob('*.json')):
    slug = f.stem
    page = json.load(open(f))
    it = page['it']
    blocks = [clean_block(b) for b in it['blocks']]
    blocks = split_long(blocks)

    # h2 -> domande (indici riferiti ai blocchi originali: ricostruisco per testo)
    h2map = H2_MAP.get(slug)
    if h2map:
        # gli indici sono ancora validi: clean/split non toccano gli h2 e split
        # aggiunge solo dopo il punto di split; verifico per sicurezza sul testo
        seen_h2 = 0
        orig = json.load(open(f))['it']['blocks']
        h2_texts = {i: b['text'] for i, b in enumerate(orig) if b['type'] == 'h2'}
        h2_iter = iter(h2_texts.items())
        cur_idx, cur_txt = next(h2_iter, (None, None))
        for b in blocks:
            if b['type'] == 'h2' and cur_txt is not None and b['text'] == cur_txt:
                new = h2map.get(cur_idx, cur_txt)
                if new is None:
                    b['_drop'] = True
                else:
                    b['text'] = new
                cur_idx, cur_txt = next(h2_iter, (None, None))
        blocks = [b for b in blocks if not b.pop('_drop', False)]

    # terapia: disclaimer immagini -> note, h2-frase -> p
    if slug == 'la-terapia-chirurgica':
        for b in blocks:
            if b['type'] == 'h2' and b['text'].startswith('Questa pagina contiene immagini'):
                b['type'], b['html'] = 'note', b.pop('text')
            elif b['type'] == 'h2' and b['text'].startswith('Al di là delle specifiche'):
                b['type'], b['html'] = 'p', b.pop('text')
    if slug == 'difetti-della-parete-addominale-e-classificazione':
        for i, b in enumerate(blocks):
            if b['type'] == 'h2' and b['text'] == 'Che cosa cambia fra ernia primaria e laparocele?':
                # il testo lungo dell'heading originale diventa un paragrafo sotto la domanda
                orig_txt = 'I difetti secondari della Parete Addominale , o ernie incisionali o laparoceli, sono i difetti che occorrono su pregresse incisioni, o sono conseguenza di esse.'
                blocks.insert(i + 1, {'type': 'p', 'html': 'I difetti secondari della parete addominale, o ernie incisionali o laparoceli, sono i difetti che occorrono su pregresse incisioni, o sono conseguenza di esse.'})
                break
        # tabelle EHS dopo il paragrafo sulla classificazione EHS
        for i, b in enumerate(blocks):
            if b['type'] == 'p' and 'European Hernia Society' in b.get('html', ''):
                t1 = table(['Sede', 'Sigla EHS', 'Definizione'], [
                    ['Sotto-xifoidea', 'M1', 'Dal processo xifoideo a 3 cm al di sotto di esso'],
                    ['Epigastrica', 'M2', 'Da 3 cm sotto lo xifoide a 3 cm sopra l\u2019ombelico'],
                    ['Ombelicale', 'M3', 'Da 3 cm sopra a 3 cm sotto l\u2019ombelico'],
                    ['Infraombelicale', 'M4', 'Da 3 cm sotto l\u2019ombelico a 3 cm sopra il pube'],
                    ['Soprapubica', 'M5', 'Dal pube a 3 cm al di sopra di esso'],
                    ['Sottocostale', 'L1', 'Dal margine costale a 3 cm sopra l\u2019ombelico, in laterale'],
                    ['Del fianco', 'L2', 'Laterale alla guaina dei retti, fra 3 cm sopra e 3 cm sotto l\u2019ombelico'],
                    ['Iliaca', 'L3', 'Da 3 cm sotto l\u2019ombelico alla regione inguinale'],
                    ['Lombare', 'L4', 'Latero-dorsale rispetto alla linea ascellare anteriore'],
                ], caption='Classificazione EHS delle ernie della parete addominale per sede.',
                   source='Muysoms F.E. et al., <i>Hernia</i>, 2009;13(4):407-414. DOI: 10.1007/s10029-009-0518-x')
                t2 = table(['Dimensione del difetto', 'Ernia primaria', 'Ernia incisionale (laparocele)'], [
                    ['Piccola', '&lt; 2 cm', 'W1: &lt; 4 cm'],
                    ['Media', '2\u20134 cm', 'W2: 4\u201310 cm'],
                    ['Grande', '&gt; 4 cm', 'W3: &gt; 10 cm'],
                ], caption='Classificazione EHS per dimensione del difetto erniario.')
                blocks[i + 1:i + 1] = [t1, t2]
                break

    if slug == 'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi':
        for i, b in enumerate(blocks):
            if b['type'] == 'p' and 'Protesi Composite/Ibride/Dual Mesh' in b.get('html', ''):
                # la tabella dei materiali va dopo il paragrafo successivo
                pass
        for i, b in enumerate(blocks):
            if b['type'] == 'h2' and b['text'] == 'Come si classificano le protesi?':
                t1 = table(['Materiale', 'Tipo', 'Caratteristica'], [
                    ['Polipropilene (PPM)', 'Sintetico non assorbibile', 'La protesi più utilizzata nella chirurgia della parete'],
                    ['Poliestere', 'Sintetico non assorbibile', 'Alternativa storica al polipropilene'],
                    ['ePTFE / cPTFE', 'Sintetico non assorbibile', 'Superficie adatta al contatto viscerale'],
                    ['PVDF', 'Fluoropolimero non assorbibile', 'Uso crescente nelle riparazioni della parete'],
                    ['Reti biosintetiche', 'Riassorbibili a lento assorbimento', 'Combinano vantaggi di reti sintetiche e biologiche'],
                    ['Protesi composite / dual mesh', 'Ibride', 'Più materiali per il contatto con i visceri'],
                ], caption='Materiali delle protesi per la chirurgia della parete addominale.')
                blocks.insert(i, t1)
                break
        for i, b in enumerate(blocks):
            if b['type'] == 'ul' and any('onlay' in it for it in b.get('items', [])):
                t2 = table(['Piano di posizionamento', 'Posizione della protesi'], [
                    ['Onlay', 'Al di sopra della fascia muscolare'],
                    ['Inlay', 'A ponte, nel difetto'],
                    ['Sublay', 'Retromuscolare o preperitoneale'],
                    ['Intraperitoneale (IPOM)', 'Al di sotto del peritoneo'],
                ], caption='Piani di posizionamento della protesi, dalla superficie alla profondità.')
                blocks[i] = t2
                break

    if slug == 'radiologia':
        for i, b in enumerate(blocks):
            if b['type'] == 'h2' and b['text'] == 'Quali esami servono prima di operare la parete?':
                t = table(['Esame', 'Che cosa mostra', 'Quando si richiede'], [
                    ['Ecografia', 'Piani cutaneo-sottocutanei e muscolari, linea alba, porte erniarie, diastasi dei retti',
                     'Imaging di primo approccio; esame dinamico, senza radiazioni né preparazione'],
                    ['TC', 'Visione panoramica della parete, misurazioni riproducibili dei difetti',
                     'Secondo livello, su indicazione specialistica, nei difetti complessi'],
                    ['Risonanza magnetica', 'Come la TC, senza radiazioni ionizzanti',
                     'Secondo livello, su indicazione specialistica'],
                ], caption='Diagnostica per immagini nella valutazione della parete addominale.')
                blocks.insert(i + 1, t)
                break

    if slug == 'preabilitazione-dei-pazienti-all-intervento-chirurgico':
        for i, b in enumerate(blocks):
            if (b['type'] in ('p', 'ul')) and 'fumo' in plain_text(b.get('html', '') or ' '.join(b.get('items', []))).lower():
                blocks.insert(i, {'type': 'h2', 'text': "Che cosa devo fare nelle settimane prima dell'intervento?"})
                break

    if slug in ('cookie-policy', 'privacy-policy'):
        blocks.insert(1, {'type': 'h2', 'text': 'Cookie tecnici di piattaforma'})
        blocks.insert(2, {'type': 'p', 'html': f'<strong>{COOKIE_TXT.split(" — ")[0]}</strong> — {COOKIE_TXT.split(" — ",1)[1]}'})

    for kw, href in INLINE.get(slug, []):
        inject_link(blocks, kw, href)

    if slug in RELATED:
        it['related'] = RELATED[slug]

    blocks = tag_images(blocks)
    it['blocks'] = blocks
    # igiene anche su answer e faq
    if it.get('answer'):
        it['answer'] = re.sub(r' {2,}', ' ', CONCAT_RE.sub(r'\1 \2', it['answer'].replace('\xa0', ' ')))
        it['answer'] = re.sub(r'\bpazienti\b', 'Pazienti', re.sub(r'\bpaziente\b', 'Paziente', it['answer']))
    for fq in it.get('faq') or []:
        fq['a'] = re.sub(r' {2,}', ' ', CONCAT_RE.sub(r'\1 \2', fq['a'].replace('\xa0', ' ')))
        fq['a'] = re.sub(r'\bpazienti\b', 'Pazienti', re.sub(r'\bpaziente\b', 'Paziente', fq['a']))

    json.dump(page, open(f, 'w'), ensure_ascii=False, indent=1)
    words = sum(wc(b.get('html', '') or b.get('text', '')) + sum(wc(x) for x in b.get('items', [])) for b in blocks)
    n_q = len([b for b in blocks if b['type'] == 'h2' and '?' in b.get('text', '')])
    n_links = sum(b.get('html', '').count('href="/') for b in blocks if b['type'] == 'p')
    n_tab = len([b for b in blocks if b['type'] == 'table'])
    report[slug] = (words, n_q, n_links, n_tab)
    print(f'{slug[:60]:62s} w={words:5d} h2?={n_q:2d} link={n_links} tab={n_tab}')

print('TOTALE:', sum(r[0] for r in report.values()))
