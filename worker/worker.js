// Serves the site from this repository through jsDelivr, pinned to a commit.
// Paths: / -> site/index.html, /resume -> site/resume.html, /assets/* and /fonts/* -> site/...
const REF = 'COMMIT_SHA';
const BASE = `https://cdn.jsdelivr.net/gh/jdaws97/jdaws-site@${REF}/site`;
const TYPES = { html: 'text/html; charset=utf-8', glb: 'model/gltf-binary', bin: 'application/octet-stream', woff2: 'font/woff2' };

export default {
  async fetch(req) {
    const url = new URL(req.url);
    if (url.hostname.startsWith('www.')) return Response.redirect(`https://${url.hostname.slice(4)}${url.pathname}${url.search}`, 301);
    let path = url.pathname;
    if (path === '/' || path === '/index.html') path = '/index.html';
    else if (path === '/resume' || path === '/resume/' || path === '/resume.html') path = '/resume.html';
    else if (!/^\/(assets|fonts)\/[\w.-]+$/.test(path)) return new Response('Not found', { status: 404 });
    const up = await fetch(BASE + path, { cf: { cacheTtl: 86400, cacheEverything: true } });
    if (!up.ok) return new Response('Not found', { status: 404 });
    const ext = path.split('.').pop();
    const h = new Headers({ 'content-type': TYPES[ext] || 'application/octet-stream', 'x-content-type-options': 'nosniff' });
    h.set('cache-control', ext === 'html' ? 'no-cache' : 'public, max-age=86400');
    if (ext === 'html') h.set('referrer-policy', 'strict-origin-when-cross-origin');
    return new Response(up.body, { headers: h });
  },
};
