import { useEffect, useState } from 'react';
import { Link, useParams, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useSite } from '../lib/SiteContext';
import { api } from '../lib/api';
import useSEO from '../hooks/useSEO';
import { Blocks, tocOf } from '../components/Blocks';
import { Reveal } from '../components/Reveal';

export const KNOWN_SLUGS = [
    'anatomia-della-parete-addominale-e-abdominal-core',
    'la-terapia-chirurgica', 'chi-sono', 'radiologia',
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi',
    'le-complicanze-chirurgiche-la-vac-therapy', 'sintomi-e-complicanze',
    'difetti-della-parete-addominale-e-classificazione', 'la-diastasi-dei-muscoli-retti',
    'preabilitazione-dei-pazienti-all-intervento-chirurgico', 'contatti',
    'privacy-policy', 'cookie-policy',
];

function Toc({ items }) {
    const [active, setActive] = useState('');
    useEffect(() => {
        const obs = new IntersectionObserver(
            (entries) => {
                entries.forEach((e) => { if (e.isIntersecting) setActive(e.target.id); });
            },
            { rootMargin: '-20% 0px -70% 0px' });
        items.forEach((t) => {
            const el = document.getElementById(t.id);
            if (el) obs.observe(el);
        });
        return () => obs.disconnect();
    }, [items]);
    if (items.length < 3) return null;
    return (
        <nav className="pw-toc" aria-label="Indice della pagina" data-testid="page-toc">
            {items.map((t) => (
                <a key={t.id} href={`#${t.id}`} className={active === t.id ? 'active' : ''}>{t.label}</a>
            ))}
        </nav>
    );
}

function Faq({ faq, title }) {
    const [openIdx, setOpenIdx] = useState(-1);
    if (!faq?.length) return null;
    return (
        <section className="pw-faq" data-testid="faq-section">
            <h2>{title}</h2>
            {faq.map((f, i) => (
                <div className="pw-faq-item" key={i}>
                    <button
                        className="pw-faq-q"
                        data-testid={`faq-question-${i}`}
                        aria-expanded={openIdx === i}
                        onClick={() => setOpenIdx(openIdx === i ? -1 : i)}
                    >
                        {f.q}
                        <ChevronDown size={16} style={{
                            flex: 'none', transition: 'transform .3s ease',
                            transform: openIdx === i ? 'rotate(180deg)' : 'none',
                        }} />
                    </button>
                    <AnimatePresence initial={false}>
                        {openIdx === i && (
                            <motion.div
                                className="pw-faq-a"
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.32, ease: 'easeOut' }}
                            >
                                <div data-testid={`faq-answer-${i}`}>{f.a}</div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            ))}
        </section>
    );
}

export default function PillarPage() {
    const { slug } = useParams();
    const { site, ui } = useSite();
    const [page, setPage] = useState(null);
    const [missing, setMissing] = useState(false);

    useEffect(() => {
        setPage(null); setMissing(false);
        api.page(slug).then(setPage).catch(() => setMissing(true));
    }, [slug]);

    useSEO({
        title: page?.metaTitle,
        description: page?.metaDescription,
        canonical: site && page ? `${site.domain}${page.path}` : undefined,
        domain: site?.domain,
    });

    if (missing) return <Navigate to="/404" replace />;
    if (!page) return <div className="pw-page pw-shell" data-testid="page-loading" />;

    const toc = tocOf(page.blocks);

    return (
        <div className="pw-page" data-testid={`pillar-${slug}`}>
            <div className="pw-shell">
                <nav className="pw-crumbs" aria-label="breadcrumb" data-testid="breadcrumb">
                    <Link to="/">{ui.breadcrumb_home}</Link>
                    <span aria-hidden="true">/</span>
                    <span>{page.h1}</span>
                </nav>
                <div className="pw-grid">
                    <article>
                        <Reveal y={18}>
                            <h1 className="pw-h1" data-testid="page-h1">{page.h1}</h1>
                        </Reveal>
                        {page.answer && (
                            <Reveal delay={0.1}>
                                <p className="pw-answer" data-testid="direct-answer">
                                    <span className="pw-label">{ui.hero_answer_label}</span>
                                    {page.answer}
                                </p>
                            </Reveal>
                        )}
                        <Blocks blocks={page.blocks} />
                        <Faq faq={page.faq} title={ui.faq_title} />
                    </article>
                    <Toc items={toc} />
                </div>
            </div>
        </div>
    );
}
