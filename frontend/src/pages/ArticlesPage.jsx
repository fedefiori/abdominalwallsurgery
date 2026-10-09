import { useEffect, useState } from 'react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import { useSite } from '../lib/SiteContext';
import { api } from '../lib/api';
import useSEO from '../hooks/useSEO';
import { Reveal } from '../components/Reveal';

export default function ArticlesPage() {
    const { site, ui } = useSite();
    const en = site?.lang === 'en';
    const location = useLocation();
    const [data, setData] = useState(null);

    useEffect(() => {
        api.articles().then(setData).catch(() => setData({ items: [] }));
    }, []);

    useSEO({
        title: `${ui.articles_title} | ${ui.site_name}`,
        description: ui.articles_meta || ui.articles_sub,
        canonical: site ? `${site.domain}${site.articlesIndex}` : undefined,
        domain: site?.domain,
        siteName: ui?.site_name,
        lang: site?.lang,
        alternates: site?.articlesAlternates,
    });

    if (location.pathname !== (site?.articlesIndex || '/articoli')) {
        return <Navigate to={site?.articlesIndex || '/articoli'} replace />;
    }

    return (
        <div className="pw-page" data-testid="articles-index">
            <div className="pw-shell">
                <nav className="pw-crumbs" aria-label="breadcrumb" data-testid="breadcrumb">
                    <Link to="/">{ui.breadcrumb_home}</Link>
                    <span aria-hidden="true">/</span>
                    <span>{ui.breadcrumb_articles}</span>
                </nav>
                <Reveal y={18}>
                    <h1 className="pw-h1">{ui.articles_title}</h1>
                </Reveal>
                <Reveal delay={0.1}>
                    <p style={{ color: 'var(--muted)', maxWidth: '60ch' }}>{ui.articles_sub}</p>
                </Reveal>
                <div className="pw-article-list" data-testid="article-list">
                    {(data?.items || []).map((a, i) => (
                        <Reveal key={a.slug} delay={i * 0.06}>
                            <div>
                                <Link className="pw-article-card" to={`${site?.articlesIndex || '/articoli'}/${a.slug}`} data-testid={`article-card-${a.slug}`}>
                                    {a.coverUrl
                                        ? <img src={a.coverUrl} alt={a.title} width="1200" height="675" loading="lazy" decoding="async" />
                                        : <span />}
                                    <span>
                                        {a.categoryLabel && <span className="pw-label">{a.categoryLabel}</span>}
                                        <h2>{a.title}</h2>
                                        <p>{a.summary || a.excerpt}</p>
                                    </span>
                                </Link>
                                {a.siteLink && (
                                    <p className="pw-card-sitelink" data-testid={`article-sitelink-${a.slug}`}>
                                        {en ? 'Related page on this site:' : 'Pagina del sito collegata:'} <Link to={a.siteLink[1]}>{a.siteLink[0]}</Link>
                                    </p>
                                )}
                            </div>
                        </Reveal>
                    ))}
                    {data && data.items.length === 0 && (
                        <p style={{ color: 'var(--muted)' }} data-testid="articles-empty">—</p>
                    )}
                </div>
                <div className="pw-content" style={{ marginTop: '3.5rem' }}>
                    {en ? <IndexFaqEn /> : <IndexFaqIt />}
                </div>
            </div>
        </div>
    );
}

function IndexFaqEn() {
    return (
        <>
            <section className="pw-sect pw-sect-1">
                <h2>What will I find in these articles?</h2>
                <p>
                    The articles in this index are the educational texts written and approved in the
                    federicofiori.com editorial area and served here for this site’s readers: they explain in
                    plain words topics that the clinical pages cover in technical terms, from the TESAR technique
                    to preventing the recurrence of umbilical hernia.
                </p>
            </section>
            <section className="pw-sect pw-sect-2">
                <h2>Where are the other in-depth articles published?</h2>
                <p>
                    The full editorial plan lives on the hub <a href="https://www.federicofiori.com">federicofiori.com</a>:
                    there you will find the acronym glossary, the TESAR technique, the MILA technique and the results
                    gallery. The reference clinical pages stay on this site: to find your way, start from
                    the <Link to="/abdominal-wall-defects-and-classification/">classification of wall defects</Link> and
                    the <Link to="/surgical-treatment/">surgical treatment</Link>.
                </p>
            </section>
        </>
    );
}

function IndexFaqIt() {
    return (
        <>
                    <section className="pw-sect pw-sect-1">
                        <h2>Che cosa trovo in questi articoli?</h2>
                        <p>
                            Gli articoli di questo indice sono i testi divulgativi scritti e approvati nell’area
                            editoriale di federicofiori.com e serviti qui per i lettori di questo sito: spiegano in
                            parole semplici argomenti che le pagine cliniche trattano in modo tecnico, dalla tecnica
                            TESAR alla prevenzione delle recidive dell’ernia ombelicale.
                        </p>
                    </section>
                    <section className="pw-sect pw-sect-2">
                        <h2>Dove sono pubblicati gli altri approfondimenti?</h2>
                        <p>
                            Il piano editoriale completo vive sull’hub <a href="https://www.federicofiori.com">federicofiori.com</a>:
                            lì si trovano il glossario degli acronimi, la tecnica TESAR, la tecnica MILA e la galleria
                            dei risultati. Le pagine cliniche di riferimento restano su questo sito: per orientarsi si
                            parte dalla <Link to="/difetti-della-parete-addominale-e-classificazione/">classificazione dei difetti di parete</Link> e
                            dalla <Link to="/la-terapia-chirurgica/">terapia chirurgica</Link>.
                        </p>
                    </section>
        </>
    );
}
