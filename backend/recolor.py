"""Palette del verticale inglese: le illustrazioni di marca (fondo notte + tratto
azzurro) vengono ricolorate in verde, le foto cliniche restano fedeli.

Riconoscimento automatico (vale anche per le immagini future): immagine scura
con colore quasi tutto nella banda azzurra. Ricolorazione: il tratto azzurro
diventa verde a due toni (morbido #6FE06F nei mezzi toni, fluo #00FF00 nelle
luci), il fondo notte diventa il quasi-nero caldo del sito. I toni non azzurri
(es. muscoli nel busto del video) restano invariati."""
import numpy as np
from PIL import Image

BLUE_LO, BLUE_HI = 165.0, 255.0       # banda azzurra/ciano (gradi)
HUE_SOFT, HUE_FLUO = 120.0, 120.0     # #6FE06F / #00FF00 (stessa tinta, cambia la saturazione)


def is_brand_illustration(im):
    hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(np.float32) / 255
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    colored = (s > 0.25) & (v > 0.15)
    if colored.mean() < 0.08 or v.mean() > 0.25:
        return False
    blue = ((h > BLUE_LO) & (h < BLUE_HI) & colored).sum() / colored.sum()
    return blue > 0.9


def recolor_array(rgb, gain=1.0):
    """rgb: uint8 HxWx3 -> uint8 HxWx3 in palette verde. gain>1 schiarisce (video)."""
    img = Image.fromarray(rgb, 'RGB')
    hsv = np.asarray(img.convert('HSV')).astype(np.float32)
    h, s, v = hsv[..., 0] * (360 / 255), hsv[..., 1] / 255, hsv[..., 2] / 255
    # peso "azzurro": 1 dentro la banda, sfuma ai bordi (niente scalini)
    w = np.clip((h - BLUE_LO + 15) / 15, 0, 1) * np.clip((BLUE_HI + 15 - h) / 15, 0, 1)
    # tono lime: morbido nei mezzi toni, fluo nelle luci
    t = np.clip((v - 0.35) / 0.45, 0, 1)
    lime_h = HUE_SOFT + (HUE_FLUO - HUE_SOFT) * t
    new_h = h * (1 - w) + lime_h * w
    # fondo notte (scuro e azzurro) -> quasi-nero caldo: saturazione giu'
    dark = np.clip((0.42 - v) / 0.3, 0, 1) * w
    new_s = s * (1 - 0.93 * dark)
    # morbido nei mezzi toni (saturazione ~0.5), fluo pieno nelle luci
    new_s = np.where(w > 0, np.clip(new_s * (0.6 + 1.0 * t) * w + new_s * (1 - w), 0, 1), new_s)
    v = np.clip(v * gain, 0, 1)
    out = np.stack([new_h * (255 / 360), new_s * 255, v * 255], -1)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return np.asarray(Image.fromarray(out, 'HSV').convert('RGB'))


def recolor_image(im):
    return Image.fromarray(recolor_array(np.asarray(im.convert('RGB'))), 'RGB')


_seen = {}


def palette_file(src, cache_dir):
    """Percorso da servire: la versione lime (in cache su disco) se src e'
    un'illustrazione di marca, altrimenti l'originale."""
    key = (src.name, src.stat().st_mtime)
    if key not in _seen:
        out = cache_dir / src.name
        if out.exists() and out.stat().st_mtime >= key[1]:
            _seen[key] = out
        else:
            with Image.open(src) as im:
                if is_brand_illustration(im):
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    recolor_image(im).save(out, 'WEBP', quality=86, method=6)
                    _seen[key] = out
                else:
                    _seen[key] = src
    return _seen[key]
