#!/usr/bin/env python3
"""Migrazione chirurgiadellaparete.it: WordPress HTML -> blocchi strutturati JSON.
Nessuna riscrittura del testo clinico: si estrae e si struttura soltanto."""
import json, re, os, io, hashlib, unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image

DATA = Path('/app/backend/data')
MEDIA = Path('/app/backend/static/media')
MEDIA.mkdir(parents=True, exist_ok=True)
PAGES_DIR = DATA / 'pages'
PAGES_DIR.mkdir(parents=True, exist_ok=True)

WP = 'https://www.chirurgiadellaparete.it'
HUB = 'https://www.federicofiori.com'
DIASTASI_IT = 'https://www.diastasiedintorni.it'

# ---------------------------------------------------------------- alt generati
ALT_GENERATI = {
    'VAC-01': "Medicazione VAC therapy su ferita chirurgica della parete addominale",
    'VAC-02': "Applicazione del sistema VAC therapy per complicanze della ferita addominale",
    'Protesi-Chirurgia-Della-Parete-01': "Protesi in materiale sintetico per la riparazione della parete addominale",
    'Protesi-Chirurgia-Della-Parete-02': "Dettaglio di una protesi per chirurgia della parete addominale",
    'Protesi-Chirurgia-Della-Parete-03': "Protesi a maglia larga per il rinforzo della parete addominale",
    'Protesi-Chirurgia-Della-Parete-04': "Protesi biologica utilizzata nella chirurgia della parete addominale",
    'Protesi-Chirurgia-Della-Parete-05': "Posizionamento della protesi nel piano retromuscolare",
    'Diastasi-muscoli-retti-addome-01': "Rappresentazione della diastasi dei muscoli retti dell'addome",
    'Diastasi-muscoli-retti-addome-02': "Diastasi dei muscoli retti: allontanamento dei retti sulla linea alba",
    'Diastasi-muscoli-retti-addome-03': "Visione anatomica della diastasi dei retti addominali",
    'rete-con-ponti-1': "Cicatrice addominale con ponti cutanei dopo intervento sulla parete",
    'cica-a-t-ok': "Cicatrice addominale a T dopo intervento di chirurgia della parete",
    'ipom': "Schema della tecnica IPOM con protesi intraperitoneale",
    'tht1': "Imaging della parete addominale prima dell'intervento",
    'tht2': "Imaging della parete addominale dopo il trattamento chirurgico",
    'Chirurgia-Parete-Addominale-01': "Intervento di chirurgia della parete addominale in sala operatoria",
    'Chirurgia-Parete-Addominale-03': "Fase di preparazione della parete addominale durante l'intervento",
    'Chirurgia-Parete-Addominale-04': "Dettaglio intraoperatorio della ricostruzione della parete addominale",
    'Chirurgia-Parete-Addominale-05': "Ricostruzione della parete addominale con protesi",
    'Chirurgia-Parete-Addominale-06': "Chirurgia ricostruttiva della parete addominale",
    'Chirurgia-Robotica-01': "Consolle robotica per la chirurgia della parete addominale",
    'Chirurgia-Robotica-02': "Bracci robotici durante un intervento sulla parete addominale",
    'Chirurgia-Della-Parete-05': "Risultato di un intervento di chirurgia della parete addominale",
    'Chirurgia-Della-Parete-07': "Esito cicatriziale dopo ricostruzione della parete addominale",
    'Tar-3': "Schema della tecnica TAR di separazione dei componenti addominali",
    'Anterior-component-separation': "Schema della separazione anteriore dei componenti della parete",
    'Modifica-Endoscopica': "Modifica endoscopica della separazione dei componenti addominali",
    'Ecografia-Parete-Addominale': "Ecografia della parete addominale in ambulatorio",
    'Ecografia-Parete-Addominale-01': "Immagine ecografica della parete addominale anteriore",
    'Ecografia-Parete-Addominale-01-1': "Immagine ecografica della linea alba e dei muscoli retti",
    'Ecografia-Parete-Addominale-02': "Misurazione ecografica dei muscoli della parete addominale",
    'Ecografia-Addominale': "Esame ecografico dell'addome per lo studio della parete",
    'Ecografia-Sicura': "Ecografia addominale, esame non invasivo e privo di radiazioni",
    'TC-E-RM-NELLA-VALUTAZIONE-DELLA-PARETE-ADDOMINALE': "TC della parete addominale per la valutazione dei difetti",
    'TC-E-RM-NELLA-VALUTAZIONE-DELLA-PARETE-ADDOMINALE-01': "Scansione TC assiale della parete addominale",
    'TC-E-RM-NELLA-VALUTAZIONE-DELLA-PARETE-ADDOMINALE-02': "Ricostruzione RM della parete addominale",
    'logo-chirurgia-della-parete': "Logo di Chirurgia della Parete, sito del dott. Federico Fiori",
}

