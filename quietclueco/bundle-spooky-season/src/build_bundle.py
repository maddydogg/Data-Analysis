"""Build the Storm & Moon Double Feature bundle and check it:

    python3 make_case_covers.py && python3 art.py && python3 build_bundle.py

1. Two front pages per format: the double-feature cover (art.py) and a programme-style
   contents page with clickable lines for every section of both cases.
2. The two finished case books (no solutions) appended unchanged; their own links are kept
   and re-pointed, and their bookmarks are nested under a bookmark per case.
3. bundle_SOLUTIONS.zip with the six solution files.
4. Checks: no solution text, each killer's name only on their own log line, every link and
   bookmark lands on the right page, file sizes, page counts. Report: bundle_check.md/.json.
"""
import json, os, re, shutil, sys, zipfile
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import bundle as B

PAGES = {"letter": (612, 792), "a4": (595.28, 841.89), "ipad": (768, 1024)}
DELIV = os.path.join(B.ROOT, "delivery")
ART = os.path.join(B.HERE, "art")
SOLUTION_MARKERS = ["What really happened", "Elimination index", "Ruled out by", "THE ENVELOPE", "Step by step"]

def rgb(c, a=1):
    return Color(c[0] / 255, c[1] / 255, c[2] / 255, alpha=a)

def register_fonts():
    for name, d, f in [("Fraunces-SemiBold", B.FONTS, "Fraunces-SemiBold"), ("Fraunces-Italic", B.FONTS, "Fraunces-Italic"),
                       ("Nunito", B.FONTS, "Nunito-Regular"), ("Nunito-Bold", B.FONTS, "Nunito-Bold"),
                       ("Nunito-ExtraBold", B.FONTS, "Nunito-ExtraBold"), ("Nunito-Italic", B.FONTS, "Nunito-Italic"),
                       ("Abril", B.HORROR, "AbrilFatface-Regular"), ("Bebas", B.HORROR, "BebasNeue-Regular")]:
        pdfmetrics.registerFont(TTFont(name, os.path.join(d, f + ".ttf")))

def sections(book):
    """Top-level sections of a case book: (title, 0-based page index), cover first."""
    return [("Case cover", 0)] + [(t, p - 1) for lv, t, p in book.get_toc() if lv == 1]

def fit_size(text, font, size, width):
    while pdfmetrics.stringWidth(text, font, size) > width and size > 5:
        size -= 0.25
    return size

