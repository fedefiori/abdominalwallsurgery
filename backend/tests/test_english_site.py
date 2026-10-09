"""Backend QA for English site (SITE_KEY=parete_en)"""
import os, re
import pytest
import html
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://abdominal-wall-site.preview.emergentagent.com').rstrip('/')

PILLAR_PAGES = [
    "/abdominal-wall-anatomy-and-abdominal-core/",
    "/abdominal-wall-defects-and-classification/",
    "/symptoms-and-complications/",
    "/imaging-and-radiology/",
    "/surgical-treatment/",
    "/meshes-and-the-plane-of-placement/",
    "/surgical-complications-and-vac-therapy/",
    "/patient-prehabilitation-before-surgery/",
]

OTHER_PAGES = ["/", "/videos/", "/contact/", "/privacy-policy/", "/cookie-policy/", "/articles"]
ALL_PAGES = PILLAR_PAGES + OTHER_PAGES

# mappa delle coppie IT <-> EN (14), decisa con l'hub
IT = "https://www.chirurgiadellaparete.it"
PAIRS = {
    "/": "/",
    "/abdominal-wall-anatomy-and-abdominal-core/": "/anatomia-della-parete-addominale-e-abdominal-core/",
    "/abdominal-wall-defects-and-classification/": "/difetti-della-parete-addominale-e-classificazione/",
    "/symptoms-and-complications/": "/sintomi-e-complicanze/",
    "/imaging-and-radiology/": "/radiologia/",
    "/surgical-treatment/": "/la-terapia-chirurgica/",
    "/meshes-and-the-plane-of-placement/": "/le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/",
    "/surgical-complications-and-vac-therapy/": "/le-complicanze-chirurgiche-la-vac-therapy/",
    "/patient-prehabilitation-before-surgery/": "/preabilitazione-dei-pazienti-all-intervento-chirurgico/",
    "/videos/": "/video/",
    "/contact/": "/contatti/",
    "/articles": "/articoli",
    "/privacy-policy/": "/privacy-policy/",
    "/cookie-policy/": "/cookie-policy/",
}


def prerender(path):
    r = requests.get(f"{BASE_URL}/api/seo/prerender", params={"path": path, "absolute": "true"}, timeout=25)
    return r


@pytest.fixture(scope="session")
def site():
    r = requests.get(f"{BASE_URL}/api/site", timeout=15)
    assert r.status_code == 200
    return r.json()


def test_site_lang_en(site):
    assert site["lang"] == "en"
    assert site["key"] == "parete_en"
    assert site["brand"]["palette"] == "green"


def test_site_domain(site):
    assert "abdominalwallsurgery.com" in site["domain"]


@pytest.mark.parametrize("path", ALL_PAGES)
def test_prerender_hreflang_pair_no_videoobject(path):
    r = prerender(path)
    assert r.status_code == 200, f"{path} -> {r.status_code}"
    body = r.text
    tags = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)" />', body)
    assert tags == [("it", IT + PAIRS[path]),
                    ("en", "https://www.abdominalwallsurgery.com" + path),
                    ("x-default", IT + PAIRS[path])], f"{path}: {tags}"
    assert "federicofiori.com" not in "".join(u for _, u in tags)
    assert "VideoObject" not in body, f"VideoObject leak on {path}"
    assert "abdominalwallsurgery.com" in body, f"missing canonical domain on {path}"


def test_articles_have_no_hreflang():
    arts = requests.get(f"{BASE_URL}/api/blog/articles", timeout=20).json()["items"]
    for a in arts:
        body = prerender("/articles/" + a["slug"]).text
        assert "hreflang" not in body, a["slug"]


