"""Collaudo 19/06/2026: fix dati JSON delle 14 pagine.
- 'della Unità' -> "dell'Unità" ovunque
- link interni normalizzati con barra finale (pagine), articoli senza barra
- home: via il riquadro-residuo WordPress, maiuscole ereditate normalizzate
- contatti: riscrittura blocchi (ctaRow + contactList, via mappa scura e paragrafo privacy)
- fonti esterne VERIFICATE sulle 5 pagine pilastro
- bump 'modified' solo dove il contenuto cambia davvero
"""
import json
import re
from pathlib import Path

PAGES = Path('/app/backend/data/pages')
TODAY = '2026-09-19T10:00:00'

paths = {}
for f in PAGES.glob('*.json'):
    d = json.load(open(f))
    paths[d['path'].rstrip('/')] = d['path']  # '/slug' -> '/slug/'


def fix_html(s):
    if not s:
        return s
    s = s.replace('della Unità', "dell'Unità")
    # barra finale sui link interni di pagina (non articoli, non tel/mailto/http)
    def repl(m):
        href = m.group(1)
        if href.startswith('/') and not href.startswith('/api/') and not href.startswith('/articoli'):
            bare = href.rstrip('/')
            if bare in paths and paths[bare] != '/':
                return f'href="{paths[bare]}"'
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, s)


def walk(blocks):
    for b in blocks or []:
        if 'html' in b:
            b['html'] = fix_html(b['html'])
        if 'text' in b:
            b['text'] = (b['text'] or '').replace('della Unità', "dell'Unità")
        for it in b.get('items') or []:
            if isinstance(it, str):
                pass
        if b.get('items') and all(isinstance(x, str) for x in b['items']):
            b['items'] = [fix_html(x).replace('della Unità', "dell'Unità") for x in b['items']]
        if b.get('caption'):
            b['caption'] = b['caption'].replace('della Unità', "dell'Unità")


FONTI = {
    'ehs_class': {'label': 'European Hernia Society — classificazione delle ernie primarie e incisionali della parete (Muysoms et al., Hernia 2009)',
                  'href': 'https://pubmed.ncbi.nlm.nih.gov/19495920/'},
    'ehs_site': {'label': 'European Hernia Society (EHS)', 'href': 'https://europeanherniasociety.eu/'},
    'ehs_guidelines': {'label': 'European Hernia Society — linee guida', 'href': 'https://europeanherniasociety.eu/about-ehs/guidelines/'},
    'herniasurge': {'label': 'HerniaSurge Group — linee guida internazionali per l’ernia inguinale (2018)',
                    'href': 'https://pubmed.ncbi.nlm.nih.gov/29330835/'},
    'herniasurge_upd': {'label': 'Aggiornamento 2023 delle linee guida internazionali HerniaSurge',
                        'href': 'https://pubmed.ncbi.nlm.nih.gov/37862616/'},
    'tesar': {'label': 'Fiori F. — TESAR: Totally Endoscopic Sublay Anterior Repair (J Laparoendosc Adv Surg Tech A, 2019)',
              'href': 'https://pubmed.ncbi.nlm.nih.gov/30807248/'},
    'ishaws': {'label': 'ISHAWS — Italian Society of Hernia and Abdominal Wall Surgery', 'href': 'https://www.ishaws.it/'},
}
FONTI_PER_SLUG = {
    'anatomia-della-parete-addominale-e-abdominal-core': ['ehs_class', 'ehs_site', 'ishaws'],
    'difetti-della-parete-addominale-e-classificazione': ['ehs_class', 'ehs_guidelines', 'ehs_site'],
    'la-terapia-chirurgica': ['tesar', 'herniasurge', 'herniasurge_upd', 'ehs_guidelines'],
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi': ['ehs_guidelines', 'herniasurge_upd', 'ehs_class'],
    'le-complicanze-chirurgiche-la-vac-therapy': ['ehs_guidelines', 'ehs_site', 'ishaws'],
}

