"""Render natural.html over a local http server (so assets/ can be fetched).
Usage: python3 -I serve.py '<query>' '<jobs json>'      (renders frames/<name>.png)
       python3 -I serve.py '<query with export=1>' export <outdir>"""
import asyncio, os, sys, json, time, threading, base64, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); FR = os.path.abspath(os.path.join(HERE, "..", "frames")); TH = os.path.join(HERE, "node_modules/three")
class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=FR)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    query, mode = sys.argv[1], sys.argv[2]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": 1280, "height": 720})
        logs = []
        pg.on("pageerror", lambda e: (logs.append(str(e)), print("PAGEERROR", e, flush=True)))
        pg.on("console", lambda m: logs.append(m.text) if m.type in ("error", "warning") else None)
        async def route(r):
            u = r.request.url
            if "three@0.160.0/" in u: await r.fulfill(path=os.path.join(TH, u.split("three@0.160.0/")[1]), content_type="application/javascript")
            else: await r.continue_()
        await pg.route("**/*", route)
        await pg.goto(f"http://127.0.0.1:{port}/natural.html?{query}", timeout=120000)
        try:
            await pg.wait_for_function("window.__done === true || window.__err", timeout=300000)
        except Exception:
            print("LOGS", logs); raise
        if mode == "export":
            out = sys.argv[3]; os.makedirs(out, exist_ok=True)
            d = await pg.evaluate("window.__export")
            open(os.path.join(out, "terrain_pos.bin"), "wb").write(base64.b64decode(d["pos"]))
            open(os.path.join(out, "occluders.glb"), "wb").write(base64.b64decode(d["occ"]))
            json.dump({"trees": d["trees"], "booz": d["booz"]}, open(os.path.join(out, "placements.json"), "w"))
            print("exported", len(d["trees"]), "trees", len(d["booz"]), "placements", logs[:3])
        else:
            for name, opts in json.loads(mode):
                t0 = time.time()
                await pg.evaluate("o => window.renderFrame(o)", opts)
                await pg.screenshot(path=os.path.join(FR, name + ".png"), timeout=300000)
                print(name, round(time.time() - t0, 1), "s", logs[:3], flush=True)
        await b.close()
asyncio.run(main())