# ---------------------------------------------------------------- the two front pages
def front_pages(fmt, path, offsets, books):
    W, H = PAGES[fmt]; s = W / 612
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(f"{B.NAME} — {B.BRAND}"); c.setAuthor(B.BRAND); c.setSubject("Two printable murder mystery puzzles")
    # page 1: the cover art, plus the words as invisible text so the PDF stays searchable
    c.drawImage(os.path.join(ART, f"cover_{fmt}.jpg"), 0, 0, W, H)
    t = c.beginText(); t.setTextRenderMode(3); t.setFont("Nunito", 12)
    for i, line in enumerate([B.NAME, "A double feature", B.TAGLINE,
                              f"Feature 1: {B.CASES[0]['title']}", f"Feature 2: {B.CASES[1]['title']}",
                              f"{B.BRAND} · Printable case files"]):
        t.setTextOrigin(40, H - 60 - i * 16); t.textLine(line)
    c.drawText(t)
    c.showPage()
    # page 2: the programme (contents)
    links = []
    c.setFillColor(rgb(B.PARCH)); c.rect(0, 0, W, H, fill=1, stroke=0)
    hb = 132 * s
    c.setFillColor(rgb(B.STORM["dark"])); c.rect(0, H - hb, W / 2, hb, fill=1, stroke=0)
    c.setFillColor(rgb(B.MOON["dark"])); c.rect(W / 2, H - hb, W / 2, hb, fill=1, stroke=0)
    c.setFillColor(rgb(B.MOON["accent"])); c.rect(W / 2 - 1.5 * s, H - hb, 3 * s, 24 * s, fill=1, stroke=0)
    n = 22
    for i in range(n):
        x = (i + 0.5) * W / n
        c.setFillColor(rgb((0xFF, 0xD2, 0x7A), 0.35)); c.circle(x, H - hb + 12 * s, 6 * s, fill=1, stroke=0)
        c.setFillColor(rgb((0xFF, 0xE6, 0xA8))); c.circle(x, H - hb + 12 * s, 3 * s, fill=1, stroke=0)
    c.setFillColor(rgb((0xF4, 0xEA, 0xD0))); c.setFont("Bebas", 46 * s)
    c.drawCentredString(W / 2, H - 62 * s, "TONIGHT’S PROGRAMME")
    c.setFillColor(rgb(B.MOON["accent"])); c.setFont("Fraunces-Italic", 13 * s)
    c.drawCentredString(W / 2, H - 88 * s, f"{B.NAME} · two complete cases · {B.BRAND}")
    m = 36 * s; gap = 18 * s; cw = (W - 2 * m - gap) / 2
    lows = []
    note_h = 104 * s
    top = H - hb - 20 * s
    blurb_st = ParagraphStyle("b", fontName="Nunito-Italic", fontSize=8.6 * s, leading=11.6 * s, textColor=rgb(B.INK))
    for k, case in enumerate(B.CASES):
        pal = case["pal"]; x0 = m + k * (cw + gap); y = top
        c.setFillColor(rgb(pal["dark"])); c.rect(x0, y - 70 * s, cw, 70 * s, fill=1, stroke=0)
        c.setFillColor(rgb(pal["accent"])); c.rect(x0, y - 70 * s, cw, 4 * s, fill=1, stroke=0)
        c.setFont("Bebas", 17 * s); c.drawString(x0 + 12 * s, y - 22 * s, case["feature"])
        c.setFont("Nunito-Bold", 8 * s); c.setFillColor(rgb(pal["light"], 0.85))
        c.drawRightString(x0 + cw - 12 * s, y - 21 * s, f"QuietClueCo case No. {case['no']}")
        fs = fit_size(case["title"], "Abril", 19 * s, cw - 24 * s)
        c.setFillColor(rgb(pal["light"])); c.setFont("Abril", fs); c.drawString(x0 + 12 * s, y - 52 * s, case["title"])
        y -= 70 * s + 8 * s
        p = Paragraph(case["blurb"], blurb_st); _, ph = p.wrap(cw - 8 * s, 1000); p.drawOn(c, x0 + 4 * s, y - ph); y -= ph + 8 * s
        secs = sections(books[k])
        avail = y - (m + note_h + 14 * s)
        lh = min(16 * s, avail / len(secs))
        fsz = min(9.4 * s, lh * 0.62)
        for title, pidx in secs:
            pageno = offsets[k] + pidx + 1
            c.setFont("Nunito", fsz); c.setFillColor(rgb(B.INK))
            label = title.replace("Evidence ", "Ev. ") if pdfmetrics.stringWidth(title, "Nunito", fsz) > cw - 46 * s else title
            c.drawString(x0 + 4 * s, y - lh * 0.72, label)
            c.setFont("Nunito-Bold", fsz); c.drawRightString(x0 + cw - 4 * s, y - lh * 0.72, str(pageno))
            tw = pdfmetrics.stringWidth(label, "Nunito", fsz)
            c.setStrokeColor(rgb((0xC9, 0xBD, 0xA8))); c.setLineWidth(0.6); c.setDash(1, 2)
            c.line(x0 + 8 * s + tw, y - lh * 0.72 + 1.5, x0 + cw - 10 * s - pdfmetrics.stringWidth(str(pageno), "Nunito-Bold", fsz), y - lh * 0.72 + 1.5)
            c.setDash()
            links.append(dict(rect=(x0, H - y, x0 + cw, H - (y - lh)), target=offsets[k] + pidx, case=k, title=title, orig=pidx))
            y -= lh
        c.setFillColor(rgb(pal["accent"])); c.rect(x0, y - 4 * s, cw, 2 * s, fill=1, stroke=0)
        lows.append(y - 4 * s)
    free = min(lows) - (m + note_h)
    if free > 60 * s:                                                   # an intermission card in the gap
        cy = m + note_h + free / 2
        c.setFillColor(rgb(B.STORM["dark"])); c.setFont("Bebas", 22 * s)
        c.drawCentredString(W / 2, cy + 2 * s, "— INTERMISSION —")
        c.setFillColor(rgb(B.MOON["mid"])); c.setFont("Fraunces-Italic", 11 * s)
        c.drawCentredString(W / 2, cy - 16 * s, "Put the kettle on between features.")
    # how the double feature works
    by = m + note_h
    c.setFillColor(rgb((0xFB, 0xF7, 0xEE))); c.setStrokeColor(rgb(B.MOON["accent"])); c.setLineWidth(1.2)
    c.roundRect(m, m, W - 2 * m, note_h, 8 * s, fill=1, stroke=1)
    c.setFillColor(rgb(B.MOON["dark"])); c.setFont("Bebas", 16 * s)
    c.drawString(m + 14 * s, by - 22 * s, "HOW THE DOUBLE FEATURE WORKS")
    st = ParagraphStyle("n", fontName="Nunito", fontSize=8.6 * s, leading=11.4 * s, textColor=rgb(B.INK))
    yy = by - 30 * s
    for line in ["Two complete, separate cases, each with its own 6,000 suspects, 18 clues and one killer. "
                 "Play them in any order, one per evening.",
                 "The numbers on this page are PDF page numbers: tap a line to jump there. Inside each case, the "
                 "page numbers in the footer and on its own contents page count from that case’s cover.",
                 "The solutions are in the separate SOLUTIONS file: one Envelope per case. Open them only after "
                 "the Sealed Check."]:
        p = Paragraph("•&nbsp;&nbsp;" + line, st); _, ph = p.wrap(W - 2 * m - 28 * s, 1000)
        p.drawOn(c, m + 14 * s, yy - ph); yy -= ph + 3 * s
    c.setFont("Nunito", 7.5 * s); c.setFillColor(rgb((0x6B, 0x62, 0x59)))
    c.drawCentredString(W / 2, m - 16 * s, f"{B.BRAND} · {B.NAME} · For personal use. Please don’t share or resell the files.")
    c.showPage(); c.save()
    return links

