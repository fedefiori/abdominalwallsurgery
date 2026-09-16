import { API } from '../lib/api';
import { useLightbox } from './Lightbox';

export function anchorOf(text) {
    return (text || '').toLowerCase()
        .normalize('NFD').replace(/[̀-ͯ]/g, '')
        .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

function imgSrc(src) {
    if (!src) return src;
    if (src.startsWith('http')) return src; // figure dell'hub: URL assoluti, invariati
    return `${API}${src}`;
}

function Figure({ b, first }) {
    const open = useLightbox();
    const kind = b.kind === 'schema' ? 'schema' : 'photo';
    const src = imgSrc(b.src);
    return (
        <figure className={`pw-img-${kind}`} data-testid={`page-figure-${kind}`}>
            <img
                src={src}
                alt={b.alt || ''}
                width={b.width || 1200}
                height={b.height || 800}
                loading={first ? undefined : 'lazy'}
                fetchPriority={first ? 'high' : undefined}
                decoding="async"
                onClick={() => open({ src, alt: b.alt, caption: b.caption })}
                onKeyDown={(e) => { if (e.key === 'Enter') open({ src, alt: b.alt, caption: b.caption }); }}
                tabIndex={0}
                role="button"
                aria-label={`Ingrandisci: ${b.alt || ''}`}
            />
            {b.caption && <figcaption>{b.caption}</figcaption>}
        </figure>
    );
}

export function Blocks({ blocks }) {
    let imgIndex = 0;
    // raggruppa i blocchi in sezioni delimitate dagli h2: sfondi alternati
    const sections = [];
    let current = [];
    for (const b of blocks) {
        if (b.type === 'h2' && current.length) {
            sections.push(current);
            current = [];
        }
        current.push(b);
    }
    if (current.length) sections.push(current);

    const renderBlock = (b, i) => {
        switch (b.type) {
            case 'h2':
                return <h2 key={i} id={anchorOf(b.text)}>{b.text}</h2>;
            case 'h3':
                return <h3 key={i} id={anchorOf(b.text)}>{b.text}</h3>;
            case 'p':
                return <p key={i} dangerouslySetInnerHTML={{ __html: b.html }} />;
            case 'ul': {
                const List = b.ordered ? 'ol' : 'ul';
                return (
                    <List key={i}>
                        {b.items.map((it, j) => (
                            <li key={j} dangerouslySetInnerHTML={{ __html: it }} />
                        ))}
                    </List>
                );
            }
            case 'plainBox':
                return <div key={i} className="pw-plainbox" data-testid="plain-box" dangerouslySetInnerHTML={{ __html: `<p>${b.html}</p>` }} />;
            case 'proBox':
                return <div key={i} className="pw-probox" data-testid="pro-box" dangerouslySetInnerHTML={{ __html: `<p>${b.html}</p>` }} />;
            case 'note':
                return <div key={i} className="pw-note" data-testid="note-box" dangerouslySetInnerHTML={{ __html: `<p>${b.html}</p>` }} />;
            case 'keyPoints':
                return (
                    <ul key={i} className="pw-keypoints">
                        {b.items.map((it, j) => <li key={j} dangerouslySetInnerHTML={{ __html: it }} />)}
                    </ul>
                );
            case 'table':
                return <div key={i} className="pw-table" data-testid="content-table" dangerouslySetInnerHTML={{ __html: b.html }} />;
            default:
                return null;
        }
    };

    const out = [];
    sections.forEach((sec, s) => {
        const band = s === 0 && sec[0].type !== 'h2' ? 0 : ((s - 1) % 3) + 1;
        const children = [];
        for (let i = 0; i < sec.length; i += 1) {
            const b = sec[i];
            if (b.type === 'img') {
                const duo = [];
                while (i < sec.length && sec[i].type === 'img' && duo.length < 2) {
                    duo.push(sec[i]);
                    i += 1;
                }
                i -= 1;
                const items = duo.map((d) => {
                    imgIndex += 1;
                    return <Figure key={imgIndex} b={d} first={imgIndex === 1} />;
                });
                children.push(duo.length === 2
                    ? <div className="pw-img-duo" data-testid="figure-duo" key={`duo-${i}`}>{items}</div>
                    : <div key={`solo-${i}`}>{items}</div>);
            } else {
                children.push(renderBlock(b, i));
            }
        }
        out.push(
            <section key={s} className={`pw-sect pw-sect-${band}`} data-testid={`content-section-${s}`}>
                {children}
            </section>
        );
    });
    return <div className="pw-content" data-testid="page-blocks">{out}</div>;
}

export function Related({ items, title = 'Leggi anche' }) {
    if (!items?.length) return null;
    return (
        <nav className="pw-related" data-testid="related-block" aria-label={title}>
            <span className="pw-label">{title}</span>
            <ul>
                {items.map((r) => (
                    <li key={r.href}>
                        <a href={r.href} {...(r.href.startsWith('http') ? { target: '_blank', rel: 'noopener' } : {})}>
                            {r.label}<span aria-hidden="true">→</span>
                        </a>
                    </li>
                ))}
            </ul>
        </nav>
    );
}

export function tocOf(blocks) {
    return blocks
        .filter((b) => b.type === 'h2')
        .map((b) => ({ id: anchorOf(b.text), label: b.text }));
}
