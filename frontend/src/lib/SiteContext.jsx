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
