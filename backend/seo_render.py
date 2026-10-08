"""Rendering SEO: blocchi -> HTML, JSON-LD, canonical/hreflang, sitemap, robots, llms."""
import html as htmllib
import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROME = ZoneInfo('Europe/Rome')


def rome_dt(s):
    """Data-ora ISO 8601 con fuso italiano (+02:00 da aprile a ottobre,
    +01:00 il resto dell'anno). Google la pretende sulle ProfilePage."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(str(s))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ROME)
    return dt.isoformat()

TAG_RE = re.compile(r'<[^>]+>')


def esc(s):
    return htmllib.escape(s or '', quote=True)


def text_of(html):
    return re.sub(r'\s+', ' ', TAG_RE.sub(' ', html or '')).strip()


def abs_url(domain, src):
    if not src:
        return src
    if src.startswith('http'):
        return src
    return domain + (src if src.startswith('/') else '/' + src)


def render_blocks(blocks, domain, lang, lazy_from=1):
    """Blocchi -> HTML semantico. lazy_from: indice img da cui parte il lazy loading."""
    out, img_i = [], 0
    for b in blocks:
        t = b.get('type')
        if t == 'h2':
            anchor = re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', (b.get('text') or '').lower())).strip('-')
            out.append(f'<h2 id="{esc(anchor)}">{esc(b.get("text"))}</h2>')
        elif t == 'h3':
            out.append(f'<h3>{esc(b.get("text"))}</h3>')
        elif t == 'p':
            out.append(f'<p>{b.get("html", "")}</p>')
        elif t == 'ul':
            tag = 'ol' if b.get('ordered') else 'ul'
            items = ''.join(f'<li>{i}</li>' for i in b.get('items', []))
            out.append(f'<{tag}>{items}</{tag}>')
        elif t == 'img':
            img_i += 1
            src = abs_url(domain, b.get('src', ''))
            w, h = b.get('width') or 1200, b.get('height') or 800
            lazy = ' loading="lazy"' if img_i > lazy_from else ' fetchpriority="high"'
            cap = f'<figcaption>{esc(b.get("caption"))}</figcaption>' if b.get('caption') else ''
            out.append(
                f'<figure><img src="{esc(src)}" alt="{esc(b.get("alt"))}" width="{w}" height="{h}"'
                f'{lazy} decoding="async" />{cap}</figure>')
        elif t == 'video':
            # Nell'HTML dei crawler il video e' un LINK (i crawler non eseguono
            # clic): copertina, titolo, didascalia e link interno restano
            # leggibili. Nessun iframe, nessun VideoObject (contratto hub:
            # i dati strutturati dei video stanno solo sull'hub).
            yt = esc(b.get('yt', ''))
            link = b.get('link', '')
            link_url = esc(domain + link if link.startswith('/') else link)
            link_html = f' — <a href="{link_url}">{esc(b.get("linkLabel", ""))}</a>' if link else ''
            out.append(
                f'<figure class="pw-video">'
                f'<a href="https://www.youtube.com/watch?v={yt}">'
                f'<img src="https://i.ytimg.com/vi/{yt}/hqdefault.jpg" alt="{esc(b.get("alt") or b.get("title", ""))}" '
                f'width="480" height="360" loading="lazy" decoding="async" />'
                f'<span>{esc(b.get("title", ""))}</span></a>'
                f'<figcaption>{esc(b.get("caption", ""))}{link_html}</figcaption></figure>')
        elif t == 'plainBox':
            out.append(f'<div class="pw-plainbox"><p>{b.get("html", "")}</p></div>')
        elif t == 'proBox':
            out.append(f'<div class="pw-probox"><p>{b.get("html", "")}</p></div>')
        elif t == 'note':
            out.append(f'<div class="pw-note"><p>{b.get("html", "")}</p></div>')
        elif t == 'keyPoints':
            items = ''.join(f'<li>{i}</li>' for i in b.get('items', []))
            out.append(f'<ul class="pw-keypoints">{items}</ul>')
        elif t == 'table':
            out.append(f'<div class="pw-table">{b.get("html", "")}</div>')
        elif t == 'ctaRow':
            btns = ''.join(f'<p><a class="pw-cta" href="{esc(i.get("href", ""))}">{esc(i.get("label", ""))}</a></p>'
                           for i in b.get('items', []))
            out.append(f'<div class="pw-ctarow">{btns}</div>')
        elif t == 'contactList':
            rows = []
            for it in b.get('items', []):
                row = f'<p><strong>{esc(it.get("label", ""))}</strong>: '
                if it.get('href'):
                    row += f'<a href="{esc(it["href"])}">{esc(it.get("value", ""))}</a>'
                else:
                    row += esc(it.get('value', ''))
                if it.get('hrefLabel'):
                    row += f' — <a href="{esc(it["href"])}" target="_blank" rel="noopener">{esc(it["hrefLabel"])}</a>'
                rows.append(row + '</p>')
            out.append('\n'.join(rows))
    return '\n'.join(out)


def active_path(page, site):
    c = page.get(site['lang']) or {}
    return c.get('path') or page['path']


# Override accento lime per il gemello inglese (solo HTML dei crawler).
EN_ACCENT_CSS = ":root{--accent:#2FA23A;--accent-soft:#7FCF86;--accent-ink:#0B6B1E;--signal:#0B6B1E;--on-deep:#6FE06F;--deep-text:#EDE4D8}"


def base_css(site):
    return BASE_CSS + (EN_ACCENT_CSS if site.get('lang') == 'en' else '')


def breadcrumb_ld(items):
    return {
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
            for i, (n, u) in enumerate(items)
        ],
    }


def org_ld(entity, domain, lang):
    same = [
        'https://www.federicofiori.com',
        'https://www.diastasiedintorni.it',
        'https://www.diastasisandbeyond.com',
        'https://www.federico-fiori.it',
        'https://www.chirurgiadellaparete.it',
    ]
    org = {
        '@type': 'Organization',
        '@id': f'{domain}/#organization',
        'name': 'Chirurgia della Parete Addominale - Dott. Federico Fiori',
        'url': domain,
        'sameAs': same,
    }
    return org


# @id autorevole del centro, dall'hub: vive sotto /contatti, mai alla radice.
HUB_CLINIC_ID = 'https://www.federicofiori.com/contatti#fi-multicare'
# @id autorevole della persona, dall'endpoint hub /api/seo/entity: mai cambiarlo.
PERSON_REF_ID = 'https://www.federicofiori.com/curriculum#federico-fiori'

# Meta robots del go-live (collaudo 21/09): esplicito su entrambi i lati.
# Sull'host canonico index/follow con snippet illimitato; altrove noindex.
ROBOTS_LIVE = 'index, follow, max-snippet:-1, max-image-preview:large'


def robots_meta(noindex):
    content = 'noindex,nofollow' if noindex else ROBOTS_LIVE
    return f'<meta name="robots" content="{content}" />'

# Mappa articolo -> pagine affini del sito (blocco "Su questo sito")
ARTICLE_RELATED = {
    'incisional-hernia-after-abdominal-surgery-when-to-operate': [
        ('Abdominal wall defects and classification', '/abdominal-wall-defects-and-classification/'),
        ('Symptoms and complications', '/symptoms-and-complications/'),
        ('Surgical treatment', '/surgical-treatment/')],
    'umbilical-hernia-why-it-recurs-and-how-to-prevent-recurrence': [
        ('Symptoms and complications', '/symptoms-and-complications/'),
        ('Meshes and the plane of placement', '/meshes-and-the-plane-of-placement/'),
        ('Contact and specialist assessment', '/contact/')],
    'tecnica-tesar-riparazione-endoscopica-sublay-anteriore': [
        ('La terapia chirurgica dei difetti della parete', '/la-terapia-chirurgica/'),
        ('Le protesi e il piano di posizionamento', '/le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/'),
        ("La pre-abilitazione prima dell'intervento", '/preabilitazione-dei-pazienti-all-intervento-chirurgico/')],
    'laparocele-dopo-intervento-addominale-quando-operare': [
        ('La classificazione dei difetti di parete', '/difetti-della-parete-addominale-e-classificazione/'),
        ('Sintomi e complicanze dei difetti', '/sintomi-e-complicanze/'),
        ('La terapia chirurgica', '/la-terapia-chirurgica/')],
    'ernia-ombelicale-recidiva-come-prevenirla': [
        ('Sintomi e complicanze dei difetti', '/sintomi-e-complicanze/'),
        ('Le protesi e il piano di posizionamento', '/le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/'),
        ('Contatti e valutazione specialistica', '/contatti/')],
}

def clinic_ld(domain, entity=None):
    """Lo studio e' un nodo condiviso dell'hub: si incorpora cosi' come arriva,
    in /contatti/ soltanto; altrove si richiama per @id. Unica fonte per tutta
    la rete: l'endpoint hub /api/seo/entity (campi clinic + contactPoints).
    Nessun fallback locale: se l'entita' manca, si emette solo il riferimento."""
    clinic = (entity or {}).get('clinic')
    if not clinic:
        return {'@type': 'MedicalClinic', '@id': HUB_CLINIC_ID}
    c = dict(clinic)
    c.pop('@context', None)
    c.setdefault('@id', (entity or {}).get('clinicId', HUB_CLINIC_ID))
    # contactPoint: si copiano COSI' COME SONO dal campo contactPoints
    # dell'entita' condivisa dell'hub, mai riscritti a mano.
    cps = (entity or {}).get('contactPoints')
    if cps:
        c['contactPoint'] = cps
    return c


def person_ld(entity, lang='it'):
    """Il nodo Person si copia COSI' COM'E' dall'endpoint hub /api/seo/entity
    (regola di rete, giro 5): nessuna riscrittura, nessun campo aggiunto.
    Unica modifica consentita: inLanguage."""
    person = (entity or {}).get('person') or {}
    p = dict(person)
    p.pop('@context', None)
    if p:
        p['inLanguage'] = lang
    return p


def author_box_html(domain, person, updated_iso, lang):
    """Firma e revisione in coda alle pagine cliniche e agli articoli (prerender)."""
    data = (updated_iso or '')[:10]
    try:
        y, m, d = data.split('-')
        data = f'{d}/{m}/{y}'
    except Exception:
        pass
    img = f'{domain}/api/media/ritratto-dottor-fiori.webp'
    if lang == 'en':
        return f'''<aside class="pw-authorbox" aria-label="Author and review">
<img src="{esc(img)}" alt="Portrait of Dr. Federico Fiori" width="72" height="72" loading="lazy" decoding="async" />
<div>
<strong>Dr. Federico Fiori</strong><br />
<span>General surgeon</span><br />
<span>Head of the Abdominal Wall Surgery Unit — ASST Santi Paolo e Carlo, San Carlo Borromeo Hospital, Milan</span><br />
<span>Written and reviewed by Dr. Federico Fiori.{f' Last reviewed: {esc(data)}.' if data else ''}</span><br />
<a rel="author" href="https://www.federicofiori.com/curriculum">Full curriculum</a>
</div>
</aside>'''
    return f'''<aside class="pw-authorbox" aria-label="Autore e revisione">
<img src="{esc(img)}" alt="Ritratto del Dott. Federico Fiori" width="72" height="72" loading="lazy" decoding="async" />
<div>
<strong>Dott. Federico Fiori</strong><br />
<span>Medico Chirurgo — Specialista in Chirurgia Generale</span><br />
<span>Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, Milano</span><br />
<span>Scritto e rivisto dal Dott. Federico Fiori.{f' Ultima revisione: {esc(data)}.' if data else ''}</span><br />
<a rel="author" href="https://www.federicofiori.com/curriculum">Curriculum completo</a> · <a href="{domain}/contatti/">Dove riceve</a>
</div>
</aside>'''


# about per slug: condizione o procedura clinica della pagina (mai generico)
ABOUT_MAP = {
    'anatomia-della-parete-addominale-e-abdominal-core':
        {'@type': 'AnatomicalStructure', 'name': 'Parete addominale anteriore'},
    'difetti-della-parete-addominale-e-classificazione':
        {'@type': 'MedicalCondition', 'name': 'Ernia della parete addominale'},
    'sintomi-e-complicanze':
        {'@type': 'MedicalCondition', 'name': 'Ernia e laparocele'},
    'la-terapia-chirurgica':
        {'@type': 'MedicalProcedure', 'name': 'Rives-Stoppa, TAR e TESAR per la riparazione della parete addominale'},
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi':
        {'@type': 'MedicalProcedure', 'name': 'Riparazione protesica della parete addominale'},
    'preabilitazione-dei-pazienti-all-intervento-chirurgico':
        {'@type': 'MedicalProcedure', 'name': 'Pre-abilitazione alla Chirurgia della Parete Addominale'},
    'le-complicanze-chirurgiche-la-vac-therapy':
        {'@type': 'MedicalProcedure', 'name': 'Terapia a pressione negativa (VAC therapy)'},
    'radiologia':
        {'@type': 'MedicalProcedure', 'name': 'Diagnostica per immagini della parete addominale'},
    'video':
        {'@type': 'MedicalProcedure', 'name': 'Chirurgia della Parete Addominale'},
}


def page_jsonld(page, content, site, entity, canonical, breadcrumb_items):
    """JSON-LD per le 14 pagine ereditate, in base al kind."""
    kind = page.get(site['lang'], {}).get('kind', 'clinical') if page.get(site['lang']) else 'clinical'
    graphs = []
    person = person_ld(entity, site['lang'])
    org = org_ld(entity, site['domain'], site['lang'])
    web_type = 'WebPage' if kind in ('home', 'legal') else 'MedicalWebPage'
    web = {
        '@type': web_type,
        '@id': canonical,
        'url': canonical,
        'name': content.get('metaTitle') or content.get('h1'),
        'description': content.get('metaDescription'),
        'inLanguage': site['lang'],
        'isPartOf': {'@id': f"{site['domain']}/#website"},
        'about': ABOUT_MAP.get(page.get('slug')) or ({'@id': person.get('@id')} if person.get('@id') else None),
        'author': {'@id': PERSON_REF_ID},
        'reviewedBy': {'@id': PERSON_REF_ID},
        'speakable': {
            '@type': 'SpeakableSpecification',
            'cssSelector': ['h1', '.pw-answer'],
        },
        'lastReviewed': page.get('modified', '')[:10] or None,
    }
    first_img = next((b for b in (content.get('blocks') or []) if b.get('type') == 'img'), None)
    if first_img and first_img.get('src'):
        web['primaryImageOfPage'] = abs_url(site['domain'], first_img['src'])
    web = {k: v for k, v in web.items() if v is not None}
    graphs.append(web)
    graphs.append({'@type': 'WebSite', '@id': f"{site['domain']}/#website",
                   'url': site['domain'], 'name': site['ui']['site_name'],
                   'inLanguage': site['lang'], 'publisher': {'@id': PERSON_REF_ID}})
    graphs.append(org)

    if kind == 'clinical-condition':
        graphs.append({
            '@type': 'MedicalCondition',
            'name': content.get('h1'),
            'url': canonical,
            'code': {'@type': 'MedicalCode', 'codingSystem': 'mesh'},
        })
    elif kind == 'clinical-procedure':
        graphs.append({
            '@type': 'MedicalProcedure',
            'name': content.get('h1'),
            'url': canonical,
            'procedureType': 'https://schema.org/SurgicalProcedure',
        })
    elif kind == 'classifications':
        graphs.append({
            '@type': 'DefinedTermSet',
            'name': 'Classificazione EHS delle ernie della parete addominale',
            'url': canonical,
            'hasDefinedTerm': [
                {'@type': 'DefinedTerm', 'name': 'EHS', 'description': 'European Hernia Society'},
                {'@type': 'DefinedTerm', 'name': 'Ernia primaria', 'description': 'Ernia della parete addominale non associata a precedente incisione chirurgica'},
                {'@type': 'DefinedTerm', 'name': 'Ernia incisionale (laparocele)', 'description': 'Ernia su cicatrice di precedente intervento chirurgico addominale'},
            ],
        })
    elif kind == 'profile':
        graphs = [{
            '@type': 'ProfilePage',
            '@id': canonical,
            'url': canonical,
            'name': content.get('metaTitle'),
            'inLanguage': site['lang'],
            'mainEntity': person,
            'isPartOf': {'@id': f"{site['domain']}/#website"},
            'lastReviewed': page.get('modified', '')[:10] or None,
            'dateModified': rome_dt(page.get('modified')),
            'dateCreated': rome_dt(page.get('created') or page.get('modified')),
        }, person] if person else graphs
    elif kind == 'contact':
        person_node = person_ld(entity, site['lang'])
        clinic = clinic_ld(site['domain'], entity)
        graphs.append(clinic)
        if person_node:
            graphs.append(person_node)
    if breadcrumb_items:
        graphs.append(breadcrumb_ld(breadcrumb_items))
    faq = content.get('faq') or []
    if faq:
        graphs.append({
            '@type': 'FAQPage',
            'mainEntity': [
                {'@type': 'Question', 'name': f['q'],
                 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}}
                for f in faq
            ],
        })
    # il nodo Person c'e' su OGNI pagina (collaudo 19/06): mai duplicarlo se gia' presente
    if person and not any(g.get('@type') == 'Person' for g in graphs):
        graphs.append(person)
    return {'@context': 'https://schema.org', '@graph': graphs}


def article_jsonld(article, site, entity, canonical, breadcrumb_items):
    faq = article.get('faq') or []
    graphs = [
        {
            '@type': 'Article',
            '@id': f'{canonical}#post',
            'headline': article.get('title'),
            'description': article.get('metaDescription') or article.get('excerpt'),
            'image': article.get('coverUrl'),
            'datePublished': article.get('publishedAt'),
            'dateModified': article.get('updatedAt') or article.get('publishedAt'),
            'inLanguage': article.get('lang', site['lang']),
            'mainEntityOfPage': canonical,
            'isBasedOn': article.get('hubUrl') or f"https://www.federicofiori.com/articoli/{article.get('slug')}",
            'author': {'@id': PERSON_REF_ID},
            'reviewedBy': {'@id': PERSON_REF_ID},
            'publisher': {'@id': f"{site['domain']}/#website"},
            'isPartOf': {'@id': f"{site['domain']}/#website"},
        },
        {
            '@type': 'WebSite', '@id': f"{site['domain']}/#website",
            'url': site['domain'], 'name': site['ui']['site_name'],
            'inLanguage': site['lang'], 'publisher': {'@id': PERSON_REF_ID},
        },
        {
            '@type': 'MedicalWebPage',
            '@id': canonical,
            'url': canonical,
            'name': article.get('metaTitle') or article.get('title'),
            'description': article.get('metaDescription') or article.get('excerpt'),
            'inLanguage': article.get('lang', site['lang']),
            'isPartOf': {'@id': f"{site['domain']}/#website"},
            'speakable': {'@type': 'SpeakableSpecification', 'cssSelector': ['h1', '.pw-answer']},
        },
        breadcrumb_ld(breadcrumb_items),
    ]
    graphs[0] = {k: v for k, v in graphs[0].items() if v is not None}
    if faq:
        graphs.append({
            '@type': 'FAQPage',
            'mainEntity': [
                {'@type': 'Question', 'name': f['q'],
                 'acceptedAnswer': {'@type': 'Answer', 'text': text_of(f.get('a', ''))}}
                for f in faq
            ],
        })
    person = person_ld(entity, article.get('lang', site['lang']))
    if person:
        graphs.append(person)
    return {'@context': 'https://schema.org', '@graph': graphs}


BASE_CSS = """
:root{--ink:#FBF4EF;--surface:#FFFDF8;--line:#E3D5C6;--text:#1E1512;--muted:#6E5D52;--title:#0F1B2A;--accent:#3C83E1;--accent-ink:#1B4F96;--signal:#1B4F96;--deep:#0C0A09;--deep-text:#EDE4D8;--on-deep:#9FBEE8}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--ink);color:var(--text);font-family:Manrope,ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.75;font-size:18px}
main{max-width:44em;margin:0 auto;padding:2rem 1.25rem}
h1,h2,h3{font-family:"Inter Tight",ui-sans-serif,sans-serif;font-weight:600;letter-spacing:-0.02em;color:var(--title)}
h1{font-size:2.2rem;line-height:1.2;margin-bottom:1rem}
h2{font-size:1.5rem;margin:2.75rem 0 .8rem}
h3{font-size:1.2rem;margin:2.2rem 0 .75rem}
p{margin-bottom:1rem;max-width:68ch}
ul,ol{margin:0 0 1rem 1.4rem}
a{color:var(--accent-ink);text-underline-offset:2px}
figure{margin:1.4rem 0}
img{max-width:100%;height:auto;border-radius:10px;border:1px solid var(--line)}
figcaption{color:var(--muted);font-size:12.5px;margin-top:.5rem}
.pw-answer{border-left:3px solid var(--accent);padding:.8rem 1.1rem;background:var(--deep);color:var(--deep-text);margin:1.2rem 0}
.pw-answer a{color:var(--on-deep)}
.pw-plainbox,.pw-note{border:1px solid var(--line);padding:1rem 1.2rem;background:var(--surface);margin:1.4rem 0}
.pw-note{background:var(--deep);color:var(--deep-text);border-left:3px solid var(--accent)}
.pw-note a{color:var(--on-deep)}
.pw-table{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:520px}
td,th{border:1px solid var(--line);padding:.5rem .7rem;text-align:left}
th{background:var(--deep);color:var(--deep-text)}
tr:nth-child(even) td{background:#E3EEFB}
.pw-crumbs{font-size:.8rem;color:var(--muted);margin-bottom:1.4rem}
.pw-crumbs a{color:var(--muted)}
.pw-menu{margin-bottom:1.6rem;font-size:.95rem}
.pw-menu a{margin-right:1.2rem}
.pw-faq details{border-top:1px solid var(--line);padding:.8rem 0}
.pw-faq summary{cursor:pointer;font-weight:600}
.pw-net{border-top:1px solid var(--line);margin-top:3rem;padding-top:1.4rem;color:var(--muted);font-size:.9rem}
.pw-rel{border:1px solid var(--line);background:var(--surface);padding:1rem 1.2rem;margin-top:2.4rem;font-size:.95rem}
.pw-rel li{margin:.3rem 0}
.pw-authorbox{border:1px solid var(--line);background:var(--surface);padding:1rem 1.2rem;margin-top:2.4rem;font-size:.9rem;display:flex;gap:1rem;align-items:flex-start}
.pw-authorbox img{border-radius:50%;width:72px;height:72px;object-fit:cover}
.pw-authorbox span{color:var(--muted)}
"""


def og_description(text, limit=125):
    """og:description max 125 caratteri, taglio all'ultimo confine di frase
    (contratto hub 04/10): mai a meta' frase, mai un punto dopo una preposizione."""
    t = (text or '').strip()
    if len(t) <= limit:
        return t
    out = ''
    for m in re.finditer(r'[^.!?]*[.!?]', t):
        cand = (out + ' ' + m.group(0).strip()).strip()
        if len(cand) > limit:
            break
        out = cand
    if out:
        return out
    return t[:limit].rsplit(' ', 1)[0].rstrip(',;:') + '…'


def og_meta(site, title, description, canonical, image, image_alt):
    """Set completo Open Graph + Twitter card (collaudo 19/06)."""
    locale = 'it_IT' if site['lang'] == 'it' else 'en_US'
    og_desc = og_description(description)
    return f'''<meta property="og:type" content="website" />
<meta property="og:url" content="{esc(canonical)}" />
<meta property="og:site_name" content="{esc(site['ui']['site_name'])}" />
<meta property="og:locale" content="{locale}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(og_desc)}" />
<meta property="og:image" content="{esc(image)}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="{esc(image_alt)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(og_desc)}" />
<meta name="twitter:image" content="{esc(image)}" />
<link rel="icon" type="{site['brand']['faviconType']}" href="{esc(site['domain'] + site['brand']['favicon'])}" />
<link rel="apple-touch-icon" href="{esc(site['domain'] + site['brand']['appleTouch'])}" />'''


def og_fallback(site):
    return site['domain'] + site['brand']['ogFallback']


def menu_html(site, pages=None):
    """Il menu principale del sito, presente anche nell'HTML servito ai
    crawler: scoperta degli indirizzi principali senza eseguire JavaScript.
    Le voci pagina (Video, Dott. Fiori, Contatti) compaiono solo se la
    pagina esiste nella lingua del sito."""
    ui = site['ui']
    d = site['domain']
    items = [(d + '/', ui['breadcrumb_home']),
             (d + site['articlesIndex'], ui['nav_articles'])]
    for slug, key in (('video', 'nav_video'), ('about', 'nav_about'), ('chi-sono', 'nav_about'), ('contatti', 'nav_contacts')):
        p = (pages or {}).get(slug)
        if p and p.get(site['lang']):
            items.append((d + active_path(p, site), ui.get(key, slug)))
    links = ''.join(f'<a href="{esc(u)}">{esc(lbl)}</a>' for u, lbl in items)
    # i bot devono vedere una vera navigazione: <header><nav> (contratto 04/10)
    return f'<header><nav class="pw-menu" aria-label="Menu principale">{links}</nav></header>'


def prerender_404(site, pages=None):
    """HTML della pagina 404 per il Worker della rete: il backend la consegna
    con 200, il codice di stato 404 lo mette il Worker sull'indirizzo vero.
    Sempre noindex: la pagina di errore non deve mai entrare nell'indice."""
    domain = site['domain']
    ui = site['ui']
    canonical = domain + '/404'
    title = f"404 — {ui['notfound_title']}"
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': canonical, 'url': canonical,
         'name': title, 'description': ui['notfound_text'],
         'inLanguage': site['lang'], 'isPartOf': {'@id': f'{domain}/#website'}},
        {'@type': 'WebSite', '@id': f'{domain}/#website', 'url': domain,
         'name': ui['site_name'], 'inLanguage': site['lang'],
         'publisher': {'@id': PERSON_REF_ID}},
    ]}
    og = og_meta(site, f"{title} | {ui['site_name']}", ui['notfound_text'],
                 canonical, og_fallback(site), ui['notfound_title'])
    return f"""<!DOCTYPE html>
<html lang="{site['lang']}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)} | {esc(ui['site_name'])}</title>
<meta name="description" content="{esc(ui['notfound_text'])}" />
<link rel="canonical" href="{esc(canonical)}" />
{og}
{robots_meta(True)}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{base_css(site)}</style>
</head>
<body>
<main>
{menu_html(site, pages)}
<nav class="pw-crumbs" aria-label="breadcrumb"><a href="{domain}/">{esc(ui['breadcrumb_home'])}</a> / <span>404</span></nav>
<p aria-hidden="true" style="font-family:'Azeret Mono',monospace;font-size:4rem;color:var(--line);margin:0">404</p>
<h1>{esc(ui['notfound_title'])}</h1>
<p>{esc(ui['notfound_text'])}</p>
<p><a href="{domain}/">{esc(ui['notfound_cta'])}</a></p>
{network_html(site)}
</main>
</body>
</html>"""


