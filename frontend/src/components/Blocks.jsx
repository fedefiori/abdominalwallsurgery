import { API } from '../lib/api';

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

export function Blocks({ blocks }) {
    let imgIndex = 0;
    return (
        <div className="pw-content" data-testid="page-blocks">
            {blocks.map((b, i) => {
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
                    case 'img': {
                        imgIndex += 1;
                        const first = imgIndex === 1;
                        return (
                            <figure key={i} data-testid="page-figure">
                                <img
                                    src={imgSrc(b.src)}
                                    alt={b.alt || ''}
                                    width={b.width || 1200}
                                    height={b.height || 800}
                                    loading={first ? undefined : 'lazy'}
                                    fetchPriority={first ? 'high' : undefined}
                                    decoding="async"
                                />
                                {b.caption && <figcaption>{b.caption}</figcaption>}
                            </figure>
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
            })}
        </div>
    );
}

export function tocOf(blocks) {
    return blocks
        .filter((b) => b.type === 'h2')
        .map((b) => ({ id: anchorOf(b.text), label: b.text }));
}
