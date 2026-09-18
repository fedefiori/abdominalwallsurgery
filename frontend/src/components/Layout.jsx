import { useEffect, useState, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, Menu, X } from 'lucide-react';
import { useSite } from '../lib/SiteContext';
import { track } from '../lib/api';

function Halo() {
    const ref = useRef(null);
    useEffect(() => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined;
        let raf = 0;
        const onScroll = () => {
            cancelAnimationFrame(raf);
            raf = requestAnimationFrame(() => {
                if (ref.current) {
                    const y = window.scrollY * 0.04; // pochi pixel, parallasse lento
                    ref.current.style.transform = `translate3d(0, ${y}px, 0)`;
                }
            });
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => { window.removeEventListener('scroll', onScroll); cancelAnimationFrame(raf); };
    }, []);
    return <div className="pw-halo" ref={ref} aria-hidden="true" />;
}

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
        { to: site?.articlesIndex || '/articoli', label: ui.nav_articles },
        { to: '/chi-sono/', label: ui.nav_about },
        { to: '/contatti/', label: ui.nav_contacts },
    ].map((i) => (i.path ? { to: i.path, label: i.label } : i));

    return (
        <>
            <Halo />
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
                <nav className="pw-nav-strip pw-shell" aria-label="Tutti i contenuti" data-testid="nav-strip">
                    {(site?.nav || []).map((item) => (
                        <Link key={item.path} to={item.path}
                            aria-current={location.pathname === item.path ? 'page' : undefined}>
                            {item.label}
                        </Link>
                    ))}
                </nav>
                <AnimatePresence>
                    {open && (
                        <motion.nav
                            className="pw-mobile-menu" data-testid="mobile-menu"
                            initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: 'easeOut' }}
                        >
                            <div className="pw-shell" style={{ padding: '1rem 1.25rem 1.5rem' }}>
                                {[...mainNav, ...(site?.nav || [])].map((item) => (
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
                    <div className="pw-footer-grid">
                        <section data-testid="footer-chi-opera">
                            <h3>Chi opera</h3>
                            <p><strong>Dott. Federico Fiori</strong> — Chirurgo</p>
                            <p>Responsabile della Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, PO San Carlo Borromeo, Milano</p>
                            <p>Contatto diretto della rete: <a href="mailto:info@federicofiori.com">info@federicofiori.com</a></p>
                            <p><a href="https://www.federicofiori.com/curriculum" target="_blank" rel="noopener">Curriculum completo sull’hub</a></p>
                        </section>
                        <section data-testid="footer-dove-riceve">
                            <h3>Dove riceve</h3>
                            <p><strong>Fi Multicare</strong> — Centro Medico Multidisciplinare</p>
                            <p>Galleria del Corso 4, 20122 Milano</p>
                            <p>Telefono <a href={site?.clinic?.telHref || 'tel:+390276021568'}>{site?.clinic?.telLabel || '+39 02 76021568'}</a><br />
                                E-mail <a href="mailto:info@fimulticare.it">info@fimulticare.it</a></p>
                            <p>Visite su appuntamento</p>
                            <p><a href="https://www.fimulticare.it/" target="_blank" rel="noopener">fimulticare.it</a></p>
                        </section>
                        <section data-testid="footer-la-rete">
                            <h3>La rete</h3>
                            <ul className="pw-footer-net">
                                {(site?.network || []).map((n) => (
                                    <li key={n.url}>
                                        <a href={n.url} target="_blank" rel="noopener">{n.label}</a>
                                        <p>{n.desc}</p>
                                    </li>
                                ))}
                            </ul>
                        </section>
                        <section data-testid="footer-legale">
                            <h3>Legale e servizio</h3>
                            <ul>
                                <li><Link to="/privacy-policy/">Privacy policy</Link></li>
                                <li><Link to="/cookie-policy/">Cookie policy</Link></li>
                                <li><a href="/api/seo/sitemap.xml">Sitemap</a></li>
                                <li>
                                    <button
                                        className="pw-footer-toplink"
                                        data-testid="back-to-top"
                                        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                                        style={{ color: 'var(--accent-soft)', fontSize: '14px' }}
                                    >
                                        Torna su ↑
                                    </button>
                                </li>
                            </ul>
                        </section>
                    </div>
                    <div className="pw-footer-legal">
                        <span className="pw-footer-disclaimer" data-testid="footer-disclaimer">
                            Le informazioni di questo sito hanno finalità divulgativa e non sostituiscono la visita medica.
                        </span>
                        <span className="pw-label">© {new Date().getFullYear()} Dott. Federico Fiori — Milano</span>
                    </div>
                </div>
            </footer>
        </>
    );
}
