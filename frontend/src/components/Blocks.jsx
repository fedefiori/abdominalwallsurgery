import { API } from '../lib/api';
import { useLightbox } from './Lightbox';
import { Phone, Mail, MapPin, Globe } from 'lucide-react';

const CONTACT_ICONS = { phone: Phone, mail: Mail, 'map-pin': MapPin, globe: Globe };

/** Riga di due grandi CTA (contatti) e lista contatti con icone lucide. */
function CtaRow({ b }) {
    return (
        <div className="pw-ctarow" data-testid="contact-ctas">
            {b.items.map((it, i) => {
                const Icon = CONTACT_ICONS[it.icon] || Phone;
                return (
                    <a key={i} className={`pw-cta${i === 0 ? ' solid' : ''}`} href={it.href}
                        data-testid={`contact-cta-${it.icon}`}>
                        <Icon size={20} strokeWidth={1.8} aria-hidden="true" />
                        <span>{it.label}</span>
                    </a>
                );
            })}
        </div>
    );
}

function ContactList({ b }) {
    return (
        <div className="pw-contactlist" data-testid="contact-list">
            {b.items.map((it, i) => {
                const Icon = CONTACT_ICONS[it.icon] || Globe;
                const ext = it.href?.startsWith('http');
                return (
                    <div className="pw-contactrow" key={i}>
                        <span className="pw-contactrow-icon"><Icon size={18} strokeWidth={1.8} aria-hidden="true" /></span>
                        <span className="pw-contactrow-label">{it.label}</span>
                        <span className="pw-contactrow-value">
                            {it.href
                                ? <a href={it.href} {...(ext ? { target: '_blank', rel: 'noopener' } : {})}>{it.value}</a>
                                : it.value}
                            {it.hrefLabel && <> — <a href={it.href} target="_blank" rel="noopener">{it.hrefLabel}</a></>}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}

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

function Figure({ b, first, side }) {
    const open = useLightbox();
    const kind = b.kind === 'schema' ? 'schema' : 'photo';
    const src = imgSrc(b.src);
    return (
        <figure className={`pw-img-${kind}${side ? ` pw-fig-side-${side}` : ''}`} data-testid={`page-figure-${kind}`}>
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

export function Blocks({ blocks, wideFigures = false, decorate = true }) {
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

    // Illustrazioni (schemi) gia' previste dalla pagina: riusate come fondo
    // sfumato delle sezioni prive di figure — attinenti per costruzione.
    const artPool = decorate
        ? [...new Set(blocks.filter((b) => b.type === 'img' && b.kind === 'schema').map((b) => b.src))]
        : [];

    const textLenOf = (sec) => sec.reduce((n, b) => {
        const raw = b.text || b.html
            || (b.items || []).map((it) => (typeof it === 'string' ? it : '')).join(' ');
        return n + String(raw).replace(/<[^>]+>/g, ' ').length;
    }, 0);

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
            case 'ctaRow':
                return <CtaRow key={i} b={b} />;
            case 'contactList':
                return <ContactList key={i} b={b} />;
            default:
                return null;
        }
    };

    const out = [];
    sections.forEach((sec, s) => {
        const band = s === 0 && sec[0].type !== 'h2' ? 0 : ((s - 1) % 3) + 1;
        const hasImg = sec.some((b) => b.type === 'img');
        const wide = wideFigures && hasImg;
        // figure a lato del testo: la seconda SOLO se c'e' abbastanza testo,
        // altrimenti la colonna fra le due si strozza in uno spillo di parole
        const sideIdx = [];
        const maxSide = textLenOf(sec) > 1100 ? 2 : 1;
        for (let i = 0; i < sec.length && sideIdx.length < maxSide; i += 1) {
            const b = sec[i];
            if (b.type === 'img' && (b.kind === 'schema' || b.kind === 'photo')) sideIdx.push(i);
        }
        const children = [];
        // la prima figura apre la sezione: parte dall'alto e il testo la
        // avvolge — niente fascia vuota accanto all'immagine
        const headIdx = sideIdx.length ? sideIdx[0] : -1;
        if (headIdx >= 0) {
            imgIndex += 1;
            children.push(<Figure key={`side-${headIdx}`} b={sec[headIdx]} first={imgIndex === 1}
                side={s % 2 === 0 ? 'r' : 'l'} />);
        }
        // poi gli altri blocchi, nell'ordine originale del testo; l'eventuale
        // seconda figura fluttua nella sua posizione naturale lungo il testo
        for (let i = 0; i < sec.length; i += 1) {
            const b = sec[i];
            if (b.type === 'img') {
                if (i === headIdx) continue;
                const k = sideIdx.indexOf(i);
                if (k > 0) {
                    imgIndex += 1;
                    children.push(<Figure key={`side-${i}`} b={b} first={false}
                        side={(s + k) % 2 === 0 ? 'r' : 'l'} />);
                    continue;
                }
                const duo = [];
                while (i < sec.length && sec[i].type === 'img' && !sideIdx.includes(i) && duo.length < 2) {
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
                    : <div className="pw-img-solo" key={`solo-${i}`}>{items}</div>);
            } else {
                children.push(renderBlock(b, i));
            }
        }
        // sezione senza figure: fondo sfumato con un'illustrazione della
        // pagina; se la pagina non ne ha, cornice tecnica con angoli
        let decoClass = '';
        let decoStyle;
        if (decorate && !hasImg && !wide) {
            if (artPool.length) {
                const left = band === 2; // lato opposto al filetto colorato
                decoClass = ` pw-sect--bg${left ? ' pw-sect--bg-l' : ''}`;
                decoStyle = { '--bg-art': `url(${imgSrc(artPool[s % artPool.length])})` };
            } else {
                decoClass = ' pw-sect--framed';
            }
        }
        out.push(
            <section key={s} className={`pw-sect pw-sect-${band}${wide ? ' pw-sect--wide' : ''}${decoClass}`}
                style={decoStyle} data-testid={`content-section-${s}`}>
                {children}
            </section>
        );
    });
    return <div className="pw-content" data-testid="page-blocks">{out}</div>;
}

export function Related({ items, title = 'Leggi anche' }) {
    if (!items?.length) return null;
    const norm = items.map((r) => (Array.isArray(r) ? { label: r[0], href: r[1] } : r));
    return (
        <nav className="pw-related" data-testid="related-block" aria-label={title}>
            <span className="pw-label">{title}</span>
            <ul>
                {norm.map((r) => (
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
