"""Genera le immagini di condivisione (OG 1200x630) e le favicon del gemello
inglese AWS. Font: Inter Tight / Azeret Mono (variabili, Google Fonts) in /tmp/fonts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PUB = Path('/app/frontend/public')
FLUO, SOFT, INK, CREAM, WHITE = '#00FF00', '#6FE06F', '#0C0A09', '#FBF4EF', '#FFFFFF'
INTER, MONO = '/tmp/fonts/InterTight.ttf', '/tmp/fonts/Azeret.ttf'


def font(path, size, weight='Bold'):
    f = ImageFont.truetype(path, size)
    f.set_variation_by_name(weight)
    return f


def logo(size):
    """Monogramma AWS: quadrato quasi-nero, bordo fluo, A/S fluo e W bianca."""
    s = 4  # supersampling
    S = size * s
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad, stroke = round(S * 0.025), max(round(S * 0.045), 2)
    d.rounded_rectangle([pad, pad, S - pad, S - pad], radius=round(S * 0.22), fill=INK, outline=FLUO, width=stroke)
    f = font(INTER, round(S * 0.30))
    parts = [('A', FLUO), ('W', WHITE), ('S', FLUO)]
    gap = round(S * 0.012)
    widths = [d.textlength(t, font=f) for t, _ in parts]
    x = (S - sum(widths) - gap * 2) / 2
    for (t, c), w in zip(parts, widths):
        d.text((x, S / 2), t, font=f, fill=c, anchor='lm')
        x += w + gap
    return im.resize((size, size), Image.LANCZOS)


def wordmark(d, x, y, dark):
    d.text((x, y), 'Abdominal Wall Surgery', font=font(INTER, 54), fill=WHITE if dark else INK, anchor='lm')
    d.text((x + 2, y + 52), 'DR. FEDERICO FIORI', font=font(MONO, 22, 'Medium'),
           fill=SOFT if dark else '#0B6B1E', anchor='lm')


def og_home():
    W, H, band = 1200, 630, 150
    bg = Image.open(PUB / 'media/hero-loop-parete-addominale-en.webp').convert('RGB')
    bg = bg.resize((W, round(bg.height * W / bg.width)), Image.LANCZOS)
    im = Image.new('RGB', (W, H), INK)
    im.paste(bg.crop((0, 70, W, 70 + H - band)), (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - band, W, H], fill=INK)
    d.rectangle([0, H - band, 10, H], fill=FLUO)
    d.rectangle([0, H - band, 420, H - band + 3], fill=SOFT)
    im.paste(logo(96), (52, H - band + 27), logo(96))
    wordmark(d, 172, H - band + 58, True)
    d.text((W - 52, H - band + 75), 'abdominalwallsurgery.com', font=font(MONO, 20, 'Medium'),
           fill='#A8A29E', anchor='rm')
    im.save(PUB / 'og/og-home-en.jpg', quality=86, optimize=True)


def og_fallback():
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle([80, 80, 85, 550], fill=SOFT)
    d.rectangle([0, H - 18, W, H], fill=FLUO)
    im.paste(logo(220), (150, 205), logo(220))
    d.text((420, 270), 'Abdominal Wall', font=font(INTER, 76), fill=INK, anchor='lm')
    d.text((420, 352), 'Surgery', font=font(INTER, 76), fill=INK, anchor='lm')
    d.text((424, 425), 'DR. FEDERICO FIORI  ·  HERNIAS · INCISIONAL HERNIAS', font=font(MONO, 20, 'Medium'),
           fill='#0B6B1E', anchor='lm')
    im.save(PUB / 'og/og-fallback-en.jpg', quality=88, optimize=True)


def favicons():
    for name, size in [('favicon-aws-32.png', 32), ('favicon-aws-192.png', 192),
                       ('favicon-aws-512.png', 512)]:
        logo(size).save(PUB / name)
    # apple-touch: niente trasparenza, fondo quasi-nero pieno
    t = Image.new('RGB', (180, 180), INK)
    t.paste(logo(180), (0, 0), logo(180))
    t.save(PUB / 'apple-touch-icon-aws.png')
    (PUB / 'favicon-aws.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60">'
        '<rect x="1.5" y="1.5" width="57" height="57" rx="13" fill="#0C0A09" stroke="#00FF00" stroke-width="2.6"/>'
        '<text x="30" y="30" text-anchor="middle" dominant-baseline="central" '
        'font-family="Inter Tight,Arial,Helvetica,sans-serif" font-weight="700" font-size="21" letter-spacing="1">'
        '<tspan fill="#00FF00">A</tspan><tspan fill="#FFFFFF">W</tspan><tspan fill="#00FF00">S</tspan></text></svg>')


if __name__ == '__main__':
    og_home()
    og_fallback()
    favicons()
    print('ok')
