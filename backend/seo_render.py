"""Rendering SEO: blocchi -> HTML, JSON-LD, canonical/hreflang, sitemap, robots, llms."""
import html as htmllib
import json
import re
from urllib.parse import urlparse

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
        '@type': 'MedicalBusiness',
        '@id': f'{domain}/#organization',
        'name': 'Chirurgia della Parete Addominale - Dott. Federico Fiori',
        'url': domain,
        'sameAs': same,
        'medicalSpecialty': 'Chirurgia della parete addominale',
    }
    return org


HUB_CLINIC_ID = 'https://www.federicofiori.com/#fi-multicare'
HUB_HOSPITAL_ID = 'https://www.federicofiori.com/#asst-santi-paolo-carlo'
# @id autorevole della persona, dall'endpoint hub /api/seo/entity: mai cambiarlo.
PERSON_REF_ID = 'https://www.federicofiori.com/curriculum#federico-fiori'

# Mappa articolo -> pagine affini del sito (blocco "Su questo sito")
ARTICLE_RELATED = {
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

CLINIC_FALLBACK = {
    '@type': 'MedicalClinic',
    '@id': HUB_CLINIC_ID,
    'name': 'Fi Multicare — Centro Medico Multidisciplinare',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'Galleria del Corso 4',
        'postalCode': '20122',
        'addressLocality': 'Milano',
        'addressCountry': 'IT',
    },
    'telephone': '+390276021568',
    'email': 'info@fimulticare.it',
    'url': 'https://www.fimulticare.it',
    'geo': {'@type': 'GeoCoordinates', 'latitude': 45.4644978, 'longitude': 9.1951134},
    'physician': {'@id': PERSON_REF_ID},
    'sameAs': ['https://www.fimulticare.it/'],
}


def clinic_ld(domain, entity=None):
    """Lo studio e' un nodo condiviso dell'hub: si incorpora cosi' come arriva,
    in /contatti/ soltanto; altrove si richiama per @id."""
    clinic = (entity or {}).get('clinic')
    if clinic:
        c = dict(clinic)
        c.pop('@context', None)
        c.setdefault('@id', (entity or {}).get('clinicId', HUB_CLINIC_ID))
        return c
    return dict(CLINIC_FALLBACK)


def person_ld(entity):
    person = (entity or {}).get('person') or {}
    p = dict(person)
    p.pop('@context', None)
    if p:
        # regola di rete (collaudo 19/06): jobTitle e' SOLO la qualifica;
        # il ruolo in ASST e' un incarico -> hasOccupation. Apostrofo: dell'Unita'.
        p['jobTitle'] = 'Medico Chirurgo — Specialista in Chirurgia Generale'
        p['hasOccupation'] = {
            '@type': 'Occupation',
            'name': "Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale",
            'occupationLocation': {'@id': HUB_HOSPITAL_ID},
        }
        p['worksFor'] = {'@id': HUB_CLINIC_ID}
        p['url'] = 'https://www.federicofiori.com/'
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
    return f'''<aside class="pw-authorbox" aria-label="Autore e revisione">
<img src="{esc(img)}" alt="Ritratto del dott. Federico Fiori" width="72" height="72" loading="lazy" decoding="async" />
<div>
<strong>Dott. Federico Fiori</strong><br />
<span>Medico Chirurgo — Specialista in Chirurgia Generale</span><br />
<span>Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, PO San Carlo Borromeo, Milano</span><br />
<span>Scritto e rivisto dal dott. Federico Fiori.{f' Ultima revisione: {esc(data)}.' if data else ''}</span><br />
<a rel="author" href="https://www.federicofiori.com/curriculum">Curriculum completo</a> · <a href="{domain}/contatti/">Dove riceve</a>
</div>
</aside>'''


# about per slug: condizione o procedura clinica della pagina (mai generico)
ABOUT_MAP = {
    'anatomia-della-parete-addominale-e-abdominal-core':
        {'@type': 'AnatomicalStructure', 'name': 'Parete addominale anteriore'},
    'la-diastasi-dei-muscoli-retti':
        {'@type': 'MedicalCondition', 'name': 'Diastasi dei muscoli retti'},
    'difetti-della-parete-addominale-e-classificazione':
        {'@type': 'MedicalCondition', 'name': 'Ernia della parete addominale'},
    'sintomi-e-complicanze':
        {'@type': 'MedicalCondition', 'name': 'Ernia e laparocele'},
    'la-terapia-chirurgica':
        {'@type': 'MedicalProcedure', 'name': 'Rives-Stoppa, TAR e TESAR per la riparazione della parete addominale'},
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi':
        {'@type': 'MedicalProcedure', 'name': 'Riparazione protesica della parete addominale'},
    'preabilitazione-dei-pazienti-all-intervento-chirurgico':
        {'@type': 'MedicalProcedure', 'name': 'Pre-abilitazione alla chirurgia della parete addominale'},
    'le-complicanze-chirurgiche-la-vac-therapy':
        {'@type': 'MedicalProcedure', 'name': 'Terapia a pressione negativa (VAC therapy)'},
    'radiologia':
        {'@type': 'MedicalProcedure', 'name': 'Diagnostica per immagini della parete addominale'},
}


