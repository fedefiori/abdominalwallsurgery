import { useEffect } from 'react';

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
    qui gestiamo la vista per gli utenti nel browser. */
export default function useSEO({ title, description, canonical, noindex, domain }) {
    useEffect(() => {
        if (title) document.title = title;
        if (description) {
            setMeta('name', 'description', description);
            setMeta('property', 'og:description', description);
        }
        if (title) setMeta('property', 'og:title', title);
        if (canonical) setLink('canonical', canonical);
        const hostMismatch = domain && !window.location.host.endsWith(
            domain.replace(/^https?:\/\//, ''));
        setMeta('name', 'robots', (noindex || hostMismatch) ? 'noindex,nofollow' : 'index,follow');
    }, [title, description, canonical, noindex, domain]);
}
