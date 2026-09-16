#!/usr/bin/env python3
"""Banca immagini + sostituzione figure generate con la serie corretta.
Posizione: DOPO il primo paragrafo della sezione di cui la figura parla."""
import json
from pathlib import Path

PAGES = Path('/app/backend/data/pages')
MEDIA = Path('/app/backend/static/media')
DATA = Path('/app/backend/data')

BANK = {
    'strati-della-parete': {
        'title': 'Gli strati della parete addominale',
        'subject': 'exploded schematic of the layered abdominal wall seen from the side: skin, fat, anterior fascia, two rectus muscles, posterior fascia, peritoneum, as thin parallel luminous planes slightly offset',
        'alt': 'Schema esploso degli strati della parete addominale visti di lato: cute, grasso, fasce, muscoli retti e peritoneo come piani luminosi paralleli',
        'caption': 'Gli strati della parete addominale, dal piano superficiale al peritoneo.',
        'tags': ['anatomia', 'strati', 'fascia', 'retti'],
    },
    'difetto-e-pressione': {
        'title': 'Il difetto e la pressione interna',
        'subject': 'schematic side section of a layered abdominal wall with a small gap in the fascia and a soft rounded protrusion emerging outward through it, concentric pressure lines pushing from inside',
        'alt': 'Sezione schematica della parete con una breccia nella fascia, una sporgenza arrotondata che fuoriesce e linee di pressione concentriche che spingono dall\u2019interno',
        'caption': 'Il rigonfiamento nasce dove la fascia cede e la pressione interna spinge.',
        'tags': ['ernia', 'difetto', 'pressione', 'sintomi'],
    },
    'piani-della-rete': {
        'title': 'I quattro piani della rete',
        'subject': 'four stacked schematic sections of a layered abdominal wall, each with a thin mesh lattice line at a different depth, from superficial to deep',
        'alt': 'Quattro sezioni schematiche sovrapposte della parete, ciascuna con una sottile trama di rete a una profondità diversa, dalla più superficiale alla più profonda',
        'caption': 'Onlay, sublay, preperitoneale, intraperitoneale: cambia il piano, non solo il materiale.',
        'tags': ['protesi', 'rete', 'piani', 'onlay', 'sublay'],
    },
    'vac-pressione-negativa': {
        'title': 'La pressione negativa della VAC',
        'subject': 'schematic section of a wound cavity sealed by a thin transparent membrane with a fine sponge lattice inside and converging inward pressure lines, one slim tube leaving the field',
        'alt': 'Sezione schematica di una cavità di ferita sigillata da una membrana con trama di garza all\u2019interno, linee di pressione convergenti e un sottile tubo di drenaggio che esce dal campo',
        'caption': 'La pressione negativa avvicina i margini e drena: la medicazione lavora in un sistema chiuso.',
        'tags': ['vac', 'medicazione', 'pressione negativa'],
    },
    'gradini-preparazione': {
        'title': 'I gradini della preparazione',
        'subject': 'abstract ascending stepped line made of thin luminous segments rising left to right inside a wide empty field, no numbers',
        'alt': 'Linea luminosa a gradini ascendenti da sinistra a destra in un campo vuoto, senza numeri',
        'caption': 'La preparazione procede a gradini: ogni tappa si conquista, non si salta.',
        'tags': ['preabilitazione', 'percorso', 'gradini'],
    },
    'respiro-diaframma': {
        'title': 'Il diaframma e la pressione interna',
        'subject': 'abstract schematic of a dome-shaped diaphragm descending inside a torso outline, soft pressure gradient below',
        'alt': 'Schema astratto di un diaframma a cupola che discende dentro il profilo del torace, con un gradiente di pressione al di sotto',
        'caption': 'Il respiro governa la pressione interna: è il primo esercizio, non l\u2019ultimo.',
        'tags': ['preabilitazione', 'diaframma', 'respiro'],
    },
}

bank = {'style': 'vedi /app/scripts/gen_figures.py (costante STILE, ricetta hub)', 'images': BANK}
json.dump(bank, open(DATA / 'imagebank.json', 'w'), ensure_ascii=False, indent=1)


