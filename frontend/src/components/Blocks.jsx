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
    const out = [];
    for (let i = 0; i < blocks.length; i += 1) {
        const b = blocks[i];
        if (b.type === 'img') {
            // coppie di immagini consecutive -> due colonne
            const duo = [];
            while (i < blocks.length && blocks[i].type === 'img' && duo.length < 2) {
                duo.push(blocks[i]);
                i += 1;
            }
            i -= 1;
            const items = duo.map((d) => {
                imgIndex += 1;
                return <Figure key={imgIndex} b={d} first={imgIndex === 1} />;
            });
            out.push(duo.length === 2
                ? <div className="pw-img-duo" data-testid="figure-duo" key={`duo-${i}`}>{items}</div>
                : <div key={`solo-${i}`}>{items}</div>);
            continue;
        }
        switch (b.type) {
            case 'h2':
                out.push(<h2 key={i} id={anchorOf(b.text)}>{b.text}</h2>);
                break;
            case 'h3':
                out.push(<h3 key={i} id={anchorOf(b.text)}>{b.text}</h3>);
                break;
            case 'p':
                out.push(<p key={i} dangerouslySetInnerHTML={{ __html: b.html }} />);
                break;
            case 'ul': {
                const List = b.ordered ? 'ol' : 'ul';
                out.push(
                    <List key={i}>
                        {b.items.map((it, j) => (
                            <li key={j} dangerouslySetInnerHTML={{ __html: it }} />
                        ))}
                    </List>);
                break;
            }
            case 'plainBox':
                out.push(<div key={i} className="pw-plainbox" data-testid="plain-box" dangerouslySetInnerHTML={{ __html: `<p>${b.html}</p>` }} />);
                break;
            case 'proBox':
                out.push(<div key={i} className="pw-probox" data-testid="pro-box" dangerouslySetInnerHTML={{ __html: `<p>${b.html}</p>` }} />);
                break;
            case 'note':
                out.push(<div key={i} className="pw-note" data-testid="note-box" dangerouslySetInnerHTML={{ __html: `<p>${b.html}</p>` }} />);
                break;
            case 'keyPoints':
                out.push(
                    <ul key={i} className="pw-keypoints">
                        {b.items.map((it, j) => <li key={j} dangerouslySetInnerHTML={{ __html: it }} />)}
                    </ul>);
                break;
            case 'table':
                out.push(<div key={i} className="pw-table" data-testid="content-table" dangerouslySetInnerHTML={{ __html: b.html }} />);
                break;
            default:
                break;
        }
    }
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
