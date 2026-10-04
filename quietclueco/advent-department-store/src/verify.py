"""Independent checks for The Windows at Quillon's (advent calendar).

Reads the Lantern Register from data/lantern_register.csv (not from the generator's memory),
evaluates every window, and returns a structured report. build.py also calls the PDF checks
after rendering.
"""
import csv, os, re
from fontTools.ttLib import TTFont
import case as C
import hints as H

HERE = os.path.dirname(os.path.abspath(__file__))
CLUE = {c["id"]: c for c in C.CLUES}

# Borrowed brands and titles (whole-word, case-insensitive): earlier cases plus this brief.
STOP_PREVIOUS = ["Killer Isn", "Cluedo", "Traitors", "Agatha", "Christie", "Poirot", "Sherlock", "Holmes",
                 "Harry Potter", "Hogwarts", "Marple", "Frankenstein", "Shelley", "Dracula", "Karloff", "Igor",
                 "Universal", "Addams", "Hotel Transylvania", "Scooby", "Hocus Pocus", "Sanderson",
                 "Practical Magic", "Owens", "Sabrina", "Charmed", "Halliwell", "Wicked", "Elphaba", "Glinda",
                 "The Craft", "Quidditch", "Hermione", "Discworld", "Weatherwax", "Kiki", "Maleficent", "Ursula",
                 "Winifred", "Salem", "Moonfall"]
STOP_THIS = ["Clue", "Knives Out", "Glass Onion", "Orient Express", "Express", "Home Alone",
             "Miracle on 34th Street", "Macy", "Harrods", "Selfridges", "Selfridge", "Liberty", "Fortnum",
             "Bloomingdale", "Saks", "Nordstrom", "Hamleys", "Galeries Lafayette", "John Lewis", "Fenwick",
             "Christmas Carol", "Scrooge", "Marley", "Cratchit", "Tiny Tim", "Hellsing", "Cowboy Bebop",
             "Bebop", "Dragon Ball", "Detective Conan", "Conan", "Lupin", "Polar Express", "Closing Time",
             "Ashcombe", "Ember Square", "Wren", "Ambrose"]
BANNED = STOP_PREVIOUS + STOP_THIS

def load():
    rows = []
    with open(os.path.join(HERE, "data", "lantern_register.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(dict(entry=C.tmin(r["entry"]), ticket=int(r["ticket"]), first=r["first"],
                             last=r["last"], town=r["town"], gate=r["gate"], stall=int(r["stall"])))
    return rows

def survivors(rows, preds):
    return [r for r in rows if all(p(r) for p in preds)]

def name(r):
    return f"{r['first']} {r['last']}"

def readings(c):
    return [c["pred"]] + [a[1] for a in c["alts"]]

def seal(r):
    return (r["ticket"] * 7 + len(r["first"]) + len(r["last"])) % 1000