def prerender_page(page, content, site, entity, absolute, noindex, pages=None):
    domain = site['domain']
    path = active_path(page, site)
    canonical = domain + path
    h1 = content.get('h1', '')
    body = render_blocks(content.get('blocks', []), domain, site['lang'])
    answer = content.get('answer') or ''
    faq = content.get('faq') or []
    ui = site['ui']
    crumbs_html = ''
    crumb_items = None
    if path != '/':
        crumb_items = [(ui['breadcrumb_home'], domain + '/'), (h1, canonical)]
        crumbs_html = (f'<nav class="pw-crumbs" aria-label="breadcrumb">'
                       f'<a href="{domain}/">{esc(ui["breadcrumb_home"])}</a> / <span>{esc(h1)}</span></nav>')
    faq_html = ''
    if faq:
        items = ''.join(f'<details><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>' for f in faq)
        faq_html = f'<section class="pw-faq" aria-label="{esc(ui["faq_title"])}"><h2>{esc(ui["faq_title"])}</h2>{items}</section>'
    ld = page_jsonld(page, content, site, entity, canonical, crumb_items)
    robots = robots_meta(noindex)
    net = network_html(site)
    kind = (page.get(site['lang']) or {}).get('kind', 'clinical')
    abox = ''
    if kind not in ('legal', 'contact', 'video'):
        abox = author_box_html(site['domain'], (entity or {}).get('person') or {}, page.get('modified', ''), site['lang'])
    rel = content.get('related') or []
    rel_html = ''
    if rel:
        lis = ''.join(f'<li><a href="{esc(r["href"] if r["href"].startswith("http") else domain + r["href"])}">{esc(r["label"])}</a></li>' for r in rel)
        rel_html = f'<nav class="pw-rel" aria-label="Leggi anche"><strong>Leggi anche</strong><ul>{lis}</ul></nav>'
    fonti = content.get('fonti') or []
    fonti_html = ''
    if fonti:
        lis = ''.join(f'<li><a href="{esc(x["href"])}" target="_blank" rel="noopener">{esc(x["label"])}</a></li>' for x in fonti)
        fonti_html = f'<section class="pw-rel" aria-label="Fonti"><strong>Fonti</strong><ul>{lis}</ul></section>'
    first_img = next((b for b in (content.get('blocks') or []) if b.get('type') == 'img'), None)
    if kind == 'home':
        og_image = site['domain'] + site['brand']['ogHome']
    elif first_img:
        og_image = abs_url(domain, first_img['src'])
    else:
        og_image = og_fallback(site)
    og = og_meta(site, content.get('metaTitle') or h1, content.get('metaDescription', ''),
                 canonical, og_image, h1)
    return f"""<!DOCTYPE html>
<html lang="{site['lang']}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(content.get('metaTitle') or h1)}</title>
<meta name="description" content="{esc(content.get('metaDescription', ''))}" />
<link rel="canonical" href="{esc(canonical)}" />
{og}
{robots}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{base_css(site)}</style>
</head>
<body>
<main>
{menu_html(site, pages)}
{crumbs_html}
<h1>{esc(h1)}</h1>
{f'<p class="pw-answer">{esc(answer)}</p>' if answer else ''}
{body}
{faq_html}
{abox}
{rel_html}
{fonti_html}
{net}
</main>
</body>
</html>"""


