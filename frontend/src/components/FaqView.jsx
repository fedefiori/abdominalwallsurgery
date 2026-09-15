import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

export function FaqView({ faq, title }) {
    const [openIdx, setOpenIdx] = useState(-1);
    if (!faq?.length) return null;
    return (
        <section className="pw-faq" data-testid="faq-section">
            <h2>{title}</h2>
            {faq.map((f, i) => (
                <div className="pw-faq-item" key={i}>
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
                    <AnimatePresence initial={false}>
                        {openIdx === i && (
                            <motion.div
                                className="pw-faq-a"
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.32, ease: 'easeOut' }}
                            >
                                <div data-testid={`faq-answer-${i}`}
                                    dangerouslySetInnerHTML={{ __html: f.a }} />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            ))}
        </section>
    );
}