# Extra readings of the plans and the spatial words, beyond the alternatives the generator already
# guards against. "reasonable" readings must keep the killer and give the same single answer;
# "far-fetched" ones are listed so we can see what happens (ideally nothing is left, so the slip shows).
SPATIAL = [
    ("4", "straight / through", "reasonable", "‘straight across’ = only the door directly opposite the shelter (Tram)",
     lambda r: r["gate"] == "Tram"),
    ("4", "straight / through", "reasonable", "both routes, plus the Clock Door at the corner of the yard",
     lambda r: r["gate"] in C.TRAM_SIDE_WIDE),
    ("4", "opposite", "reasonable", "‘the shelter opposite the store’: any door on Tramway Yard or reached from it",
     lambda r: r["gate"] in C.TRAM_SIDE),
    ("4", "through", "far-fetched", "only ‘through the Winter Garden’ (ignoring ‘straight across’)",
     lambda r: r["gate"] == "Garden"),
    ("5", "higher / between floors", "reasonable", "everything above the Second Floor (official)",
     lambda r: C.above_toy_hall(r["stall"])),
    ("5", "higher / between floors", "reasonable", "half-landings are between floors, so they don’t count",
     lambda r: C.above_toy_hall(r["stall"], halves=False)),
    ("5", "higher / between floors", "reasonable", "the Roof Terrace is outdoors, so it doesn’t count",
     lambda r: C.above_toy_hall(r["stall"], roof=False)),
    ("5", "higher / between floors", "reasonable", "only full floors count: the Third Floor",
     lambda r: C.dept_level(r["stall"]) == "3"),
    ("5", "higher", "reasonable", "‘higher up’ taken loosely: the Second Floor itself counts too",
     lambda r: C.LEVEL_ORDER.index(C.dept_level(r["stall"])) >= C.LEVEL_ORDER.index("2")),
    ("5", "higher / between floors", "far-fetched", "only the very next level up (the Clock Gallery)",
     lambda r: C.dept_level(r["stall"]) == "CG"),
    ("6", "between", "reasonable", "stops strictly between Vell Bridge and Gasworks (official)",
     lambda r: C.tram_between(r["town"])),
    ("6", "between", "reasonable", "the two named stops included", lambda r: C.tram_between(r["town"], inclusive=True)),
    ("6", "between", "reasonable", "‘between’ read on the map, not along the route: the district on the straight "
     "line from Bridgefoot to Gasworks (Old Mint)", lambda r: r["town"] in ("Old Mint",)),
    ("6", "between", "reasonable", "‘between’ read on the map, generously: every district the straight line from "
     "Bridgefoot to Gasworks passes or grazes (Ferrygate, Old Mint, Pinchgate)",
     lambda r: r["town"] in ("Ferrygate", "Old Mint", "Pinchgate")),
    ("11", "next to", "reasonable", "shares a side with the park (official)", lambda r: C.touches_park(r["town"])),
    ("11", "next to", "reasonable", "a corner touch counts too", lambda r: C.touches_park(r["town"], corners=True)),
    ("16", "lower half / below", "reasonable", "minutes 15–45 (official)", lambda r: C.lower_half(r["entry"] % 60)),
    ("16", "lower half / below", "reasonable", "minutes 16–44 (hands on 3 or 9 left out)",
     lambda r: C.lower_half(r["entry"] % 60, edges=False)),
    ("16", "lower half / below", "reasonable", "pointing roughly down: minutes 20–40", lambda r: 20 <= r["entry"] % 60 <= 40),
    ("16", "lower half / below", "reasonable", "pointing straight down only: minutes 25–35", lambda r: 25 <= r["entry"] % 60 <= 35),
    ("10", "before / clocks", "reasonable", "the five minutes forgotten: 19:00 or earlier",
     lambda r: r["entry"] <= C.tmin(C.TREE_BY_GALLERY)),
    ("10", "before / clocks", "reasonable", "the five minutes subtracted twice: 18:50 or earlier",
     lambda r: r["entry"] <= C.TREE_REAL - 5),
]