def prerender_article(article, site, entity, absolute, noindex, pages=None):
    domain = site['domain']
    canonical = article.get('canonical') or (domain + site['articlePath'] + article['slug'])
    ui = site['lang']
    body = render_blocks(article.get('sections', []), domain, site['lang'])
    da = article.get('directAnswer') or article.get('excerpt') or ''
    faq = article.get('faq') or []
    u = site['ui']
    crumb_items = [(u['breadcrumb_home'], domain + '/'),
                   (u['breadcrumb_articles'], domain + site['articlesIndex']),
                   (article.get('title', ''), canonical)]
    crumbs_html = (f'<nav class="pw-crumbs" aria-label="breadcrumb">'
                   f'<a href="{domain}/">{esc(u["breadcrumb_home"])}</a> / '
                   f'<a href="{domain}{site["articlesIndex"]}">{esc(u["breadcrumb_articles"])}</a> / '
                   f'<span>{esc(article.get("title", ""))}</span></nav>')
    cover = ''
    if article.get('coverUrl'):
        cover = (f'<figure><img src="{esc(article["coverUrl"])}" alt="{esc(article.get("title", ""))}" '
                 f'width="1200" height="675" fetchpriority="high" decoding="async" /></figure>')
    faq_html = ''
    if faq:
        items = ''.join(f'<details><summary>{esc(f["q"])}</summary><p>{esc(text_of(f.get("a","")))}</p></details>' for f in faq)
        faq_html = f'<section class="pw-faq"><h2>{esc(u["faq_title"])}</h2>{items}</section>'
    ld = article_jsonld(article, site, entity, canonical, crumb_items)
    robots = robots_meta(noindex)
    og = og_meta(site, article.get('metaTitle') or article.get('title', ''),
                 article.get('metaDescription') or article.get('excerpt') or '',
                 canonical, article.get('coverUrl') or og_fallback(site),
                 article.get('title', ''))
    rel = ARTICLE_RELATED.get(article.get('slug'), [])
    abox = author_box_html(site['domain'], (entity or {}).get('person') or {},
                           article.get('updatedAt') or article.get('publishedAt') or '', site['lang'])
    rel_html = ''
    if rel:
        lis = ''.join(f'<li><a href="{esc(domain + h)}">{esc(l)}</a></li>' for l, h in rel)
        lis += f'<li><a href="{esc(domain + site["articlesIndex"])}">{esc(u["breadcrumb_articles"])}</a></li>'
        rel_html = f'<nav class="pw-rel" aria-label="Su questo sito"><strong>Su questo sito</strong><ul>{lis}</ul></nav>'
    hreflang = ''
    tr = article.get('translation')
    if tr and tr.get('url'):
        hreflang = (f'<link rel="alternate" hreflang="{"en" if site["lang"]=="it" else "it"}" href="{esc(tr["url"])}" />\n'
                    f'<link rel="alternate" hreflang="{site["lang"]}" href="{esc(canonical)}" />\n'
                    f'<link rel="alternate" hreflang="x-default" href="{esc(canonical if site["lang"]=="it" else tr["url"])}" />')
    return f"""<!DOCTYPE html>
<html lang="{site['lang']}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(article.get('metaTitle') or article.get('title', ''))}</title>
<meta name="description" content="{esc(article.get('metaDescription') or article.get('excerpt') or '')}" />
<link rel="canonical" href="{esc(canonical)}" />
{hreflang}
{og}
{robots}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{base_css(site)}</style>
</head>
<body>
<main>
{menu_html(site, pages)}
{crumbs_html}
<h1>{esc(article.get('title', ''))}</h1>
{f'<p class="pw-answer">{esc(da)}</p>' if da else ''}
{cover}
{body}
{faq_html}
{abox}
{rel_html}
{network_html(site)}
</main>
</body>
</html>"""


