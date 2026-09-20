import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Lenis from 'lenis';
import { SiteProvider } from './lib/SiteContext';
import { LightboxProvider } from './components/Lightbox';
import { trackPageview, initStatsClicks } from './lib/stats';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import PillarPage, { KNOWN_SLUGS } from './pages/PillarPage';
import ArticlesPage from './pages/ArticlesPage';
import ArticlePage from './pages/ArticlePage';
import NotFoundPage from './pages/NotFoundPage';

function useLenis() {
    useEffect(() => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
        let raf;
        const loop = (t) => { lenis.raf(t); raf = requestAnimationFrame(loop); };
        raf = requestAnimationFrame(loop);
        return () => { cancelAnimationFrame(raf); lenis.destroy(); };
    }, []);
}

function ScrollTop() {
    const { pathname } = useLocation();
    useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
    return null;
}

function StatsTracker() {
    const { pathname } = useLocation();
    // il titolo della scheda arriva dopo il fetch dei contenuti
    useEffect(() => {
        const t = setTimeout(() => trackPageview(pathname), 800);
        return () => clearTimeout(t);
    }, [pathname]);
    useEffect(() => { initStatsClicks(); }, []);
    return null;
}

function SlugRedirect() {
    const { pathname } = useLocation();
    const slug = pathname.replace(/^\//, '');
    if (KNOWN_SLUGS.includes(slug)) return <Navigate to={`/${slug}/`} replace />;
    return <NotFoundPage />;
}

export default function App() {
    useLenis();
    return (
        <SiteProvider>
            <LightboxProvider>
            <BrowserRouter>
                <ScrollTop />
                <StatsTracker />
                <Layout>
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/articoli" element={<ArticlesPage />} />
                        <Route path="/articoli/:slug" element={<ArticlePage />} />
                        <Route path="/404" element={<NotFoundPage />} />
                        <Route path="/:slug/" element={<PillarPage />} />
                        <Route path="/:slug" element={<SlugRedirect />} />
                        <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                </Layout>
            </BrowserRouter>
            </LightboxProvider>
        </SiteProvider>
    );
}
