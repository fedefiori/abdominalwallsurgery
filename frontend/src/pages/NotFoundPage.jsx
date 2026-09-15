import { Link } from 'react-router-dom';
import { useSite } from '../lib/SiteContext';
import useSEO from '../hooks/useSEO';

export default function NotFoundPage() {
    const { site, ui } = useSite();
    useSEO({
        title: `404 — ${ui.notfound_title || 'Pagina non trovata'}`,
        description: ui.notfound_text,
        noindex: true,
        domain: site?.domain,
    });
    return (
        <div className="pw-page pw-shell pw-404" data-testid="not-found-page">
            <span className="pw-404-code" aria-hidden="true">404</span>
            <h1 className="pw-h1">{ui.notfound_title || 'Pagina non trovata'}</h1>
            <p style={{ color: 'var(--muted)', maxWidth: '48ch' }}>{ui.notfound_text}</p>
            <div style={{ marginTop: '2rem' }}>
                <Link className="pw-btn pw-btn-solid" to="/" data-testid="notfound-home-cta">
                    {ui.notfound_cta || 'Home'}
                </Link>
            </div>
        </div>
    );
}
