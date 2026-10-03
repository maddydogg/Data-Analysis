"""Independent checks for Full Moon over Morrowmere.

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

# Borrowed brands and titles. The first group is the stop list from case 2, the second the
# witch-film/book stop list for this case (whole-word match, case-insensitive).
STOP_LIST_CASE2 = ["Killer Isn", "Cluedo", "Traitors", "Agatha", "Christie", "Poirot", "Sherlock", "Holmes",
                   "Harry Potter", "Hogwarts", "Marple", "Frankenstein", "Shelley", "Dracula", "Karloff", "Igor",
                   "Universal", "Addams", "Hotel Transylvania", "Scooby", "Hollowfen", "Grimwood", "Witch Hunt",
                   "Autumn Pact", "Graveyard Game", "Monster Mash"]
STOP_LIST_CASE3 = ["Hocus Pocus", "Sanderson", "Practical Magic", "Owens", "Sabrina", "Charmed", "Halliwell",
                   "Wicked", "Elphaba", "Glinda", "Agatha All Along", "The Craft", "Harry Potter", "Hogwarts",
                   "Quidditch", "Hermione", "Discworld", "Weatherwax", "Kiki", "Maleficent", "Ursula", "Winifred",
                   "Salem"]
BANNED = STOP_LIST_CASE2 + STOP_LIST_CASE3 + ["Moonfall", "Hammer", "Wicca", "Wiccan", "witch trial", "burned"]

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
    ok(f"Entry times within opening hours {C.OPEN_FROM}-{C.LAST_ENTRY}",
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
    brews = sorted(k for k, (_, ing) in C.BREWS.items() if "rosehip" in ing and "star anise" in ing and "honey" not in ing)
    sellers = sorted(n for n, (_, g) in C.STALLS.items() if any(b in g for b in brews))
    ok("Evidence D: the Book of Brews and the stall directory give exactly the stalls in the clue "
       "(rosehip + star anise, no honey)", brews == C.DREG_BREWS and sellers == C.DREG_STALLS
       and [C.BREWS[b][0] for b in brews] == ["Hearth Chai", "Rosehip Ember"],
       f"brews {[C.BREWS[b][0] for b in brews]}; stalls {sellers}")
    trap = [C.BREWS[k][0] for k, (_, ing) in C.BREWS.items() if "rosehip" in ing and "star anise" in ing and "honey" in ing]
    ok("Evidence D has a trap: a brew with rosehip and star anise but also honey, sold elsewhere",
       bool(trap) and all(not any(k in g for k, v in C.BREWS.items() if v[0] in trap) or n not in C.DREG_STALLS
                          for n, (_, g) in C.STALLS.items()), ", ".join(trap))
    ok("Stall directory: every stall sells two different things, every brew is sold somewhere",
       all(len(set(g)) == 2 and all(x in C.GOODS for x in g) for _, g in C.STALLS.values())
       and all(any(b in g for _, g in C.STALLS.values()) for b in C.BREWS))
    rt = [ts for d, ts in C.ROUNDS if d == C.CARRIER_DAY]
    ok(f"Evidence E: exactly one {C.CARRIER_DAY} round, and its villages match the clue",
       len(rt) == 1 and rt[0] == C.ROUTE_TOWNS and all(t in C.TOWNS for _, ts in C.ROUNDS for t in ts), str(rt))
    vis = [(C.tmin(a), C.tmin(b)) for a, b, _, v in C.MOON_LOG if v]
    cover = sorted(m for a, b, _, _ in C.MOON_LOG for m in range(C.tmin(a), C.tmin(b) + 1))
    ok("Evidence B: moon-log periods are contiguous, non-overlapping and match the clear-moon windows",
       vis == C.MOON_WINDOWS and cover == list(range(C.tmin("16:00"), C.tmin("21:00") + 1))
       and all("Full moon" in sky for _, _, sky, v in C.MOON_LOG if v)
       and not any("Full moon" in sky for _, _, sky, v in C.MOON_LOG if not v))
    ok("Evidence C: the reading book has the crescent-pin reading at the clue's time, and its dregs "
       "match Evidence D", any(t == C.READING_TIME and "crescent" in who and "rosehip" in cup.lower()
                                and "star anise" in cup.lower() and "No honey" in cup for t, who, cup, _ in C.READINGS))
    ok("Evidence A: the Hob Stones lie on the paths to exactly Mill Stile and Orchard Gap",
       C.STONE_GATES == {"Mill", "Orchard"})
    ok("Evidence E/F: the ledger says Thursday and the margin note says the same letter twice",
       any("Thursday" in t for _, t, _ in C.LEDGER) and any("same curly letter" in t for t in C.LEDGER_NOTE))
    ok("Killer's own story is consistent (came in under the moon before the reading, bought a "
       "rosehip-and-anise brew, lives on the Thursday round)",
       kr["entry"] <= C.tmin(C.READING_TIME) and kr["stall"] in C.DREG_STALLS and kr["town"] in C.ROUTE_TOWNS
       and C.in_windows(kr["entry"], excl=True) and C.lane_of(kr["stall"]) != "Rowan Close"
       and "rosehip" in C.STALLS[kr["stall"]][1])

    # ---- 7b. the shortlist must not point at the answer
    pool = [r for r, _ in fin]
    attrs = {"entrance": lambda r: r["gate"], "village": lambda r: r["town"], "last stall": lambda r: r["stall"],
             "lane": lambda r: C.lane_of(r["stall"]), "entry hour": lambda r: r["entry"] // 60}
    spread = []; bad_attr = []
    for an, fn in attrs.items():
        cnt = {}
        for r in pool:
            cnt[fn(r)] = cnt.get(fn(r), 0) + 1
        kv = fn(kr); kc = cnt.get(kv, 0)
        other = max([v for k, v in cnt.items() if k != kv] or [0])
        top = max(cnt.values()) / len(pool)
        spread.append(f"{an}: killer's value shared by {kc - 1} of {len(pool) - 1} finalists, "
                      f"most common value {max(cnt.values())}/{len(pool)}")
        if not (kc >= 3 and kc <= other and top <= 0.5):
            bad_attr.append(an)
    ok("Finalists don't point at the answer: for entrance, village, last stall, lane and entry hour the "
       "killer's value is shared by at least two finalists, is never the single most common value, "
       "and no value covers more than half the shortlist", not bad_attr,
       "; ".join(spread) + (f"; FAILS: {bad_attr}" if bad_attr else ""))
    rep["facts"]["spread"] = spread

    # ---- 8. hints agree with the clues
    # Each level-3 hint is re-implemented here as its own rule, straight from the hint's
    # wording, and must keep exactly the same visitors as the clue.
    no_h = [t.strip() for t in H.HINTS["9"][2].split("from")[1].rstrip(".").split(",")]
    h3 = {
        "1": lambda r: r["first"][0] in "AEIOU",
        "2": lambda r: not (len(r["last"]) <= len(r["first"]) + 1),
        "3": lambda r: not (r["last"].upper().count("E") == 0 or r["last"].upper().count("E") >= 2),
        "4": lambda r: not (len(r["first"]) >= 6),
        "5": lambda r: not r["last"].upper().endswith("S"),
        "6": lambda r: f"{r['ticket']:04d}"[-1] not in "02468",
        "7": lambda r: not (f"{r['ticket']:04d}".count("0") == 0 or f"{r['ticket']:04d}".count("0") >= 2),
        "8": lambda r: not (int(C.tstr(r["entry"])[3:]) <= 9 or int(C.tstr(r["entry"])[3:]) >= 40),
        "9": lambda r: r["town"] not in no_h,
        "10": lambda r: r["stall"] not in range(1, 10),
        "11": lambda r: r["stall"] not in range(28, 37),
        "12": lambda r: "I" not in r["first"].upper(),
        "A": lambda r: r["gate"] not in [g.strip() for g in H.HINTS["A"][2].split("came in by")[1].rstrip(".").split(" or ")],
        "B": lambda r: any(C.tmin(a) <= r["entry"] <= C.tmin(b) for a, b in
                           re.findall(r"(\d\d:\d\d)–(\d\d:\d\d)", H.HINTS["B"][2])),
        "C": lambda r: r["entry"] < C.tmin(re.search(r"came in at (\d\d:\d\d) or later", H.HINTS["C"][2]).group(1)),
        "D": lambda r: r["stall"] in [int(x) for x in re.findall(r"\d+", H.HINTS["D"][2].split("sold at stalls")[1].split(".")[0])],
        "E": lambda r: r["town"] in [t.strip() for t in re.split(r",| and ", H.HINTS["E"][2].split("calls at")[1].split(".")[0])],
        "F": lambda r: r["first"][0] == r["last"][0],
    }
    bad = []
    for cid, rule in h3.items():
        a = {r["ticket"] for r in rows if CLUE[cid]["pred"](r)}
        b = {r["ticket"] for r in rows if rule(r)}
        if a != b:
            bad.append(f"{cid}: {len(a ^ b)} visitors differ")
    ok("Level-3 hints keep exactly the same visitors as their clues (all 18)", not bad, "; ".join(bad))
    P = lambda cid, **kw: CLUE[cid]["pred"](kw)
    claims = [
        ("Ada and Oscar pass clue 1; Bella and Yvonne fail", P("1", first="Ada") and P("1", first="Oscar") and not P("1", first="Bella") and not P("1", first="Yvonne")),
        ("Ruth Barlow passes clue 2 (4 and 6), Ruth Gale fails (4 and 4)", P("2", first="Ruth", last="Barlow") and not P("2", first="Ruth", last="Gale") and (len("Ruth"), len("Barlow"), len("Gale")) == (4, 6, 4)),
        ("Ellwood has one E (passes clue 3), Elmore two, Abbott none (both fail)", P("3", last="Ellwood") and not P("3", last="Elmore") and not P("3", last="Abbott")),
        ("Oscar (5) passes clue 4, Arthur (6) fails", P("4", first="Oscar") and not P("4", first="Arthur") and (len("Oscar"), len("Arthur")) == (5, 6)),
        ("Edwards fails clue 5, Abbott passes", not P("5", last="Edwards") and P("5", last="Abbott")),
        ("ticket 0472 is even (fails clue 6)", not P("6", ticket=472)),
        ("0472 has one zero (passes 7), 3006 two and 1234 none (fail)", P("7", ticket=472) and not P("7", ticket=3006) and not P("7", ticket=1234)),
        ("18:10 and 18:39 pass clue 8; 18:09 and 18:40 fail", all(P("8", entry=C.tmin(t)) for t in ("18:10", "18:39")) and not any(P("8", entry=C.tmin(t)) for t in ("18:09", "18:40"))),
        ("Hint 9 level 2 names exactly the villages with an H", all(t in H.HINTS["9"][1] for t in C.TOWNS if "H" in t.upper()) and not any(t in H.HINTS["9"][1] for t in C.TOWNS if "H" not in t.upper())),
        ("Ida and Elsie contain an I (fail clue 12)", not P("12", first="Ida") and not P("12", first="Elsie")),
        ("Rowan Close is stalls 28-36", [n for n in C.STALLS if C.lane_of(n) == "Rowan Close"] == list(range(28, 37))),
        ("Glossary: 18:07 has minutes 07; 0472/3006/1234 have 1/2/0 zeros", C.tmin("18:07") % 60 == 7 and [C.zeros(x) for x in (472, 3006, 1234)] == [1, 2, 0]),
        ("Hint D names the two brews from the Book of Brews", all(C.BREWS[b][0] in H.HINTS["D"][2] for b in C.DREG_BREWS)),
        ("Hint A names Mill Stile and Orchard Gap", all(C.GATE_NAMES[g] in H.HINTS["A"][2] for g in C.STONE_GATES)),
    ]
    ok("Examples and facts quoted in hints and house rules are correct",
       all(v for _, v in claims), "; ".join(f"{k}: {'ok' if v else 'WRONG'}" for k, v in claims))
    spoil = [f"{cid} level {i + 1}" for cid, hs in H.HINTS.items() for i, h in enumerate(hs)
             if K["first"] in h or K["last"] in h or f"{K['ticket']}" in h]
    ok("No hint names the killer or their ticket", not spoil, ", ".join(spoil))

    # ---- 9. wording rules
    texts = [C.TITLE, C.SUBTITLE, C.TAGLINE] + C.INTRO + C.KNOWN_FACTS + [t for _, t in C.GLOSSARY] \
        + [t for _, t in C.HOW_TO_PLAY] + C.NOTE + C.LEDGER_NOTE + C.EPILOGUE \
        + [x for row in C.READINGS for x in row] + [x for row in C.LEDGER for x in row] \
        + [n for n, _ in C.STALLS.values()] + list(C.GOODS.values()) + C.TOWNS + C.LANES \
        + [i for _, ing in C.BREWS.values() for i in ing] + [sky for _, _, sky, _ in C.MOON_LOG] \
        + list(C.GATE_NAMES.values()) + [C.VICTIM, C.INSPECTOR, C.WITNESS, C.READER, C.SHOPBOY, C.WATCHER, C.CARRIER, C.SHOP] \
        + [c["text"] for c in C.CLUES] + [c.get("fact", "") for c in C.CLUES] \
        + [h for hs in H.HINTS.values() for h in hs]
    rep["texts"] = texts
    banned = BANNED
    hit = sorted({b for b in banned if any(re.search(r"\b" + re.escape(b.lower()) + r"\b", t.lower()) for t in texts + C.FIRST + C.LAST)})
    ok("No borrowed brands, titles or famous witches in any text or name pool (" + ", ".join(STOP_LIST_CASE3) + " ...)",
       not hit, ", ".join(hit))
    famous = {"Holmes", "Watson", "Marple", "Poirot", "Christie", "Owens", "Sanderson", "Halliwell", "Weatherwax",
              "Spellman", "Ogg", "Nitt", "Aching", "Garlick", "Granger", "Potter"}
    famous_first = {"Hermione", "Glinda", "Elphaba", "Sabrina", "Agatha", "Winifred", "Ursula", "Maleficent", "Kiki",
                    "Hilda", "Zelda", "Phoebe", "Piper", "Prue", "Paige", "Minerva", "Sybill", "Sybil", "Luna",
                    "Tabitha", "Esme", "Magrat", "Tiffany", "Gillian", "Wanda", "Salem"}
    ok("No famous-detective or famous-witch names in the name pools",
       not (famous & set(C.LAST)) and not (famous_first & set(C.FIRST)),
       ", ".join(sorted((famous & set(C.LAST)) | (famous_first & set(C.FIRST)))))
    people = {C.VICTIM, C.WITNESS, C.SHOPBOY, C.CARRIER, C.WATCHER, "Hollis Drummond"}
    ok("Story characters and the killer's own names are kept out of the random name pools",
       not any(p.split()[-1] in C.LAST for p in people) and C.KILLER["first"] not in C.FIRST and C.KILLER["last"] not in C.LAST)
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
         f"entered {C.tstr(K['entry'])} by {C.GATE_NAMES[K['gate']]}, last stall {K['stall']}.", "",
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
    L += ["", "## Is the shortlist free of patterns?", ""] + [f"- {x}" for x in rep["facts"].get("spread", [])]
    if rep.get("pages"):
        L += ["", "## Page counts", ""] + [f"- {k}: {v}" for k, v in rep["pages"].items()]
    open(path_md, "w").write("\n".join(L) + "\n")
    slim = dict(checks=rep["checks"], answer=K, necessity=rep["facts"]["necessity"], alts=rep["facts"]["alts"],
                walk=[{k: v for k, v in w.items() if k != "why"} for w in rep["facts"]["walk"]],
                finalists=[dict(ticket=r["ticket"], name=f"{r['first']} {r['last']}", clue=c) for r, c in rep["facts"]["finalists"]],
                seal=rep["facts"]["seal"], pages=rep.get("pages"))
    json.dump(slim, open(path_json, "w"), indent=1)
    return passed, total
