"""chirurgiadellaparete.it — verticale della rete federicofiori.com.
Identita' da variabili d'ambiente (SITE_KEY, SITE_LANG, SITE_DOMAIN):
la stessa app diventa il gemello inglese cambiando solo quelle tre variabili."""
import asyncio
import hashlib
import json
import logging
import os
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


# ---------------------------------------------------------------- helpers
def clean_article(a):
    a = dict(a)
    a.pop('_id', None)
    return a


def is_final_host(request: Request):
    host = urlparse(SITE['domain']).netloc
    return request.headers.get('host', '') == host


def source_name(ref: str):
    if not ref:
        return 'diretto'
    h = urlparse(ref).netloc.lower()
    if not h or urlparse(SITE['domain']).netloc in h:
        return 'interno'
    for key, name in [('google', 'Google'), ('bing', 'Bing'), ('duckduckgo', 'DuckDuckGo'),
                      ('chatgpt', 'ChatGPT'), ('perplexity', 'Perplexity'), ('claude', 'Claude'),
                      ('facebook', 'Facebook'), ('instagram', 'Instagram'), ('youtube', 'YouTube')]:
        if key in h:
            return name
    return h


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
            'telLabel': '02 7602 1568', 'telHref': 'tel:+390276021568',
            'email': 'info@fimulticare.it',
            'url': 'https://www.fimulticare.it/',
            'note': {'it': 'Visite su appuntamento', 'en': 'Visits by appointment'}[SITE['lang']],
        },
        'homeKicker': ui['home_kicker'],
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
        'related': content.get('related') or [],
        'blocks': content.get('blocks') or [],
    }


# ---------------------------------------------------------------- articoli
@api_router.get('/blog/articles')
async def list_articles():
    arts = await db.articles.find({'site': SITE['key']}).sort('publishedAt', -1).to_list(500)
    return {
        'site': SITE['key'], 'lang': SITE['lang'], 'articlePath': SITE['articlePath'],
        'total': len(arts),
        'items': [{
            'slug': a['slug'], 'title': a.get('title'), 'excerpt': a.get('excerpt'),
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
    return JSONResponse({'post': clean_article(a)}, media_type='application/json')


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
    noindex = not is_final_host(request)
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
            seo_render.breadcrumb_ld([(ui['breadcrumb_home'], domain + '/'),
                                      (ui['breadcrumb_articles'], domain + SITE['articlesIndex'])]),
        ]}
        robots = '<meta name="robots" content="noindex,nofollow" />' if noindex else ''
        return HTMLResponse(f"""<!DOCTYPE html><html lang="{SITE['lang']}"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{seo_render.esc(ui['articles_title'])} | {seo_render.esc(ui['site_name'])}</title>
<meta name="description" content="{seo_render.esc(ui['articles_sub'])}" />
<link rel="canonical" href="{seo_render.esc(domain + SITE['articlesIndex'])}" />{robots}
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


@api_router.get('/seo/sitemap.xml')
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


@api_router.get('/seo/robots.txt', response_class=PlainTextResponse)
async def seo_robots():
    return PlainTextResponse(seo_render.robots_txt(SITE['domain']))


@api_router.get('/seo/llms.txt', response_class=PlainTextResponse)
async def seo_llms():
    pages = [p for p in load_pages().values() if page_content(p)]
    pages.sort(key=lambda p: p['path'])
    arts = [clean_article(a) for a in await db.articles.find({'site': SITE['key']}).to_list(500)]
    return PlainTextResponse(seo_render.llms_txt(SITE, pages, arts, entity()))


# ---------------------------------------------------------------- statistiche
@api_router.post('/stats/track')
async def stats_track(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    path = str(payload.get('path', '/'))[:300]
    ref = str(payload.get('referrer', ''))[:500]
    ip = request.client.host if request.client else ''
    ua = request.headers.get('user-agent', '')
    day = datetime.now(timezone.utc).date().isoformat()
    vid = hashlib.sha256(f'{ip}|{ua}|{day}'.encode()).hexdigest()[:24]
    kind = 'article' if path.startswith(SITE['articlePath']) else 'page'
    slug = path[len(SITE['articlePath']):].strip('/') if kind == 'article' else None
    await db.pageviews.insert_one({
        'path': path, 'ts': datetime.now(timezone.utc).isoformat(),
        'day': day, 'vid': vid, 'src': source_name(ref), 'kind': kind, 'slug': slug,
    })
    return {'ok': True}


@api_router.get('/stats/summary')
async def stats_summary(request: Request, days: int = Query(30, ge=1, le=365), token: str = ''):
    provided = request.headers.get('x-network-token') or token
    if not siteconfig.NETWORK_STATS_TOKEN or provided != siteconfig.NETWORK_STATS_TOKEN:
        raise HTTPException(401, 'token di rete mancante o non valido')
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    rows = await db.pageviews.find({'day': {'$gte': since}}, {'_id': 0}).to_list(100000)
    pageviews = len(rows)
    visitors = len({r['vid'] for r in rows})
    visits = len({(r['vid'], r['day']) for r in rows})
    top_pages, top_articles, sources = {}, {}, {}
    titles = {a['slug']: a.get('title') for a in await db.articles.find({'site': SITE['key']}).to_list(500)}
    for r in rows:
        if r['kind'] == 'article' and r.get('slug'):
            top_articles[r['slug']] = top_articles.get(r['slug'], 0) + 1
        else:
            top_pages[r['path']] = top_pages.get(r['path'], 0) + 1
        sources[r['src']] = sources.get(r['src'], 0) + 1
    return {
        'site': urlparse(SITE['domain']).netloc, 'days': days,
        'visits': visits, 'visitors': visitors, 'pageviews': pageviews,
        'topPages': [{'path': k, 'views': v} for k, v in
                     sorted(top_pages.items(), key=lambda x: -x[1])[:15]],
        'topArticles': [{'slug': k, 'title': titles.get(k, k), 'views': v} for k, v in
                        sorted(top_articles.items(), key=lambda x: -x[1])[:15]],
        'sources': [{'name': k, 'visits': v} for k, v in
                    sorted(sources.items(), key=lambda x: -x[1])[:15]],
    }


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