# ---------------------------------------------------------------- assemble
def build(fmt):
    books = [fitz.open(c["book"][fmt]) for c in B.CASES]
    offsets = [2, 2 + len(books[0])]
    tmp = os.path.join(B.HERE, f"_front_{fmt}.pdf")
    links = front_pages(fmt, tmp, offsets, books)
    doc = fitz.open(tmp)
    for bk in books:
        doc.insert_pdf(bk, links=True, annots=True)
    os.remove(tmp)
    for L in links:
        doc[1].insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(*L["rect"]), "page": L["target"], "to": fitz.Point(0, 0)})
    toc = [[1, "Cover — " + B.NAME, 1], [1, "Programme (contents)", 2]]
    for k, (case, bk) in enumerate(zip(B.CASES, books)):
        toc.append([1, f"{case['feature'].title()} — {case['title']}", offsets[k] + 1])
        toc.append([2, "Case cover", offsets[k] + 1])
        for lv, t, p in bk.get_toc():
            toc.append([lv + 1, t, p + offsets[k]])
    doc.set_toc(toc)
    doc.set_metadata({"title": f"{B.NAME} — two printable murder mystery puzzles", "author": B.BRAND,
                      "subject": "QuietClueCo double feature: Storm over Corvenmoor and Full Moon over Morrowmere",
                      "creator": f"{B.BRAND} bundle builder", "producer": "PyMuPDF", "keywords": "murder mystery puzzle"})
    out = os.path.join(DELIV, B.OUT_NAMES[fmt])
    doc.save(out, garbage=4, deflate=True)
    return out, offsets, links

