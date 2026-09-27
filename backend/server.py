"""chirurgiadellaparete.it — verticale della rete federicofiori.com.
Identita' da variabili d'ambiente (SITE_KEY, SITE_LANG, SITE_DOMAIN):
la stessa app diventa il gemello inglese cambiando solo quelle tre variabili."""
import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

import siteconfig
from siteconfig import site, nav_pages, NETWORK_ECOSYSTEM
import seo_render

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

PAGES_DIR = ROOT_DIR / 'data' / 'pages'
MEDIA_DIR = ROOT_DIR / 'static' / 'media'
ENTITY_CACHE = ROOT_DIR / 'data' / 'hub_entity.json'

app = FastAPI(title='chirurgiadellaparete.it')
api_router = APIRouter(prefix='/api')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('parete')

SITE = site()
_entity = {}


# ---------------------------------------------------------------- contenuti pagine
def load_pages():
    pages = {}
    for f in sorted(PAGES_DIR.glob('*.json')):
        p = json.load(open(f))
        pages[p['slug']] = p
    return pages


def page_content(page):
    return page.get(SITE['lang'])


def entity():
    global _entity
    if _entity:
        return _entity
    if ENTITY_CACHE.exists():
        _entity = json.load(open(ENTITY_CACHE))
    return _entity


# ---------------------------------------------------------------- sync articoli hub
async def sync_articles(full=True):
    """Sincronizza il catalogo completo dall'hub. Upsert su groupId,
    sections sempre sovrascritte, ritirati -> 301 verso l'indice."""
    url = SITE['syndication']
    try:
        async with httpx.AsyncClient(timeout=30) as http:
            r = await http.get(url)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        logger.warning('sync articoli fallita: %s', e)
        return {'ok': False, 'error': str(e)}
    items = data.get('items', [])
    seen = set()
    now = datetime.now(timezone.utc).isoformat()
    for it in items:
        gid = it.get('groupId') or it.get('id')
        seen.add(gid)
        doc = dict(it)
        doc['groupId'] = gid
        doc['syncedAt'] = now
        existing = await db.articles.find_one({'groupId': gid, 'site': SITE['key']})
        if existing:
            await db.articles.update_one({'_id': existing['_id']}, {'$set': doc})
        else:
            doc['site'] = SITE['key']
            await db.articles.insert_one(doc)
    # ritirati: non piu' nel catalogo -> via dall'indice, redirect verso /articoli
    withdrawn = await db.articles.find(
        {'site': SITE['key'], 'groupId': {'$nin': list(seen)}}).to_list(1000)
    for w in withdrawn:
        await db.retired_redirects.update_one(
            {'path': SITE['articlePath'] + w['slug']},
            {'$set': {'path': SITE['articlePath'] + w['slug'],
                      'target': SITE['domain'] + SITE['articlesIndex']}},
            upsert=True)
        await db.articles.delete_one({'_id': w['_id']})
        logger.info('articolo ritirato: %s', w['slug'])
    return {'ok': True, 'total': len(items), 'withdrawn': len(withdrawn)}


async def refresh_entity():
    global _entity
    try:
        async with httpx.AsyncClient(timeout=20) as http:
            r = await http.get(f'{siteconfig.HUB_URL}/api/seo/entity')
            r.raise_for_status()
            _entity = r.json()
            ENTITY_CACHE.write_text(json.dumps(_entity, ensure_ascii=False))
    except Exception as e:
        logger.warning('entity hub non raggiungibile: %s', e)
        _entity = entity()


async def sync_loop():
    while True:
        await asyncio.sleep(3600)
        await sync_articles()


@app.on_event('startup')
async def startup():
    await refresh_entity()
    await sync_articles()
    asyncio.create_task(sync_loop())
    asyncio.create_task(sync_loop())
    await db.stats_hits.create_index('ts')


# ---------------------------------------------------------------- statistiche di rete
# Contatore di prima parte: nessun IP, nessun cookie, nessun referrer completo,
# mai un identificativo che riconduca a una persona (per questo la rete non ha
# banner di consenso). Contratto condiviso con l'hub federicofiori.com.
BOT_RE = re.compile(r'bot|crawler|spider|slurp|bingpreview|headless|lighthouse|'
                    r'gptbot|claudebot|perplexity|ahrefs|semrush', re.I)
