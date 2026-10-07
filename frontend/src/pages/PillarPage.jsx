import { useEffect, useState } from 'react';
import { Link, useParams, Navigate } from 'react-router-dom';
import { useSite } from '../lib/SiteContext';
import { api } from '../lib/api';
import useSEO from '../hooks/useSEO';
import { Blocks, tocOf, Related } from '../components/Blocks';
import { AuthorBox } from '../components/AuthorBox';
import { ContactForm } from '../components/ContactForm';
import { FaqView } from '../components/FaqView';
import { Reveal } from '../components/Reveal';
import { ExternalLink } from 'lucide-react';

export const KNOWN_SLUGS = [
    'anatomia-della-parete-addominale-e-abdominal-core',
    'la-terapia-chirurgica', 'radiologia',
    'le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi',
    'le-complicanze-chirurgiche-la-vac-therapy', 'sintomi-e-complicanze',
    'difetti-della-parete-addominale-e-classificazione',
    'preabilitazione-dei-pazienti-all-intervento-chirurgico', 'contatti', 'video',
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

function FontiView({ fonti }) {
    const { site } = useSite();
    if (!fonti?.length) return null;
    return (
        <section className="pw-fonti" data-testid="fonti-section" aria-label={site?.lang === 'en' ? 'Sources' : 'Fonti'}>
            <h2>{site?.lang === 'en' ? 'Sources' : 'Fonti'}</h2>
            <ul>
                {fonti.map((f, i) => (
                    <li key={i}>
                        <a href={f.href} target="_blank" rel="noopener">
                            {f.label} <ExternalLink size={13} style={{ display: 'inline', verticalAlign: '-2px' }} />
                        </a>
                    </li>
                ))}
            </ul>
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
        siteName: ui?.site_name,
        lang: site?.lang,
        image: page?.blocks?.find((b) => b.type === 'img')?.src
            ? `${site?.domain}${page.blocks.find((b) => b.type === 'img').src}` : undefined,
        imageAlt: page?.h1,
    });

    if (missing) return <Navigate to="/404" replace />;
    if (!page) return <div className="pw-page pw-shell" data-testid="page-loading" />;

    const toc = tocOf(page.blocks);

    return (
        <div className="pw-page" data-testid={`pillar-${slug}`}>
            <div className="pw-shell">
                <div className="pw-pagehead" data-testid="page-head">
                    <nav className="pw-crumbs" aria-label="breadcrumb" data-testid="breadcrumb">
                        <Link to="/">{ui.breadcrumb_home}</Link>
                        <span aria-hidden="true">/</span>
                        <span>{page.h1}</span>
                    </nav>
                    <Reveal y={18}>
                        <h1 className="pw-h1" data-testid="page-h1">{page.h1}</h1>
                    </Reveal>
                </div>
                <div className="pw-grid">
                    <article>
                        {page.answer && (
                            <Reveal delay={0.1}>
                                <p className="pw-answer" data-testid="direct-answer">
                                    <span className="pw-label">{ui.hero_answer_label}</span>
                                    {page.answer}
                                </p>
                            </Reveal>
                        )}
                        <Blocks blocks={page.blocks} decorate={!['legal', 'contact', 'video'].includes(page.kind)} />
                        {page.kind === 'contact' && <ContactForm />}
                        <FaqView faq={page.faq} title={ui.faq_title} />
                        {!['legal', 'contact', 'home', 'video'].includes(page.kind) && (
                            <AuthorBox updated={page.modified} />
                        )}
                        <FontiView fonti={page.fonti} />
                        <Related items={page.related} title={site?.lang === 'en' ? 'See also' : 'Leggi anche'} />
                    </article>
                    <Toc items={toc} />
                </div>
            </div>
        </div>
    );
}