def page_jsonld(page, content, site, entity, canonical, breadcrumb_items):
    """JSON-LD per le 14 pagine ereditate, in base al kind."""
    kind = page.get('it', {}).get('kind', 'clinical') if page.get('it') else 'clinical'
    graphs = []
    person = person_ld(entity)
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
        }, person] if person else graphs
    elif kind == 'contact':
        person_node = person_ld(entity)
        clinic = clinic_ld(site['domain'], entity)
        if person_node:
            person_node['workLocation'] = {'@id': clinic['@id']}
            person_node['affiliation'] = {
                '@type': 'Hospital',
                'name': "Divisione di Chirurgia d'Urgenza – Chirurgia Generale e Robotica – ASST Santi Paolo e Carlo – PO San Carlo Borromeo, Milano",
            }
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
            'isBasedOn': article.get('hubUrl') or None,
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
    person = person_ld(entity)
    if person:
        graphs.append(person)
    return {'@context': 'https://schema.org', '@graph': graphs}


BASE_CSS = """
:root{--ink:#FBF4EF;--surface:#FFFDF8;--line:#E3D5C6;--text:#1E1512;--muted:#6E5D52;--title:#0F1B2A;--accent:#E03E1A;--accent-ink:#AE2F10;--signal:#1B4F96;--deep:#0C0A09;--deep-text:#EDE4D8;--on-deep:#9FBEE8}
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
.pw-faq details{border-top:1px solid var(--line);padding:.8rem 0}
.pw-faq summary{cursor:pointer;font-weight:600}
.pw-net{border-top:1px solid var(--line);margin-top:3rem;padding-top:1.4rem;color:var(--muted);font-size:.9rem}
.pw-rel{border:1px solid var(--line);background:var(--surface);padding:1rem 1.2rem;margin-top:2.4rem;font-size:.95rem}
.pw-rel li{margin:.3rem 0}
.pw-authorbox{border:1px solid var(--line);background:var(--surface);padding:1rem 1.2rem;margin-top:2.4rem;font-size:.9rem;display:flex;gap:1rem;align-items:flex-start}
.pw-authorbox img{border-radius:50%;width:72px;height:72px;object-fit:cover}
.pw-authorbox span{color:var(--muted)}
"""


def og_meta(site, title, description, canonical, image, image_alt):
    """Set completo Open Graph + Twitter card (collaudo 19/06)."""
    locale = 'it_IT' if site['lang'] == 'it' else 'en_US'
    return f'''<meta property="og:type" content="website" />
<meta property="og:url" content="{esc(canonical)}" />
<meta property="og:site_name" content="{esc(site['ui']['site_name'])}" />
<meta property="og:locale" content="{locale}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:image" content="{esc(image)}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="{esc(image_alt)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(description)}" />
<meta name="twitter:image" content="{esc(image)}" />'''


def prerender_page(page, content, site, entity, absolute, noindex):
    domain = site['domain']
    path = page['path']
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
    robots = '<meta name="robots" content="noindex,nofollow" />' if noindex else ''
    net = network_html(site)
    kind = (page.get('it') or {}).get('kind', 'clinical')
    abox = ''
    if kind not in ('home', 'legal', 'contact'):
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
    og_image = abs_url(domain, first_img['src']) if first_img else f'{domain}/og/og-fallback.jpg'
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
<style>{BASE_CSS}</style>
</head>
<body>
<main>
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


def prerender_article(article, site, entity, absolute, noindex):
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
    robots = '<meta name="robots" content="noindex,nofollow" />' if noindex else ''
    og = og_meta(site, article.get('metaTitle') or article.get('title', ''),
                 article.get('metaDescription') or article.get('excerpt') or '',
                 canonical, article.get('coverUrl') or f'{domain}/og/og-fallback.jpg',
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
<style>{BASE_CSS}</style>
</head>
<body>
<main>
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
    return (f'<footer class="pw-net"><h2>{esc(site["ui"]["network_title"])}</h2>'
            f'<p>{esc(site["ui"]["network_intro"])}</p><ul>{items}</ul></footer>')


def sitemap_xml(entries):
    """entries: lista di (loc, lastmod)"""
    rows = ''.join(
        f'  <url><loc>{esc(loc)}</loc>{f"<lastmod>{lm}</lastmod>" if lm else ""}</url>\n'
        for loc, lm in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{rows}</urlset>')


def robots_txt(domain):
    return f"""# chirurgia della parete - rete federicofiori.com
User-agent: *
Allow: /
Disallow: /api/stats/

# Bot AI: esplicitamente benvenuti (allow-list)
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /

Sitemap: {domain}/api/seo/sitemap.xml
# Mappa per i modelli linguistici:
# {domain}/api/seo/llms.txt
"""


def llms_txt(site, pages, articles, entity):
    lang = site['lang']
    domain = site['domain']
    person = (entity or {}).get('person', {})
    lines = [
        f"# {site['ui']['site_name']}",
        '',
        f"> Sito verticale italiano sulla chirurgia della parete addominale del {person.get('name', 'Dott. Federico Fiori')}: ernie, laparoceli, protesi, classificazioni e pre-abilitazione. Parte della rete editoriale di federicofiori.com.",
        '',
        '## Chi',
        f"- {person.get('name', 'Dott. Federico Fiori')}, {person.get('jobTitle', '')}",
        f"- Sede: Galleria del Corso 4, 20122 Milano. Telefono: +39 02 76021568",
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
        '- Contenuto medico a scopo informativo; citare con attribuzione al dott. Federico Fiori e link alla pagina.',
        '- I dati clinici pubblicati sono citati con autore, rivista, anno e DOI/PMID nelle fonti.',
    ]
    return '\n'.join(lines) + '\n'
