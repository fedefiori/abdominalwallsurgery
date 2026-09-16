import { useEffect, useState } from 'react';
import { Link, useParams, useLocation, Navigate } from 'react-router-dom';
import { useSite } from '../lib/SiteContext';
import { api } from '../lib/api';
import useSEO from '../hooks/useSEO';
import { Blocks, tocOf } from '../components/Blocks';
import { Reveal } from '../components/Reveal';
import { FaqView } from '../components/FaqView';

function fmt(iso, lang) {
    if (!iso) return '';
    try {
        return new Date(iso).toLocaleDateString(lang === 'en' ? 'en-US' : 'it-IT',
            { day: 'numeric', month: 'long', year: 'numeric' });
    } catch { return ''; }
}

export default function ArticlePage() {
    const { slug } = useParams();
    const location = useLocation();
    const { site, ui } = useSite();
    const [post, setPost] = useState(null);
    const [missing, setMissing] = useState(false);

    useEffect(() => {
        setPost(null); setMissing(false);
        if (!site) return;
        api.article(site.lang, slug)
            .then((d) => setPost(d.post))
            .catch(() => setMissing(true));
    }, [slug, site]);

    useSEO({
        title: post ? (post.metaTitle || post.title) : undefined,
        description: post ? (post.metaDescription || post.excerpt) : undefined,
        canonical: post?.canonical,
        domain: site?.domain,
    });

    if (!site) return null;
    if (location.pathname.endsWith('/')) {
        return <Navigate to={location.pathname.slice(0, -1)} replace />;
    }
    if (missing) return <Navigate to="/404" replace />;
    if (!post) return <div className="pw-page pw-shell" data-testid="article-loading" />;

    const toc = tocOf(post.sections || []);

    return (
        <div className="pw-page" data-testid={`article-${slug}`}>
            <div className="pw-shell">
                <div className="pw-pagehead" data-testid="page-head">
                    <nav className="pw-crumbs" aria-label="breadcrumb" data-testid="breadcrumb">
                        <Link to="/">{ui.breadcrumb_home}</Link>
                        <span aria-hidden="true">/</span>
                        <Link to={site.articlesIndex}>{ui.breadcrumb_articles}</Link>
                        <span aria-hidden="true">/</span>
                        <span>{post.title}</span>
                    </nav>
                    <Reveal y={18}>
                        {post.categoryLabel && <span className="pw-label" data-testid="article-category">{post.categoryLabel}</span>}
                        <h1 className="pw-h1" data-testid="article-h1">{post.title}</h1>
                        <p className="pw-label" style={{ marginBottom: 0, marginTop: '1rem' }}>
                            {ui.published} {fmt(post.publishedAt, site.lang)}
                            {post.updatedAt && post.updatedAt !== post.publishedAt &&
                                ` — ${ui.updated} ${fmt(post.updatedAt, site.lang)}`}
                        </p>
                    </Reveal>
                </div>
                <div className="pw-grid">
                    <article>
                        {post.directAnswer && (
                            <Reveal delay={0.08}>
                                <p className="pw-answer" data-testid="direct-answer">
                                    <span className="pw-label">{ui.hero_answer_label}</span>
                                    {post.directAnswer}
                                </p>
                            </Reveal>
                        )}
                        {post.coverUrl && (
                            <figure className="pw-article-cover" data-testid="article-cover">
                                <img src={post.coverUrl} alt={post.title} width="1200" height="675"
                                    fetchPriority="high" decoding="async" />
                            </figure>
                        )}
                        <Blocks blocks={post.sections || []} />
                        {post.tags?.length > 0 && (
                            <div className="pw-tags" data-testid="article-tags">
                                <span className="pw-label" style={{ alignSelf: 'center' }}>{ui.tags_label}</span>
                                {post.tags.map((t) => <span className="pw-tag" key={t}>{t}</span>)}
                            </div>
                        )}
                        <FaqView faq={post.faq} title={ui.faq_title} />
                    </article>
                    {toc.length >= 3 && (
                        <nav className="pw-toc" aria-label="Indice dell'articolo" data-testid="page-toc">
                            {toc.map((t) => <a key={t.id} href={`#${t.id}`}>{t.label}</a>)}
                        </nav>
                    )}
                </div>
            </div>
        </div>
    );
}
