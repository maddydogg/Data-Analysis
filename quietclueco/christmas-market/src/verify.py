"""Independent checks for Snowfall at Ember Square.

Reads the Visitor Log from data/visitor_log.csv (not from the generator's memory),
evaluates every clue, and returns a structured report. build.py also calls the PDF
checks after rendering.
"""
import csv, os, re, itertools
from fontTools.ttLib import TTFont
import case as C
import hints as H

HERE = os.path.dirname(os.path.abspath(__file__))
CLUE = {c["id"]: c for c in C.CLUES}

def load():
    rows = []
    with open(os.path.join(HERE, "data", "visitor_log.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(dict(entry=C.tmin(r["entry"]), ticket=int(r["ticket"]), first=r["first"],
                             last=r["last"], town=r["town"], gate=r["gate"], stall=int(r["stall"])))
    return rows

def survivors(rows, preds):
    return [r for r in rows if all(p(r) for p in preds)]

def name(r):
    return f"{r['first']} {r['last']}"

def check_all(rows):
    rep = {"checks": [], "facts": {}}
    def ok(name_, passed, detail=""):
        rep["checks"].append(dict(name=name_, passed=bool(passed), detail=detail))
        return passed

    K = C.KILLER
    std = [c["pred"] for c in C.CLUES]

    # ---- data integrity
    tickets = [r["ticket"] for r in rows]
    ok("Tickets 0001-6000, each exactly once", sorted(tickets) == list(range(1, C.N_VISITORS + 1)))
    names = [(r["first"], r["last"]) for r in rows]
    ok("Every full name is unique", len(set(names)) == len(names))
    ok("Names are letters only (no spaces, hyphens, apostrophes)",
       all(r["first"].isalpha() and r["last"].isalpha() for r in rows))
    ok("Entry times within opening hours 16:00-20:29",
       all(C.tmin(C.OPEN_FROM) <= r["entry"] <= C.tmin(C.LAST_ENTRY) for r in rows))
    ok("Towns, gates and stalls are valid",
       all(r["town"] in C.TOWNS and r["gate"] in C.GATES and 1 <= r["stall"] <= 36 for r in rows))
    ok("Log is sorted by entry time", all(a["entry"] <= b["entry"] for a, b in zip(rows, rows[1:])))

    # ---- 1. unique answer
    sol = survivors(rows, std)
    ok("Unique answer: all 18 clues together leave exactly one visitor",
       len(sol) == 1 and sol[0]["ticket"] == K["ticket"],
       f"survivors: {[name(r) + ' #%04d' % r['ticket'] for r in sol]}")
    rep["facts"]["answer"] = sol[0] if sol else None

    # ---- 2. every clue is needed
    need = {}
    for i, c in enumerate(C.CLUES):
        s = survivors(rows, std[:i] + std[i + 1:])
        need[c["id"]] = len(s)
    ok("Every clue is needed: removing any one leaves more than one visitor",
       all(v > 1 for v in need.values()),
       "; ".join(f"{C.CLUES[i]['label']} removed -> {need[c['id']]} left" for i, c in enumerate(C.CLUES)))
    rep["facts"]["necessity"] = need

    # ---- 3. robustness to misreadings
    alt_results = []
    for i, c in enumerate(C.CLUES):
        for label, alt in c["alts"]:
            s = survivors(rows, std[:i] + [alt] + std[i + 1:])
            alt_results.append(dict(clue=c["label"], reading=label, survivors=len(s),
                                    same=len(s) == 1 and s[0]["ticket"] == K["ticket"]))
    ok("Each alternative reading on its own gives the same single answer",
       all(a["same"] for a in alt_results),
       "; ".join(f"{a['clue']} [{a['reading']}] -> {a['survivors']}" for a in alt_results))
    # all combinations at once: proven by 'every other visitor fails some clue under every reading'
    def robust_fail(c, r):
        return not any(p(r) for p in [c["pred"]] + [a[1] for a in c["alts"]])
    def robust_pass(c, r):
        return all(p(r) for p in [c["pred"]] + [a[1] for a in c["alts"]])
    weak = [r for r in rows if r["ticket"] != K["ticket"] and not any(robust_fail(c, r) for c in C.CLUES)]
    kr = next(r for r in rows if r["ticket"] == K["ticket"])
    combos = 1
    for c in C.CLUES:
        combos *= 1 + len(c["alts"])
    ok(f"Every combination of readings ({combos} in total) gives the same answer",
       not weak and all(robust_pass(c, kr) for c in C.CLUES),
       "proof: the killer passes every clue under every reading, and each of the other 5,999 "
       "visitors fails at least one clue under every reading"
       + (f"; problem visitors: {[name(r) for r in weak][:10]}" if weak else ""))
    rep["facts"]["alts"] = alt_results
    rep["facts"]["combos"] = combos

    # ---- 4. finalists (fit every clue but one)
    fin = []
    for r in rows:
        fails = [c["id"] for c in C.CLUES if not c["pred"](r)]
        if len(fails) == 1:
            fin.append((r, fails[0]))
    per = {c["id"]: sum(1 for _, f in fin if f == c["id"]) for c in C.CLUES}
    ok("Every clue rules out at least one finalist (a visitor who fits all the other clues)",
       all(v >= 1 for v in per.values()), str(per))
    rep["facts"]["finalists"] = fin

    # ---- 5. walkthrough
    left = rows; walk = []
    for cid in C.WALK_ORDER:
        c = CLUE[cid]
        nxt = [r for r in left if c["pred"](r)]
        walk.append(dict(id=cid, label=c["label"], out=len(left) - len(nxt), left=len(nxt),
                         why=c.get("fact") or c["text"]))
        left = nxt
    ok("Walkthrough uses all 18 clues once and ends on the killer",
       sorted(C.WALK_ORDER) == sorted(CLUE) and len(left) == 1 and left[0]["ticket"] == K["ticket"])
    ok("No step in the walkthrough rules out zero visitors", all(w["out"] > 0 for w in walk),
       " -> ".join(f"{w['label']}: -{w['out']} ({w['left']})" for w in walk))
    rep["facts"]["walk"] = walk
    index = {}
    for r in rows:
        for cid in C.WALK_ORDER:
            if not CLUE[cid]["pred"](r):
                index[r["ticket"]] = cid; break
        else:
            index[r["ticket"]] = "KILLER"
    rep["facts"]["index"] = index

    # ---- 6. Sealed Check
    def seal(r):
        return (r["ticket"] * 7 + len(r["first"]) + len(r["last"])) % 1000
    ks = seal(kr)
    same = [r for r in rows if seal(r) == ks and r["ticket"] != K["ticket"]]
    fin_same = [r for r, _ in fin if seal(r) == ks]
    ok("Sealed Check: no finalist shares the killer's check number",
       not fin_same, f"check number {ks:03d}; other visitors with the same number: {len(same)} of 5,999")
    rep["facts"]["seal"] = f"{ks:03d}"

    # ---- 7. documents agree with the clue predicates
    punch = sorted(s for s, (_, g) in C.STALLS.items() if "punch" in g)
    ok("Evidence D: the stall directory's punch sellers match the clue", punch == C.PUNCH_STALLS, str(punch))
    rt = [ts for d, _, ts in C.COACHES if d == C.COACH_TIME]
    ok("Evidence E: exactly one coach leaves at 21:15, and its towns match the clue",
       len(rt) == 1 and rt[0] == C.ROUTE_TOWNS, str(rt))
    snow = [(C.tmin(a), C.tmin(b)) for a, b, _, s in C.WEATHER if s]
    cover = sorted(m for a, b, _, _ in C.WEATHER for m in range(C.tmin(a), C.tmin(b) + 1))
    ok("Evidence B: weather log periods are contiguous, non-overlapping and match the snow windows",
       snow == C.SNOW_WINDOWS and cover == list(range(C.tmin("16:00"), C.tmin("21:00") + 1)))
    ok("Evidence A: footbridges drawn at exactly the East and South gates",
       C.FOOTBRIDGE_GATES == {g for g, s in C.GATE_SIDE.items() if "footbridge" in s})
    ok("Killer's own story is consistent (entered before buying, bought punch at a punch stall, "
       "lives on the 21:15 route)",
       kr["entry"] <= C.tmin(C.RECEIPT_TIME) and kr["stall"] in C.PUNCH_STALLS and kr["town"] in C.ROUTE_TOWNS
       and C.lane_of(kr["stall"]) != "Holly Lane")

    # ---- 8. hints agree with the clues
    # Each level-3 hint is re-implemented here as its own rule, straight from the hint's
    # wording, and must keep exactly the same visitors as the clue.
    two_word = [t for t in C.TOWNS if " " in t]
    h3 = {
        "1": lambda r: len(r["first"]) not in (2, 4, 6, 8),
        "2": lambda r: len(r["last"]) >= len(r["first"]) + 1,
        "3": lambda r: ord(r["last"][0]) > ord(r["first"][0]),
        "4": lambda r: sum(r["last"].upper().count(v) for v in "AEIOU") == 2,
        "5": lambda r: r["first"][-1] not in "aeiouAEIOU",
        "6": lambda r: not (1 <= r["ticket"] <= 2499),
        "7": lambda r: sum(map(int, f"{r['ticket']:04d}")) % 2 == 1,
        "8": lambda r: C.tstr(r["entry"])[-1] not in "02468",
        "9": lambda r: r["town"] not in two_word,
        "10": lambda r: r["stall"] % 2 == 0,
        "11": lambda r: r["stall"] not in range(1, 10),
        "12": lambda r: "O" not in r["last"].upper(),
        "A": lambda r: r["gate"] not in ("North", "West"),
        "B": lambda r: any(a <= r["entry"] <= b for a, b in C.SNOW_WINDOWS),
        "C": lambda r: r["entry"] < C.tmin(C.RECEIPT_TIME) + 1,
        "D": lambda r: r["stall"] in [int(x) for x in re.findall(r"\d+", H.HINTS["D"][2].split("Only stalls")[1].split("sell")[0])],
        "E": lambda r: r["town"] in [t.strip() for t in H.HINTS["E"][2].split("Route 4:")[1].split(".")[0].split(",")],
        "F": lambda r: re.search(r"(.)\1", r["last"].lower()) is not None,
    }
    bad = []
    for cid, rule in h3.items():
        a = {r["ticket"] for r in rows if CLUE[cid]["pred"](r)}
        b = {r["ticket"] for r in rows if rule(r)}
        if a != b:
            bad.append(f"{cid}: {len(a ^ b)} visitors differ")
    ok("Level-3 hints keep exactly the same visitors as their clues (all 18)", not bad, "; ".join(bad))
    # factual claims inside level-2 hints and examples
    claims = [
        ("Ida 3, Enid 4, Clara 5, Martha 6 letters", [len(x) for x in ("Ida", "Enid", "Clara", "Martha")] == [3, 4, 5, 6]),
        ("Bennett has exactly two vowels", C.vowels("Bennett") == 2),
        ("Molly and Percy end in Y and pass clue 5", all(CLUE["5"]["pred"](dict(first=n)) for n in ("Molly", "Percy"))),
        ("ticket 0472 digits sum to 13", C.digit_sum(472) == 13),
        ("18:07 odd minutes, 18:40 even", C.tmin("18:07") % 2 == 1 and C.tmin("18:40") % 2 == 0),
        ("Oakes and Brook contain O", all("o" in n.lower() for n in ("Oakes", "Brook"))),
        ("Bell and Abbott have double letters; Garner repeats R but has no double letter", C.has_double("Bell") and C.has_double("Abbott") and not C.has_double("Garner") and C.has_repeat("Garner")),
        ("Ada Webb passes clue 3", CLUE["3"]["pred"](dict(first="Ada", last="Webb"))),
        ("Hint 9 names exactly the two-word towns", all(t in H.HINTS["9"][1] for t in two_word)),
        ("Hint A names the footbridge gates", all(g in H.HINTS["A"][2] for g in C.FOOTBRIDGE_GATES)),
        ("Hint B quotes both snow windows", all(C.tstr(a) in H.HINTS["B"][2] and C.tstr(b) in H.HINTS["B"][2] for a, b in C.SNOW_WINDOWS)),
        ("Hint C quotes the receipt time", C.RECEIPT_TIME in H.HINTS["C"][2]),
        ("Glossary example Garner is not a visitor surname (it is only an example)", "Garner" not in C.LAST),
    ]
    ok("Examples and facts quoted in hints and house rules are correct",
       all(v for _, v in claims), "; ".join(f"{k}: {'ok' if v else 'WRONG'}" for k, v in claims))
    spoil = [f"{cid} level {i + 1}" for cid, hs in H.HINTS.items() for i, h in enumerate(hs)
             if K["first"] in h or K["last"] in h or f"{K['ticket']}" in h]
    ok("No hint names the killer or their ticket", not spoil, ", ".join(spoil))

    # ---- 9. wording rules
    texts = [C.TITLE, C.SUBTITLE, C.TAGLINE] + C.INTRO + C.KNOWN_FACTS + [t for _, t in C.GLOSSARY] \
        + [t for _, t in C.HOW_TO_PLAY] + C.PIP_NOTE + C.STEWARD[1] + C.DRIVER[1] + C.EPILOGUE \
        + [c["text"] for c in C.CLUES] + [c.get("fact", "") for c in C.CLUES] \
        + [h for hs in H.HINTS.values() for h in hs]
    banned = ["Killer Isn", "Cluedo", "Traitors", "Agatha", "Christie", "Poirot", "Sherlock", "Holmes",
              "Harry Potter", "Hogwarts", "Marple", "Lantern Court", "Murder at the Christmas Market"]
    hit = [b for b in banned if any(b.lower() in t.lower() for t in texts)]
    ok("No borrowed brands or titles (Killer Isn't, Clue/Cluedo, Traitors, Christie, Sherlock, ...)",
       not hit, ", ".join(hit))
    ok("No famous-detective surnames in the name pool", not ({"Holmes", "Watson", "Marple", "Poirot", "Christie"} & set(C.LAST)))
    cmap = set(TTFont(os.path.join(HERE, "fonts", "Nunito-Regular.ttf")).getBestCmap())
    missing = sorted({ch for t in texts for ch in t if ord(ch) not in cmap and ch not in "\n"})
    ok("Every character in the text exists in the embedded fonts", not missing, repr(missing))
    return rep

