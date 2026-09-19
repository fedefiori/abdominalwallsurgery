import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

/** Fisarmonica FAQ: la risposta e' SEMPRE nel DOM (collaudo 19/06, bloccante 2).
    Si chiude solo via CSS (grid-template-rows 0fr/1fr), mai con rendering condizionale. */
export function FaqView({ faq, title }) {
    const [openIdx, setOpenIdx] = useState(-1);
    if (!faq?.length) return null;
    return (
        <section className="pw-faq" data-testid="faq-section">
            <h2>{title}</h2>
            {faq.map((f, i) => (
                <div className={`pw-faq-item${openIdx === i ? ' open' : ''}`} key={i}>
                    <button
                        className="pw-faq-q"
                        data-testid={`faq-question-${i}`}
                        aria-expanded={openIdx === i}
                        onClick={() => setOpenIdx(openIdx === i ? -1 : i)}
                    >
                        {f.q}
                        <ChevronDown size={16} style={{
                            flex: 'none', transition: 'transform .3s ease',
                            transform: openIdx === i ? 'rotate(180deg)' : 'none',
                        }} />
                    </button>
                    <div className="pw-faq-a">
                        <div className="pw-faq-a-inner">
                            <p data-testid={`faq-answer-${i}`} dangerouslySetInnerHTML={{ __html: f.a }} />
                        </div>
                    </div>
                </div>
            ))}
        </section>
    );
}