def mk(stem):
    b = BANK[stem]
    im = stem
    size = {'piani-della-rete': (1200, 896), 'gradini-preparazione': (1200, 896)}.get(stem, (1024, 1024))
    return {'type': 'img', 'src': f'/api/media/{im}.webp', 'alt': b['alt'],
            'caption': b['caption'], 'kind': 'schema', 'width': size[0], 'height': size[1]}


def load(slug):
    f = PAGES / f'{slug}.json'
    return f, json.load(open(f))


def save(f, p):
    json.dump(p, open(f, 'w'), ensure_ascii=False, indent=1)


def remove_art(bl, stem_part):
    return [b for b in bl if not (b['type'] == 'img' and stem_part in b.get('src', ''))]


def insert_after_first_para_of_section(bl, h2_key, block):
    """Dopo il primo paragrafo della sezione il cui h2 contiene h2_key."""
    in_sec = False
    for i, b in enumerate(bl):
        if b['type'] == 'h2':
            in_sec = h2_key in b.get('text', '')
            continue
        if in_sec and b['type'] == 'p':
            bl.insert(i + 1, block)
            return True
    return False


# privacy e cookie: via le figure, pagine legali non si illustrano
for slug, part in [('privacy-policy', 'arte-privacy-scudo'), ('cookie-policy', 'arte-cookie-radar')]:
    f, p = load(slug)
    p['it']['blocks'] = remove_art(p['it']['blocks'], part)
    save(f, p)
    print(slug, 'figura rimossa')

# home: sostituisci le due arte-*
f, p = load('home')
bl = remove_art(p['it']['blocks'], 'arte-')
for i, b in enumerate(bl):
    if b['type'] == 'p' and 'verticale italiano' in b.get('html', ''):
        bl.insert(i + 1, mk('strati-della-parete'))
        break
for i, b in enumerate(bl):
    if b['type'] == 'ul' and b.get('ordered'):
        bl.insert(i + 1, mk('gradini-preparazione'))
        break
p['it']['blocks'] = bl
save(f, p)
print('home: strati + gradini')

# sintomi
f, p = load('sintomi-e-complicanze')
bl = remove_art(p['it']['blocks'], 'arte-sintomi')
ok = insert_after_first_para_of_section(bl, 'Quali sintomi', mk('difetto-e-pressione'))
p['it']['blocks'] = bl
save(f, p)
print('sintomi:', ok)

# vac
f, p = load('le-complicanze-chirurgiche-la-vac-therapy')
bl = remove_art(p['it']['blocks'], 'arte-vac')
ok = insert_after_first_para_of_section(bl, 'VAC therapy', mk('vac-pressione-negativa'))
p['it']['blocks'] = bl
save(f, p)
print('vac:', ok)

# preabilitazione: sostituisci pulso con diaframma + aggiungi gradini
f, p = load('preabilitazione-dei-pazienti-all-intervento-chirurgico')
bl = remove_art(p['it']['blocks'], 'arte-')
ok1 = insert_after_first_para_of_section(bl, 'pre-abilitazione', mk('respiro-diaframma'))
ok2 = insert_after_first_para_of_section(bl, "settimane prima dell'intervento", mk('gradini-preparazione'))
p['it']['blocks'] = bl
save(f, p)
print('preabilitazione:', ok1, ok2)

# anatomia: 1 figura (strati), dopo il primo paragrafo della prima sezione
f, p = load('anatomia-della-parete-addominale-e-abdominal-core')
bl = p['it']['blocks']
ok = insert_after_first_para_of_section(bl, "Com'è fatta", mk('strati-della-parete'))
p['it']['blocks'] = bl
save(f, p)
print('anatomia:', ok)

# protesi: piani della rete
f, p = load('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi')
bl = p['it']['blocks']
ok = insert_after_first_para_of_section(bl, 'In quale piano', mk('piani-della-rete'))
p['it']['blocks'] = bl
save(f, p)
print('protesi:', ok)

# cancella i file arte-*
import glob, os
for x in glob.glob(str(MEDIA / 'arte-*.webp')):
    os.remove(x)
print('arte-* cancellate')
