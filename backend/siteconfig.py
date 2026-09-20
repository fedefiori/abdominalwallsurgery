"""Configurazione di sito: identita' da variabili d'ambiente, nessun valore
italiano cablato nei percorsi o nei testi di interfaccia serviti."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

SITE_KEY = os.environ.get('SITE_KEY', '')
SITE_LANG = os.environ.get('SITE_LANG', '')
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', '').rstrip('/')
HUB_URL = os.environ.get('HUB_URL', 'https://www.federicofiori.com').rstrip('/')
NETWORK_STATS_TOKEN = os.environ.get('NETWORK_STATS_TOKEN', '')

# La mappa di rete deriva da SITE_KEY: nessuna altra variabile necessaria.
NETWORK_SITES = {
    'parete': {
        'lang': 'it',
        'domain': 'https://www.chirurgiadellaparete.it',
        'articlePath': '/articoli/',
        'articlesIndex': '/articoli',
        'twin': 'parete_en',
        'syndication': f'{HUB_URL}/api/blog/syndication/parete',
    },
    'parete_en': {
        'lang': 'en',
        'domain': 'https://www.abdominalwallsurgery.com',
        'articlePath': '/articles/',
        'articlesIndex': '/articles',
        'twin': 'parete',
        'syndication': f'{HUB_URL}/api/blog/syndication/parete_en',
    },
}

# Ecosistema (GEO): i siti della rete, con descrizione per lingua.
NETWORK_ECOSYSTEM = [
    {'url': HUB_URL, 'label': {'it': 'federicofiori.com', 'en': 'federicofiori.com'},
     'desc': {'it': "L'hub: identità, curriculum, tecnica TESAR, tecnica MILA, glossario e galleria dei risultati del Dott. Federico Fiori.",
              'en': 'The hub: identity, curriculum, TESAR and MILA techniques, glossary and results gallery of Dr. Federico Fiori.'}},
    {'url': 'https://www.diastasiedintorni.it', 'label': {'it': 'diastasiedintorni.it', 'en': 'diastasiedintorni.it'},
     'desc': {'it': 'Il verticale italiano sulla diastasi dei muscoli retti: sintomi, misurazione, riabilitazione e intervento.',
              'en': 'The Italian vertical on rectus diastasis: symptoms, measurement, rehabilitation and surgery.'}},
    {'url': 'https://www.diastasisandbeyond.com', 'label': {'it': 'diastasisandbeyond.com', 'en': 'diastasisandbeyond.com'},
     'desc': {'it': 'Il verticale inglese sulla diastasi dei retti e il percorso del paziente.',
              'en': 'The English vertical on rectus diastasis and the patient journey.'}},
    {'url': 'https://www.chirurgiadellaparete.it', 'label': {'it': 'chirurgiadellaparete.it', 'en': 'chirurgiadellaparete.it'},
     'desc': {'it': 'Questo sito: ernie, laparoceli e pre-abilitazione, in italiano.',
              'en': 'The Italian site on hernias, incisional hernias and prehabilitation.'}},
    {'url': 'https://www.abdominalwallsurgery.com', 'label': {'it': 'abdominalwallsurgery.com', 'en': 'abdominalwallsurgery.com'},
     'live': False,
     'desc': {'it': 'Il verticale inglese su ernie, laparoceli e Chirurgia della Parete addominale.',
              'en': 'The English vertical on hernias, incisional hernias and abdominal wall surgery.'}},
    {'url': 'https://www.federico-fiori.it', 'label': {'it': 'federico-fiori.it', 'en': 'federico-fiori.it'},
     'desc': {'it': 'La chirurgia plastica del Dott. Federico Fiori: la forma.',
              'en': 'Dr. Federico Fiori’s plastic surgery practice: the form.'}},
]

# Stringhe di interfaccia (non contenuti clinici), per lingua.
UI = {
    'it': {
        'site_name': 'Chirurgia della Parete addominale',
        'site_baseline': 'Ernie, laparoceli e ricostruzione della parete addominale',
        'nav_home': 'Home', 'nav_articles': 'Articoli', 'nav_contacts': 'Contatti', 'nav_about': 'Il Dott. Federico Fiori',
        'nav_chapters': 'Capitoli',
        'index_title': 'Indice dei contenuti', 'on_this_page': 'In questa pagina',
        'faq_title': 'Domande frequenti', 'network_title': 'La rete',
        'network_intro': 'Questo sito fa parte della rete editoriale del Dott. Federico Fiori: ogni argomento ha un sito di riferimento.',
        'articles_title': 'Articoli di approfondimento',
        'articles_sub': 'Gli articoli divulgativi scritti e approvati nell’area editoriale di federicofiori.com, serviti qui per i lettori di questo sito.',
        'read_article': 'Leggi l’articolo', 'updated': 'Aggiornato il', 'published': 'Pubblicato il',
        'breadcrumb_home': 'Home', 'breadcrumb_articles': 'Articoli',
        'notfound_title': 'Pagina non trovata',
        'notfound_text': 'L’indirizzo richiesto non esiste o è stato spostato. Usa il menu o torna alla pagina iniziale.',
        'notfound_cta': 'Torna alla home', 'theme_light': 'Tema chiaro', 'theme_dark': 'Tema scuro',
        'menu_open': 'Apri il menu', 'menu_close': 'Chiudi il menu',
        'contact_cta': 'Richiedi una valutazione',
        'home_kicker': 'A cura del Dott. Federico Fiori',
        'hero_answer_label': 'In sintesi',
        'figures_disclaimer': 'Immagini cliniche a scopo illustrativo.',
        'tags_label': 'Argomenti',
    },
    'en': {
        'site_name': 'Abdominal Wall Surgery',
        'site_baseline': 'Hernias, incisional hernias and abdominal wall reconstruction',
        'nav_home': 'Home', 'nav_articles': 'Articles', 'nav_contacts': 'Contact', 'nav_about': 'Dr. Federico Fiori',
        'nav_chapters': 'Chapters',
        'index_title': 'Table of contents', 'on_this_page': 'On this page',
        'faq_title': 'Frequently asked questions', 'network_title': 'The network',
        'network_intro': 'This site is part of Dr. Federico Fiori’s editorial network: each topic has a reference site.',
        'articles_title': 'In-depth articles',
        'articles_sub': 'Educational articles written and approved in the federicofiori.com editorial area, served here for this site’s readers.',
        'read_article': 'Read the article', 'updated': 'Updated on', 'published': 'Published on',
        'breadcrumb_home': 'Home', 'breadcrumb_articles': 'Articles',
        'notfound_title': 'Page not found',
        'notfound_text': 'The requested address does not exist or has been moved. Use the menu or go back to the home page.',
        'notfound_cta': 'Back to home', 'theme_light': 'Light theme', 'theme_dark': 'Dark theme',
        'menu_open': 'Open menu', 'menu_close': 'Close menu',
        'contact_cta': 'Request an evaluation',
        'home_kicker': 'Vertical site of the federicofiori.com network',
        'hero_answer_label': 'In brief',
        'figures_disclaimer': 'Clinical images for illustrative purposes.',
        'tags_label': 'Topics',
    },
}

def site():
    cfg = NETWORK_SITES.get(SITE_KEY)
    if not cfg:
        raise RuntimeError('SITE_KEY non riconosciuta')
    lang = SITE_LANG or cfg['lang']
    return {
        'key': SITE_KEY,
        'lang': lang,
        'domain': SITE_DOMAIN or cfg['domain'],
        'articlePath': cfg['articlePath'],
        'articlesIndex': cfg['articlesIndex'],
        'syndication': cfg['syndication'],
        'twinKey': cfg['twin'],
        'twin': NETWORK_SITES[cfg['twin']],
        'ui': UI[lang],
    }

def nav_pages(lang):
    """Ordine di navigazione con etichette per lingua."""
    if lang == 'en':
        return [
            ('anatomia-della-parete-addominale-e-abdominal-core', 'Anatomy'),
            ('difetti-della-parete-addominale-e-classificazione', 'Defects & classification'),
            ('sintomi-e-complicanze', 'Symptoms & complications'),
            ('radiologia', 'Radiology'),
            ('la-terapia-chirurgica', 'Surgical treatment'),
            ('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi', 'Meshes'),
            ('le-complicanze-chirurgiche-la-vac-therapy', 'Complications & VAC'),
            ('preabilitazione-dei-pazienti-all-intervento-chirurgico', 'Prehabilitation'),
            ('la-diastasi-dei-muscoli-retti', 'Rectus diastasis'),
        ]
    return [
        ('anatomia-della-parete-addominale-e-abdominal-core', 'Anatomia'),
        ('difetti-della-parete-addominale-e-classificazione', 'Difetti e classificazione'),
        ('sintomi-e-complicanze', 'Sintomi e complicanze'),
        ('radiologia', 'Radiologia'),
        ('la-terapia-chirurgica', 'Terapia chirurgica'),
        ('le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi', 'Protesi'),
        ('le-complicanze-chirurgiche-la-vac-therapy', 'Complicanze e VAC'),
        ('preabilitazione-dei-pazienti-all-intervento-chirurgico', 'Preabilitazione'),
        ('la-diastasi-dei-muscoli-retti', 'Diastasi dei retti'),
    ]
