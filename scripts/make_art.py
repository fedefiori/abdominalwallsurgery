#!/usr/bin/env python3
"""Illustrazioni stilizzate in stile hub: fondo blu notte, reticolo tenue,
linee luminose blu acciaio. Motivi geometrici attinenti al tema della pagina."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

MEDIA = Path('/app/backend/static/media')
BG = (8, 22, 34)
GRID = (23, 42, 58)
LINE = (79, 176, 245)
LINE2 = (43, 122, 190)
ACCENT = (11, 129, 225)
W, H = 1200, 675


def base():
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 48):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 48):
        d.line([(0, y), (W, y)], fill=GRID, width=1)
    return im


def glow(im, draw_fn, color=LINE, width=3):
    """Linea luminosa: alone sfocato + tratto nitido."""
    ov = Image.new('RGB', (W, H), (0, 0, 0))
    od = ImageDraw.Draw(ov)
    draw_fn(od, width + 6, tuple(c // 2 for c in color))
    ov = ov.filter(ImageFilter.GaussianBlur(12))
    im = ImageChops.screen(im, ov)
    od2 = ImageDraw.Draw(im)
    draw_fn(od2, width, tuple(min(255, c + 70) for c in color))
    return im


def arc_wave(od, w, c, ybase=340, amp=90, phase=0.0, span=(80, 1120)):
    pts = []
    for x in range(span[0], span[1], 6):
        y = ybase + amp * math.sin((x / 160.0) + phase)
        pts.append((x, y))
    if len(pts) > 1:
        od.line(pts, fill=c, width=w)


def circles(od, w, c, cx=600, cy=338, radii=(60, 130, 210, 300)):
    for r in radii:
        od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=w)


def steps(od, w, c, x0=220, y0=470, n=5, dx=150, dy=70):
    x, y = x0, y0
    for _ in range(n):
        od.line([(x, y), (x + dx, y)], fill=c, width=w)
        od.line([(x + dx, y), (x + dx, y - dy)], fill=c, width=w)
        x += dx
        y -= dy


def pulse(od, w, c):
    pts = [(80, 340), (320, 340), (380, 240), (470, 460), (560, 270),
           (620, 340), (900, 340), (950, 300), (1000, 340), (1120, 340)]
    od.line(pts, fill=c, width=w, joint='curve')


def shield(od, w, c):
    pts = [(600, 140), (840, 220), (840, 380), (780, 480), (600, 560),
           (420, 480), (360, 380), (360, 220)]
    od.line(pts + [pts[0]], fill=c, width=w, joint='curve')
    od.ellipse([565, 300, 635, 370], outline=c, width=w)
    od.line([(600, 370), (600, 440)], fill=c, width=w)


def mesh(od, w, c):
    for i in range(0, 11):
        x = 200 + i * 80
        od.line([(x, 180), (x - 120, 500)], fill=c, width=w)
        od.line([(x - 120, 180), (x, 500)], fill=c, width=w)


def arcs_layers(od, w, c):
    for i, r in enumerate(range(120, 420, 60)):
        od.arc([600 - r, 470 - r, 600 + r, 470 + r], start=180, end=360, fill=c, width=w)
    for x in (330, 470, 610, 750, 870):
        od.ellipse([x - 7, 470 - (x - 330) * 0 // 1 - 7 - abs(x - 600) * 0 - 7, x + 7, 483], outline=c, width=w)


def wave_down(od, w, c):
    for phase in (0.0, 0.9, 1.8):
        pts = []
        for x in range(140, 1060, 6):
            y = 250 + phase * 60 + 55 * math.sin(x / 120.0 + phase)
            pts.append((x, y))
        od.line(pts, fill=c, width=w)
    for x in (300, 600, 900):
        od.line([(x, 430), (x, 520)], fill=c, width=w)
        od.line([(x - 14, 500), (x, 524), (x + 14, 500)], fill=c, width=w)


def scan(od, w, c):
    od.ellipse([430, 130, 770, 550], outline=c, width=w)
    od.ellipse([510, 210, 690, 470], outline=c, width=w)
    od.line([(80, 340), (1120, 340)], fill=c, width=w)
    for x in range(80, 1120, 80):
        od.line([(x, 328), (x, 352)], fill=c, width=w)


def profile(od, w, c):
    od.arc([300, 180, 900, 780], start=180, end=360, fill=c, width=w)
    od.arc([420, 300, 780, 700], start=180, end=360, fill=c, width=w)
    od.ellipse([580, 380, 660, 460], outline=c, width=w)
    od.line([(600, 300), (600, 380)], fill=c, width=w)


def radar(od, w, c):
    circles(od, w, c, 600, 340, (70, 150, 240, 330))
    od.line([(600, 340), (950, 160)], fill=c, width=w)
    od.ellipse([880, 190, 910, 220], fill=c)


def build(name, motif):
    im = base()
    im = glow(im, motif)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(35, 58, 76), width=2)
    im.save(MEDIA / f'{name}.webp', 'WEBP', quality=82)
    print(name, (MEDIA / f'{name}.webp').stat().st_size, 'bytes')


build('arte-parete-strati', lambda od, w, c: arcs_layers(od, w, c))
build('arte-sintomi-profilo', lambda od, w, c: profile(od, w, c))
build('arte-preabilitazione-passi', lambda od, w, c: steps(od, w, c))
build('arte-preabilitazione-pulso', lambda od, w, c: pulse(od, w, c))
build('arte-vac-onde', lambda od, w, c: wave_down(od, w, c))
build('arte-privacy-scudo', lambda od, w, c: shield(od, w, c))
build('arte-cookie-radar', lambda od, w, c: radar(od, w, c))
build('arte-protesi-trama', lambda od, w, c: mesh(od, w, c))
build('arte-radiologia-scansione', lambda od, w, c: scan(od, w, c))
build('arte-onde-core', lambda od, w, c: (arc_wave(od, w, c, 300, 80, 0.0), arc_wave(od, w, c, 380, 70, 1.2), arc_wave(od, w, c, 240, 60, 2.1)))