def check_pdfs(rep, paths, rows):
    """Text-level checks on the rendered PDFs."""
    import pymupdf as fitz
    def ok(name_, passed, detail=""):
        rep["checks"].append(dict(name=name_, passed=bool(passed), detail=detail))
    K = C.KILLER
    norm = lambda s: re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()
    for fmt in ("letter", "a4", "ipad"):
        doc = fitz.open(paths[f"book_{fmt}"])
        text = norm(" ".join(p.get_text() for p in doc))
        miss = [c["label"] for c in C.CLUES if norm(c["text"]) not in text]
        ok(f"[{fmt}] every clue is printed word for word in the case book", not miss, ", ".join(miss))
        miss = [cid for cid, hs in H.HINTS.items() for h in hs if norm(h) not in text]
        ok(f"[{fmt}] all 54 hints are printed word for word", not miss, ", ".join(miss[:10]))
        ok(f"[{fmt}] the killer's name appears exactly once in the case book (their line in the log)",
           text.count(f"{K['first']} {K['last']}") == 1, f"{text.count(K['first'] + ' ' + K['last'])} times")
        # the visitor log pages: parse every row back and compare with the data
        got = []
        for p in doc:
            for ln in p.get_text().splitlines():
                pass
            words = p.get_text("words")
            lines = {}
            for w in words:
                lines.setdefault(round(w[3], 0), []).append(w)
            for yk, ws in lines.items():
                ws.sort(key=lambda w: w[0])
                toks = [w[4] for w in ws]
                if len(toks) >= 7 and re.fullmatch(r"\d\d:\d\d", toks[0]) and re.fullmatch(r"\d{4}", toks[1]):
                    got.append(toks)
        parsed = []
        for t in got:
            stall = t[-1]; gate = t[-2]; first, last = t[2], t[3]; town = " ".join(t[4:-2])
            parsed.append((t[0], t[1], first, last, town, gate, stall))
        want = [(C.tstr(r["entry"]), f"{r['ticket']:04d}", r["first"], r["last"], r["town"], r["gate"], str(r["stall"]))
                for r in rows]
        ok(f"[{fmt}] Visitor Log in the PDF matches the data line for line (6,000 rows)",
           parsed == want, f"parsed {len(parsed)} rows")
        ok(f"[{fmt}] the book has a clickable contents page and bookmarks",
           len(doc.get_toc()) >= 15 and any(l.get("kind") == fitz.LINK_GOTO or l.get("kind") == fitz.LINK_NAMED
                                             for l in doc[2].get_links()),
           f"{len(doc.get_toc())} bookmarks, {len(doc[2].get_links())} links on the contents page")
        fonts = {f[3] for p in doc for f in p.get_fonts()}
        emb = all(any(n in f for f in fonts) for n in ("Fraunces", "Nunito"))
        ok(f"[{fmt}] Fraunces and Nunito are embedded", emb, ", ".join(sorted(fonts)))
        rep.setdefault("pages", {})[f"book_{fmt}"] = len(doc)
        sdoc = fitz.open(paths[f"solution_{fmt}"])
        stext = norm(" ".join(p.get_text() for p in sdoc))
        ok(f"[{fmt}] solution file names the same killer the code found",
           f"{K['first']} {K['last']}" in stext and f"Ticket {K['ticket']:04d}" in stext)
        steps_ok = all(f"{w['left']:,}" in stext for w in rep["facts"]["walk"])
        ok(f"[{fmt}] solution walkthrough counts match the code", steps_ok)
        rep["pages"][f"solution_{fmt}"] = len(sdoc)
    return rep

