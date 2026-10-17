# jdaws-site

Jarod Daws' site: a low-poly archipelago in three.js where each island is a stop in the career, plus a plain résumé at `/resume`.

## Layout

- `src/index.html` is the source of the 3D tour (one file: styles, markup and the module script).
- `site/` is what gets served. `node tools/build.mjs` writes `site/index.html` and `site/assets/app.js` (three.js and the tour code, bundled and minified) and adds content hashes to asset URLs.
- `site/assets/world.glb.gz`: the Blender models (meshopt-compressed, then gzip). `site/assets/terrain.bin.gz`: the baked terrain (heights, colors with soft shadows, tree placements).
- `blender/` builds the models with Blender's Python module (`pip install bpy`) and bakes their soft shadows; `bake_terrain.py` bakes terrain shadows.
- `tools/` holds the build script, the art-direction mockup page, and headless Playwright scripts for screenshots and interaction tests.
- `worker/` is the Cloudflare Worker that serves the site from this repository, pinned to a commit.
- `legacy/` is the previous version of jdaws.com.

## Rebaking the terrain

Open the built site with `?bake=1` (see `tools/apptest.py`, step `bake`) to recompute the terrain from its noise functions and write a new `terrain.bin`, then `gzip -9` it into `site/assets/terrain.bin.gz`.