def check_all(rows):
    rep = {"checks": [], "facts": {}}
    def ok(name_, passed, detail=""):
        rep["checks"].append(dict(name=name_, passed=bool(passed), detail=detail))
        return passed

    K = C.KILLER
    std = [c["pred"] for c in C.CLUES]
    kr = next(r for r in rows if r["ticket"] == K["ticket"])

    # ---- data integrity
    ok("Passes 0001-2400, each exactly once", sorted(r["ticket"] for r in rows) == list(range(1, C.N_PASSES + 1)))
    names = [(r["first"], r["last"]) for r in rows]
    ok("Every full name is unique", len(set(names)) == len(names))
    ok("Names are letters only (no spaces, hyphens, apostrophes)",
       all(r["first"].isalpha() and r["last"].isalpha() for r in rows))
    ok(f"Times in within opening hours {C.OPEN_FROM}-{C.LAST_ENTRY}",
       all(C.tmin(C.OPEN_FROM) <= r["entry"] <= C.tmin(C.LAST_ENTRY) for r in rows))
    ok("Districts, doors and tills are valid",
       all(r["town"] in C.DISTRICTS and r["gate"] in C.DOORS and r["stall"] in C.DEPTS for r in rows))
    ok("Register is sorted by time in", all(a["entry"] <= b["entry"] for a, b in zip(rows, rows[1:])))

    # ---- 1. unique answer
    sol = survivors(rows, std)
    ok("Unique answer: windows 3–23 together leave exactly one pass",
       len(sol) == 1 and sol[0]["ticket"] == K["ticket"], f"survivors: {[name(r) + ' #%04d' % r['ticket'] for r in sol]}")
    rep["facts"]["answer"] = sol[0] if sol else None

    # ---- 2. every window is needed
    need = {}
    for i, c in enumerate(C.CLUES):
        need[c["id"]] = len(survivors(rows, std[:i] + std[i + 1:]))
    ok("Every window is needed: leaving any one out leaves more than one pass",
       all(v > 1 for v in need.values()),
       "; ".join(f"{c['label']} left out -> {need[c['id']]} left" for c in C.CLUES))
    rep["facts"]["necessity"] = need

    # ---- 3. robustness to misreadings
    alt_results = []
    for i, c in enumerate(C.CLUES):
        for label, alt in c["alts"]:
            s = survivors(rows, std[:i] + [alt] + std[i + 1:])
            alt_results.append(dict(clue=c["label"], reading=label, survivors=len(s),
                                    same=len(s) == 1 and s[0]["ticket"] == K["ticket"]))
    ok(f"Each alternative reading on its own gives the same single answer ({len(alt_results)} readings)",
       all(a["same"] for a in alt_results),
       "; ".join(f"{a['clue']} [{a['reading']}] -> {a['survivors']}" for a in alt_results))
    weak = [r for r in rows if r["ticket"] != K["ticket"]
            and not any(not any(p(r) for p in readings(c)) for c in C.CLUES)]
    combos = 1
    for c in C.CLUES:
        combos *= 1 + len(c["alts"])
    ok(f"Every combination of readings ({combos:,} in total) gives the same answer",
       not weak and all(all(p(kr) for p in readings(c)) for c in C.CLUES),
       "proof: the killer passes every window under every reading, and each of the other 2,399 passes "
       "fails at least one window under every reading" + (f"; problem passes: {[name(r) for r in weak][:10]}" if weak else ""))
    rep["facts"]["alts"] = alt_results
    rep["facts"]["combos"] = combos

    # ---- 3a. plans and spatial words
    sp = []
    for cid, word, kind, label, pred in SPATIAL:
        i = [c["id"] for c in C.CLUES].index(cid)
        s = survivors(rows, std[:i] + [pred] + std[i + 1:])
        sp.append(dict(window=int(cid), word=word, kind=kind, reading=label, survivors=len(s),
                       killer_kept=pred(kr), same=len(s) == 1 and s[0]["ticket"] == K["ticket"]))
    reas = [x for x in sp if x["kind"] == "reasonable"]
    ok(f"Plans and spatial words (straight, through, opposite, higher, between floors, between, next to, lower "
       f"half): all {len(reas)} reasonable readings keep the killer and give the same single answer",
       all(x["killer_kept"] and x["same"] for x in reas),
       "; ".join(f"W{x['window']} [{x['reading']}] -> {x['survivors']}" for x in reas))
    far = [x for x in sp if x["kind"] == "far-fetched"]
    ok("Far-fetched readings that would drop the killer leave nobody at all, so the slip shows at once",
       all(x["survivors"] == 0 or x["same"] for x in far),
       "; ".join(f"W{x['window']} [{x['reading']}] -> {x['survivors']} left" for x in far))
    rep["facts"]["spatial"] = sp

    # ---- 4. finalists (fit every window but one)
    fin = []
    for r in rows:
        fails = [c["id"] for c in C.CLUES if not c["pred"](r)]
        if len(fails) == 1:
            fin.append((r, fails[0]))
    per = {c["id"]: sum(1 for _, f in fin if f == c["id"]) for c in C.CLUES}
    ok("Every window rules out at least one finalist (a pass that fits all the other windows)",
       all(v >= 1 for v in per.values()), str(per))
    rep["facts"]["finalists"] = fin

    # ---- 5. day-by-day curve
    left = rows; walk = []
    for c in C.CLUES:
        nxt = [r for r in left if c["pred"](r)]
        walk.append(dict(id=c["id"], day=c["day"], label=c["label"], out=len(left) - len(nxt), left=len(nxt),
                         why=c["fact"]))
        left = nxt
    ok("Calendar order uses all 21 windows once and ends on the killer on Day 23",
       len(walk) == 21 and len(left) == 1 and left[0]["ticket"] == K["ticket"])
    ok("Every day from 3 to 23 rules out at least one pass", all(w["out"] > 0 for w in walk),
       " -> ".join(f"D{w['day']}: -{w['out']} ({w['left']})" for w in walk))
    lft = {w["day"]: w["left"] for w in walk}
    ok("The ending stays open: at least 7 passes after Day 19, 5 after Day 20, 3 after Day 21 and 2 after Day 22",
       lft[19] >= 7 and lft[20] >= 5 and lft[21] >= 3 and lft[22] >= 2,
       f"after Day 19: {lft[19]}, Day 20: {lft[20]}, Day 21: {lft[21]}, Day 22: {lft[22]}, Day 23: {lft[23]}")
    rep["facts"]["walk"] = walk
    rep["facts"]["checkpoints"] = {d: lft[d] for d in C.CHECKPOINTS}
    index = {}
    for r in rows:
        for c in C.CLUES:
            if not c["pred"](r):
                index[r["ticket"]] = c["id"]; break
        else:
            index[r["ticket"]] = "KILLER"
    rep["facts"]["index"] = index
    # chapters fully crossed out at each checkpoint (whole hours with no pass left)
    chap = {}
    for d in C.CHECKPOINTS:
        alive = {r["entry"] // 60 for r in rows if all(c["pred"](r) for c in C.CLUES if c["day"] <= d)}
        allh = sorted({r["entry"] // 60 for r in rows})
        chap[d] = [h for h in allh if h not in alive]
    rep["facts"]["empty_chapters"] = chap

    # ---- 6. Sealed Check
    ks = seal(kr)
    fin_same = [r for r, _ in fin if seal(r) == ks]
    same = [r for r in rows if seal(r) == ks and r["ticket"] != K["ticket"]]
    ok("Sealed Check: no finalist shares the killer's check number", not fin_same,
       f"check number {ks:03d}; other passes with the same number: {len(same)} of 2,399")
    rep["facts"]["seal"] = f"{ks:03d}"

    # ---- 7. documents agree with the clue predicates
    dtext = {d: " ".join([v.get("title", "")] + [x for kv in v.get("lines", []) for x in kv]
                         + list(v.get("statement", ("", ""))) + [v.get("extra", "")]) for d, v in C.DOCS.items()}
    ok("Window 3: the band programme prints exactly the three sets in the clue",
       all(f"{a} – {b}" in dtext[3] for a, b in C.BAND_SETS) and dtext[3].count("set") == 3)
    ok("Window 4: the newsvendor gives both routes and names no door",
       "straight across" in dtext[4] and "through the Winter Garden" in dtext[4]
       and not any(n in dtext[4] for n in C.DOOR_NAMES.values()))
    ok("Window 5: the Toy Hall is on the Second Floor, the Clock Gallery is a half-landing between the "
       "Second and Third Floors, and the lift doesn’t decide anything",
       C.dept_level(C.TOY_HALL) == "2" and C.LEVEL_ORDER.index("CG") == C.LEVEL_ORDER.index("2") + 1
       and C.LEVEL_ORDER.index("3") == C.LEVEL_ORDER.index("CG") + 1 and "lift" not in dtext[5].lower())
    ok("Window 6: the conductor names Vell Bridge and Gasworks, both on Route 7, and no district",
       "Vell Bridge" in dtext[6] and "Gasworks" in dtext[6] and C.TRAM_FROM in [s for s, _ in C.TRAM7]
       and not any(d in C.DOCS[6]["statement"][1] for d in C.DISTRICTS if d not in ("Gasworks",)))
    ok("Window 11: exactly four districts share a side with Vell Park",
       sorted(d for d in C.DISTRICTS if C.touches_park(d)) == sorted(H.PARK_IN) and len(H.PARK_IN) == 4)
    ok("Window 12: the store guide names exactly the striped-cup counters, and the trap (tins, powder) points "
       "to counters outside the clue",
       all(f"({n})" in dtext[12] for n in C.CUP_DEPTS) and "Food Hall, 1" in dtext[12] and "Sweet Shop, 3" in dtext[12]
       and all("hot cocoa" in " ".join(C.DEPTS[n][2]) for n in C.CUP_DEPTS))
    ok("Window 10: the store guide says the gallery clocks run five minutes fast, and the clockmaker says seven o’clock",
       "five minutes fast" in dtext[10] and "seven o’clock" in dtext[10] and C.TREE_REAL == C.tmin("18:55"))
    ok("Window 20: the printer’s note matches the clue (green 0001–1200, red 1201–2400)",
       "0001 to 1200" in dtext[20] and "1201 to 2400" in dtext[20])
    ok("Killer’s own story is consistent with every document",
       C.in_band(kr["entry"], excl=True) and kr["gate"] == "Tram" and C.dept_level(kr["stall"]) == "3"
       and kr["stall"] in C.CUP_DEPTS and C.tram_between(kr["town"]) and C.touches_park(kr["town"])
       and 20 <= kr["entry"] % 60 <= 40 and kr["entry"] < C.TREE_REAL)

    # ---- 7b. the shortlist must not point at the answer
    pool = [r for r, _ in fin]
    attrs = {"door": lambda r: r["gate"], "district": lambda r: r["town"], "last till": lambda r: r["stall"],
             "entry hour": lambda r: r["entry"] // 60}
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
    ok("Finalists don't point at the answer: for door, district, last till and entry hour the killer's value "
       "is shared by at least two finalists, is never the single most common value, and no value covers more "
       "than half the shortlist", not bad_attr, "; ".join(spread) + (f"; FAILS: {bad_attr}" if bad_attr else ""))
    names_f = [r["first"] for r in pool]; names_l = [r["last"] for r in pool]
    ok("Finalists all have different first names and different surnames",
       len(set(names_f)) == len(names_f) and len(set(names_l)) == len(names_l))
    rep["facts"]["spread"] = spread

    # ---- 8. hints agree with the clues
    def after(text, key):
        return text.split(key)[1]
    h3 = {
        "3": lambda r: any(C.tmin(a) <= r["entry"] <= C.tmin(b)
                           for a, b in re.findall(r"(\d\d:\d\d)–(\d\d:\d\d)", H.HINTS["3"][2])),
        "4": lambda r: r["gate"] not in re.findall(r"the (\w+) Door", H.HINTS["4"][2]),
        "5": lambda r: r["stall"] in [int(x) for x in re.findall(r"\d+", after(H.HINTS["5"][2], "last till is").split(".")[0])],
        "6": lambda r: r["town"] in [t.strip() for t in re.split(r",| and ", after(H.HINTS["6"][2], "are in").split(".")[0])],
        "7": lambda r: "R" in r["first"].upper(),
        "8": lambda r: not ("A" <= r["last"][0].upper() <= "M"),
        "9": lambda r: f"{r['ticket']:04d}"[-1] not in "02468",
        "10": lambda r: r["entry"] < C.tmin(re.search(r"came in at (\d\d:\d\d) or later", H.HINTS["10"][2]).group(1)),
        "11": lambda r: r["town"] in [t.strip() for t in re.split(r",| and ", after(H.HINTS["11"][2], "park are").split(".")[0])],
        "12": lambda r: r["stall"] in [int(x) for x in re.findall(r"\d+", after(H.HINTS["12"][2], "last till is").split(".")[0])],
        "13": lambda r: r["first"][-1].upper() in "AEIOU",
        "14": lambda r: not (sum(map(int, f"{r['ticket']:04d}")) <= 10),
        "15": lambda r: any(a == b for a, b in zip(r["last"].upper(), r["last"].upper()[1:])),
        "16": lambda r: not (r["entry"] % 60 <= 14 or r["entry"] % 60 >= 46),
        "17": lambda r: not (len(r["last"]) <= len(r["first"])),
        "18": lambda r: not any(f"{r['ticket']:04d}".count(d) > 1 for d in "0123456789"),
        "19": lambda r: len(r["first"]) == 6,
        "20": lambda r: not (r["ticket"] <= 1200),
        "21": lambda r: not (r["last"].upper().count("E") == 0 or r["last"].upper().count("E") >= 2),
        "22": lambda r: r["first"][0].upper() != r["last"][0].upper(),
        "23": lambda r: (len(r["first"]) + len(r["last"])) % 2 == 1,
    }
    bad = []
    for cid, rule in h3.items():
        a = {r["ticket"] for r in rows if CLUE[cid]["pred"](r)}
        b = {r["ticket"] for r in rows if rule(r)}
        if a != b:
            bad.append(f"{cid}: {len(a ^ b)} passes differ")
    ok("Level-3 hints keep exactly the same passes as their windows (all 21)", not bad, "; ".join(bad))
    P = lambda cid, **kw: CLUE[cid]["pred"](kw)
    claims = [
        ("Rita and Laura contain an R", P("7", first="Rita") and P("7", first="Laura")),
        ("0472 is even; 0+4+7+2 = 13 > 10; 2+3+1+0 = 6", not P("9", ticket=472) and P("14", ticket=472) and not P("14", ticket=2310)),
        ("Laura and Annie end on a vowel; Henry and Mabel don't", P("13", first="Laura") and P("13", first="Annie")
         and not P("13", first="Henry") and not P("13", first="Mabel")),
        ("Wallace and Carrier have a double letter; Hebden has two Es apart and no double", P("15", last="Wallace")
         and P("15", last="Carrier") and not P("15", last="Hebden") and C.repeat_letter("Hebden")),
        ("Ruth Barlow passes Window 17, Ruth Gale fails", P("17", first="Ruth", last="Barlow") and not P("17", first="Ruth", last="Gale")),
        ("4825 has four different digits; 1301 and 0402 don't", P("18", ticket=4825) and not P("18", ticket=1301) and not P("18", ticket=402)),
        ("Marina and Gertie have six letters; Clara and Harriet don't", P("19", first="Marina") and P("19", first="Gertie")
         and not P("19", first="Clara") and not P("19", first="Harriet")),
        ("Lacey has one E, Ellery two, Pollard none", P("21", last="Lacey") and not P("21", last="Ellery") and not P("21", last="Pollard")),
        ("Sally Sutton fails Window 22, Maria Pell passes", not P("22", first="Sally", last="Sutton") and P("22", first="Maria", last="Pell")),
        ("Mary Pell has an even total (8)", not P("23", first="Mary", last="Pell")),
        ("House rules: Ellery has two Es, Lacey one; 0472 digits add to 13", "Ellery" in C.GLOSSARY[2][1]
         and C.repeat_letter("Ellery") and sum(map(int, "0472")) == 13),
        ("Hint 16: a quarter past to a quarter to = minutes 15 to 45", C.lower_half(15) and C.lower_half(45) and not C.lower_half(46)),
    ]
    ok("Examples and facts quoted in hints and house rules are correct",
       all(v for _, v in claims), "; ".join(f"{k}: {'ok' if v else 'WRONG'}" for k, v in claims))
    reg_names = {name(r) for r in rows}
    ex = ["Sally Sutton", "Maria Pell", "Mary Pell", "Ruth Barlow", "Ruth Gale"]
    ok("Names used as examples in hints are not in the register", not any(e in reg_names for e in ex),
       ", ".join(e for e in ex if e in reg_names))
    spoil = [f"{cid} level {i + 1}" for cid, hs in H.HINTS.items() for i, h in enumerate(hs)
             if K["first"] in h or K["last"] in h or f"{K['ticket']:04d}" in h or str(K["ticket"]) in h]
    ok("No hint names the killer or their pass", not spoil, ", ".join(spoil))

    # ---- 9. wording rules
    texts = [C.TITLE, C.SUBTITLE, C.TAGLINE] + C.INTRO + C.KNOWN_FACTS + [t for _, t in C.GLOSSARY] \
        + [t for _, t in C.HOW_TO_PLAY] + C.LETTER + [C.LETTER_NOTE] + C.EPILOGUE + list(dtext.values()) \
        + [c["note"] for c in C.CLUES] + [c["fact"] for c in C.CLUES] + [c["window"] for c in C.CLUES] \
        + [v[0] for v in C.DEPTS.values()] + [x for v in C.DEPTS.values() for x in v[2]] + C.DISTRICTS \
        + [s for s, _ in C.TRAM7] + list(C.DOOR_NAMES.values()) + [h for hs in H.HINTS.values() for h in hs] \
        + [C.STORE, C.CITY, C.VICTIM, C.INSPECTOR, C.FINDER, C.NEWSVENDOR, C.DOORMAN, C.TOYCLERK, C.CONDUCTOR,
           C.WRAPPER, C.CLOCKMAKER, C.TEAROOM]
    rep["texts"] = texts
    hit = sorted({b for b in BANNED if any(re.search(r"\b" + re.escape(b.lower()) + r"\b", t.lower())
                                           for t in texts + C.FIRST + C.LAST)})
    ok("No borrowed brands, titles, real stores or names from the earlier cases in any text or name pool",
       not hit, ", ".join(hit))
    famous = {"Holmes", "Watson", "Marple", "Poirot", "Christie", "Marlowe", "Spade", "Fletcher", "Drew",
              "Scrooge", "Cratchit", "Marley", "Fezziwig", "Kringle", "Claus", "Selfridge", "Harrod", "Macy"}
    ok("No famous-detective, Christmas-story or store-founder surnames in the name pools",
       not (famous & set(C.LAST)), ", ".join(sorted(famous & set(C.LAST))))
    people = [C.VICTIM, C.FINDER, C.NEWSVENDOR, C.DOORMAN, C.TOYCLERK, C.CONDUCTOR, C.WRAPPER, C.CLOCKMAKER,
              "Rhea Linfoot", "Mrs Haddow"]
    ok("Story characters and the killer's own names are kept out of the random name pools",
       not any(p.split()[-1] in C.LAST or p.split()[0] in C.FIRST for p in people)
       and C.KILLER["first"] not in C.FIRST and C.KILLER["last"] not in C.LAST)
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
    want = [(C.tstr(r["entry"]), f"{r['ticket']:04d}", r["first"], r["last"], r["town"], r["gate"], str(r["stall"]))
            for r in rows]
    for fmt in ("letter", "a4", "ipad"):
        doc = fitz.open(paths[f"book_{fmt}"])
        pages = [norm(p.get_text()) for p in doc]
        text = " ".join(pages)
        # one window per page: every window title starts a page that carries no other window's title
        starts = {}
        for i, t in enumerate(pages):
            for d in range(1, 25):
                if f"WINDOW {d} OF 24" in t:
                    starts.setdefault(d, []).append(i)
        ok(f"[{fmt}] each of the 24 windows starts on its own page, in order",
           all(d in starts for d in range(1, 25)) and all(len({x for x in starts[d]}) >= 1 for d in starts)
           and all(min(starts[d]) < min(starts[d + 1]) for d in range(1, 24))
           and all(sum(f"WINDOW {d} OF 24" in t for d in range(1, 25)) <= 1 for t in pages),
           f"first pages: {[min(starts[d]) + 1 for d in sorted(starts)]}")
        miss = [c["label"] for c in C.CLUES if norm(c["note"]) not in text]
        ok(f"[{fmt}] every window’s question is printed word for word", not miss, ", ".join(miss))
        miss = [d for d, v in C.DOCS.items() if norm(v["statement"][1]) not in text]
        ok(f"[{fmt}] every window’s evidence text is printed word for word", not miss, str(miss))
        miss = [cid for cid, hs in H.HINTS.items() for h in hs if norm(h) not in text]
        ok(f"[{fmt}] all 63 hints are printed word for word", not miss, ", ".join(miss[:10]))
        ok(f"[{fmt}] the killer's name appears exactly once in the calendar (their line in the register)",
           text.count(f"{K['first']} {K['last']}") == 1, f"{text.count(K['first'] + ' ' + K['last'])} times")
        cps = all(f"{rep['facts']['checkpoints'][d]:,} passes" in text for d in C.CHECKPOINTS)
        ok(f"[{fmt}] check-ins on Windows 6, 12 and 18 print the counts the code found", cps,
           str(rep["facts"]["checkpoints"]))
        got = []
        for p in doc:
            lines = {}
            for w in p.get_text("words"):
                lines.setdefault(round(w[3], 0), []).append(w)
            for _, ws in lines.items():
                ws.sort(key=lambda w: w[0])
                toks = [w[4] for w in ws]
                if len(toks) >= 7 and re.fullmatch(r"\d\d:\d\d", toks[0]) and re.fullmatch(r"\d{4}", toks[1]):
                    got.append(toks)
        parsed = [(t[0], t[1], t[2], t[3], " ".join(t[4:-2]), t[-2], t[-1]) for t in got]
        ok(f"[{fmt}] Lantern Register in the PDF matches the data line for line (2,400 rows)",
           parsed == want, f"parsed {len(parsed)} rows")
        ok(f"[{fmt}] the book has a clickable contents page and bookmarks",
           len(doc.get_toc()) >= 24, f"{len(doc.get_toc())} bookmarks")
        if fmt == "ipad":
            cal = next(i for i, t in enumerate(pages) if "TAP TODAY’S WINDOW" in t)
            targets = {l.get("page") for l in doc[cal].get_links() if l.get("kind") == fitz.LINK_GOTO}
            ok("[ipad] the calendar page has 24 tappable windows, each opening its own day",
               len(targets) == 24 and all(min(starts[d]) in targets for d in range(1, 25)),
               f"{len(targets)} link targets")
            back = sum(1 for d in range(1, 25) if any(l.get("page") == cal for l in doc[min(starts[d])].get_links()))
            ok("[ipad] every window page links back to the calendar", back == 24, f"{back} of 24")
        else:
            ok(f"[{fmt}] set-up pages include the envelope template and day numbers 1–24",
               any("ENVELOPE TEMPLATE" in t for t in pages)
               and any("DAY NUMBERS 1 – 24" in t and all(f" {d} " in f" {t} " for d in range(1, 25)) for t in pages))
        fonts = {f[3] for p in doc for f in p.get_fonts()}
        ok(f"[{fmt}] Fraunces and Nunito are embedded", all(any(n in f for f in fonts) for n in ("Fraunces", "Nunito")))
        rep.setdefault("pages", {})[f"book_{fmt}"] = len(doc)
        sdoc = fitz.open(paths[f"solution_{fmt}"])
        stext = norm(" ".join(p.get_text() for p in sdoc))
        ok(f"[{fmt}] solution file names the same killer the code found",
           f"{K['first']} {K['last']}" in stext and f"Pass {K['ticket']:04d}" in stext)
        ok(f"[{fmt}] solution day-by-day counts match the code", all(f"{w['left']:,}" in stext for w in rep["facts"]["walk"]))
        ok(f"[{fmt}] the calendar itself has no solution pages",
           "What really happened" not in text and "Elimination index" not in text)
        rep["pages"][f"solution_{fmt}"] = len(sdoc)
    return rep

def write_report(rep, path_md, path_json):
    import json
    passed = sum(c["passed"] for c in rep["checks"]); total = len(rep["checks"])
    K = rep["facts"]["answer"]
    L = [f"# Verification report: {C.TITLE_PLAIN}", "",
         f"Result: **{passed} of {total} checks passed**" + (" — ALL CLEAR" if passed == total else " — FAILURES BELOW"), "",
         f"Answer found by the code: **{K['first']} {K['last']}**, pass {K['ticket']:04d}, {K['town']}, "
         f"in at {C.tstr(K['entry'])} by the {C.DOOR_NAMES[K['gate']]}, last till {K['stall']}.", "",
         "## Checks", "", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(rep["checks"], 1):
        L.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    L += ["", "## Day by day (the elimination curve)", "", "| Day | Window | Ruled out | Left |", "|---|---|---|---|",
          "| 2 | Lantern Register | 0 | 2,400 |"]
    for w in rep["facts"]["walk"]:
        L.append(f"| {w['day']} | {CLUE[w['id']]['window']} | {w['out']:,} | {w['left']:,} |")
    L += ["", "## Is every window needed?", "", "| Window left out | Passes left |", "|---|---|"]
    for c in C.CLUES:
        L.append(f"| {c['label']} | {rep['facts']['necessity'][c['id']]} |")
    L += ["", "## Misreadings tested", "", "| Window | Alternative reading | Passes left | Same answer? |", "|---|---|---|---|"]
    for a in rep["facts"]["alts"]:
        L.append(f"| {a['clue']} | {a['reading']} | {a['survivors']} | {'yes' if a['same'] else 'NO'} |")
    L += ["", "## Plans and spatial words", "", "| Window | Word | Kind | Reading | Passes left | Killer kept? |",
          "|---|---|---|---|---|---|"]
    for x in rep["facts"]["spatial"]:
        L.append(f"| {x['window']} | {x['word']} | {x['kind']} | {x['reading']} | {x['survivors']} | "
                 f"{'yes' if x['killer_kept'] else 'no'} |")
    L += ["", "## Finalists (fit every window but one)", "", "| Pass | Shopper | Ruled out only by |", "|---|---|---|"]
    for r, cid in sorted(rep["facts"]["finalists"], key=lambda x: int(x[1])):
        L.append(f"| {r['ticket']:04d} | {r['first']} {r['last']} | Window {cid} |")
    L += ["", "## Is the shortlist free of patterns?", ""] + [f"- {x}" for x in rep["facts"].get("spread", [])]
    if rep.get("pages"):
        L += ["", "## Page counts", ""] + [f"- {k}: {v}" for k, v in rep["pages"].items()]
    open(path_md, "w").write("\n".join(L) + "\n")
    slim = dict(checks=rep["checks"], answer=K, necessity=rep["facts"]["necessity"], alts=rep["facts"]["alts"],
                spatial=rep["facts"]["spatial"], checkpoints=rep["facts"]["checkpoints"],
                walk=[{k: v for k, v in w.items() if k != "why"} for w in rep["facts"]["walk"]],
                finalists=[dict(ticket=r["ticket"], name=f"{r['first']} {r['last']}", clue=c) for r, c in rep["facts"]["finalists"]],
                seal=rep["facts"]["seal"], pages=rep.get("pages"))
    json.dump(slim, open(path_json, "w"), indent=1)
    return passed, total

if __name__ == "__main__":
    rows = load()
    rep = check_all(rows)
    for c in rep["checks"]:
        print("PASS" if c["passed"] else "FAIL", "|", c["name"], "|", c["detail"][:400])
    print(rep["facts"]["checkpoints"], rep["facts"]["empty_chapters"])
