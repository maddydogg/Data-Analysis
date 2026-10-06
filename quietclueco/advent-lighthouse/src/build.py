"""One command builds everything: python3 build.py [--art] [--no-previews]
generate -> check -> art -> render PDFs -> check PDFs -> report -> PNG previews."""
import os, sys, shutil
import generate, verify, render, cover
import case as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)          # quietclueco/advent-lighthouse/
SLUG = "the-keeper-of-candleholm"

def main(previews=True):
    rows, meta = generate.build()
    generate.save(rows, meta, os.path.join(HERE, "data"))
    rows = verify.load()
    rep = verify.check_all(rows)
    render.register_fonts()
    render.ensure_art(force="--art" in sys.argv)
    if "--art" in sys.argv or not os.path.exists(os.path.join(HERE, "art", "cover_letter.jpg")):
        cover.make_pdf_covers(os.path.join(HERE, "art"))
    paths = {}
    render.Book.counts = rep["facts"]["checkpoints"]; render.Book.empty = rep["facts"]["empty_chapters"]
    for fmt, folder in (("letter", "print"), ("a4", "print"), ("ipad", "ipad")):
        d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
        tag = {"letter": "print-US-Letter", "a4": "print-A4", "ipad": "iPad"}[fmt]
        paths[f"book_{fmt}"] = os.path.join(d, f"{SLUG}_{tag}.pdf")
        render.build_book(fmt, paths[f"book_{fmt}"])
        sd = os.path.join(OUT, "solution"); os.makedirs(sd, exist_ok=True)
        paths[f"solution_{fmt}"] = os.path.join(sd, f"{SLUG}_SOLUTION_{tag}.pdf")
        fin = [dict(rec=rep["facts"]["answer"], clue="KILLER", why="Fits every window: the killer")]
        for r, cid in sorted(rep["facts"]["finalists"], key=lambda x: (int(x[1]), x[0]["tally"])):
            fin.append(dict(rec=r, clue=cid, why=f"Window {cid}"))
        render.build_solution(fmt, paths[f"solution_{fmt}"], rep["facts"]["walk"], fin, rep["facts"]["index"])
    verify.check_pdfs(rep, paths, rows)
    passed, total = verify.write_report(rep, os.path.join(OUT, "verification_report.md"),
                                        os.path.join(OUT, "verification_report.json"))
    print(f"checks: {passed}/{total}")
    for c in rep["checks"]:
        if not c["passed"]:
            print("FAIL:", c["name"], "|", c["detail"][:300])
    print(rep.get("pages"))
    if previews:
        make_previews(paths)
    return passed == total

def make_previews(paths):
    import pymupdf as fitz
    from PIL import Image
    for key, sub in (("book_letter", "print-letter"), ("book_a4", "print-a4"), ("book_ipad", "ipad"),
                     ("solution_letter", "solution-letter"), ("solution_a4", "solution-a4"),
                     ("solution_ipad", "solution-ipad")):
        d = os.path.join(OUT, "previews", sub)
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        doc = fitz.open(paths[key])
        for i, p in enumerate(doc, 1):
            pix = p.get_pixmap(dpi=40 if "ipad" in key else 50)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img.quantize(64).save(os.path.join(d, f"page-{i:03d}.png"), optimize=True)

if __name__ == "__main__":
    ok = main(previews="--no-previews" not in sys.argv)
    sys.exit(0 if ok else 1)