def network_html(site):
    from siteconfig import NETWORK_ECOSYSTEM
    lang = site['lang']
    items = ''.join(
        f'<li><a href="{esc(s["url"])}">{esc(s["label"][lang])}</a> — {esc(s["desc"][lang])}</li>'
        for s in NETWORK_ECOSYSTEM
        if s['url'] != site['domain'] and s.get('live', True))
    # Le due porte dei contatti, identiche su tutti i siti della rete e presenti
    # anche nell'HTML servito ai crawler (contratto hub 26/09).
    notify = os.environ.get('CONTACT_NOTIFY_EMAIL', '')
    direct = os.environ.get('CONTACT_DIRECT_EMAIL', '')
    contacts = ''
    if notify and direct:
        if lang == 'en':
            contacts = ('<div class="pw-net-contacts">'
                        f'<p>Information and appointments<br /><a href="mailto:{esc(notify)}">{esc(notify)}</a></p>'
                        f'<p>Write to Dr. Fiori<br /><a href="mailto:{esc(direct)}">{esc(direct)}</a></p>'
                        '<p>Phone <a href="tel:+390276021568">+39 02 7602 1568</a></p></div>')
        else:
            contacts = ('<div class="pw-net-contacts">'
                        f'<p>Informazioni e appuntamenti<br /><a href="mailto:{esc(notify)}">{esc(notify)}</a></p>'
                        f'<p>Scrivi al Dott. Fiori<br /><a href="mailto:{esc(direct)}">{esc(direct)}</a></p>'
                        '<p>Telefono <a href="tel:+390276021568">+39 02 7602 1568</a></p></div>')
    return (f'<footer class="pw-net"><h2>{esc(site["ui"]["network_title"])}</h2>'
            f'<p>{esc(site["ui"]["network_intro"])}</p><ul>{items}</ul>{contacts}</footer>')


