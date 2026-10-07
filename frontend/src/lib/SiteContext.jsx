import { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';

const SiteCtx = createContext(null);

export function SiteProvider({ children }) {
    const [site, setSite] = useState(null);
    const [theme, setThemeState] = useState(() => {
        try { return localStorage.getItem('pw-theme') || 'light'; } catch { return 'light'; }
    });

    useEffect(() => {
        api.site().then(setSite).catch(() => setSite(null));
    }, []);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.setAttribute('lang', site?.lang || 'it');
        try { localStorage.setItem('pw-theme', theme); } catch { /* ignore */ }
    }, [theme, site]);

    useEffect(() => {
        const b = site?.brand;
        if (!b) return;
        const icon = document.head.querySelector('link[rel="icon"]');
        if (icon) { icon.setAttribute('href', b.favicon); icon.setAttribute('type', b.faviconType); }
        let touch = document.head.querySelector('link[rel="apple-touch-icon"]');
        if (!touch) {
            touch = document.createElement('link');
            touch.setAttribute('rel', 'apple-touch-icon');
            document.head.appendChild(touch);
        }
        touch.setAttribute('href', b.appleTouch);
    }, [site]);

    const ui = site?.ui || {};
    return (
        <SiteCtx.Provider value={{ site, ui, theme, setTheme: setThemeState }}>
            {children}
        </SiteCtx.Provider>
    );
}

export function useSite() {
    return useContext(SiteCtx);
}