@pytest.mark.parametrize("path,target", [
    ("/about/", "https://www.federicofiori.com/en/curriculum"),
    ("/about", "https://www.federicofiori.com/en/curriculum"),
    ("/rectus-diastasis/", "https://www.diastasisandbeyond.com/"),
    ("/rectus-diastasis", "https://www.diastasisandbeyond.com/"),
])
def test_retired_pages_301(path, target):
    r = requests.get(f"{BASE_URL}/api/seo/prerender", params={"path": path, "absolute": "true"},
                     timeout=20, allow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == target


def test_home_h1_and_lang():
    body = prerender("/").text
    assert "<h1>Abdominal Wall Surgery: from diagnosis to repair</h1>" in body
    assert "<title>Abdominal Wall Surgery | Dr. Federico Fiori</title>" in body
    assert '<link rel="canonical" href="https://www.abdominalwallsurgery.com/" />' in body


def test_probe_endpoint_json():
    slug = "incisional-hernia-after-abdominal-surgery-when-to-operate"
    r = requests.get(f"{BASE_URL}/api/blog/posts/en/{slug}", timeout=20)
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/json")
    assert r.json()["post"]["slug"] == slug


def test_robots_first_line():
    assert requests.get(f"{BASE_URL}/api/robots.txt", timeout=15).text.splitlines()[0] == \
        "# Abdominal Wall Surgery — federicofiori.com network"


@pytest.mark.parametrize("path", ALL_PAGES)
def test_meta_description_length_150_160(path):
    body = prerender(path).text
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', body, re.IGNORECASE)
    assert m, f"no description on {path}"
    desc = html.unescape(m.group(1))  # conta i caratteri visibili, non le entita' HTML
    L = len(desc)
    # Contract says 150-160; flag anything outside
    assert 150 <= L <= 160, f"{path}: desc length {L} outside 150-160: {desc!r}"


@pytest.mark.parametrize("path", PILLAR_PAGES)
def test_medical_webpage_schema_on_pillars(path):
    body = prerender(path).text
    assert "MedicalWebPage" in body, f"missing MedicalWebPage on pillar {path}"


def test_favicon_in_prerender():
    body = prerender("/").text
    assert "/favicon-aws.svg" in body


def test_og_home_image():
    body = prerender("/").text
    assert "og-home-en.jpg" in body


def test_html_lang_en():
    body = prerender("/").text
    assert '<html lang="en"' in body


def test_sitemap_english():
    r = requests.get(f"{BASE_URL}/api/sitemap.xml", timeout=15)
    assert r.status_code == 200
    assert "abdominalwallsurgery.com" in r.text
    locs = re.findall(r"<loc>([^<]+)</loc>", r.text)
    assert len(locs) == 16, locs
    assert not any("/about" in l or "rectus-diastasis" in l for l in locs)
    assert "chirurgiadellaparete.it" not in r.text


def test_robots_english():
    r = requests.get(f"{BASE_URL}/api/robots.txt", timeout=15)
    assert r.status_code == 200
    assert "abdominalwallsurgery.com" in r.text


def test_llms_english():
    r = requests.get(f"{BASE_URL}/api/llms.txt", timeout=15)
    assert r.status_code == 200
    assert "abdominalwallsurgery.com" in r.text


def test_articles_list():
    r = requests.get(f"{BASE_URL}/api/blog/articles", timeout=20)
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, (list, dict))


def test_contact_invalid_email_rejected():
    payload = {"name": "Test User", "email": "not-an-email", "message": "hello world test",
               "reason": "appuntamento", "consent": True}
    r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=15)
    assert r.status_code in (400, 422), f"invalid email accepted: {r.status_code}: {r.text[:200]}"


def test_contact_empty_rejected():
    r = requests.post(f"{BASE_URL}/api/contact", json={}, timeout=15)
    assert r.status_code in (400, 422)


def test_contact_honeypot_silent_ok():
    payload = {
        "name": "TEST Honeypot",
        "email": "honeypot@example.com",
        "message": "TEST silent — do not send",
        "reason": "appuntamento",
        "consent": True,
        "company": "honeypot-bot",
    }
    r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=15)
    assert r.status_code in (200, 202), f"honeypot got {r.status_code}: {r.text[:300]}"


def test_hero_mobile_media_served():
    for ext in ("webm", "mp4"):
        r = requests.get(f"{BASE_URL}/media/hero-loop-parete-addominale-en-mobile.{ext}",
                         timeout=20, stream=True, allow_redirects=True)
        assert r.status_code == 200, f"mobile hero {ext}: {r.status_code}"


def test_hero_desktop_media_served():
    for ext in ("webm", "mp4"):
        r = requests.get(f"{BASE_URL}/media/hero-loop-parete-addominale-en.{ext}",
                         timeout=20, stream=True, allow_redirects=True)
        assert r.status_code == 200, f"desktop hero {ext}: {r.status_code}"


def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert r.status_code == 200
    j = r.json()
    assert j.get("lang") == "en"
    assert j.get("site") == "parete_en"


def test_no_italian_leftover_on_contact_prerender():
    body = prerender("/contact/").text
    forbidden = [">Contatti<", ">Contattaci<", "Scrivici", "Appuntamento in studio"]
    for s in forbidden:
        assert s not in body, f"IT text found: {s}"
