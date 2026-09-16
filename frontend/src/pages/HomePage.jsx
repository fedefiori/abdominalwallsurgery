import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowUpRight } from 'lucide-react';
import { useSite } from '../lib/SiteContext';
import { api } from '../lib/api';
import useSEO from '../hooks/useSEO';
import { MaskLines, Reveal } from '../components/Reveal';
import { Blocks } from '../components/Blocks';
import { FaqView } from '../components/FaqView';
import { useState } from 'react';

const MARQUEE = [
    'Ernia ombelicale', 'Laparocele', 'Diastasi dei retti', 'Tecnica Rives-Stoppa',
    'Separazione dei componenti', 'TAR', 'Chirurgia robotica', 'Protesi retromuscolare',
    'Preabilitazione', 'VAC therapy', 'Classificazione EHS', 'Abdominal core',
];

function WallArt() {
    const ref = useRef(null);
    const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
    const y = useTransform(scrollYProgress, [0, 1], [0, 90]);
    return (
        <motion.div className="pw-hero-art" ref={ref} style={{ y }} aria-hidden="true">
            <svg viewBox="0 0 400 520" fill="none" role="presentation">
                <rect x="60" y="20" width="280" height="480" stroke="var(--line)" strokeWidth="1" />
                <line x1="200" y1="20" x2="200" y2="500" stroke="var(--accent)" strokeWidth="1.5" strokeDasharray="3 6" />
                {[80, 150, 220, 290, 360, 430].map((yy) => (
                    <g key={yy}>
                        <path d={`M70 ${yy} Q 160 ${yy - 16} 190 ${yy}`} stroke="var(--steel)" strokeWidth="1" opacity="0.7" />
                        <path d={`M330 ${yy} Q 240 ${yy - 16} 210 ${yy}`} stroke="var(--steel)" strokeWidth="1" opacity="0.7" />
                    </g>
                ))}
                <circle cx="200" cy="220" r="10" stroke="var(--accent)" strokeWidth="1.5" />
                <circle cx="200" cy="220" r="26" stroke="var(--line)" strokeWidth="1" />
            </svg>
        </motion.div>
    );
}

function splitLines(text) {
    const words = (text || '').split(' ');
    if (words.length <= 3) return [text];
    const mid = Math.ceil(words.length / 2);
    return [words.slice(0, mid).join(' '), words.slice(mid).join(' ')];
}

