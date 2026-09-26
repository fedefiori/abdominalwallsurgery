import { useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

function setMeta(attr, key, content) {
    let el = document.head.querySelector(`meta[${attr}="${key}"]`);
    if (!el) {
        el = document.createElement('meta');
        el.setAttribute(attr, key);
        document.head.appendChild(el);
    }
    el.setAttribute('content', content || '');
}

function setLink(rel, href) {
    let el = document.head.querySelector(`link[rel="${rel}"]`);
    if (!el) {
        el = document.createElement('link');
        el.setAttribute('rel', rel);
        document.head.appendChild(el);
    }
    el.setAttribute('href', href);
}

/** SEO lato client: il crawler riceve l'HTML dal prerender del Worker;
    qui gestiamo la vista per gli utenti nel browser, con OG completi. */
export default function useSEO({ title, description, canonical, noindex, domain, siteName, lang, image, imageAlt, ogType }) {
    useEffect(() => {
        if (title) document.title = title;
        if (title) setMeta('property', 'og:title', title);
        if (description) {
            setMeta('name', 'description', description);
            setMeta('property', 'og:description', description);
        }
        if (canonical) {
            setLink('canonical', canonical);
            setMeta('property', 'og:url', canonical);
        }
        if (domain) {
            const img = image || `${domain}/og/og-fallback.jpg`;
            setMeta('property', 'og:type', ogType || 'website');
            setMeta('property', 'og:site_name', siteName || '');
            setMeta('property', 'og:locale', lang === 'en' ? 'en_US' : 'it_IT');
            setMeta('property', 'og:image', img);
            setMeta('property', 'og:image:width', '1200');
            setMeta('property', 'og:image:height', '630');
            setMeta('property', 'og:image:alt', imageAlt || title || '');
            setMeta('name', 'twitter:card', 'summary_large_image');
            if (title) setMeta('name', 'twitter:title', title);
            if (description) setMeta('name', 'twitter:description', description);
            setMeta('name', 'twitter:image', img);
        }
        // Meta robots del go-live: index/follow SOLO sugli host canonici
        // (stessa logica del gemello diastasiedintorni.it), noindex altrove.
        const host = window.location.hostname.toLowerCase();
        const canon = (domain || '').replace(/^https?:\/\//, '').split(':')[0].toLowerCase();
        const canonHosts = [canon, canon.replace(/^www\./, '')].filter(Boolean);
        const hostMismatch = domain && !canonHosts.includes(host);
        setMeta('name', 'robots', (noindex || hostMismatch)
            ? 'noindex,nofollow'
            : 'index, follow, max-snippet:-1, max-image-preview:large');
    }, [title, description, canonical, noindex, domain, siteName, lang, image, imageAlt, ogType]);
}

/** BLOCCANTE 1 (collaudo 19/06): i dati strutturati devono esistere nel DOM vivo.
    Un unico <script type="application/ld+json"> con @graph per pagina, identico
    a quello del prerender (stesso endpoint, stessi @id dell'hub). */
export function useJsonLd(path) {
    useEffect(() => {
        let cancelled = false;
        const tag = `script[data-seo-jsonld]`;
        fetch(`${API}/api/seo/jsonld?path=${encodeURIComponent(path)}`)
            .then((r) => (r.ok ? r.json() : null))
            .then((ld) => {
                if (cancelled || !ld) return;
                document.head.querySelectorAll(tag).forEach((el) => el.remove());
                const el = document.createElement('script');
                el.type = 'application/ld+json';
                el.setAttribute('data-seo-jsonld', path);
                el.textContent = JSON.stringify(ld);
                document.head.appendChild(el);
            })
            .catch(() => { /* rete o 404: niente jsonld su questa rotta */ });
        return () => {
            cancelled = true;
            document.head.querySelectorAll(tag).forEach((el) => el.remove());
        };
    }, [path]);
}
