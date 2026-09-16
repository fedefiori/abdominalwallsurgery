import { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';

const SiteCtx = createContext(null);

export function SiteProvider({ children }) {
    const [site, setSite] = useState(null);
    const [theme, setThemeState] = useState(() => {
        try { return localStorage.getItem('pw-theme') || 'dark'; } catch { return 'dark'; }
    });
    const [variant, setVariant] = useState(() => {
        const q = new URLSearchParams(window.location.search).get('v');
        if (q && ['1', '2', '3', '4'].includes(q)) return q;
        try { return localStorage.getItem('pw-variant') || '1'; } catch { return '1'; }
    });
    const showPicker = new URLSearchParams(window.location.search).has('v');

    useEffect(() => {
        api.site().then(setSite).catch(() => setSite(null));
    }, []);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.setAttribute('data-variant', variant);
        document.documentElement.setAttribute('lang', site?.lang || 'it');
        try {
            localStorage.setItem('pw-theme', theme);
            localStorage.setItem('pw-variant', variant);
        } catch { /* ignore */ }
    }, [theme, variant, site]);

    const ui = site?.ui || {};
    return (
        <SiteCtx.Provider value={{ site, ui, theme, setTheme: setThemeState, variant, setVariant, showPicker }}>
            {children}
        </SiteCtx.Provider>
    );
}

export function useSite() {
    return useContext(SiteCtx);
}
