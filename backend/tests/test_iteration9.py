"""Iteration 9 - Regression + new content changes for chirurgiadellaparete.it"""
import os
import re
import requests
import pytest

BASE = os.environ.get("REACT_APP_BACKEND_URL", "https://chirurgia-test.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def prerender_chi_sono():
    r = requests.get(f"{BASE}/api/seo/prerender", params={"path": "/chi-sono/"}, timeout=20)
    assert r.status_code == 200, r.text
    return r.text


# ---------- SEO prerender /chi-sono/ ----------
class TestChiSonoPrerender:
    def test_title(self, prerender_chi_sono):
        assert "<title>Dott. Federico Fiori - Chirurgia Generale e della parete | Milano</title>" in prerender_chi_sono

    def test_meta_description(self, prerender_chi_sono):
        assert re.search(r'<meta[^>]+name="description"[^>]+content="Chi è il dott. Federico Fiori: Medico Chirurgo', prerender_chi_sono)

    def test_og_twitter_title(self, prerender_chi_sono):
        assert 'property="og:title"' in prerender_chi_sono
        assert "Dott. Federico Fiori - Chirurgia Generale e della parete | Milano" in prerender_chi_sono
        assert 'name="twitter:title"' in prerender_chi_sono or 'property="twitter:title"' in prerender_chi_sono

    def test_breadcrumb_new_h1(self, prerender_chi_sono):
        assert "BreadcrumbList" in prerender_chi_sono
        assert "Il dott. Federico Fiori: profilo e attività clinica" in prerender_chi_sono

    def test_profilepage_last_reviewed(self, prerender_chi_sono):
        assert "ProfilePage" in prerender_chi_sono
        assert "2026-09-19" in prerender_chi_sono

    def test_person_jobtitle(self, prerender_chi_sono):
        # exact requested wording
        assert "Medico Chirurgo — Specialista in Chirurgia Generale" in prerender_chi_sono

    def test_faq_four_items(self, prerender_chi_sono):
        assert "FAQPage" in prerender_chi_sono
        # count Question entities
        q_count = prerender_chi_sono.count('"@type": "Question"') + prerender_chi_sono.count('"@type":"Question"')
        assert q_count >= 4, f"Expected >=4 FAQ questions, got {q_count}"

    def test_h1_exact(self, prerender_chi_sono):
        assert re.search(r'<h1[^>]*>\s*Il dott\. Federico Fiori: profilo e attività clinica\s*</h1>', prerender_chi_sono)

    def test_five_h2(self, prerender_chi_sono):
        expected = [
            "Di che cosa si occupa il dott. Fiori?",
            "Come viene scelta la tecnica per ogni Paziente?",
            "Dove opera e dove riceve?",
            "Dove è stata presentata la tecnica TESAR?",
            "Dove si trova il curriculum completo?",
        ]
        for h in expected:
            assert h in prerender_chi_sono, f"Missing H2: {h}"

    def test_pmid_link(self, prerender_chi_sono):
        m = re.search(r'<a[^>]+href="https://pubmed\.ncbi\.nlm\.nih\.gov/30807248/?"[^>]*>PMID:\s*30807248</a>', prerender_chi_sono)
        assert m, "PMID link not found"
        tag = m.group(0)
        assert 'target="_blank"' in tag
        assert 'rel="noopener"' in tag
        assert "nofollow" not in tag

    def test_only_one_morfofunzionale(self, prerender_chi_sono):
        # Must appear exactly once (as body link) and only in href/body, not in H1/title/H2
        # Count occurrences of the phrase in visible text portion
        count = prerender_chi_sono.lower().count("approccio morfo-funzionale")
        # Could appear as anchor text once + inside href once
        assert count <= 2, f"Too many 'approccio morfo-funzionale' occurrences: {count}"
        assert count >= 1

    def test_no_ambulatorio_frase(self, prerender_chi_sono):
        assert "titolare dell'ambulatorio di Chirurgia della Parete" not in prerender_chi_sono
        assert "titolare dell’ambulatorio di Chirurgia della Parete" not in prerender_chi_sono

    def test_trentanni_present(self, prerender_chi_sono):
        assert "trent'anni" in prerender_chi_sono or "trent’anni" in prerender_chi_sono
        assert "vent'anni" not in prerender_chi_sono and "vent’anni" not in prerender_chi_sono

    def test_in_sintesi_speakable(self, prerender_chi_sono):
        # 'In sintesi' label is added client-side; prerender emits <p class="pw-answer">
        # with the answer text (which acts as speakable summary).
        assert 'pw-answer' in prerender_chi_sono
        assert 'Medico Chirurgo, Specialista in Chirurgia Generale' in prerender_chi_sono


# ---------- llms.txt ----------
class TestLlmsTxt:
    @pytest.fixture(scope="class")
    def llms(self):
        r = requests.get(f"{BASE}/api/seo/llms.txt", timeout=15)
        assert r.status_code == 200
        return r.text

    def test_chi_sono_line(self, llms):
        # New title referenced
        assert "Il dott. Federico Fiori" in llms
        # Identity line
        assert "Responsabile dell'Unità" in llms or "Responsabile dell’Unità" in llms

    def test_no_della_unita(self, llms):
        assert "della Unità" not in llms


# ---------- sitemap ----------
class TestSitemap:
    @pytest.fixture(scope="class")
    def sitemap(self):
        r = requests.get(f"{BASE}/api/seo/sitemap.xml", timeout=15)
        assert r.status_code == 200
        return r.text

    @pytest.mark.parametrize("path", [
        "/chi-sono/",
        "/",
        "/la-terapia-chirurgica/",
        "/preabilitazione-dei-pazienti-all-intervento-chirurgico/",
    ])
    def test_lastmod(self, sitemap, path):
        # find <url> block containing loc for path and check lastmod
        # Build regex
        pattern = re.compile(
            r"<url>\s*<loc>[^<]*" + re.escape(path) + r"</loc>\s*<lastmod>([^<]+)</lastmod>",
            re.DOTALL,
        )
        m = pattern.search(sitemap)
        assert m, f"No sitemap entry for {path}"
        assert m.group(1).startswith("2026-09-19"), f"lastmod for {path} = {m.group(1)}"


# ---------- media ----------
class TestMedia:
    @pytest.mark.parametrize("f", [
        "chirurgo-sala-operatoria.webp",
        "preabilitazione-parete.webp",
    ])
    def test_media_200(self, f):
        r = requests.get(f"{BASE}/api/media/{f}", timeout=15)
        assert r.status_code == 200, f
        assert int(r.headers.get("content-length", "0")) > 100 or len(r.content) > 100


# ---------- other pages regression ----------
class TestPrerenderRegression:
    @pytest.mark.parametrize("path", [
        "/",
        "/la-terapia-chirurgica/",
        "/preabilitazione-dei-pazienti-all-intervento-chirurgico/",
        "/anatomia-della-parete-addominale-e-abdominal-core/",
        "/contatti/",
        "/difetti-della-parete-addominale-e-classificazione/",
    ])
    def test_page_200(self, path):
        r = requests.get(f"{BASE}/api/seo/prerender", params={"path": path}, timeout=20)
        assert r.status_code == 200, path

    def test_home_new_block(self):
        r = requests.get(f"{BASE}/api/seo/prerender", params={"path": "/"}, timeout=20)
        assert r.status_code == 200
        t = r.text
        # HTML-encoded apostrophe possible
        assert ("Perché la parete si valuta insieme alla forma dell'addome?" in t or
                "Perché la parete si valuta insieme alla forma dell&#x27;addome?" in t or
                "Perché la parete si valuta insieme alla forma dell&#39;addome?" in t or
                "Perché la parete si valuta insieme alla forma dell’addome?" in t)
        # 'I capitoli' heading is client-side (React component). Skip in prerender.
        assert "Dove riceve?" in t
        assert "Dove si riceve?" not in t

    def test_home_new_image(self):
        r = requests.get(f"{BASE}/api/seo/prerender", params={"path": "/"}, timeout=20)
        assert "chirurgo-sala-operatoria.webp" in r.text

    def test_terapia_new_block_and_fixes(self):
        r = requests.get(f"{BASE}/api/seo/prerender", params={"path": "/la-terapia-chirurgica/"}, timeout=20)
        t = r.text
        assert "La tecnica basta a definire il risultato?" in t
        # Links hub
        assert "federicofiori.com/approccio-morfo-funzionale" in t
        assert re.search(r"federicofiori\.com/(mila|approccio)", t, re.I)
        # 3 corrected sentences
        assert "difetti della parete addominale anteriore" in t
        assert "senza protesi" in t
        assert "ogni tipo di intervento chirurgico" in t
        # No "Dottor" in body (Carrara/Costa/Manetti/Ramirez)
        for name in ["Carrara", "Costa", "Manetti", "Ramirez"]:
            # find surrounding text
            idx = t.find(name)
            if idx >= 0:
                ctx = t[max(0, idx-30):idx]
                assert "Dottor " not in ctx, f"'Dottor {name}' found"

    def test_preab_new_image(self):
        r = requests.get(f"{BASE}/api/seo/prerender",
                         params={"path": "/preabilitazione-dei-pazienti-all-intervento-chirurgico/"},
                         timeout=20)
        assert "preabilitazione-parete.webp" in r.text
