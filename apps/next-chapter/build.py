"""Build the demo and full versions of Next Chapter from src/index.html.

    python3 build.py

Writes dist/next-chapter-demo/ and dist/next-chapter/, each a folder you can
drop onto Cloudflare Pages as is: index.html, manifest, service worker, icons.
"""
import json
import pathlib
import re

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).parent
SRC = (HERE / "src" / "index.html").read_text(encoding="utf-8")
VERSION = "1.0.0"

BUILDS = {
    "next-chapter-demo": dict(
        demo=True,
        key="next-chapter-demo-v1",
        title="Next Chapter — Free Demo",
        name="Next Chapter Demo",
        short="Chapter Demo",
        desc="Free demo of Next Chapter, the book tracker app.",
    ),
    "next-chapter": dict(
        demo=False,
        key="next-chapter-v1",
        title="Next Chapter",
        name="Next Chapter",
        short="Next Chapter",
        desc="Book tracker: reading goal, series, spice ratings and stats.",
    ),
}


def icon(size):
    im = Image.new("RGB", (size, size), "#9C3D54")
    d = ImageDraw.Draw(im)
    s = size / 512
    # three book spines on a shelf
    for x, w, h, c in [(136, 70, 250, "#FBF6EE"), (216, 62, 222, "#F4D3D3"), (288, 70, 262, "#FBF6EE")]:
        d.rounded_rectangle([x * s, (390 - h) * s, (x + w) * s, 390 * s], radius=10 * s, fill=c)
    d.rounded_rectangle([112 * s, 390 * s, 400 * s, 410 * s], radius=8 * s, fill="#E8B65E")
    # bookmark ribbon on the last spine
    d.polygon([(338 * s, 128 * s), (358 * s, 128 * s), (358 * s, 176 * s), (348 * s, 166 * s), (338 * s, 176 * s)], fill="#9C3D54")
    return im


def build(folder, cfg):
    out = HERE / "dist" / folder
    out.mkdir(parents=True, exist_ok=True)
    html = SRC
    html = html.replace("const DEMO=true,", f"const DEMO={'true' if cfg['demo'] else 'false'},", 1)
    html = html.replace("const KEY='next-chapter-demo-v1'", f"const KEY='{cfg['key']}'", 1)
    html = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", html, count=1)
    assert f"const DEMO={'true' if cfg['demo'] else 'false'}," in html and cfg["key"] in html
    (out / "index.html").write_text(html, encoding="utf-8")

    manifest = {
        "name": cfg["name"], "short_name": cfg["short"], "description": cfg["desc"],
        "start_url": "./", "scope": "./", "display": "standalone",
        "background_color": "#FBF6EE", "theme_color": "#FBF6EE",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (out / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    prefix = folder + "-"
    sw = (
        f"const VERSION='{prefix}{VERSION}';\n"
        "const FILES=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'];\n"
        "self.addEventListener('install',e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(FILES)));self.skipWaiting()});\n"
        f"self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('{prefix}')&&k!==VERSION).map(k=>caches.delete(k)))));self.clients.claim()}});\n"
        "self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;\n"
        "  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request).then(res=>{const copy=res.clone();caches.open(VERSION).then(c=>c.put(e.request,copy));return res}).catch(()=>caches.match('index.html'))))});\n"
    )
    (out / "sw.js").write_text(sw, encoding="utf-8")

    for n in (192, 512):
        icon(n).save(out / f"icon-{n}.png")
    print("built", out)


if __name__ == "__main__":
    for folder, cfg in BUILDS.items():
        build(folder, cfg)
