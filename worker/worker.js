// Serves jdaws.com from this repository through jsDelivr, pinned to a commit.
// / -> site/index.html, /resume -> site/resume.html, plus /assets/*, /fonts/* and /og.jpg.
// Files referenced with ?v=<content hash> are cached by browsers for a year.
const REF = 'COMMIT_SHA';
const PREVIEW = false; // true keeps search engines off the preview host
const BASE = `https://cdn.jsdelivr.net/gh/jdaws97/jdaws-site@${REF}/site`;
const TYPES = { html: 'text/html; charset=utf-8', js: 'text/javascript; charset=utf-8', gz: 'application/octet-stream', woff2: 'font/woff2', jpg: 'image/jpeg' };

export default {
  async fetch(req) {
    const url = new URL(req.url);
    if (url.hostname.startsWith('www.')) return Response.redirect(`https://${url.hostname.slice(4)}${url.pathname}${url.search}`, 301);
    let path = url.pathname;
    if (path === '/' || path === '/index.html') path = '/index.html';
    else if (path === '/resume' || path === '/resume/' || path === '/resume.html') path = '/resume.html';
    else if (path !== '/og.jpg' && !/^\/(assets|fonts)\/[\w.-]+$/.test(path)) return new Response('Not found', { status: 404 });
    const up = await fetch(BASE + path, { cf: { cacheTtl: 31536000, cacheEverything: true } });
    if (!up.ok) return new Response('Not found', { status: 404 });
    const ext = path.split('.').pop();
    const h = new Headers({ 'content-type': TYPES[ext] || 'application/octet-stream', 'x-content-type-options': 'nosniff', 'referrer-policy': 'strict-origin-when-cross-origin' });
    h.set('cache-control', ext === 'html' ? 'no-cache' : url.searchParams.has('v') ? 'public, max-age=31536000, immutable' : ext === 'woff2' ? 'public, max-age=2592000' : 'public, max-age=86400');
    if (PREVIEW) h.set('x-robots-tag', 'noindex');
    return new Response(up.body, { headers: h });
  },
};
