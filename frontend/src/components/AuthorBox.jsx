import { Link } from 'react-router-dom';
import { API } from '../lib/api';
import { useSite } from '../lib/SiteContext';

function fmtData(iso, lang) {
    if (!iso) return '';
    try {
        return new Date(iso).toLocaleDateString(lang === 'en' ? 'en-US' : 'it-IT', { day: 'numeric', month: 'long', year: 'numeric' });
    } catch { return ''; }
}

export function AuthorBox({ updated }) {
    const { site } = useSite();
    const en = site?.lang === 'en';
    const data = fmtData(updated, site?.lang);
    return (
        <aside className="pw-authorbox" data-testid="author-box" aria-label={en ? 'Page author and review' : 'Autore e revisione della pagina'}>
            <img
                src={`${API}/api/media/ritratto-dottor-fiori.webp`}
                alt={en ? 'Portrait of Dr. Federico Fiori' : 'Ritratto del Dott. Federico Fiori'}
                width="72" height="72" loading="lazy" decoding="async"
            />
            <div className="pw-authorbox-body">
                <strong>{en ? 'Dr. Federico Fiori' : 'Dott. Federico Fiori'}</strong>
                <span>{en ? 'General surgeon' : 'Medico Chirurgo — Specialista in Chirurgia Generale'}</span>
                <span className="pw-authorbox-role">{en
                    ? 'Head of the Abdominal Wall Surgery Unit — ASST Santi Paolo e Carlo, Milan'
                    : "Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, Milano"}</span>
                <span className="pw-authorbox-review">
                    {en ? 'Written and reviewed by Dr. Federico Fiori.' : 'Scritto e rivisto dal Dott. Federico Fiori.'}
                    {data && <> {en ? 'Last reviewed:' : 'Ultima revisione:'} <time dateTime={(updated || '').slice(0, 10)}>{data}</time>.</>}
                </span>
                <span className="pw-authorbox-links">
                    <a href={en ? 'https://www.federicofiori.com/en/curriculum' : 'https://www.federicofiori.com/curriculum'} target="_blank" rel="author noopener">{en ? 'Full curriculum' : 'Curriculum completo'}</a>
                    {!en && <>
                        <span aria-hidden="true"> · </span>
                        <Link to="/contatti/">Dove riceve</Link>
                    </>}
                </span>
            </div>
        </aside>
    );
}