def solutions_zip():
    z = os.path.join(DELIV, B.SOLUTIONS_ZIP)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for c in B.CASES:
            for fmt in B.FMTS:
                zf.write(c["solution"][fmt], arcname=os.path.basename(c["solution"][fmt]))
    return z

# ---------------------------------------------------------------- checks
def norm(s):
    return re.sub(r"\s+", " ", s.replace("­", "")).strip()

def check(fmt, path, offsets, links, rep):
    def ok(name, passed, detail=""):
        rep.append(dict(fmt=fmt, name=name, passed=bool(passed), detail=detail))
    doc = fitz.open(path)
    books = [fitz.open(c["book"][fmt]) for c in B.CASES]
    texts = [doc[i].get_text() for i in range(len(doc))]
    ok("Page count = 2 front pages + both case books", len(doc) == 2 + len(books[0]) + len(books[1]),
       f"{len(doc)} = 2 + {len(books[0])} + {len(books[1])}")
    ok("File is under 20 MB (Etsy limit per file)", os.path.getsize(path) < 20 * 1024 * 1024,
       f"{os.path.getsize(path) / 1024 / 1024:.2f} MB")
    # every case page is carried over unchanged
    same = all(norm(texts[offsets[k] + i]) == norm(bk[i].get_text()) for k, bk in enumerate(books) for i in range(len(bk)))
    ok("Both case books are included whole and in order (text of every page matches the source)", same)
    # no solutions
    hits = [(m_, i + 1) for i, t in enumerate(texts) for m_ in SOLUTION_MARKERS if m_ in t]
    ok("No solution content (epilogue, step-by-step, finalists table, elimination index, Envelope)", not hits, str(hits[:5]))
    for k, case in enumerate(B.CASES):
        K = case["report"]["answer"]; full = f"{K['first']} {K['last']}"
        pages = [i for i, t in enumerate(texts) if full in norm(t)]
        n = sum(norm(t).count(full) for t in texts)
        on_log = all("FIRST NAME" in texts[i] and offsets[k] <= i < offsets[k] + len(books[k]) for i in pages)
        row = any(re.search(rf"{C_time(K)}\s+{K['ticket']:04d}\s+{K['first']}\s+{K['last']}", norm(texts[i])) for i in pages)
        ok(f"{case['title']}: the killer’s name appears exactly once, on their own line of that case’s Visitor Log",
           n == 1 and on_log and row, f"{n} time(s), page(s) {[i + 1 for i in pages]}")
    front = norm(texts[0] + " " + texts[1])
    ok("Bundle cover and programme page don’t mention Halloween", "halloween" not in front.lower())
    ok("Bundle cover and programme page carry no killer names or Sealed Check numbers",
       not any(x in front for c in B.CASES for x in (c["report"]["answer"]["first"], c["report"]["answer"]["last"],
                                                       f"{c['report']['answer']['ticket']:04d}", c["report"]["seal"])))
    # links on the programme page
    got = [l for l in doc[1].get_links() if l["kind"] == fitz.LINK_GOTO]
    good = len(got) == len(links) and all(
        any(abs(g["from"].y0 - L["rect"][1]) < 1 and g["page"] == L["target"] for g in got) for L in links)
    land = all(norm(texts[L["target"]]) == norm(books[L["case"]][L["orig"]].get_text()) for L in links)
    ok("Programme page: one working link per section of both cases, each landing on that section",
       good and land, f"{len(got)} links for {len(links)} lines")
    # the cases' own links (contents pages, chapter lists, hint index) survive and point to the right page
    bad = []; total = 0
    for k, bk in enumerate(books):
        for i in range(len(bk)):
            src = [l for l in bk[i].get_links() if l["kind"] == fitz.LINK_GOTO]
            dst = [l for l in doc[offsets[k] + i].get_links() if l["kind"] == fitz.LINK_GOTO]
            total += len(src)
            if sorted(l["page"] + offsets[k] for l in src) != sorted(l["page"] for l in dst):
                bad.append(f"case {k + 1} p{i + 1}")
    ok("Every internal link of both case books still works and lands on the same page as in the case book",
       not bad and total > 0, f"{total} links checked" + (f"; wrong: {bad[:5]}" if bad else ""))
    # bookmarks
    toc = doc.get_toc()
    case_ok = True
    for k, bk in enumerate(books):
        mine = [t for t in toc if t[0] >= 2 and offsets[k] < t[2] <= offsets[k] + len(bk)]
        for lv, t, p in bk.get_toc():
            if not any(m_[1] == t and m_[2] == p + offsets[k] and m_[0] == lv + 1 for m_ in mine):
                case_ok = False
    in_range = all(1 <= t[2] <= len(doc) for t in toc)
    tops = [t[1] for t in toc if t[0] == 1]
    ok("Bookmarks: cover, programme, one bookmark per case, and every bookmark of both case books nested under it",
       case_ok and in_range and any(B.CASES[0]["title"] in t for t in tops) and any(B.CASES[1]["title"] in t for t in tops),
       f"{len(toc)} bookmarks, {len(tops)} top level")
    return doc

