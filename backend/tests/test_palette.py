"""Palette lime del verticale EN: solo le illustrazioni di marca vengono
ricolorate, le foto cliniche restano fedeli."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import recolor  # noqa: E402

MEDIA = Path(__file__).resolve().parents[1] / 'static' / 'media'

BRAND = ['strati-della-parete.webp', 'chirurgo-sala-operatoria.webp', 'piani-della-rete.webp',
         'respiro-diaframma.webp', 'vac-pressione-negativa.webp']
CLINICAL = ['chirurgia-parete-addominale-03.webp', 'ritratto-dottor-fiori.webp', 'ecografia-addominale.webp',
            'tc-e-rm-nella-valutazione-della-parete-addominale-01.webp', 'vac-02.webp', 'chirurgia-della-parete-05.webp']


def test_brand_illustrations_detected():
    for n in BRAND:
        assert recolor.is_brand_illustration(Image.open(MEDIA / n)), n


def test_clinical_photos_untouched():
    for n in CLINICAL:
        assert not recolor.is_brand_illustration(Image.open(MEDIA / n)), n


def test_recolor_turns_blue_into_lime():
    im = Image.new('RGB', (4, 4), (60, 131, 225))  # azzurro logo
    r, g, b = recolor.recolor_image(im).getpixel((0, 0))
    assert g > r and g > b