STATS_SKIP = ('/api', '/admin', '/_next', '/static', '/404')
_stats_cache = {}


def _classify_source(ref, own_host=''):
    """Classifica la provenienza dal referrer, che poi viene scartato.
    Match per etichette di dominio, mai per sottostringa ('t.co' non deve
    catturare 'chatgpt.com')."""
    if not ref:
        return 'diretto'
    try:
        h = urlparse(ref).netloc.lower()
    except Exception:
        return 'altri siti'
    if not h:
        return 'diretto'
    own = urlparse(SITE['domain']).netloc.lower()
    if h == own or h == own_host.lower() or h.endswith('.chirurgiadellaparete.it'):
        return 'interno'
    labels = set(h.split('.'))
    if labels & {'google', 'bing', 'duckduckgo', 'yahoo', 'ecosia', 'qwant', 'yandex'}:
        return 'ricerca'
    if labels & {'facebook', 'instagram', 'linkedin', 'twitter', 'youtube', 'tiktok'} \
            or h == 't.co' or h.endswith('.t.co') or h == 'x.com' or h.endswith('.x.com'):
        return 'social'
    if labels & {'chatgpt', 'openai', 'perplexity', 'claude', 'copilot', 'gemini', 'bard'}:
        return 'AI'
    return 'altri siti'


@api_router.post('/stats/hit')
async def stats_hit(request: Request):
    """Una riga per pagina vista (o per click tracciato). Silenzioso: sempre 202,
    mai un errore visibile. I bot restano fuori; nessuna riga senza user-agent."""
    try:
        ua = request.headers.get('user-agent', '')
        if not ua or BOT_RE.search(ua):
            return JSONResponse({}, status_code=202)
        body = await request.json()
        path = str(body.get('path') or '').split('?')[0].split('#')[0][:200]
        if not path.startswith('/') or path.startswith(STATS_SKIP) or '.' in path.rsplit('/', 1)[-1]:
            return JSONResponse({}, status_code=202)
        sid = re.sub(r'[^A-Za-z0-9_-]', '', str(body.get('sid') or ''))[:64]
        if not sid:
            return JSONResponse({}, status_code=202)
        doc = {
            'ts': datetime.now(timezone.utc),
            'path': path,
            'title': str(body.get('title') or '')[:200],
            'sid': sid,
            'lang': str(body.get('lang') or SITE['lang'])[:8],
        }
        if body.get('ev') == 'click':
            label = re.sub(r'[^a-z0-9-]', '', str(body.get('label') or '').lower())[:60]
            if not label:
                return JSONResponse({}, status_code=202)
            doc['kind'] = 'click'
            doc['label'] = label
        else:
            doc['kind'] = 'view'
            doc['src'] = _classify_source(str(body.get('ref') or '')[:500],
                                          request.headers.get('host', ''))
        await db.stats_hits.insert_one(doc)
    except Exception:
        pass
    return JSONResponse({}, status_code=202)


def _agg(rows):
    """visits + people (sid distinti) di un insieme di righe."""
    return len(rows), len({r['sid'] for r in rows})


