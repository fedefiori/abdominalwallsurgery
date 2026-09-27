import { useState } from 'react';
import { API } from '../lib/api';
import { Phone } from 'lucide-react';

// Le due porte dei contatti: identiche su tutti i siti della rete (hub 26/09).
const REASONS = [
    {
        value: 'appuntamento',
        label: 'Informazioni, chiarimenti o appuntamento',
        note: 'Risponde Emma Gadda, di norma entro due giorni lavorativi.',
    },
    {
        value: 'dottore',
        label: 'Scrivi al Dott. Fiori',
        note: 'Scrivi direttamente al Dott. F. Fiori.',
    },
];

export function ContactForm() {
    const [form, setForm] = useState({ name: '', email: '', message: '', reason: 'appuntamento', company: '' });
    const [state, setState] = useState('idle');
    const active = REASONS.find((r) => r.value === form.reason) || REASONS[0];
    const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

    async function submit(e) {
        e.preventDefault();
        setState('sending');
        try {
            const r = await fetch(`${API}/api/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form),
            });
            if (!r.ok) throw new Error('bad status');
            setState('done');
        } catch {
            setState('error');
        }
    }

    return (
        <section className="pw-contact" data-testid="contact-section">
            <h2>Come scriverci</h2>

            {/* Il telefono resta primo, sopra il modulo */}
            <p className="pw-contact-phone" data-testid="contact-phone-cta">
                <Phone size={18} aria-hidden="true" />
                <span>Informazioni e appuntamenti, risponde Emma Gadda:{' '}
                    <a href="tel:+390276021568"><strong>+39 02 76021568</strong></a>
                </span>
            </p>

            {state === 'done' ? (
                <div className="pw-note" data-testid="contact-success" role="status">
                    <span className="pw-label">RICHIESTA INVIATA</span>
                    <p>Grazie {form.name.split(' ')[0]}: la tua richiesta è stata registrata.</p>
                    <p>{active.note}</p>
                </div>
            ) : (
                <form onSubmit={submit} data-testid="contact-form">
                    <fieldset className="pw-reasons">
                        <legend>Di cosa hai bisogno?</legend>
                        {REASONS.map((r) => (
                            <label key={r.value} className={`pw-reason${form.reason === r.value ? ' active' : ''}`}
                                data-testid={`reason-${r.value}`}>
                                <input type="radio" name="reason" value={r.value}
                                    checked={form.reason === r.value}
                                    onChange={() => setForm({ ...form, reason: r.value })} />
                                <span>{r.label}</span>
                            </label>
                        ))}
                        <p className="pw-reason-note" data-testid="reason-note">{active.note}</p>
                    </fieldset>

                    <div className="pw-form-row">
                        <label>Nome e cognome
                            <input type="text" value={form.name} onChange={set('name')} required
                                autoComplete="name" data-testid="contact-name" />
                        </label>
                        <label>La tua email
                            <input type="email" value={form.email} onChange={set('email')} required
                                autoComplete="email" data-testid="contact-email" />
                        </label>
                    </div>
                    <label>Messaggio
                        <textarea value={form.message} onChange={set('message')} required rows={5}
                            data-testid="contact-message" />
                    </label>
                    {/* honeypot: invisibile agli utenti, lo compilano solo i bot */}
                    <input type="text" value={form.company} onChange={set('company')} tabIndex={-1}
                        autoComplete="off" aria-hidden="true" className="pw-hp" data-testid="contact-honeypot" />

                    {state === 'error' && (
                        <p className="pw-form-error" data-testid="contact-error">
                            L'invio non è riuscito: scrivi direttamente a{' '}
                            <a href="mailto:fedefiori@federicofiori.com">fedefiori@federicofiori.com</a>.
                        </p>
                    )}
                    <button type="submit" className="pw-btn pw-btn--primary" disabled={state === 'sending'}
                        data-testid="contact-submit">
                        {state === 'sending' ? 'Invio in corso…' : 'Invia la richiesta'}
                    </button>
                </form>
            )}

            {/* Indirizzo diretto in chiaro, visibile anche dopo l'invio */}
            <p className="pw-direct-line" data-testid="direct-email-line">
                Per scrivere direttamente, anche con allegati (referti, esami, immagini):{' '}
                Scrivi al Dott. Fiori —{' '}
                <a href="mailto:fedefiori@federicofiori.com">fedefiori@federicofiori.com</a>
            </p>
        </section>
    );
}
