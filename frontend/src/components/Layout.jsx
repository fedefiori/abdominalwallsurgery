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
    const en = site?.lang === 'en';

    useEffect(() => { setOpen(false); }, [location.pathname]);
    useJsonLd(location.pathname);

    // «Dott. F. Fiori» porta al curriculum canonico sull'hub (contratto 04/10:
    // nessuna pagina-persona su questo sito). Sul gemello inglese esiste invece
    // una pagina /about/ breve che rimanda al curriculum dell'hub.
    const CURRICULUM_URL = 'https://www.federicofiori.com/curriculum';
    const aboutItem = en
        ? { to: '/about/', label: ui.nav_about }
        : { to: CURRICULUM_URL, label: ui.nav_about, external: true };
    const mainNav = [
        { to: '/', label: ui.nav_home },
        { to: site?.articlesIndex || '/articoli', label: ui.nav_articles },
        ...(!site || site.hasVideo ? [{ to: en ? '/videos/' : '/video/', label: ui.nav_video || 'Video' }] : []),
        aboutItem,
        { to: en ? '/contact/' : '/contatti/', label: ui.nav_contacts },
    ];

    return (
        <>
            <Halo />
            <Aurora />
            <Progress />
            <header className="pw-header" data-testid="site-header">
                <div className="pw-shell pw-header-inner">
                    <Link to="/" className="pw-brand" data-testid="brand-link">
                        {en ? (
                            <>
                                <svg className="pw-brand-logo" width="60" height="60" viewBox="0 0 60 60"
                                    role="img" aria-label="AWS — Abdominal Wall Surgery" data-testid="brand-logo">
                                    <rect x="1.5" y="1.5" width="57" height="57" rx="13" fill="#0C0A09"
                                        stroke="#00FF00" strokeWidth="2.6" />
                                    <text x="30" y="30" textAnchor="middle" dominantBaseline="central"
                                        fontFamily="Inter Tight, sans-serif" fontWeight="700" fontSize="21"
                                        letterSpacing="1">
                                        <tspan fill="#00FF00">A</tspan><tspan fill="#FFFFFF">W</tspan><tspan fill="#00FF00">S</tspan>
                                    </text>
                                </svg>
                                <span className="pw-brand-textblock">
                                    <span className="pw-brand-name">Abdominal Wall Surgery</span>
                                    <span className="pw-brand-sub">Dr. Federico Fiori</span>
                                </span>
                            </>
                        ) : (
                            <>
                                <img className="pw-brand-logo" src={`${API}/api/media/logo-chirurgia-della-parete-orizz.webp`}
                                    alt="Chirurgia della Parete Addominale — Dott. Federico Fiori" width="172" height="60" data-testid="brand-logo" />
                                <span className="pw-brand-sub">Dott. Federico Fiori</span>
                            </>
                        )}
                    </Link>
                    <nav className="pw-nav" aria-label="Navigazione principale" data-testid="main-nav">
                        <Link to="/" aria-current={location.pathname === '/' ? 'page' : undefined}>{ui.nav_home}</Link>
                        <ChaptersDropdown items={site?.nav} label={ui.nav_chapters || 'Capitoli'} />
                        {mainNav.slice(1).map((item) => (
                            item.external ? (
                                <a key={item.to} href={item.to}>{item.label}</a>
                            ) : (
                                <Link key={item.to} to={item.to}
                                    aria-current={location.pathname === item.to ? 'page' : undefined}>
                                    {item.label}
                                </Link>
                            )
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
                                    item.external
                                        ? <a key={item.to} href={item.to}>{item.label}</a>
                                        : <Link key={item.to} to={item.to}>{item.label}</Link>
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
                            <h3>{en ? 'The surgeon' : 'Chi opera'}</h3>
                            <p><strong>{en ? 'Dr. Federico Fiori' : 'Dott. Federico Fiori'}</strong></p>
                            <p>{en ? 'General surgeon' : 'Medico Chirurgo — Specialista in Chirurgia Generale'}</p>
                            <p className="pw-footer-role">{en
                                ? 'Head of the Abdominal Wall Surgery Unit — ASST Santi Paolo e Carlo, San Carlo Borromeo Hospital, Milan'
                                : "Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, PO San Carlo Borromeo, Milano"}</p>
                            <p>{en ? 'Information and appointments' : 'Informazioni e appuntamenti'}<br />
                                <a href="mailto:info@federicofiori.com">info@federicofiori.com</a></p>
                            <p>{en ? 'Write to Dr. Fiori' : 'Scrivi al Dott. Fiori'}<br />
                                <a href="mailto:fedefiori@federicofiori.com">fedefiori@federicofiori.com</a></p>
                            <p>{en ? 'Phone' : 'Telefono'} <a href="tel:+390276021568">+39 02 7602 1568</a></p>
                            <p><a href="https://www.federicofiori.com/curriculum" target="_blank" rel="noopener">{en ? 'Full curriculum on the hub' : 'Curriculum completo sull’hub'}</a></p>
                        </section>
                        <section data-testid="footer-dove-riceve">
                            <h3>{en ? 'Where he practices' : 'Dove riceve'}</h3>
                            <p><strong>Fi Multicare</strong> — {en ? 'Multidisciplinary Medical Center' : 'Centro Medico Multidisciplinare'}</p>
                            <p>Galleria del Corso 4, 20122 Milano</p>
                            <p>{en ? 'Phone' : 'Telefono'} <a href={site?.clinic?.telHref || 'tel:+390276021568'}>{site?.clinic?.telLabel || '+39 02 7602 1568'}</a><br />
                                {en ? 'E-mail' : 'E-mail'} <a href="mailto:info@fimulticare.it">info@fimulticare.it</a></p>
                            <p>{en ? 'Visits by appointment' : 'Visite su appuntamento'}</p>
                            <p><a href="https://www.fimulticare.it/" target="_blank" rel="noopener">fimulticare.it</a></p>
                        </section>
                        <section data-testid="footer-la-rete">
                            <h3>{en ? 'The network' : 'La rete'}</h3>
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
                            <h3>{en ? 'Legal & service' : 'Legale e servizio'}</h3>
                            <ul>
                                <li><Link to="/privacy-policy/">{en ? 'Privacy policy' : 'Privacy policy'}</Link></li>
                                <li><Link to="/cookie-policy/">{en ? 'Cookie policy' : 'Cookie policy'}</Link></li>
                                <li><a href="/sitemap.xml">Sitemap</a></li>
                                <li>
                                    <button
                                        className="pw-footer-toplink"
                                        data-testid="back-to-top"
                                        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                                        style={{ color: 'var(--accent-soft)', fontSize: '14px' }}
                                    >
                                        {en ? 'Back to top ↑' : 'Torna su ↑'}
                                    </button>
                                </li>
                            </ul>
                        </section>
                    </div>
                    <div className="pw-footer-legal">
                        <span className="pw-footer-disclaimer" data-testid="footer-disclaimer">
                            {en
                                ? 'The information on this site is for educational purposes and does not replace a medical consultation.'
                                : 'Le informazioni di questo sito hanno finalità divulgativa e non sostituiscono la visita medica.'}
                        </span>
                        <span className="pw-label">© {new Date().getFullYear()} {en ? 'Dr. Federico Fiori — Milan' : 'Dott. Federico Fiori — Milano'}</span>
                    </div>
                </div>
            </footer>
        </>
    );
}