for f in sorted(PAGES.glob('*.json')):
    d = json.load(open(f))
    it = d.get('it')
    if not it:
        continue
    changed = False
    before = json.dumps(it, ensure_ascii=False)
    walk(it.get('blocks'))
    for r in it.get('related') or []:
        if r.get('href', '').startswith('/'):
            bare = r['href'].rstrip('/')
            if bare in paths and paths[bare] != '/' and not bare.startswith('/articoli'):
                r['href'] = paths[bare]
    if it.get('answer'):
        it['answer'] = it['answer'].replace('della Unità', "dell'Unità")
    for qa in it.get('faq') or []:
        qa['q'] = qa['q'].replace('della Unità', "dell'Unità")
        qa['a'] = qa['a'].replace('della Unità', "dell'Unità")
    if json.dumps(it, ensure_ascii=False) != before:
        changed = True

    # ---- home: via il riquadro residuo WP + maiuscole normalizzate
    if d['slug'] == 'home':
        blocks = it['blocks']
        it['blocks'] = [b for b in blocks if not (
            b.get('type') == 'note' and 'Dott. Federico Fiori' in (b.get('html') or '')
            and 'Chirurgia della parete' in (b.get('html') or ''))]
        for b in it['blocks']:
            if b.get('type') == 'p' and 'branca superspecialistica' in (b.get('html') or ''):
                b['html'] = ("La chirurgia della parete è oramai una branca superspecialistica della chirurgia generale. "
                             "La conoscenza approfondita dell’anatomia e la precisa comprensione della fisiopatologia "
                             "consentono oggi di affrontare questo tipo di chirurgia, molto eterogenea, con differenti "
                             "tecniche operative utili a massimizzare il risultato per il paziente. Esistono difetti di "
                             "vario tipo, dalle piccole ernie ombelicali ai disastri di parete, ed esistono tecniche di "
                             "chirurgia open, laparoscopica ed endoscopica, fino all’approccio robotico. Come sempre è "
                             "la corretta indicazione a fare il buon chirurgo e a determinare il risultato.")
                changed = True
            if b.get('type') == 'p' and 'PARETE ADDOMINALE ANTERIORE' in (b.get('html') or ''):
                b['html'] = (b['html']
                             .replace('delle diagnostica', 'della diagnostica')
                             .replace('PARETE ADDOMINALE ANTERIORE', 'parete addominale anteriore'))
                changed = True

    # ---- contatti: riscrittura blocchi
    if d['slug'] == 'contatti':
        it['blocks'] = [
            {'type': 'ctaRow', 'items': [
                {'icon': 'phone', 'label': 'Chiama +39 02 76021568', 'href': 'tel:+390276021568'},
                {'icon': 'mail', 'label': 'Scrivi a info@fimulticare.it', 'href': 'mailto:info@fimulticare.it'},
            ]},
            {'type': 'h2', 'text': 'Dove si trova lo studio?'},
            {'type': 'p', 'html': 'Il dott. Federico Fiori riceve presso <strong>Fi Multicare — Centro Medico '
                                  'Multidisciplinare</strong>, Galleria del Corso 4, 20122 Milano, a pochi passi da '
                                  'Piazza San Babila. Le visite sono su appuntamento.'},
            {'type': 'contactList', 'items': [
                {'icon': 'map-pin', 'label': 'Indirizzo', 'value': 'Galleria del Corso 4, 20122 Milano',
                 'href': 'https://www.google.com/maps/search/?api=1&query=Galleria+del+Corso+4,+20122+Milano',
                 'hrefLabel': 'Apri in Google Maps'},
                {'icon': 'phone', 'label': 'Telefono', 'value': '+39 02 76021568', 'href': 'tel:+390276021568'},
                {'icon': 'mail', 'label': 'E-mail', 'value': 'info@fimulticare.it', 'href': 'mailto:info@fimulticare.it'},
                {'icon': 'globe', 'label': 'Sito del centro', 'value': 'fimulticare.it', 'href': 'https://www.fimulticare.it/'},
            ]},
            {'type': 'p', 'html': 'Prima della visita può essere utile leggere come funziona la '
                                  '<a href="/preabilitazione-dei-pazienti-all-intervento-chirurgico/">pre-abilitazione '
                                  'prima dell’intervento</a>, la descrizione della <a href="/la-terapia-chirurgica/">'
                                  'terapia chirurgica della parete</a> e il profilo del '
                                  '<a href="/chi-sono/">dott. Federico Fiori</a>.'},
        ]
        changed = True

    # ---- fonti esterne verificate sulle 5 pagine pilastro
    if d['slug'] in FONTI_PER_SLUG:
        it['fonti'] = [FONTI[k] for k in FONTI_PER_SLUG[d['slug']]]
        changed = True

    if changed:
        d['modified'] = TODAY
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=1)

print('collaudo19: dati aggiornati')