@api_router.get('/stats/summary')
async def stats_summary(request: Request, days: int = 30, token: str = Query('')):
    """Sola lettura, solo aggregati. Accesso SOLO col token di rete
    (X-Network-Token o ?token=): nessuna altra autenticazione coinvolta."""
    expected = os.environ.get('NETWORK_STATS_TOKEN', '')
    provided = request.headers.get('x-network-token') or token
    if not expected or provided != expected:
        raise HTTPException(401, 'unauthorized')
    days = max(1, min(int(days or 30), 365))
    hit = _stats_cache.get(days)
    if hit and hit[0] > datetime.now(timezone.utc):
        return hit[1]

    now = datetime.now(timezone.utc)
    today0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    frm = today0 - timedelta(days=days - 1)
    prev_frm = frm - timedelta(days=days)
    rows = await db.stats_hits.find(
        {'ts': {'$gte': prev_frm}},
        {'_id': 0, 'ts': 1, 'path': 1, 'title': 1, 'sid': 1, 'kind': 1, 'label': 1, 'src': 1},
    ).to_list(200000)
    for r in rows:  # pymongo restituisce datetime naive: sono UTC
        if r['ts'].tzinfo is None:
            r['ts'] = r['ts'].replace(tzinfo=timezone.utc)
    views = [r for r in rows if r.get('kind') == 'view']
    clicks = [r for r in rows if r.get('kind') == 'click']
    cur_v = [r for r in views if r['ts'] >= frm]
    prev_v = [r for r in views if frm > r['ts'] >= prev_frm]
    today_v = [r for r in views if r['ts'] >= today0]
    cur_c = [r for r in clicks if r['ts'] >= frm]
    prev_c = [r for r in clicks if frm > r['ts'] >= prev_frm]
    today_c = [r for r in clicks if r['ts'] >= today0]
    visits, people = _agg(cur_v)
    prev_visits, prev_people = _agg(prev_v)
    apath = SITE['articlePath']

    by_path = {}
    for r in cur_v:
        by_path.setdefault(r['path'], []).append(r)
    pages_out = []
    articles_out = []
    for p, rs in by_path.items():
        v, pe = _agg(rs)
        title = next((x['title'] for x in reversed(rs) if x.get('title')), '')
        if p.startswith(apath):
            articles_out.append({'slug': p[len(apath):].strip('/'), 'lang': SITE['lang'],
                                 'visits': v, 'people': pe})
        else:
            pages_out.append({'path': p, 'title': title, 'visits': v, 'people': pe})
    pages_out.sort(key=lambda x: -x['visits'])
    articles_out.sort(key=lambda x: -x['visits'])

    def contact(rs):
        return [r for r in rs if (r.get('label') or '').startswith('contatti')]

    labels = {}
    for r in cur_c:
        labels[r['label']] = labels.get(r['label'], 0) + 1
    by_label = [{'key': k, 'clicks': n} for k, n in sorted(labels.items(), key=lambda x: -x[1])]

    by_src = {}
    for r in cur_v:
        by_src.setdefault(r.get('src') or 'diretto', []).append(r)
    sources = [{'key': k, 'visits': len(rs), 'people': len({x['sid'] for x in rs})}
               for k, rs in sorted(by_src.items(), key=lambda x: -len(x[1]))]

    out = {
        'site': urlparse(SITE['domain']).netloc.replace('www.', ''),
        'days': days,
        'from': frm.isoformat(),
        'to': now.isoformat(),
        'visits': visits,
        'people': people,
        'prevVisits': prev_visits,
        'prevPeople': prev_people,
        'today': len(today_v),
        'pages': pages_out[:10],
        'articles': articles_out,
        'clicks': {
            'total': len(cur_c),
            'prev': len(prev_c),
            'contact': len(contact(cur_c)),
            'prevContact': len(contact(prev_c)),
            'contactToday': len(contact(today_c)),
            'byLabel': by_label,
        },
        'sources': sources,
    }
    _stats_cache[days] = (now + timedelta(minutes=5), out)
    return out


# ---------------------------------------------------------------- contatti di rete
# Le due porte, identiche su tutti i siti della rete (contratto hub 26/09).
# Destinatari in variabili d'ambiente, mai nel codice.
CONTACT_NOTIFY_EMAIL = os.environ.get('CONTACT_NOTIFY_EMAIL', '')
CONTACT_DIRECT_EMAIL = os.environ.get('CONTACT_DIRECT_EMAIL', '')
EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', '')
# Invio diretto Resend con la chiave del Dottore (dominio federicofiori.com
# verificato nel suo account Resend): il mittente torna configurabile
# (MAIL_FROM) e Reply-To resta l'indirizzo di chi ha scritto. Una sola
# chiave per tutti e cinque i siti della rete (contratto hub).
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
MAIL_FROM = os.environ.get('MAIL_FROM', '')
RESEND_API_URL = 'https://api.resend.com/emails'  # costante, mai da env

# reason: qualunque valore mancante, sconosciuto o manomesso ricade su
# 'appuntamento': una richiesta non deve mai perdersi per un campo sbagliato.
CONTACT_REASONS = {
    'dottore': ('Per il Dott. Fiori', CONTACT_DIRECT_EMAIL),
    'appuntamento': ('Informazioni e appuntamenti', CONTACT_NOTIFY_EMAIL),
}

# --- guardrail gate email (playbook rete: copiato as-is, chiamato a ogni invio)
import ipaddress
from html import escape as hesc
from html.parser import HTMLParser as _HTMLParser

_SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "goo.gl", "rebrand.ly")
_CRED_ASK = ("reply with your password", "reply with the code", "send your password", "cvv",
             "send us your password", "enter your password below", "confirm your card number",
             "your full card number", "seed phrase", "recovery phrase", "verify your card",
             "social security number", "confirm your bank details")
_HOSTISH = re.compile(r"\b(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)


def _host_ok(host: str) -> bool:
    if not host or "xn--" in host:
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    return not any(host == s or host.endswith("." + s) for s in _SHORTENERS)


def _same_site(shown: str, real: str) -> bool:
    return shown == real or real.endswith("." + shown) or shown.endswith("." + real)


class _EmailScan(_HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.urls, self.anchors = set(), [], []
        self._href, self._text = None, []

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag.lower())
        self.urls += [v for k, v in attrs if k.lower() in ("href", "src") and v]
        if tag.lower() == "a":
            self._href = dict((k.lower(), v) for k, v in attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, "".join(self._text)))
            self._href, self._text = None, []


def _assert_safe_email(subject: str, html: str) -> None:
    scan = _EmailScan(); scan.feed(html)
    if scan.tags & {"form", "input", "textarea", "select"}:
        raise ValueError("No forms or input fields in email (G2)")
    body = f"{subject}\n{html}".lower()
    for p in _CRED_ASK:
        if p in body:
            raise ValueError(f"Email asks the recipient for credentials: {p!r} (G2)")
    for url in scan.urls:
        low = url.strip().lower()
        if low.startswith(("mailto:", "tel:", "cid:", "#")):
            continue
        if not low.startswith("https://"):
            raise ValueError(f"Email links/assets must be absolute https: {url!r} (G3)")
        host = urlparse(low).hostname or ""
        if not _host_ok(host) or urlparse(low).username is not None:
            raise ValueError(f"Shortened, numeric-host or credential-bearing URL: {url!r} (G3)")
    for href, text in scan.anchors:
        real = urlparse(href.strip().lower()).hostname or ""
        if not real:
            continue
        for m in _HOSTISH.finditer(text):
            if not _same_site(m.group(1).lower(), real):
                raise ValueError(f"Anchor text {m.group(1)!r} != real link host {real!r} (G3)")


async def send_contact_email(to, subject, html, reply_to):
    """Notifica via Resend con la chiave del Dottore. From: MAIL_FROM (dominio
    verificato federicofiori.com) con nome visualizzato EMAIL_FROM_NAME;
    Reply-To = l'indirizzo di chi ha scritto. Restituisce l'id Resend."""
    _assert_safe_email(subject, html)
    payload = {
        'from': f'{EMAIL_FROM_NAME} <{MAIL_FROM}>' if EMAIL_FROM_NAME else MAIL_FROM,
        'to': [to],
        'subject': subject,
        'html': html,
    }
    if reply_to:
        payload['reply_to'] = [reply_to]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(RESEND_API_URL,
                                 headers={'Authorization': f'Bearer {RESEND_API_KEY}'},
                                 json=payload)
    if resp.status_code >= 400:
        # mai loggare la chiave: solo codice e messaggio del provider
        raise RuntimeError(f'Resend {resp.status_code}: {resp.text[:300]}')
    return resp.json().get('id')