def write_report(rep, path_md, path_json):
    import json
    passed = sum(c["passed"] for c in rep["checks"]); total = len(rep["checks"])
    K = rep["facts"]["answer"]
    L = [f"# Verification report: {C.TITLE}", "",
         f"Result: **{passed} of {total} checks passed**" + (" \u2014 ALL CLEAR" if passed == total else " \u2014 FAILURES BELOW"), "",
         f"Answer found by the code: **{K['first']} {K['last']}**, ticket {K['ticket']:04d}, {K['town']}, "
         f"entered {C.tstr(K['entry'])} via the {K['gate']} Gate, last stall {K['stall']}.", "",
         "## Checks", "", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(rep["checks"], 1):
        d = c["detail"].replace("|", "/")
        L.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {d} |")
    L += ["", "## Is every clue needed?", "",
          "Visitors left when all clues except the one named are applied (1 would mean the clue is redundant).", "",
          "| Clue removed | Visitors left |", "|---|---|"]
    for c in C.CLUES:
        L.append(f"| {c['label']} | {rep['facts']['necessity'][c['id']]} |")
    L += ["", "## Misreadings tested", "",
          "| Clue | Alternative reading | Visitors left | Same answer? |", "|---|---|---|---|"]
    for a in rep["facts"]["alts"]:
        L.append(f"| {a['clue']} | {a['reading']} | {a['survivors']} | {'yes' if a['same'] else 'NO'} |")
    L += ["", f"All {rep['facts']['combos']} combinations of these readings were also covered (see the proof in the checks table).",
          "", "## Walkthrough (elimination curve)", "", "| Step | Clue | Ruled out | Left |", "|---|---|---|---|",
          "| 0 | start | 0 | 6,000 |"]
    for i, w in enumerate(rep["facts"]["walk"], 1):
        L.append(f"| {i} | {w['label']} | {w['out']:,} | {w['left']:,} |")
    L += ["", "## Finalists (fit every clue but one)", "", "| Ticket | Visitor | Ruled out only by |", "|---|---|---|"]
    lab = {c["id"]: c["label"] for c in C.CLUES}
    for r, cid in sorted(rep["facts"]["finalists"], key=lambda x: C.WALK_ORDER.index(x[1])):
        L.append(f"| {r['ticket']:04d} | {r['first']} {r['last']} | {lab[cid]} |")
    if rep.get("pages"):
        L += ["", "## Page counts", ""] + [f"- {k}: {v}" for k, v in rep["pages"].items()]
    open(path_md, "w").write("\n".join(L) + "\n")
    slim = dict(checks=rep["checks"], answer=K, necessity=rep["facts"]["necessity"], alts=rep["facts"]["alts"],
                walk=[{k: v for k, v in w.items() if k != "why"} for w in rep["facts"]["walk"]],
                finalists=[dict(ticket=r["ticket"], name=f"{r['first']} {r['last']}", clue=c) for r, c in rep["facts"]["finalists"]],
                seal=rep["facts"]["seal"], pages=rep.get("pages"))
    json.dump(slim, open(path_json, "w"), indent=1)
    return passed, total