# ---------------------------------------------------------------- SEO per pagina
SEO = {
    'home': dict(
        title="Chirurgia della Parete Addominale | Dott. Federico Fiori",
        desc="Ernie, laparoceli e difetti della parete addominale: diagnosi, classificazione e chirurgia ricostruttiva a Milano con il dott. Federico Fiori."),
    'anatomia-della-parete-addominale-e-abdominal-core': dict(
        title="Anatomia della Parete Addominale e Abdominal Core",
        desc="Muscoli retti, obliqui, trasverso e linea alba: l'anatomia della parete addominale spiegata per capire ernie, laparoceli e loro riparazione."),
    'la-terapia-chirurgica': dict(
        title="La Terapia Chirurgica dei Difetti della Parete Addominale",
        desc="Tecniche di riparazione di ernie e laparoceli: Rives-Stoppa, TAR, separazione dei componenti, chirurgia robotica ed endoscopica della parete."),
    'chi-sono': dict(
        title="Chi Sono | Dott. Federico Fiori, Chirurgo della Parete",
        desc="Il dott. Federico Fiori, responsabile dell'Unità Operativa di Chirurgia della Parete Addominale: attività clinica e ambito di lavoro a Milano."),
    'radiologia': dict(
        title="Radiologia della Parete Addominale: Ecografia, TC e RM",
        desc="Ecografia, TC e risonanza magnetica nella valutazione dei difetti della parete addominale: cosa mostra ogni esame e quando è indispensabile."),
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': dict(
        title="Protesi in Chirurgia della Parete e Piano di Posizionamento",
        desc="Tipi di protesi per ernie e laparoceli e piani di posizionamento: sottocutaneo, retromuscolare, preperitoneale e intraperitoneale."),
    'le-complicanze-chirurgiche-la-vac-therapy': dict(
        title="Complicanze Chirurgiche e VAC Therapy nella Parete Addominale",
        desc="Sieromi, infezioni e deiscenze dopo chirurgia della parete addominale: come si trattano e che ruolo ha la VAC therapy nella guarigione."),
    'sintomi-e-complicanze': dict(
        title="Sintomi e Complicanze dei Difetti della Parete Addominale",
        desc="Sintomi di ernie e laparoceli per tipo di difetto, segni di allarme di incarceramento e strangolamento e quando serve l'urgenza chirurgica."),
    'difetti-della-parete-addominale-e-classificazione': dict(
        title="Difetti della Parete Addominale e Classificazione EHS",
        desc="Classificazione delle ernie della parete addominale secondo l'European Hernia Society: sedi, dimensioni del difetto e definizioni cliniche."),
    'la-diastasi-dei-muscoli-retti': dict(
        title="Diastasi dei Muscoli Retti in Chirurgia della Parete",
        desc="La diastasi dei retti vista dalla chirurgia della parete: rapporto con l'ernia ombelicale e come cambia l'indicazione all'intervento."),
    'preabilitazione-dei-pazienti-all-intervento-chirurgico': dict(
        title="Preabilitazione prima dell'Intervento sulla Parete Addominale",
        desc="Come prepararsi all'intervento sulla parete addominale: peso, glicemia, fumo, nutrizione ed esercizio fisico prima della chirurgia."),
    'contatti': dict(
        title="Contatti | Chirurgia della Parete Addominale a Milano",
        desc="Come contattare il dott. Federico Fiori per una valutazione dei difetti della parete addominale: sede in Galleria del Corso 4, Milano."),
    'privacy-policy': dict(
        title="Privacy Policy | Chirurgia della Parete Addominale",
        desc="Informativa privacy del sito chirurgiadellaparete.it: titolare del trattamento, finalità, basi giuridiche, diritti dell'interessato e contatti."),
    'cookie-policy': dict(
        title="Cookie Policy | Chirurgia della Parete Addominale",
        desc="Cookie policy del sito chirurgiadellaparete.it: tipologie di cookie utilizzati, finalità, durata e come gestire o revocare il consenso."),
}

