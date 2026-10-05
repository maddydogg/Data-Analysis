"""Build and check every listing asset for Murder at the Lantern Supper:

    cd listing/src && python3 build_listing.py [--no-video]

Outputs: ../mockups/*.jpg (10 + overview), ../video/*.mp4 (trailer, kit presentation), ../../out/ (the archives),
../spoiler_check.md / .json. Run src/build.py first (it makes the PDFs and delivery/). Exits non-zero on any failure.
"""
import json, os, re, shutil, subprocess, sys, zipfile
from PIL import Image
import imageio_ffmpeg
import pymupdf as fitz
import kit
import party_listing as PL
import mockups as M

LISTING = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PL.CASE, "out"); DELIV = os.path.join(PL.CASE, "delivery")

def probe(path):
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", path], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out); size = re.search(r"Video: .*?, (\d+)x(\d+)", out)
    return dict(seconds=int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3)),
                width=int(size.group(1)), height=int(size.group(2)), audio="Audio:" in out)

def main(video=True):
    checks = []
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=str(detail))); return passed
    bad = PL.forbidden()
    ok("Spoiler list loaded: the solution, all 12 secrets, every Round 2 and 3 line and card, the sealed pages",
       sum(k.startswith("secret") for k in bad) == 12 and any(k.startswith("card 9") for k in bad), f"{len(bad)} tokens")
    G = PL.Pages()
    sealed = G.H.find("SEALED SOLUTION", "STOP")
    r2 = G.P.find("ROUND 2 · CARD 5")
    sec = G.P.find(PL.C.name("isadora"), "YOUR CHARACTER")
    ctrl = kit.spoiler_scan([("pdf", "sealed", G.H.doc[sealed + 1].get_text()), ("pdf", "r2", G.P.doc[r2].get_text()),
                             ("pdf", "booklet", G.P.doc[sec].get_text())], bad)
    labels = {h["label"].split(" line")[0] for h in ctrl}
    ok("Control test: the scanner catches the solution page, a Round 2 card and a whole booklet front with its secret",
       any(l.startswith("solution") for l in labels) and "card 5" in labels and "secret of isadora" in labels,
       f"{len(ctrl)} hits")

    res, _, _ = M.build(os.path.join(LISTING, "mockups"))
    drawn = []
    for r in res:
        im = Image.open(r["path"])
        ok(f"Mockup {r['name']}: 2000x2000 JPG", im.size == (2000, 2000) and im.format == "JPEG",
           f"{os.path.getsize(r['path']) // 1024} KB")
        ok(f"Mockup {r['name']}: no spoilers in any visible text ({len(r['sources'])} sources)", not r["hits"],
           "; ".join(f"{h['label']} in {h['source']}" for h in r["hits"]))
        drawn += [t for k, _, t in r["sources"]]
    hero = " ".join(t for _, _, t in res[0]["sources"])
    need = ["MURDER AT THE", "LANTERN SUPPER", "6–12 PLAYERS", "PRINTABLE PARTY KIT"]
    ok("Image 01 carries the title, “6–12 players” and “Printable party kit”", all(n in hero for n in need),
       ", ".join(n for n in need if n not in hero) or "all present")
    allsrc = " ".join(t for r in res for _, _, t in r["sources"])
    ok("Only Round 1 evidence cards appear in the mockups", "ROUND 1 · CARD" in allsrc and "ROUND 2 · CARD" not in allsrc
       and "ROUND 3 · CARD" not in allsrc)
    ok("Booklets appear only above the secret (no “Your secret” box in any image)", "Your secret" not in allsrc)
    ok("Host guide pages in the images all come before the sealed section",
       "SEALED SOLUTION" not in allsrc and PL.C.SOLUTION_INTRO not in allsrc)

    vids = []
    if video:
        import video as VID
        for k, (path, n, hits, hf) in VID.build().items():
            ok(f"Video {k}: every one of {n} frames scanned, no spoilers", hf == 0, f"{hf} frames with hits")
            pv = probe(path)
            ok(f"Video {k}: 1080x1080, 12–15 s, no sound", pv["width"] == 1080 and pv["height"] == 1080 and
               12 <= pv["seconds"] <= 15 and not pv["audio"], json.dumps(pv))
            vids.append(path)
        captions = re.findall(r'"([A-Z][A-Z0-9 ·.…?,’\'–-]{6,})"', open(VID.__file__).read())
        drawn += captions
    else:
        vd = os.path.join(LISTING, "video"); vids = [os.path.join(vd, f) for f in sorted(os.listdir(vd)) if f.endswith(".mp4")]
    hits = PL.VER.stop_hits(drawn)
    ok("Stop list: no borrowed brands, films, books, party-game names or real witch trials in any image or caption",
       not hits, ", ".join(hits) or f"{len(drawn)} strings checked")

    names = sorted(os.listdir(DELIV))
    ok("Delivery holds exactly 5 files (the Etsy limit), each under 20 MB", len(names) == 5 and all(
        os.path.getsize(os.path.join(DELIV, n)) < 20 * 2 ** 20 for n in names), ", ".join(names))
    for n in names:
        if "PLAYER-KIT" in n:
            t = " ".join(p.get_text() for p in fitz.open(os.path.join(DELIV, n)))
            ok(f"{n}: no solution anywhere in the player kit", not [x for x in PL.VER.spoiler_tokens() if x in " ".join(t.split())])
    os.makedirs(OUT, exist_ok=True)
    for fn in os.listdir(OUT):
        os.remove(os.path.join(OUT, fn))
    a1 = os.path.join(OUT, f"{PL.SLUG}_files-for-sale.zip")
    with zipfile.ZipFile(a1, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in names:
            zf.write(os.path.join(DELIV, n), arcname=n)
    a2 = os.path.join(OUT, f"{PL.SLUG}_10-mockups-JPG.zip")
    with zipfile.ZipFile(a2, "w", zipfile.ZIP_STORED) as zf:
        for r in res:
            zf.write(r["path"], arcname=os.path.basename(r["path"]))
    arch = [a1, a2]
    for v in vids:
        dst = os.path.join(OUT, os.path.basename(v)); shutil.copyfile(v, dst); arch.append(dst)
    for a in arch:
        ok(f"Archive {os.path.basename(a)} written", os.path.getsize(a) > 0, f"{os.path.getsize(a) / 2 ** 20:.1f} MB")

    passed = sum(c["passed"] for c in checks)
    lines = ["# Listing assets: spoiler and format check", "", f"Result: **{passed} of {len(checks)} checks passed**", "",
             "Every mockup and every video frame records the text of every PDF region it places and every string it "
             "draws; the scanner looks for the solution, all 12 secrets, every Round 2 and Round 3 booklet line and "
             "evidence card, and the sealed pages. The control run shows it catches them.", "",
             "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(checks, 1):
        lines.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    open(os.path.join(LISTING, "spoiler_check.md"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(checks=checks), open(os.path.join(LISTING, "spoiler_check.json"), "w"), indent=1)
    print(f"checks {passed}/{len(checks)}")
    for c in checks:
        if not c["passed"]:
            print("FAIL", c["name"], c["detail"])
    return passed == len(checks)

if __name__ == "__main__":
    sys.exit(0 if main(video="--no-video" not in sys.argv) else 1)