@api_router.post('/contact')
async def contact_send(request: Request):
    """Le due porte dei contatti. La richiesta va SEMPRE salvata nel database,
    anche quando la mail parte: se il provider ha un problema, il Paziente non
    si perde. Silenzioso verso l'utente: mai un errore visibile."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    if body.get('company'):  # honeypot: bot -> ok silenzioso, niente salvataggio
        return {'ok': True}
    name = re.sub(r'[\r\n]+', ' ', str(body.get('name') or '')).strip()[:120]
    email = str(body.get('email') or '').strip()[:200]
    message = str(body.get('message') or '').strip()[:5000]
    if not name or not message or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return JSONResponse({'ok': False, 'error': 'invalid'}, status_code=400)
    reason = body.get('reason') if body.get('reason') in CONTACT_REASONS else 'appuntamento'
    label, notify_to = CONTACT_REASONS[reason]
    subject = f'[{label}] {name} — dal sito'
    doc = {
        'ts': datetime.now(timezone.utc), 'name': name, 'email': email,
        'message': message, 'reason': reason, 'notifyTo': notify_to,
        'subject': subject,
        'site': urlparse(SITE['domain']).netloc.replace('www.', ''),
        'emailSent': False, 'emailId': None,
    }
    # 1) si salva SEMPRE, prima di qualunque invio
    await db.contact_requests.insert_one(dict(doc))
    # 2) poi la notifica: se il provider fallisce, la richiesta resta nel DB
    html = ('<table role="presentation" width="100%"><tr><td style="padding:24px;'
            'font-family:Arial,sans-serif;font-size:15px;color:#1a1a1a">'
            f'<p>Nuova richiesta dal sito <strong>chirurgiadellaparete.it</strong>.</p>'
            f'<p><strong>Motivo:</strong> {hesc(label)}</p>'
            f'<p><strong>Nome:</strong> {hesc(name)}<br/>'
            f'<strong>Email:</strong> {hesc(email)}</p>'
            f'<p><strong>Messaggio:</strong><br/>{hesc(message).replace(chr(10), "<br/>")}</p>'
            f'<p style="font-size:12px;color:#888">Inviato da {hesc(EMAIL_FROM_NAME)} — '
            'rete federicofiori.com. Rispondendo a questa email rispondi direttamente '
            'a chi ha scritto (Reply-To).</p></td></tr></table>')
    try:
        doc['emailId'] = await send_contact_email(notify_to, subject, html, reply_to=email)
        doc['emailSent'] = True
    except Exception as e:
        logger.error(f'contact email fallita ({reason} -> {notify_to}): {e}')
    await db.contact_requests.update_one(
        {'ts': doc['ts'], 'email': email},
        {'$set': {'emailSent': doc['emailSent'], 'emailId': doc['emailId']}})
    doc.pop('_id', None)
    return {'ok': True, 'reason': reason, 'emailSent': doc['emailSent']}


# ---------------------------------------------------------------- helpers
def clean_article(a):
    a = dict(a)
    a.pop('_id', None)
    # cover hub: la variante .webp e' generata al volo dall'hub (stesso percorso)
    cov = a.get('coverUrl') or ''
    if cov.startswith('https://www.federicofiori.com/') and cov.endswith('.png'):
        a['coverUrl'] = cov[:-4] + '.webp'
    return a


# Host canonici (collaudo 21/09): il meta robots index/follow vale SOLO qui;
# ogni altro host (anteprima, localhost) resta noindex. Variabile d'ambiente,
# stessa logica del gemello diastasiedintorni.it.
CANONICAL_HOSTS = [h.strip().lower() for h in
                   os.environ.get('CANONICAL_HOSTS', urlparse(SITE['domain']).netloc).split(',')
                   if h.strip()]


def is_final_host(request: Request):
    """Host effettivo della richiesta pubblica (collaudo 26/09):
    1. X-Forwarded-Host (l'host che il Worker dichiara per i crawler);
    2. in mancanza, l'Host della richiesta."""
    raw = request.headers.get('x-forwarded-host') or request.headers.get('host', '')
    host = raw.split(',')[0].split(':')[0].strip().lower()
    return host in CANONICAL_HOSTS


# ---------------------------------------------------------------- API sito
@api_router.get('/site')
async def get_site():
    ui = SITE['ui']
    pages = load_pages()
    nav = [{'path': f'/{s}/', 'label': lbl} for s, lbl in nav_pages(SITE['lang'])
           if s in pages and page_content(pages[s])]
    return {
        'key': SITE['key'], 'lang': SITE['lang'], 'domain': SITE['domain'],
        'articlePath': SITE['articlePath'], 'articlesIndex': SITE['articlesIndex'],
        'ui': ui, 'nav': nav,
        'network': [{'url': s['url'], 'label': s['label'][SITE['lang']], 'desc': s['desc'][SITE['lang']]}
                    for s in NETWORK_ECOSYSTEM if s['url'] != SITE['domain'] and s.get('live', True)],
        'clinic': {
            'name': 'Fi Multicare — Centro Medico Multidisciplinare',
            'address': 'Galleria del Corso 4, 20122 Milano',
            'telLabel': '+39 02 76021568', 'telHref': 'tel:+390276021568',
            'email': 'info@fimulticare.it',
            'networkEmail': 'info@federicofiori.com',
            'url': 'https://www.fimulticare.it/',
            'note': {'it': 'Visite su appuntamento', 'en': 'Visits by appointment'}[SITE['lang']],
        },
        'homeKicker': ui['home_kicker'],
        'person': {
            'name': (entity().get('person') or {}).get('name', 'Dott. Federico Fiori'),
            'jobTitle': (entity().get('person') or {}).get('jobTitle', ''),
            'org': ((entity().get('person') or {}).get('worksFor') or {}).get('name', ''),
        },
    }


@api_router.get('/pages/{slug}')
async def get_page(slug: str):
    pages = load_pages()
    page = pages.get(slug)
    if not page:
        raise HTTPException(404, 'pagina non trovata')
    content = page_content(page)
    if not content:
        # chiave di lingua vuota: la pagina in questa lingua non esiste
        raise HTTPException(404, 'pagina non disponibile in questa lingua')
    return {
        'slug': page['slug'], 'path': page['path'], 'modified': page.get('modified', ''),
        'lang': SITE['lang'],
        'h1': content.get('h1'), 'metaTitle': content.get('metaTitle'),
        'metaDescription': content.get('metaDescription'), 'kind': content.get('kind'),
        'answer': content.get('answer'), 'faq': content.get('faq') or [],
        'related': content.get('related') or [], 'fonti': content.get('fonti') or [],
        'blocks': content.get('blocks') or [],
    }


# ---------------------------------------------------------------- articoli
@api_router.get('/blog/articles')
async def list_articles():
    arts = await db.articles.find({'site': SITE['key']}).sort('publishedAt', -1).to_list(500)
    def trim_words(s, lo=12, hi=18):
        w = (s or '').split()
        if len(w) <= hi:
            return s or ''
        return ' '.join(w[:hi]) + '…'
    return {
        'site': SITE['key'], 'lang': SITE['lang'], 'articlePath': SITE['articlePath'],
        'total': len(arts),
        'items': [{
            'slug': a['slug'], 'title': a.get('title'), 'excerpt': a.get('excerpt'),
            'summary': trim_words(a.get('excerpt')),
            'siteLink': (seo_render.ARTICLE_RELATED.get(a['slug']) or [None])[0],
            'tags': a.get('tags', []), 'categoryLabel': a.get('categoryLabel'),
            'coverUrl': a.get('coverUrl'), 'canonical': a.get('canonical'),
            'metaTitle': a.get('metaTitle'), 'metaDescription': a.get('metaDescription'),
            'publishedAt': a.get('publishedAt'), 'updatedAt': a.get('updatedAt'),
        } for a in arts],
    }


@api_router.get('/blog/posts/{lang}/{slug}')
async def probe_post(lang: str, slug: str):
    """LA SONDA: 200 JSON con l'articolo, solo nella lingua del sito."""
    if lang != SITE['lang']:
        raise HTTPException(404, 'lingua non servita da questo sito')
    a = await db.articles.find_one({'site': SITE['key'], 'slug': slug, 'lang': lang})
    if not a:
        raise HTTPException(404, 'articolo non trovato')
    post = clean_article(a)
    post['siteRelated'] = seo_render.ARTICLE_RELATED.get(slug, [])
    return JSONResponse({'post': post}, media_type='application/json')


@api_router.post('/blog/sync')
async def manual_sync():
    return await sync_articles()


# ---------------------------------------------------------------- SEO machine
@api_router.get('/seo/routes')
async def seo_routes():
    pages = load_pages()
    paths = []
    for p in pages.values():
        if page_content(p):
            paths.append(p['path'])
    paths.append(SITE['articlesIndex'])
    arts = await db.articles.find({'site': SITE['key']}).to_list(500)
    for a in arts:
        paths.append(SITE['articlePath'] + a['slug'])
    paths.append('/404')
    redirects = {}
    # doppioni da barra finale: "/slug" -> "/slug/" (assoluto), piu' /home e /home/ -> /
    for p in pages.values():
        if page_content(p) and p['path'] != '/':
            bare = p['path'].rstrip('/')
            redirects[bare] = SITE['domain'] + p['path']
    redirects['/home'] = SITE['domain'] + '/'
    redirects['/home/'] = SITE['domain'] + '/'
    ret = await db.retired_redirects.find({}).to_list(1000)
    for r in ret:
        redirects[r['path']] = r['target']
    return {'paths': sorted(set(paths)), 'redirects': redirects}


@api_router.get('/seo/prerender', response_class=HTMLResponse)
async def seo_prerender(request: Request, path: str = Query('/'), absolute: bool = False):
    # Decisione index/noindex (giro 26/09, disegno definitivo concordato con l'hub):
    # - absolute=true e' chiamata che SOLO il Worker della rete fa per i crawler:
    #   serve per definizione l'HTML del dominio pubblico -> SEMPRE index,follow,
    #   senza guardare intestazioni (che la catena puo' riscrivere);
    # - senza absolute=true (HTML servito direttamente all'anteprima) la logica
    #   sull'host resta: noindex fuori dagli host canonici.
    noindex = False if absolute else not is_final_host(request)
    pages = load_pages()
    apath = SITE['articlePath']
    if path.startswith(apath) and path != SITE['articlesIndex']:
        slug = path[len(apath):].strip('/')
        a = await db.articles.find_one({'site': SITE['key'], 'slug': slug})
        if not a:
            raise HTTPException(404, 'articolo non trovato')
        return HTMLResponse(seo_render.prerender_article(
            clean_article(a), SITE, entity(), absolute, noindex))
    if path == SITE['articlesIndex']:
        arts = await db.articles.find({'site': SITE['key']}).sort('publishedAt', -1).to_list(500)
        ui = SITE['ui']
        domain = SITE['domain']
        lis = ''.join(
            f'<li><a href="{seo_render.esc(domain + apath + a["slug"])}">{seo_render.esc(a.get("title",""))}</a>'
            f'<p>{seo_render.esc(a.get("excerpt",""))}</p></li>' for a in arts)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', '@id': domain + SITE['articlesIndex'],
             'url': domain + SITE['articlesIndex'], 'name': ui['articles_title'],
             'inLanguage': SITE['lang'], 'isPartOf': {'@id': f'{domain}/#website'}},
            {'@type': 'WebSite', '@id': f'{domain}/#website', 'url': domain,
             'name': ui['site_name'], 'inLanguage': SITE['lang'],
             'publisher': {'@id': seo_render.PERSON_REF_ID}},
            seo_render.person_ld(entity(), SITE['lang']),
            seo_render.breadcrumb_ld([(ui['breadcrumb_home'], domain + '/'),
                                      (ui['breadcrumb_articles'], domain + SITE['articlesIndex'])]),
        ]}
        robots = seo_render.robots_meta(noindex)
        return HTMLResponse(f"""<!DOCTYPE html><html lang="{SITE['lang']}"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{seo_render.esc(ui['articles_title'])} | {seo_render.esc(ui['site_name'])}</title>
<meta name="description" content="{seo_render.esc(ui['articles_sub'])}" />
<link rel="canonical" href="{seo_render.esc(domain + SITE['articlesIndex'])}" />{robots}
{seo_render.og_meta(SITE, ui['articles_title'] + ' | ' + ui['site_name'], ui['articles_sub'], domain + SITE['articlesIndex'], domain + '/og/og-fallback.jpg', ui['articles_title'])}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{seo_render.BASE_CSS}</style></head><body><main>
<nav class="pw-crumbs"><a href="{domain}/">{seo_render.esc(ui['breadcrumb_home'])}</a> / <span>{seo_render.esc(ui['breadcrumb_articles'])}</span></nav>
<h1>{seo_render.esc(ui['articles_title'])}</h1><p>{seo_render.esc(ui['articles_sub'])}</p>
<ul>{lis}</ul>{seo_render.network_html(SITE)}</main></body></html>""")
    slug = 'home' if path in ('/', '') else path.strip('/').split('/')[0]
    page = pages.get(slug)
    if not page or page['path'] != path:
        raise HTTPException(404, 'pagina non trovata')
    content = page_content(page)
    if not content:
        raise HTTPException(404, 'pagina non disponibile in questa lingua')
    return HTMLResponse(seo_render.prerender_page(page, content, SITE, entity(), absolute, noindex))