def sitemap_xml(entries):
    """entries: lista di (loc, lastmod)"""
    rows = ''.join(
        f'  <url><loc>{esc(loc)}</loc>{f"<lastmod>{lm}</lastmod>" if lm else ""}</url>\n'
        for loc, lm in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{rows}</urlset>')


def robots_txt(domain):
    return f"""# Chirurgia della Parete - rete federicofiori.com
User-agent: *
Allow: /
Disallow: /api/stats/

# Bot AI e motori: allow-list di rete, allineata a quella completa di
# diastasisandbeyond.com (contratto hub 04/10). Mai un Disallow: / globale.
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Google-CloudVertexBot
Allow: /
User-agent: Googlebot
Allow: /
User-agent: Bingbot
Allow: /
User-agent: Applebot
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: DuckDuckBot
Allow: /
User-agent: DuckAssistBot
Allow: /
User-agent: CCBot
Allow: /
User-agent: meta-externalagent
Allow: /
User-agent: MistralAI-User
Allow: /
User-agent: Amazonbot
Allow: /
User-agent: cohere-ai
Allow: /
User-agent: YouBot
Allow: /

Sitemap: {domain}/sitemap.xml
# Structured summary for AI answer engines: {domain}/llms.txt
"""


def llms_txt(site, pages, articles, entity):
    lang = site['lang']
    domain = site['domain']
    person = (entity or {}).get('person', {})
    if lang == 'en':
        lines = [
            f"# {site['ui']['site_name']}",
            '',
            f"> English vertical site on abdominal wall surgery by {person.get('name', 'Dr. Federico Fiori')}: hernias, incisional hernias, meshes, classifications and prehabilitation. Part of the federicofiori.com editorial network.",
            '',
            '## Who',
            f"- {person.get('name', 'Dr. Federico Fiori')}, general surgeon",
            "- Role: Head of the Abdominal Wall Surgery Unit — ASST Santi Paolo e Carlo, San Carlo Borromeo Hospital, Milan",
            f"- Center: {HUB_CLINIC_ID}",
            f"- Practice: Galleria del Corso 4, 20122 Milano. Phone: +39 02 7602 1568",
            f"- Hub: https://www.federicofiori.com (curriculum, TESAR, MILA, glossary, results gallery)",
            f"- Identity: {person.get('@id', '')}",
            '',
            '## Pages',
        ]
        for p in pages:
            c = p.get('en') or {}
            lines.append(f"- [{c.get('h1', p['slug'])}]({domain}{active_path(p, site)}): {c.get('metaDescription', '')}")
        if articles:
            lines += ['', '## Articles']
            for a in articles:
                lines.append(f"- [{a.get('title')}]({a.get('canonical', '')}): {a.get('excerpt', '')}")
        lines += [
            '',
            '## Network',
            '- federicofiori.com: hub — identity, curriculum, TESAR, MILA, glossary, results',
            '- chirurgiadellaparete.it: Italian vertical on hernias and incisional hernias',
            '- diastasiedintorni.it: Italian vertical on rectus diastasis',
            '- diastasisandbeyond.com: English vertical on rectus diastasis',
            '- federico-fiori.it: plastic surgery',
            '',
            '## Usage',
            '- Medical content for information only; cite with attribution to Dr. Federico Fiori and a link to the page.',
            '- Published clinical figures are cited with author, journal, year and DOI/PMID in the sources.',
        ]
        return '\n'.join(lines) + '\n'
    lines = [
        f"# {site['ui']['site_name']}",
        '',
        f"> Sito verticale italiano sulla Chirurgia della Parete Addominale del {person.get('name', 'Dott. Federico Fiori')}: ernie, laparoceli, protesi, classificazioni e pre-abilitazione. Parte della rete editoriale di federicofiori.com.",
        '',
        '## Chi',
        f"- {person.get('name', 'Dott. Federico Fiori')}, Medico Chirurgo - Specialista in Chirurgia Generale",
        "- Incarico: Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, Milano",
        f"- Centro: {HUB_CLINIC_ID}",
        f"- Sede: Galleria del Corso 4, 20122 Milano. Telefono: +39 02 7602 1568",
        f"- Hub: https://www.federicofiori.com (curriculum, TESAR, MILA, glossario, galleria risultati)",
        f"- Identità: {person.get('@id', '')}",
        '',
        '## Pagine',
    ]
    for p in pages:
        c = p.get('it') or {}
        lines.append(f"- [{c.get('h1', p['slug'])}]({domain}{p['path']}): {c.get('metaDescription', '')}")
    if articles:
        lines += ['', '## Articoli']
        for a in articles:
            lines.append(f"- [{a.get('title')}]({a.get('canonical', '')}): {a.get('excerpt', '')}")
    lines += [
        '',
        '## Rete',
        '- federicofiori.com: hub — identità, curriculum, TESAR, MILA, glossario, risultati',
        '- diastasiedintorni.it: verticale italiano sulla diastasi dei retti',
        '- diastasisandbeyond.com: verticale inglese sulla diastasi dei retti',
        '- abdominalwallsurgery.com: verticale inglese su ernie e laparoceli',
        '- federico-fiori.it: chirurgia plastica',
        '',
        '## Regole d’uso',
        '- Contenuto medico a scopo informativo; citare con attribuzione al Dott. Federico Fiori e link alla pagina.',
        '- I dati clinici pubblicati sono citati con autore, rivista, anno e DOI/PMID nelle fonti.',
    ]
    return '\n'.join(lines) + '\n'
