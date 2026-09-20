const API = process.env.REACT_APP_BACKEND_URL;

async function get(path) {
    const r = await fetch(`${API}/api${path}`);
    if (!r.ok) {
        const err = new Error(`API ${path} -> ${r.status}`);
        err.status = r.status;
        throw err;
    }
    return r.json();
}

export const api = {
    site: () => get('/site'),
    page: (slug) => get(`/pages/${slug}`),
    articles: () => get('/blog/articles'),
    article: (lang, slug) => get(`/blog/posts/${lang}/${slug}`),
};

export { API };
