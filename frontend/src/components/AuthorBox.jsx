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
        <aside className="pw-authorbox" data-testid="author-box" aria-label="Autore della pagina">
            <img
                src={`${API}/api/media/ritratto-dottor-fiori.webp`}
                alt="Ritratto del dott. Federico Fiori"
                width="72" height="72" loading="lazy" decoding="async"
            />
            <div className="pw-authorbox-body">
                <strong>Dott. Federico Fiori</strong>
                <span>Medico Chirurgo - Specialista in Chirurgia Generale</span>
                <span>Responsabile della Unità Operativa di Chirurgia della Parete Addominale - ASST Santi Paolo e Carlo, PO San Carlo Borromeo, Milano</span>
                <span className="pw-authorbox-review">Scrive e revisiona i contenuti di questo sito.</span>
                <span className="pw-authorbox-links">
                    <a href="https://www.federicofiori.com/curriculum" target="_blank" rel="noopener">Curriculum completo</a>
                    <span aria-hidden="true"> · </span>
                    <Link to="/contatti/">Dove riceve</Link>
                </span>
                {data && <small className="pw-authorbox-date">Pagina aggiornata il {data}</small>}
            </div>
        </aside>
    );
}
