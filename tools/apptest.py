"""Serve app/ locally and drive it like a visitor. Usage: apptest.py <steps json> [w h mobile]"""
import asyncio, os, sys, json, time, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); APP = os.path.abspath(os.path.join(HERE, "..", "site")); OUT = os.path.abspath(os.path.join(HERE, "..", "shots")); TH = os.path.join(HERE, "node_modules/three")
os.makedirs(OUT, exist_ok=True)
class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.split('?')[0] == '/resume': self.path = '/resume.html'
        return super().do_GET()
srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=APP)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    steps = json.loads(sys.argv[1]); w, h = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1280, 720); mobile = len(sys.argv) > 4
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        ctx = await b.new_context(viewport={"width": w, "height": h}, has_touch=mobile, is_mobile=mobile, device_scale_factor=1)
        pg = await ctx.new_page(); logs = []
        pg.on("pageerror", lambda e: (logs.append("PAGEERROR " + str(e)), print("PAGEERROR", e, flush=True)))
        pg.on("console", lambda m: logs.append(m.type + ": " + m.text) if m.type in ("error", "warning") else None)
        async def route(r):
            u = r.request.url
            if "three@0.160.0/" in u: await r.fulfill(path=os.path.join(TH, u.split("three@0.160.0/")[1]), content_type="application/javascript")
            else: await r.continue_()
        await pg.route("**/*", route)
        t0 = time.time()
        for st in steps:
            kind = st[0]
            if kind == "goto": await pg.goto(f"http://127.0.0.1:{port}{st[1]}", timeout=120000); await pg.wait_for_function("window.__done === true", timeout=300000); print("loaded in", round(time.time() - t0, 1), "s", flush=True)
            elif kind == "open": await pg.goto(f"http://127.0.0.1:{port}{st[1]}", timeout=120000)
            elif kind == "wait": await pg.wait_for_timeout(st[1])
            elif kind == "shot": await pg.screenshot(path=os.path.join(OUT, st[1] + ".png"), timeout=300000); print("shot", st[1], flush=True)
            elif kind == "eval": print("eval", st[1][:60], "->", await pg.evaluate(st[1]), flush=True)
            elif kind == "click": await pg.click(st[1], timeout=20000, force=True)
            elif kind == "key": await pg.keyboard.press(st[1])
            elif kind == "wheel": await pg.mouse.move(w / 2, h / 2); await pg.mouse.wheel(0, st[1])
            elif kind == "drag": await pg.mouse.move(st[1], st[2]); await pg.mouse.down(); await pg.mouse.move(st[3], st[4], steps=8); await pg.mouse.up()
            elif kind == "swipe":
                await pg.evaluate("""([x0,y0,x1,y1]) => { const el = document.querySelector('canvas'); const mk = (type, x, y) => new PointerEvent(type, {pointerId: 7, pointerType: 'touch', clientX: x, clientY: y, bubbles: true});
                  el.dispatchEvent(mk('pointerdown', x0, y0)); for (let i = 1; i <= 6; i++) window.dispatchEvent(mk('pointermove', x0 + (x1 - x0) * i / 6, y0 + (y1 - y0) * i / 6)); window.dispatchEvent(mk('pointerup', x1, y1)); }""", st[1:5])
            elif kind == "tap": await pg.tap(st[1], timeout=20000, force=True) if mobile else await pg.click(st[1], timeout=20000, force=True)
        print("LOGS", logs[:8])
        await b.close()
asyncio.run(main())
