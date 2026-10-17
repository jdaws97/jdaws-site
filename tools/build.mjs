// Builds site/index.html from src/index.html:
//  - the inline module and its three.js imports become one minified, tree-shaken bundle at /assets/app.js
//  - every asset URL gets a content hash (?v=...) so browsers can cache it for a year
//  - CSS whitespace is trimmed
// Run: node tools/build.mjs   (needs three@0.160.0 and esbuild in tools/node_modules)
import { build } from 'esbuild';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = join(ROOT, 'site');
const hash = buf => createHash('sha256').update(buf).digest('hex').slice(0, 10);
const versioned = path => `${path}?v=${hash(readFileSync(join(SITE, path)))}`;

let html = readFileSync(join(ROOT, 'src/index.html'), 'utf8');
const m = html.match(/<script type="module">([\s\S]*?)<\/script>/);
if (!m) throw new Error('no inline module in src/index.html');

// asset URLs inside the code and the preload tags
const ASSETS = ['/assets/world.glb.gz', '/assets/terrain.bin.gz'];
let code = m[1];
for (const a of ASSETS) { const v = versioned(a); code = code.split(`'${a}'`).join(`'${v}'`); html = html.split(`href="${a}"`).join(`href="${v}"`); }

mkdirSync(join(ROOT, 'tools/.build'), { recursive: true });
const entry = join(ROOT, 'tools/.build/entry.js');
writeFileSync(entry, code);
const out = await build({
  entryPoints: [entry], bundle: true, minify: true, format: 'esm', target: 'es2022', write: false,
  nodePaths: [join(ROOT, 'tools/node_modules')], legalComments: 'none',
});
const js = out.outputFiles[0].contents;
writeFileSync(join(SITE, 'assets/app.js'), js);
const appUrl = `/assets/app.js?v=${hash(js)}`;

html = html.replace(/<script type="importmap">[\s\S]*?<\/script>\n?/, '');
html = html.replace(m[0], `<script type="module" src="${appUrl}"></script>`);
html = html.replace('<link rel="icon"', `<link rel="modulepreload" href="${appUrl}">\n<link rel="icon"`);
html = html.replace(/<style>([\s\S]*?)<\/style>/, (_, css) => '<style>' + css.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\n\s*/g, '').replace(/\s*([{};:,])\s*/g, '$1') + '</style>');
writeFileSync(join(SITE, 'index.html'), html);
console.log('app.js', js.length, 'bytes;', 'index.html', html.length, 'bytes');