@api_router.get('/seo/jsonld')
async def seo_jsonld(path: str = Query('/')):
    """Lo stesso @graph del prerender, servito come JSON per l'iniezione client-side."""
    pages = load_pages()
    apath = SITE['articlePath']
    domain = SITE['domain']
    ui = SITE['ui']
    if path.startswith(apath) and path != SITE['articlesIndex']:
        slug = path[len(apath):].strip('/')
        a = await db.articles.find_one({'site': SITE['key'], 'slug': slug})
        if not a:
            raise HTTPException(404, 'articolo non trovato')
        art = clean_article(a)
        canonical = art.get('canonical') or (domain + apath + slug)
        crumbs = [(ui['breadcrumb_home'], domain + '/'),
                  (ui['breadcrumb_articles'], domain + SITE['articlesIndex']),
                  (art.get('title', ''), canonical)]
        return seo_render.article_jsonld(art, SITE, entity(), canonical, crumbs)
    if path.rstrip('/') == SITE['articlesIndex']:
        return {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', '@id': domain + SITE['articlesIndex'],
             'url': domain + SITE['articlesIndex'], 'name': ui['articles_title'],
             'inLanguage': SITE['lang'], 'isPartOf': {'@id': f'{domain}/#website'}},
            {'@type': 'WebSite', '@id': f'{domain}/#website', 'url': domain,
             'name': ui['site_name'], 'inLanguage': SITE['lang'],
             'publisher': {'@id': seo_render.PERSON_REF_ID}},
            seo_render.person_ld(entity(), SITE['lang']),
            seo_render.breadcrumb_ld([(ui['breadcrumb_home'], domain + '/'),
                                      (ui['breadcrumb_articles'], domain + SITE['articlesIndex'])]),
        ]}
    slug = 'home' if path in ('/', '') else path.strip('/').split('/')[0]
    page = pages.get(slug)
    if not page:
        raise HTTPException(404, 'pagina non trovata')
    content = page_content(page)
    if not content:
        raise HTTPException(404, 'pagina non disponibile in questa lingua')
    canonical = domain + page['path']
    crumbs = None if page['path'] == '/' else [
        (ui['breadcrumb_home'], domain + '/'), (content.get('h1', ''), canonical)]
    return seo_render.page_jsonld(page, content, SITE, entity(), canonical, crumbs)