export default function HomePage() {
    const { site, ui } = useSite();
    const [page, setPage] = useState(null);
    const [articles, setArticles] = useState([]);

    useEffect(() => {
        api.page('home').then(setPage).catch(() => setPage(null));
        api.articles().then((d) => setArticles(d.items || [])).catch(() => setArticles([]));
    }, []);

    useSEO({
        title: page?.metaTitle || ui.site_name,
        description: page?.metaDescription,
        canonical: site ? `${site.domain}/` : undefined,
        domain: site?.domain,
    });

    const chapters = site?.nav || [];
    const h1 = page?.h1 || ui.site_name || '';

    return (
        <div data-testid="home-page">
            <section className="pw-hero">
                <div className="pw-hero-ghost" aria-hidden="true">PARETE</div>
                <div className="pw-shell" style={{ position: 'relative' }}>
                    <div className="pw-ticks" aria-hidden="true"><i /><i /><i /><i /></div>
                    <div className="pw-hero-kicker">
                        <span className="pw-label" data-testid="home-kicker">{ui.home_kicker}</span>
                    </div>
                    {site?.person?.jobTitle && (
                        <motion.p
                            className="pw-hero-titles" data-testid="hero-titles"
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            transition={{ duration: 0.8, delay: 0.35 }}
                        >
                            {site.person.jobTitle} — ASST Santi Paolo e Carlo, Milano
                        </motion.p>
                    )}
                    <MaskLines lines={splitLines(h1)} />
                    <motion.p
                        className="pw-hero-sub"
                        initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, delay: 0.55 }}
                    >
                        {page?.answer || ui.site_baseline}
                    </motion.p>
                    <motion.div
                        className="pw-hero-cta"
                        initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, delay: 0.7 }}
                    >
                        <Link className="pw-btn pw-btn-solid" data-testid="hero-cta-therapy" to="/la-terapia-chirurgica/">
                            {site?.lang === 'en' ? 'Surgical treatment' : 'La terapia chirurgica'}
                            <ArrowUpRight size={14} />
                        </Link>
                        <Link className="pw-btn" data-testid="hero-cta-contact" to="/contatti/">
                            {ui.contact_cta}
                        </Link>
                    </motion.div>
                    <WallArt />
                    <div className="pw-scanline" aria-hidden="true" />
                </div>
            </section>

            <div className="pw-marquee" aria-hidden="true" data-testid="home-marquee">
                <div className="pw-marquee-track">
                    {[...MARQUEE, ...MARQUEE].map((m, i) => <span key={i}>{m}</span>)}
                </div>
            </div>

            {page?.blocks?.length > 0 && (
                <section className="pw-section" data-testid="home-intro">
                    <div className="pw-shell">
                        <Blocks blocks={page.blocks.filter((b) => !(b.type === 'img' && (b.src || '').includes('logo')))} />
                    </div>
                </section>
            )}

            <div className="pw-band-deep" data-testid="chapters-band">
            <section className="pw-section">
                <div className="pw-shell">
                    <Reveal>
                        <div className="pw-section-head">
                            <span className="pw-label">{ui.index_title}</span>
                            <h2>{site?.lang === 'en' ? 'The chapters of the abdominal wall' : 'I capitoli della parete addominale'}</h2>
                        </div>
                    </Reveal>
                    <div className="pw-chapters" data-testid="home-chapters">
                        {chapters.map((c, i) => (
                            <Reveal key={c.path} delay={i * 0.05}>
                                <Link className="pw-chapter" to={c.path} data-testid={`chapter-${i + 1}`}>
                                    <span className="pw-chapter-num">{String(i + 1).padStart(2, '0')}</span>
                                    <span>
                                        <span className="pw-chapter-title">{c.label}</span>
                                    </span>
                                    <ArrowUpRight className="pw-chapter-arrow" size={20} />
                                </Link>
                            </Reveal>
                        ))}
                    </div>
                </div>
            </section>

            {articles.length > 0 && (
                <section className="pw-section" style={{ paddingTop: 0 }}>
                    <div className="pw-shell">
                        <Reveal>
                            <div className="pw-section-head">
                                <span className="pw-label">{ui.articles_title}</span>
                                <h2>{site?.lang === 'en' ? 'Latest from the editorial desk' : 'Ultimi articoli dalla redazione'}</h2>
                            </div>
                        </Reveal>
                        <div className="pw-article-list" data-testid="home-articles">
                            {articles.slice(0, 3).map((a) => (
                                <Reveal key={a.slug}>
                                    <Link className="pw-article-card" to={`${site?.articlesIndex || '/articoli'}/${a.slug}`} data-testid={`home-article-${a.slug}`}>
                                        {a.coverUrl && <img src={a.coverUrl} alt={a.title} width="1200" height="675" loading="lazy" decoding="async" />}
                                        <span>
                                            {a.categoryLabel && <span className="pw-label">{a.categoryLabel}</span>}
                                            <h2>{a.title}</h2>
                                            <p>{a.excerpt}</p>
                                        </span>
                                    </Link>
                                </Reveal>
                            ))}
                        </div>
                    </div>
                </section>
            )}
            </div>

            {page?.faq?.length > 0 && (
                <section className="pw-section" data-testid="home-faq-section">
                    <div className="pw-shell" style={{ maxWidth: '820px' }}>
                        <FaqView faq={page.faq} title={ui.faq_title} />
                    </div>
                </section>
            )}
        </div>
    );
}
