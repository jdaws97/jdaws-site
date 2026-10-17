# jdaws-site

Jarod Daws' resume website: a low-poly archipelago in three.js where each island is a stop in the career, plus a plain written resume at `/resume`.

## Layout

- `site/` is what gets served: `index.html` (the 3D tour), `resume.html`, `assets/` (Blender models and baked terrain shadows) and `fonts/`.
- `blender/` holds the scripts that build the models with Blender's Python module (`pip install bpy`) and bake their soft shadows.
  - `python3 blender/assets.py site-raw.glb` builds every model and bakes shadows into vertex colors.
  - `npx gltf-transform meshopt site-raw.glb site/assets/world.glb` compresses the result.
  - `bake_terrain.py` bakes terrain shadows from a scene export (`tools/mockup.html?export=1`).
- `tools/` holds the mockup page used for art direction and headless Playwright scripts for screenshots and interaction tests.
- `worker/` is the Cloudflare Worker that serves the site.
- `legacy/` is the previous version of jdaws.com.
