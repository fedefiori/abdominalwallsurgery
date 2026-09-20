import { API } from './api';

// Statistiche di rete, di prima parte: sid pseudonimo in sessionStorage
// (mezz'ora), nessun cookie di profilazione, mai un dato personale.
const SID_KEY = 'pw_sid';
const SID_TTL = 30 * 60 * 1000;
let lastPath = null;
let prevUrl = '';

function sessionId() {
    try {
        const now = Date.now();
        const raw = sessionStorage.getItem(SID_KEY);
        if (raw) {
            const o = JSON.parse(raw);
            if (o && o.v && now - o.t < SID_TTL) return o.v;
        }
        const v = (window.crypto && crypto.randomUUID)
            ? crypto.randomUUID()
            : Math.random().toString(36).slice(2) + now.toString(36);
        sessionStorage.setItem(SID_KEY, JSON.stringify({ v, t: now }));
        return v;
    } catch { return ''; }
}

function post(payload) {
    try {
        fetch(`${API}/api/stats/hit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            keepalive: true,
            credentials: 'omit',
        }).catch(() => {});
    } catch { /* silenzioso: mai un errore visibile */ }
}

export function trackPageview(path) {
    if (!API || typeof document === 'undefined') return;
    if (!path || path === lastPath) return; // UNA riga per pagina vista, non una per render
    lastPath = path;
    const ref = prevUrl || document.referrer || '';
    prevUrl = window.location.origin + path;
    const sid = sessionId();
    if (!sid) return;
    post({ path, title: document.title || '', sid, lang: 'it', ref });
}

function clickLabel(a) {
    const href = (a.getAttribute('href') || '').trim();
    if (href.startsWith('tel:')) return 'contatti-telefono';
    if (href.startsWith('mailto:')) return 'contatti-email';
    if (/wa\.me|whatsapp/i.test(href)) return 'contatti-whatsapp';
    if (href === '/contatti' || href === '/contatti/') {
        return a.closest('header') ? 'contatti-menu' : 'contatti-link';
    }
    return null;
}

export function initStatsClicks() {
    if (typeof document === 'undefined') return;
    document.addEventListener('click', (e) => {
        const a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
        if (!a) return;
        const label = clickLabel(a);
        if (!label) return;
        const sid = sessionId();
        if (!sid) return;
        post({
            path: window.location.pathname, title: document.title || '',
            sid, lang: 'it', ref: '', ev: 'click', label,
        });
    }, true);
}