NAV_ORDER = [
    'anatomia-della-parete-addominale-e-abdominal-core',
    'difetti-della-parete-addominale-e-classificazione',
    'sintomi-e-complicanze',
    'radiologia',
    'la-terapia-chirurgica',
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi',
    'le-complicanze-chirurgiche-la-vac-therapy',
    'preabilitazione-dei-pazienti-all-intervento-chirurgico',
    'la-diastasi-dei-muscoli-retti',
]

TAG_RE = re.compile(r'<[^>]+>')

def text_of(html):
    return re.sub(r'\s+', ' ', TAG_RE.sub(' ', html or '')).strip()

def wc(html):
    return len(text_of(html).split())

def slugify(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', name.lower())).strip('-')

# ---------------------------------------------------------------- download immagini
def process_image(src):
    base = src.split('?')[0]
    stem = slugify(Path(base).stem)
    out = MEDIA / f'{stem}.webp'
    if out.exists():
        im = Image.open(out)
        return stem, im.size
    try:
        req = urllib.request.Request(base, headers={'User-Agent': 'Mozilla/5.0'})
        raw = urllib.request.urlopen(req, timeout=40).read()
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        w, h = im.size
        if max(w, h) > 1600:
            r = 1600 / max(w, h)
            im = im.resize((int(w * r), int(h * r)), Image.LANCZOS)
        q = 82
        while True:
            im.save(out, 'WEBP', quality=q)
            if out.stat().st_size <= 150_000 or q <= 40:
                break
            q -= 10
        return stem, im.size
    except Exception as e:
        print('IMG FAIL', base, e)
        return None, None

# ---------------------------------------------------------------- parsing blocchi
INLINE_OK = {'a', 'strong', 'em', 'b', 'i', 'u', 'sup', 'sub', 'span', 'br', 'small', 'mark'}

def clean_inline(html):
    soup = BeautifulSoup(html, 'lxml')
    for t in soup.find_all(True):
        if t.name not in INLINE_OK:
            t.unwrap()
            continue
        if t.name == 'a':
            href = t.get('href', '')
            for a in list(t.attrs):
                if a != 'href':
                    del t[a]
            if href.startswith(WP):
                t['href'] = href[len(WP):] or '/'
        else:
            t.attrs = {}
    return soup.decode().strip()

def extract_blocks(rendered):
    soup = BeautifulSoup(rendered, 'lxml')
    # rimuovi script/style e div vuoti decorativi Divi
    for t in soup.select('script, style, .et_pb_divider, .et_pb_top_inside_divider, .et_pb_bottom_inside_divider'):
        t.decompose()
    # unwrap di tutti i div di impalcatura
    for div in soup.find_all('div'):
        div.unwrap()
    for sec in soup.find_all(['section', 'span']):
        sec.unwrap()
    body = soup.body or soup
    blocks, images = [], []
    seen_img = set()

    def handle_img(img):
        src = img.get('src') or img.get('data-src') or ''
        if not src or 'data:image' in src:
            return None
        src = src.split('?')[0]
        if not src.startswith('http'):
            src = WP + src
        # rimuovi suffissi di dimensione WP per prendere l'originale
        src = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', src)
        stem = slugify(Path(src.split('?')[0]).stem)
        if stem in seen_img:
            return None
        seen_img.add(stem)
        alt = (img.get('alt') or '').strip()
        if not alt:
            for key, val in ALT_GENERATI.items():
                if slugify(key) in stem:
                    alt = val
                    break
        if not alt:
            alt = f"Immagine clinica di chirurgia della parete addominale ({stem.replace('-', ' ')})"
        images.append({'stem': stem, 'src': src, 'alt': alt})
        cap = ''
        fig = img.find_parent('figure')
        if fig:
            fc = fig.find('figcaption')
            if fc:
                cap = fc.get_text(' ', strip=True)
        return {'type': 'img', 'src': f'/api/media/{stem}.webp', 'alt': alt, 'caption': cap}

    def walk(node):
        for el in node.children:
            if isinstance(el, NavigableString):
                txt = str(el).strip()
                if txt:
                    blocks.append({'type': 'p', 'html': txt})
                continue
            if not isinstance(el, Tag):
                continue
            name = el.name
            if name in ('h1', 'h2', 'h3', 'h4'):
                lvl = 'h2' if name in ('h1', 'h4') else name
                t = el.get_text(' ', strip=True)
                if t:
                    blocks.append({'type': lvl, 'text': t})
            elif name == 'p':
                for im in el.find_all('img'):
                    b = handle_img(im)
                    if b:
                        blocks.append(b)
                html = clean_inline(el.decode_contents())
                if wc(html) > 0:
                    blocks.append({'type': 'p', 'html': html})
            elif name in ('ul', 'ol'):
                items = [clean_inline(li.decode_contents()) for li in el.find_all('li', recursive=False)]
                items = [i for i in items if wc(i) > 0]
                if items:
                    blocks.append({'type': 'ul', 'ordered': name == 'ol', 'items': items})
            elif name == 'img':
                b = handle_img(el)
                if b:
                    blocks.append(b)
            elif name == 'figure':
                for im in el.find_all('img'):
                    b = handle_img(im)
                    if b:
                        blocks.append(b)
            elif name == 'table':
                blocks.append({'type': 'table', 'html': str(el)})
            elif name == 'blockquote':
                t = clean_inline(el.decode_contents())
                if wc(t):
                    blocks.append({'type': 'note', 'html': t})
            elif name in ('article', 'main', 'header', 'footer', 'body'):
                walk(el)
            else:
                walk(el)
    walk(body)
    return blocks, images

# ---------------------------------------------------------------- main
pages = json.load(open(DATA / 'wp_pages_raw.json'))
all_images = {}
manifest = {}

print('== download immagini ==')
srcs = set()
for p in pages:
    soup = BeautifulSoup(p['content']['rendered'], 'lxml')
    for im in soup.find_all('img'):
        s = (im.get('src') or im.get('data-src') or '').split('?')[0]
        if s and 'data:image' not in s:
            if not s.startswith('http'):
                s = WP + s
            s = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', s)
            srcs.add(s)
print(len(srcs), 'sorgenti')
with ThreadPoolExecutor(8) as ex:
    for stem, size in ex.map(process_image, sorted(srcs)):
        if stem:
            all_images[stem] = size
print('scaricate:', len(all_images))

for p in pages:
    slug = p['slug']
    blocks, images = extract_blocks(p['content']['rendered'])
    # inietta dimensioni reali
    for b in blocks:
        if b['type'] == 'img':
            stem = b['src'].split('/')[-1].replace('.webp', '')
            if stem in all_images and all_images[stem]:
                b['width'], b['height'] = all_images[stem]
            else:
                b['width'], b['height'] = 1200, 800
    h1 = p['title']['rendered'].strip()
    # prendi l'h1 reale dal contenuto se presente
    for b in blocks[:3]:
        if b['type'] == 'h2' and slug != 'home':
            pass
    words = sum(wc(b.get('html', '') or b.get('text', '')) + sum(wc(i) for i in b.get('items', [])) for b in blocks)
    seo = SEO.get(slug, dict(title=h1, desc=''))
    page = {
        'slug': slug,
        'path': '/' if slug == 'home' else f'/{slug}/',
        'it': {
            'h1': h1,
            'metaTitle': seo['title'],
            'metaDescription': seo['desc'],
            'blocks': blocks,
        },
        'en': None,
        'modified': p.get('modified', ''),
    }
    json.dump(page, open(PAGES_DIR / f'{slug}.json', 'w'), ensure_ascii=False, indent=1)
    manifest[slug] = {'words': words, 'images': len([b for b in blocks if b['type'] == 'img'])}
    print(f"{slug:70s} parole={words:5d} img={manifest[slug]['images']}")

json.dump(manifest, open(DATA / 'manifest_raw.json', 'w'), indent=1)
print('TOTALE parole:', sum(m['words'] for m in manifest.values()))
print('TOTALE immagini usate:', sum(m['images'] for m in manifest.values()))
