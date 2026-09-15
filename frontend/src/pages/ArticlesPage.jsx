import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSite } from '../lib/SiteContext';
import { api } from '../lib/api';
import useSEO from '../hooks/useSEO';
import { Reveal } from '../components/Reveal';

export default function ArticlesPage() {
    const { site, ui } = useSite();
    const [data, setData] = useState(null);

    useEffect(() => {
        api.articles().then(setData).catch(() => setData({ items: [] }));
    }, []);

    useSEO({
        title: `${ui.articles_title} | ${ui.site_name}`,
        description: ui.articles_sub,
        canonical: site ? `${site.domain}${site.articlesIndex}` : undefined,
        domain: site?.domain,
    });

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
                            <Link className="pw-article-card" to={`${site.articlesIndex}/${a.slug}`} data-testid={`article-card-${a.slug}`}>
                                {a.coverUrl
                                    ? <img src={a.coverUrl} alt={a.title} width="1200" height="675" loading="lazy" decoding="async" />
                                    : <span />}
                                <span>
                                    {a.categoryLabel && <span className="pw-label">{a.categoryLabel}</span>}
                                    <h2>{a.title}</h2>
                                    <p>{a.excerpt}</p>
                                </span>
                            </Link>
                        </Reveal>
                    ))}
                    {data && data.items.length === 0 && (
                        <p style={{ color: 'var(--muted)' }} data-testid="articles-empty">—</p>
                    )}
                </div>
            </div>
        </div>
    );
}
