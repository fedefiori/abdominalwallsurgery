import { createContext, useContext, useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { useSite } from '../lib/SiteContext';

const LightboxCtx = createContext(() => {});

export function LightboxProvider({ children }) {
    const [current, setCurrent] = useState(null);
    const { ui } = useSite();

    useEffect(() => {
        if (!current) return undefined;
        const onKey = (e) => { if (e.key === 'Escape') setCurrent(null); };
        document.addEventListener('keydown', onKey);
        document.body.style.overflow = 'hidden';
        return () => {
            document.removeEventListener('keydown', onKey);
            document.body.style.overflow = '';
        };
    }, [current]);

    return (
        <LightboxCtx.Provider value={setCurrent}>
            {children}
            {current && (
                <div
                    className="pw-lightbox"
                    data-testid="lightbox"
                    role="dialog"
                    aria-modal="true"
                    aria-label={current.caption || current.alt}
                    onClick={() => setCurrent(null)}
                >
                    <button className="pw-lightbox-close" data-testid="lightbox-close" aria-label={ui?.zoom_close || 'Close'}>
                        <X size={18} />
                    </button>
                    <img src={current.src} alt={current.alt} />
                    {current.caption && <figcaption>{current.caption}</figcaption>}
                </div>
            )}
        </LightboxCtx.Provider>
    );
}

export function useLightbox() {
    return useContext(LightboxCtx);
}
