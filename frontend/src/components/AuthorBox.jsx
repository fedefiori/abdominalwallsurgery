import { Link } from 'react-router-dom';
import { API } from '../lib/api';

function fmtData(iso) {
    if (!iso) return '';
    try {
        return new Date(iso).toLocaleDateString('it-IT', { day: 'numeric', month: 'long', year: 'numeric' });
    } catch { return ''; }
}

export function AuthorBox({ updated }) {
    const data = fmtData(updated);
    return (
        <aside className="pw-authorbox" data-testid="author-box" aria-label="Autore e revisione della pagina">
            <img
                src={`${API}/api/media/ritratto-dottor-fiori.webp`}
                alt="Ritratto del Dott. Federico Fiori"
                width="72" height="72" loading="lazy" decoding="async"
            />
            <div className="pw-authorbox-body">
                <strong>Dott. Federico Fiori</strong>
                <span>Medico Chirurgo — Specialista in Chirurgia Generale</span>
                <span className="pw-authorbox-role">Responsabile dell'Unità Operativa di Chirurgia della Parete Addominale — ASST Santi Paolo e Carlo, Milano</span>
                <span className="pw-authorbox-review">
                    Scritto e rivisto dal Dott. Federico Fiori.{data && <> Ultima revisione: <time dateTime={(updated || '').slice(0, 10)}>{data}</time>.</>}
                </span>
                <span className="pw-authorbox-links">
                    <a href="https://www.federicofiori.com/curriculum" target="_blank" rel="author noopener">Curriculum completo</a>
                    <span aria-hidden="true"> · </span>
                    <Link to="/contatti/">Dove riceve</Link>
                </span>
            </div>
        </aside>
    );
}
