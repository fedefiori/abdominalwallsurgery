"""Collaudo 19/06/2026 — BLOCCANTE 3 e 5:
genera i file SEO statici reali nel public/ del frontend (serviti alla radice)
e le immagini Open Graph 1200x630 (fallback crema+logo, home dal poster hero).
Rieseguire dopo ogni variazione di pagine/articoli: python3 scripts/gen_static_seo.py
"""
import re
import urllib.request
from pathlib import Path

API = 'http://localhost:8001'
PUB = Path('/app/frontend/public')
DOMAIN = 'https://www.chirurgiadellaparete.it'


def fetch(path):
    with urllib.request.urlopen(API + path, timeout=30) as r:
        return r.read().decode('utf-8')


# ---- robots.txt (contenuto esatto richiesto dal collaudo + allow-list AI)
robots = fetch('/api/seo/robots.txt')
robots = robots.replace(f'{DOMAIN}/api/seo/sitemap.xml', f'{DOMAIN}/sitemap.xml')
robots = robots.replace(f'{DOMAIN}/api/seo/llms.txt', f'{DOMAIN}/llms.txt')
(PUB / 'robots.txt').write_text(robots)

# ---- sitemap.xml (URL assoluti www, barra finale come il canonical, lastmod reale)
sitemap = fetch('/api/seo/sitemap.xml')
(PUB / 'sitemap.xml').write_text(sitemap)

# ---- llms.txt
llms = fetch('/api/seo/llms.txt')
(PUB / 'llms.txt').write_text(llms)

n_urls = sitemap.count('<url>')
print(f'robots.txt, sitemap.xml ({n_urls} URL), llms.txt scritti in public/')

# ---- og images 1200x630
from PIL import Image, ImageDraw

OG = PUB / 'og'
OG.mkdir(exist_ok=True)

# fallback: carta crema, barra corallo, logo centrato, nome del sito
CREMA = (251, 244, 239)
CORALLO = (224, 62, 26)
INK = (30, 21, 18)
card = Image.new('RGB', (1200, 630), CREMA)
dr = ImageDraw.Draw(card)
dr.rectangle([0, 630 - 18, 1200, 630], fill=CORALLO)
dr.rectangle([80, 80, 84, 550], fill=CORALLO)
logo = Image.open('/app/backend/static/media/logo-chirurgia-della-parete.webp').convert('RGB')
logo = logo.resize((300, 300))
card.paste(logo, (450, 130))
card.save(OG / 'og-fallback.jpg', 'JPEG', quality=88)

# home: poster del video hero ritagliato a 1.91:1
poster = Image.open(PUB / 'media' / 'hero-loop-parete-addominale.webp').convert('RGB')
w, h = poster.size
target = 1200 / 630
if w / h > target:
    nw = int(h * target)
    poster = poster.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
else:
    nh = int(w / target)
    poster = poster.crop((0, (h - nh) // 2, w, (h + nh) // 2))
poster = poster.resize((1200, 630), Image.LANCZOS)
band = Image.new('RGB', (1200, 90), (12, 10, 9))
poster.paste(band, (0, 540))
dr = ImageDraw.Draw(poster)
dr.rectangle([0, 540, 10, 630], fill=CORALLO)
lg = logo.resize((64, 64))
poster.paste(lg, (30, 553))
poster.save(OG / 'og-home.jpg', 'JPEG', quality=88)
print('og/og-fallback.jpg e og/og-home.jpg generati (1200x630)')
