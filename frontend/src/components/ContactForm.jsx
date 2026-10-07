import { useState } from 'react';
import { API } from '../lib/api';
import { useSite } from '../lib/SiteContext';
import { Phone } from 'lucide-react';

// Le due porte dei contatti: identiche su tutti i siti della rete (hub 26/09).
// I valori 'appuntamento'/'dottore' NON si traducono: il backend li usa per
// instradare l'email. Cambiano solo le etichette visibili, per lingua.
const REASONS = {
    it: [
        { value: 'appuntamento', label: 'Informazioni, chiarimenti o appuntamento', note: 'Risponde Emma Gadda, di norma entro due giorni lavorativi.' },
        { value: 'dottore', label: 'Scrivi al Dott. Fiori', note: 'Scrivi direttamente al Dott. F. Fiori.' },
    ],
    en: [
        { value: 'appuntamento', label: 'Information, questions or an appointment', note: 'Emma Gadda answers, usually within two working days.' },
        { value: 'dottore', label: 'Write to Dr. Fiori', note: 'Write directly to Dr. F. Fiori.' },
    ],
};

export function ContactForm() {
    const { site } = useSite();
    const en = site?.lang === 'en';
    const reasons = en ? REASONS.en : REASONS.it;
    const [form, setForm] = useState({ name: '', email: '', message: '', reason: 'appuntamento', company: '' });
    const [state, setState] = useState('idle');
    const active = reasons.find((r) => r.value === form.reason) || reasons[0];
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
            <h2>{en ? 'How to reach us' : 'Come scriverci'}</h2>

            <p className="pw-contact-phone" data-testid="contact-phone-cta">
                <Phone size={18} aria-hidden="true" />
                <span>{en ? 'Information and appointments, Emma Gadda answers:' : 'Informazioni e appuntamenti, risponde Emma Gadda:'}{' '}
                    <a href="tel:+390276021568"><strong>+39 02 7602 1568</strong></a>
                </span>
            </p>

            {state === 'done' ? (
                <div className="pw-note" data-testid="contact-success" role="status">
                    <span className="pw-label">{en ? 'REQUEST SENT' : 'RICHIESTA INVIATA'}</span>
                    <p>{en ? `Thank you ${form.name.split(' ')[0]}: your request has been recorded.` : `Grazie ${form.name.split(' ')[0]}: la tua richiesta è stata registrata.`}</p>
                    <p>{active.note}</p>
                </div>
            ) : (
                <form onSubmit={submit} data-testid="contact-form">
                    <fieldset className="pw-reasons">
                        <legend>{en ? 'What do you need?' : 'Di cosa hai bisogno?'}</legend>
                        {reasons.map((r) => (
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
                        <label>{en ? 'Full name' : 'Nome e cognome'}
                            <input type="text" value={form.name} onChange={set('name')} required
                                autoComplete="name" data-testid="contact-name" />
                        </label>
                        <label>{en ? 'Your email' : 'La tua email'}
                            <input type="email" value={form.email} onChange={set('email')} required
                                autoComplete="email" data-testid="contact-email" />
                        </label>
                    </div>
                    <label>{en ? 'Message' : 'Messaggio'}
                        <textarea value={form.message} onChange={set('message')} required rows={5}
                            data-testid="contact-message" />
                    </label>
                    <input type="text" name="company" value={form.company} onChange={set('company')} tabIndex={-1}
                        autoComplete="off" aria-hidden="true" className="pw-hp" data-testid="contact-honeypot" />

                    {state === 'error' && (
                        <p className="pw-form-error" data-testid="contact-error">
                            {en ? "The message could not be sent: write directly to " : "L'invio non è riuscito: scrivi direttamente a "}
                            <a href="mailto:fedefiori@federicofiori.com">fedefiori@federicofiori.com</a>.
                        </p>
                    )}
                    <button type="submit" className="pw-btn pw-btn--primary" disabled={state === 'sending'}
                        data-testid="contact-submit">
                        {state === 'sending' ? (en ? 'Sending…' : 'Invio in corso…') : (en ? 'Send the request' : 'Invia la richiesta')}
                    </button>
                </form>
            )}

            <p className="pw-direct-line" data-testid="direct-email-line">
                {en ? 'To write directly, including attachments (reports, scans, images): Write to Dr. Fiori — ' : 'Per scrivere direttamente, anche con allegati (referti, esami, immagini): Scrivi al Dott. Fiori — '}
                <a href="mailto:fedefiori@federicofiori.com">fedefiori@federicofiori.com</a>
            </p>
        </section>
    );
}
