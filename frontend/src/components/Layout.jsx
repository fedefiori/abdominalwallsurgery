import { useEffect, useState, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, Menu, X, ChevronDown } from 'lucide-react';
import { useSite } from '../lib/SiteContext';
import { API } from '../lib/api';
import { useJsonLd } from '../hooks/useSEO';

/** Menu «Capitoli»: i 9 capitoli in tendina, una sola riga di navigazione. */
function ChaptersDropdown({ items, label }) {
    const [open, setOpen] = useState(false);
    const ref = useRef(null);
    const location = useLocation();
    useEffect(() => { setOpen(false); }, [location.pathname]);
    useEffect(() => {
        const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
        document.addEventListener('click', close);
        return () => document.removeEventListener('click', close);
    }, []);
    if (!items?.length) return null;
    return (
        <div className="pw-dropdown" ref={ref}>
            <button type="button" className="pw-dropdown-btn" data-testid="chapters-menu-toggle"
                aria-expanded={open} aria-haspopup="true" onClick={() => setOpen(!open)}>
                {label}
                <ChevronDown size={14} aria-hidden="true" style={{
                    transition: 'transform .25s ease', transform: open ? 'rotate(180deg)' : 'none',
                }} />
            </button>
            {open && (
                <div className="pw-dropdown-panel" data-testid="chapters-menu" role="menu">
                    {items.map((item) => (
                        <Link key={item.path} to={item.path} role="menuitem"
                            aria-current={location.pathname === item.path ? 'page' : undefined}>
                            {item.label}
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}

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

function Aurora() {
    return (
        <div className="pw-aurora" aria-hidden="true" data-testid="bg-aurora">
            <i /><i /><i />
        </div>
    );
}

function Progress() {
    const ref = useRef(null);
    useEffect(() => {
        let raf = 0;
        const onScroll = () => {
            cancelAnimationFrame(raf);
            raf = requestAnimationFrame(() => {
                const max = document.documentElement.scrollHeight - window.innerHeight;
                if (ref.current) {
                    ref.current.style.width = `${max > 0 ? (window.scrollY / max) * 100 : 0}%`;
                }
            });
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => { window.removeEventListener('scroll', onScroll); cancelAnimationFrame(raf); };
    }, []);
    return <div className="pw-progress" ref={ref} aria-hidden="true" />;
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
    useJsonLd(location.pathname);

    const mainNav = [
        { to: '/', label: ui.nav_home },
        { to: site?.articlesIndex || '/articoli', label: ui.nav_articles },
        ...(!site || site.hasVideo ? [{ to: '/video/', label: ui.nav_video || 'Video' }] : []),
        { to: '/chi-sono/', label: ui.nav_about },
        { to: '/contatti/', label: ui.nav_contacts },
    ].map((i) => (i.path ? { to: i.path, label: i.label } : i));

    return (
        <>
            <Halo />
            <Aurora />
            <Progress />
            <header className="pw-header" data-testid="site-header">
                <div className="pw-shell pw-header-inner">
                    <Link to="/" className="pw-brand" data-testid="brand-link">
                        <img className="pw-brand-logo" src={`${API}/api/media/logo-chirurgia-della-parete-orizz.webp`}
                            alt="Chirurgia della Parete Addominale — Dott. Federico Fiori" width="172" height="60" data-testid="brand-logo" />
                        <span className="pw-brand-sub">Dott. Federico Fiori</span>
                    </Link>
                    <nav className="pw-nav" aria-label="Navigazione principale" data-testid="main-nav">
                        <Link to="/" aria-current={location.pathname === '/' ? 'page' : undefined}>{ui.nav_home}</Link>
                        <ChaptersDropdown items={site?.nav} label={ui.nav_chapters || 'Capitoli'} />
                        {mainNav.slice(1).map((item) => (
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
                            <p><strong>Dott. Federico Fiori</strong></p>
                            <p>Medico Chirurgo — Specialista in Chirurgia Generale</p>
                            <p className="pw-footer-role">Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, PO San Carlo Borromeo, Milano</p>
                            <p>Informazioni e appuntamenti<br />
                                <a href="mailto:info@federicofiori.com">info@federicofiori.com</a></p>
                            <p>Scrivi al Dott. Fiori<br />
                                <a href="mailto:fedefiori@federicofiori.com">fedefiori@federicofiori.com</a></p>
                            <p>Telefono <a href="tel:+390276021568">+39 02 76021568</a></p>
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
                                <li><a href="/sitemap.xml">Sitemap</a></li>
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
