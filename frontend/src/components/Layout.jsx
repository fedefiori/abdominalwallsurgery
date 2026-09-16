import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, Menu, X } from 'lucide-react';
import { useSite } from '../lib/SiteContext';
import { track } from '../lib/api';

function ThemeToggle() {
    const { theme, setTheme, ui } = useSite();
    const next = theme === 'dark' ? 'light' : 'dark';
    return (
        <button
            className="pw-iconbtn"
            data-testid="theme-toggle"
            aria-label={next === 'light' ? ui.theme_light : ui.theme_dark}
            onClick={() => setTheme(next)}
        >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>
    );
}

export default function Layout({ children }) {
    const { site, ui } = useSite();
    const [open, setOpen] = useState(false);
    const location = useLocation();

    useEffect(() => { setOpen(false); }, [location.pathname]);
    useEffect(() => { track(location.pathname); }, [location.pathname]);

    const mainNav = [
        { to: '/', label: ui.nav_home },
        ...(site?.nav || []).slice(0, 3),
        { to: site?.articlesIndex || '/articoli', label: ui.nav_articles },
        { to: '/chi-sono/', label: ui.nav_about },
        { to: '/contatti/', label: ui.nav_contacts },
    ].map((i) => (i.path ? { to: i.path, label: i.label } : i));

    return (
        <>
            <header className="pw-header" data-testid="site-header">
                <div className="pw-shell pw-header-inner">
                    <Link to="/" className="pw-brand" data-testid="brand-link">
                        <span className="pw-brand-mark" aria-hidden="true" />
                        <span className="pw-brand-name">{ui.site_name}</span>
                        <span className="pw-brand-sub">Dott. Federico Fiori</span>
                    </Link>
                    <nav className="pw-nav" aria-label="Navigazione principale" data-testid="main-nav">
                        {mainNav.map((item) => (
                            <Link key={item.to} to={item.to}
                                aria-current={location.pathname === item.to ? 'page' : undefined}>
                                {item.label}
                            </Link>
                        ))}
                        <ThemeToggle />
                    </nav>
                    <div style={{ marginLeft: 'auto', display: 'flex', gap: '.6rem' }} className="pw-mobilebar">
                        <span className="pw-nav" style={{ display: 'none' }} />
                        <button className="pw-iconbtn pw-burger" data-testid="menu-toggle"
                            aria-label={open ? ui.menu_close : ui.menu_open}
                            aria-expanded={open}
                            onClick={() => setOpen(!open)}
                            style={{ display: 'none' }}>
                            {open ? <X size={18} /> : <Menu size={18} />}
                        </button>
                    </div>
                    <style>{`@media (max-width: 980px) { .pw-burger { display: inline-flex !important; } .pw-header .pw-iconbtn[data-testid="theme-toggle"] { display: none; } }`}</style>
                </div>
                <AnimatePresence>
                    {open && (
                        <motion.nav
                            className="pw-mobile-menu" data-testid="mobile-menu"
                            initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: 'easeOut' }}
                        >
                            <div className="pw-shell" style={{ padding: '1rem 1.25rem 1.5rem' }}>
                                {[...mainNav, ...(site?.nav || []).slice(3)].map((item) => (
                                    <Link key={item.to} to={item.to}>{item.label}</Link>
                                ))}
                                <div style={{ paddingTop: '1rem' }}><ThemeToggle /></div>
                            </div>
                        </motion.nav>
                    )}
                </AnimatePresence>
            </header>
            <main>{children}</main>
            <footer className="pw-footer" data-testid="site-footer">
                <div className="pw-shell">
                    <p className="pw-label">{ui.network_title}</p>
                    <h2 style={{ fontSize: 'clamp(1.4rem,2.6vw,1.9rem)', maxWidth: '34ch', marginTop: '.6rem' }}>
                        {ui.network_intro}
                    </h2>
                    <div className="pw-net-grid" data-testid="network-grid">
                        {(site?.network || []).map((n) => (
                            <div className="pw-net-item" key={n.url}>
                                <a href={n.url} target="_blank" rel="noopener">{n.label}</a>
                                <p>{n.desc}</p>
                            </div>
                        ))}
                    </div>
                    <div className="pw-footer-base">
                        <span className="pw-label">© {new Date().getFullYear()} Dott. Federico Fiori — Milano</span>
                        <span style={{ display: 'flex', gap: '1.4rem' }}>
                            <Link to="/privacy-policy/" className="pw-label" style={{ textDecoration: 'none' }}>Privacy</Link>
                            <Link to="/cookie-policy/" className="pw-label" style={{ textDecoration: 'none' }}>Cookie</Link>
                        </span>
                    </div>
                </div>
            </footer>
        </>
    );
}