def C_time(K):
    return f"{K['entry'] // 60:02d}:{K['entry'] % 60:02d}"

def check_zip(z, rep):
    with zipfile.ZipFile(z) as zf:
        names = sorted(zf.namelist()); bad = zf.testzip()
    want = sorted(os.path.basename(c["solution"][f]) for c in B.CASES for f in B.FMTS)
    rep.append(dict(fmt="zip", name="SOLUTIONS ZIP holds the 6 solution files of both cases and is intact",
                    passed=names == want and bad is None, detail=", ".join(names)))
    ans = all(f"{c['report']['answer']['first']} {c['report']['answer']['last']}" in
              norm(" ".join(p.get_text() for p in fitz.open(c["solution"][f]))) for c in B.CASES for f in B.FMTS)
    rep.append(dict(fmt="zip", name="Each solution file names its case’s killer (the right Envelope for each case)",
                    passed=ans, detail=""))
    rep.append(dict(fmt="zip", name="SOLUTIONS ZIP is under 20 MB", passed=os.path.getsize(z) < 20 * 1024 * 1024,
                    detail=f"{os.path.getsize(z) / 1024 / 1024:.2f} MB"))

def main():
    register_fonts()
    if os.path.isdir(DELIV):
        shutil.rmtree(DELIV)
    os.makedirs(DELIV)
    rep = []; pages = {}
    for fmt in B.FMTS:
        out, offsets, links = build(fmt)
        doc = check(fmt, out, offsets, links, rep)
        pages[fmt] = len(doc)
    z = solutions_zip(); check_zip(z, rep)
    files = sorted(os.listdir(DELIV))
    rep.append(dict(fmt="all", name="Delivery folder has exactly 4 files (Etsy allows 5)", passed=len(files) == 4, detail=", ".join(files)))
    passed = sum(r["passed"] for r in rep)
    L = [f"# Bundle check: {B.NAME}", "", f"Result: **{passed} of {len(rep)} checks passed**", "",
         "| # | File | Check | Result | Detail |", "|---|---|---|---|---|"]
    for i, r in enumerate(rep, 1):
        L.append(f"| {i} | {r['fmt']} | {r['name']} | {'PASS' if r['passed'] else 'FAIL'} | {r['detail'].replace('|', '/')} |")
    L += ["", "## Files", ""] + [f"- delivery/{f} ({os.path.getsize(os.path.join(DELIV, f)) / 1024 / 1024:.2f} MB)" for f in files]
    L += ["", "## Page counts", ""] + [f"- {B.OUT_NAMES[f]}: {n} pages" for f, n in pages.items()]
    open(os.path.join(B.ROOT, "bundle_check.md"), "w").write("\n".join(L) + "\n")
    json.dump(dict(checks=rep, pages=pages, files=files), open(os.path.join(B.ROOT, "bundle_check.json"), "w"), indent=1)
    print(f"checks {passed}/{len(rep)}")
    for r in rep:
        if not r["passed"]:
            print("FAIL", r["fmt"], r["name"], r["detail"])
    return passed == len(rep)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
