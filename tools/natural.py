import asyncio, os, sys
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "frames"); TH = os.path.join(HERE, "node_modules/three")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        for v in sys.argv[1:]:
            pg = await b.new_page(viewport={"width": 1280, "height": 720})
            logs = []
            pg.on("pageerror", lambda e: logs.append(str(e)))
            async def route(r):
                u = r.request.url
                if "three@0.160.0/" in u: await r.fulfill(path=os.path.join(TH, u.split("three@0.160.0/")[1]), content_type="application/javascript")
                else: await r.continue_()
            await pg.route("**/*", route)
            await pg.goto("file://" + os.path.abspath(os.path.join(OUT, "natural.html")) + "?v=" + v, timeout=120000)
            await pg.wait_for_function("window.__done === true", timeout=300000)
            await asyncio.sleep(0.5)
            await pg.screenshot(path=os.path.join(OUT, "nat-" + v + ".png"), timeout=300000)
            print(v, "ok", logs[:2], flush=True)
            await pg.close()
        await b.close()
asyncio.run(main())