# Esposti anche alla radice /api/: e' il secondo candidato del Worker di rete
# (collaudo 26/09). Content-type: robots/llms text/plain, sitemap application/xml.
@api_router.api_route('/sitemap.xml', methods=['GET', 'HEAD'])
@api_router.api_route('/seo/sitemap.xml', methods=['GET', 'HEAD'])
async def seo_sitemap():
    pages = load_pages()
    entries = []
    for p in pages.values():
        if page_content(p):
            lm = (p.get('modified') or '')[:10]
            entries.append((SITE['domain'] + p['path'], lm))
    entries.append((SITE['domain'] + SITE['articlesIndex'], datetime.now(timezone.utc).date().isoformat()))
    arts = await db.articles.find({'site': SITE['key']}).to_list(500)
    for a in arts:
        entries.append((a.get('canonical') or SITE['domain'] + SITE['articlePath'] + a['slug'],
                        (a.get('updatedAt') or a.get('publishedAt') or '')[:10]))
    from fastapi.responses import Response
    return Response(seo_render.sitemap_xml(entries), media_type='application/xml')


@api_router.api_route('/robots.txt', methods=['GET', 'HEAD'], response_class=PlainTextResponse)
@api_router.api_route('/seo/robots.txt', methods=['GET', 'HEAD'], response_class=PlainTextResponse)
async def seo_robots():
    return PlainTextResponse(seo_render.robots_txt(SITE['domain']))


@api_router.api_route('/llms.txt', methods=['GET', 'HEAD'], response_class=PlainTextResponse)
@api_router.api_route('/seo/llms.txt', methods=['GET', 'HEAD'], response_class=PlainTextResponse)
async def seo_llms():
    pages = [p for p in load_pages().values() if page_content(p)]
    pages.sort(key=lambda p: p['path'])
    arts = [clean_article(a) for a in await db.articles.find({'site': SITE['key']}).to_list(500)]
    return PlainTextResponse(seo_render.llms_txt(SITE, pages, arts, entity()))


# ---------------------------------------------------------------- media
@api_router.get('/media/{filename}')
async def media(filename: str):
    f = MEDIA_DIR / filename
    if not f.exists() or f.suffix != '.webp':
        raise HTTPException(404, 'media non trovato')
    return FileResponse(f, media_type='image/webp',
                        headers={'Cache-Control': 'public, max-age=31536000, immutable'})


@api_router.get('/health')
async def health():
    return {'ok': True, 'site': SITE['key'], 'lang': SITE['lang']}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('shutdown')
async def shutdown_db_client():
    client.close()
