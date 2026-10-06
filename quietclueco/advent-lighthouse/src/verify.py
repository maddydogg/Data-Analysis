"""Independent checks for The Keeper of Candleholm (advent calendar B).

Reads the Sound Book from data/sound_book.csv (not from the generator's memory), evaluates every
window, and returns a structured report. build.py also calls the PDF checks after rendering.
"""
import itertools, os, re
from fontTools.ttLib import TTFont
import case as C
import hints as H
import generate as G

HERE = os.path.dirname(os.path.abspath(__file__))
CLUE = {c["id"]: c for c in C.CLUES}

# ---------------------------------------------------------------- stop lists (whole words, any case)
# Borrowed brands and titles from the earlier QuietClueCo stop lists and from this brief.
STOP_BRANDS = ["Killer Isn", "Cluedo", "Clue", "Traitors", "Agatha", "Christie", "Poirot", "Sherlock", "Holmes",
               "Marple", "Knives Out", "Glass Onion", "Orient", "Express", "Home Alone", "Christmas Carol",
               "Scrooge", "Marley", "Cratchit", "Tiny Tim", "Fezziwig", "Miracle on 34th Street", "Harry Potter",
               "Hogwarts", "Frankenstein", "Dracula", "Hocus Pocus", "Sanderson", "Winifred", "Ursula", "Salem",
               "Polar Express", "Closing Time",
               # lighthouses, islands and stories this calendar must not borrow
               "The Lighthouse", "Light Between Oceans", "Flannan", "Eilean Mor", "Skerryvore", "Bell Rock",
               "Fastnet", "Eddystone", "Longships", "Bishop Rock", "Tuskar", "Pladda", "Muckle Flugga",
               "Ardnamurchan", "Corsewall", "Sumburgh", "Fair Isle", "Skerries", "Skerry Point", "Sker Point",
               "Grace Darling", "Ducat", "MacArthur", "Hesperus", "Lamp Out", "Lights Out", "Lamplighters",
               "Tide Ledger", "Bracken Light", "Lantern Below", "Ashwood", "Blackshore", "Bumble Bay",
               "Northern Lighthouse Board", "Trinity House", "Irish Lights"]
# Places and people of calendar A, cases 1-3 and the party game (whole words).
STOP_EARLIER = [
    # calendar A
    "Quillon", "Quillons", "Vellmouth", "Teodor", "Brann", "Linfoot", "Lark Emery", "Emery", "Pim Haskett",
    "Haskett", "Albie Crane", "Nell Varney", "Varney", "Sid Kettle", "Dot Fairley", "Fairley", "Augustin",
    "Pryce", "Haddow", "Verena", "Pennock", "Lantern", "Tanners", "Saltmarket", "Cathedral Close", "Bellfounders",
    "Lamplight Quay", "Bridgefoot", "Ferrygate", "Rope Walk", "Larchwood", "Old Mint", "Furnace Row",
    "Coldharbour", "Hollin", "Pinchgate", "Gasworks", "Vell", "Tramway Yard",
    # case 1
    "Ember Square", "Emberfield", "Ashcombe", "Brambleford", "Copperwell", "Dunmoor", "Elderbrook", "Foxhollow",
    "Greyhaven", "Hartwell", "Juniper Cross", "Kestrel Bay", "Marrowby", "Nettlefold", "Oakhurst", "Pennywick",
    "Sloe Green", "Ambrose", "Thorne", "Wren Ashdown", "Ashdown",
    # case 2
    "Corvenmoor", "Ashwick", "Barrowdene", "Duskwater", "Eelmarsh", "Fernhollow", "Gloamford", "Hagstone",
    "Kettlewick", "Mothwell", "Owlsgate", "Pikesmere", "Ravensholt", "Thistle Green", "Underfell", "Wychcombe",
    "Lucan", "Lucan Marsh", "Morwenna", "Juniper Vale",
    # case 3 and the party game
    "Morrowmere", "Ashcott", "Birchfold", "Brackenhythe", "Dunwold", "Fernley", "Hatherby", "Kittlewick",
    "Larkspur Green", "Nettlebarrow", "Owlhallow", "Pennyholt", "Rushcombe", "Thornby", "Wexley", "Yarrowby",
    "Hob Stones", "Barnaby", "Quell", "Hollis", "Drummond", "Bryony", "Fettle", "Meridew", "Tobias", "Hazel Thorne",
    "Jory", "Jory Pell", "Larkwell", "Lantern Supper", "Hearth Circle", "Heatherly", "Clementine", "Cordelia",
    "Isadora", "Quince", "Linnet", "Fairweather", "Marigold", "Quarrie", "Ned Quarrie", "Percival", "Hobb",
    "Rufus", "Hawthorn", "Silas", "Ashgrove", "Tamsin Rook"]
BANNED = STOP_BRANDS + STOP_EARLIER
# names that are also ordinary words: kept out of the name pools, allowed in running text
NAME_WORDS = ["Kettle", "Crane", "Dot", "Lark", "Nell", "Sid", "Pim", "Albie", "Wren", "Marsh", "Vale", "Reed",
              "Fenn", "Rook", "Wick", "Pell", "Hazel", "Rowena", "Ned", "Juniper", "Tate", "Thorne", "Rhea"]
FAMOUS = {"Holmes", "Watson", "Marple", "Poirot", "Christie", "Marlowe", "Spade", "Fletcher", "Drew", "Scrooge",
          "Cratchit", "Marley", "Fezziwig", "Kringle", "Claus", "Stevenson", "Darling", "Ducat", "Marshall",
          "MacArthur", "Moore", "Tulloch"}

def load():
    return G.load(os.path.join(HERE, "data"))

def survivors(rows, preds):
    return [r for r in rows if all(p(r) for p in preds)]

def name(r):
    return f"{r['first']} {r['last']}"

def readings(c):
    return [c["pred"]] + [a[1] for a in c["alts"]]

seal = G.seal

def all_texts():
    docs = []
    for d, v in C.DOCS.items():
        docs += [v.get("title", "")] + list(v.get("lines", [])) + [" ".join(x) for x in v.get("rows", [])]
    texts = ([C.TITLE, C.SUBTITLE, C.TAGLINE] + C.INTRO + C.KNOWN_FACTS + [t for _, t in C.GLOSSARY]
             + [t for _, t in C.HOW_TO_PLAY] + list(C.JOURNAL.values()) + docs + C.EPILOGUE + C.FINALE
             + [c["note"] for c in C.CLUES] + [c["fact"] for c in C.CLUES] + [c["window"] for c in C.CLUES]
             + [v[0] for v in C.LANDINGS.values()] + list(C.VILLAGES) + list(C.BOAT_NAMES.values())
             + [h for hs in H.HINTS.values() for h in hs]
             + [C.ISLAND, C.LIGHT, C.SOUND, C.PORT, C.OUTER, C.LOCH, C.SKERRIES, C.REGISTER, C.VICTIM,
                C.SUPERINTENDENT, C.SKIPPER, C.TALLYMAN, C.POSTMISTRESS, C.FISHERMEN, C.PILOT, C.BAKER, C.CAT,
                C.COASTGUARD, C.MARK])
    return texts

def stop_hits(texts, words=BANNED):
    return sorted({b for b in words if any(re.search(r"\b" + re.escape(b.lower()) + r"\b", t.lower()) for t in texts)})

def check_all(rows):
    rep = {"checks": [], "facts": {}}
    def ok(name_, passed, detail=""):
        rep["checks"].append(dict(name=name_, passed=bool(passed), detail=detail))
        return passed

    K = C.KILLER
    std = [c["pred"] for c in C.CLUES]
    kr = next(r for r in rows if r["tally"] == K["tally"])

    # ---- data integrity
    ok("Tallies 0001-2400, each exactly once", sorted(r["tally"] for r in rows) == list(range(1, C.N_ROWS + 1)))
    names = [(r["first"], r["last"]) for r in rows]
    ok("Every full name is unique", len(set(names)) == len(names))
    ok("Names are letters only (no spaces, hyphens, apostrophes)",
       all(r["first"].isalpha() and r["last"].isalpha() for r in rows))
    ok(f"Dates 1-23 December and times between {C.FIRST_BOAT} and {C.LAST_BOAT}",
       all(1 <= r["day"] <= 23 and C.tmin(C.FIRST_BOAT) <= r["time"] <= C.tmin(C.LAST_BOAT) for r in rows))
    ok("Villages, boats and landings are all on the chart",
       all(r["home"] in C.VILLAGES and r["boat"] in C.BOATS and r["landing"] in C.LANDINGS for r in rows))
    ok("The Sound Book is in date and time order", all((a["day"], a["time"]) <= (b["day"], b["time"]) for a, b in zip(rows, rows[1:])))
    per_day = {d: sum(r["day"] == d for r in rows) for d in C.DAYS}
    ok("Every day from 1 to 23 December has first crossings (most on the first days)",
       all(v > 0 for v in per_day.values()) and per_day[1] > per_day[2] > per_day[3] > max(per_day[d] for d in range(4, 24)),
       ", ".join(f"{d}: {v}" for d, v in per_day.items()))
    rep["facts"]["per_day"] = per_day

    # ---- 1. unique answer
    sol = survivors(rows, std)
    ok("Unique answer: windows 3–23 together leave exactly one line",
       len(sol) == 1 and sol[0]["tally"] == K["tally"], f"survivors: {[name(r) + ' #%04d' % r['tally'] for r in sol]}")
    rep["facts"]["answer"] = sol[0] if sol else None

    # ---- 2. every window is needed
    need = {}
    for i, c in enumerate(C.CLUES):
        need[c["id"]] = len(survivors(rows, std[:i] + std[i + 1:]))
    ok("Every window is needed: leaving any one out leaves more than one line",
       all(v > 1 for v in need.values()), "; ".join(f"{c['label']} left out -> {need[c['id']]} left" for c in C.CLUES))
    rep["facts"]["necessity"] = need

    # ---- 3. readings
    alt_results = []
    for i, c in enumerate(C.CLUES):
        for label, alt in c["alts"]:
            s = survivors(rows, std[:i] + [alt] + std[i + 1:])
            alt_results.append(dict(clue=c["label"], window=c["day"], word=c["word"], reading=label, survivors=len(s),
                                    killer_kept=alt(kr), same=len(s) == 1 and s[0]["tally"] == K["tally"]))
    ok(f"Each alternative reading on its own keeps the killer and gives the same single answer "
       f"({len(alt_results)} readings)", all(a["same"] and a["killer_kept"] for a in alt_results),
       "; ".join(f"{a['clue']} [{a['reading']}] -> {a['survivors']}" for a in alt_results))
    weak = [r for r in rows if r["tally"] != K["tally"] and not any(not any(p(r) for p in readings(c)) for c in C.CLUES)]
    combos = 1
    for c in C.CLUES:
        combos *= 1 + len(c["alts"])
    ok(f"Every combination of readings ({combos:,} in total) gives the same answer",
       not weak and all(all(p(kr) for p in readings(c)) for c in C.CLUES),
       "proof: the killer passes every window under every reading, and each of the other 2,399 lines fails at "
       "least one window under every reading" + (f"; problem lines: {[name(r) for r in weak][:10]}" if weak else ""))
    rep["facts"]["alts"] = alt_results
    rep["facts"]["combos"] = combos
    words = [a for a in alt_results if a["word"]]
    ok("Spatial and time words (already, through, higher up, near, between, rising, before, a.m./p.m.): every "
       f"reasonable reading keeps the killer and gives the same single answer ({len(words)} readings)",
       all(a["same"] and a["killer_kept"] for a in words),
       "; ".join(f"W{a['window']} [{a['reading']}] -> {a['survivors']}" for a in words))
    far = []
    for i, c in enumerate(C.CLUES):
        for label, pred in c["far"]:
            s = survivors(rows, std[:i] + [pred] + std[i + 1:])
            far.append(dict(window=c["day"], word=c["word"], reading=label, survivors=len(s), killer_kept=pred(kr)))
    ok(f"Far-fetched readings that would drop the killer leave nobody at all, so the slip shows at once "
       f"({len(far)} readings)", all(x["survivors"] == 0 and not x["killer_kept"] for x in far),
       "; ".join(f"W{x['window']} [{x['reading']}] -> {x['survivors']} left" for x in far))
    rep["facts"]["far"] = far

    # ---- 4. finalists (fit every window but one)
    fin = []
    for r in rows:
        fails = [c["id"] for c in C.CLUES if not c["pred"](r)]
        if len(fails) == 1:
            fin.append((r, fails[0]))
    per = {c["id"]: sum(1 for _, f in fin if f == c["id"]) for c in C.CLUES}
    ok("Every window rules out at least one finalist (a line that fits all the other windows)",
       all(v >= 1 for v in per.values()), str(per))
    rep["facts"]["finalists"] = fin

    # ---- 5. day-by-day curve
    left = rows; walk = []
    for c in C.CLUES:
        nxt = [r for r in left if c["pred"](r)]
        walk.append(dict(id=c["id"], day=c["day"], label=c["label"], out=len(left) - len(nxt), left=len(nxt), why=c["fact"]))
        left = nxt
    ok("Calendar order uses all 21 windows once and ends on the killer on Day 23",
       len(walk) == 21 and len(left) == 1 and left[0]["tally"] == K["tally"])
    ok("Every day from 3 to 23 rules out at least one line", all(w["out"] > 0 for w in walk),
       " -> ".join(f"D{w['day']}: -{w['out']} ({w['left']})" for w in walk))
    lft = {w["day"]: w["left"] for w in walk}
    ok("The bulk goes on Days 3–6, then 1–3 a day is typical",
       sum(w["out"] for w in walk if w["day"] <= 6) >= 0.95 * (C.N_ROWS - 1)
       and sum(1 for w in walk if w["day"] >= 7 and w["out"] <= 3) >= 12,
       f"Days 3–6 rule out {sum(w['out'] for w in walk if w['day'] <= 6):,}; days 7–23: "
       + ", ".join(str(w["out"]) for w in walk if w["day"] >= 7))
    ok("The ending stays open: at least 7 lines after Day 19, 5 after Day 20, 3 after Day 21 and 2 after Day 22",
       lft[19] >= 7 and lft[20] >= 5 and lft[21] >= 3 and lft[22] >= 2,
       f"after Day 19: {lft[19]}, Day 20: {lft[20]}, Day 21: {lft[21]}, Day 22: {lft[22]}, Day 23: {lft[23]}")
    rep["facts"]["walk"] = walk
    rep["facts"]["checkpoints"] = {d: lft[d] for d in C.CHECKPOINTS}
    index = {}
    for r in rows:
        for c in C.CLUES:
            if not c["pred"](r):
                index[r["tally"]] = c["id"]; break
        else:
            index[r["tally"]] = "KILLER"
    rep["facts"]["index"] = index
    chap = {}
    for d in C.CHECKPOINTS:
        alive = {r["day"] for r in rows if all(c["pred"](r) for c in C.CLUES if c["day"] <= d)}
        chap[d] = [x for x in C.DAYS if x not in alive]
    rep["facts"]["empty_chapters"] = chap

    # ---- 6. Sealed Check
    ks = seal(kr)
    fin_same = [r for r, _ in fin if seal(r) == ks]
    same = [r for r in rows if seal(r) == ks and r["tally"] != K["tally"]]
    ok("Sealed Check: no finalist shares the killer's check number", not fin_same,
       f"check number {ks:03d}; other lines with the same number: {len(same)} of 2,399")
    rep["facts"]["seal"] = f"{ks:03d}"

    # ---- 7. the papers agree with the clue predicates
    D = C.DOCS; J = C.JOURNAL
    dtext = {d: " ".join([v.get("title", "")] + list(v.get("lines", [])) + [" ".join(x) for x in v.get("rows", [])])
             for d, v in D.items()}
    ok("Window 3: the Harbour Trust rules say a tally is given on the first crossing and only the first crossing "
       "is written in", "first crossing" in dtext[3] and "not written in again" in dtext[3] and "tally already" in J[3])
    ok("Window 4: the passages note puts exactly the Mail Boat and the fishing boats in the Inner Passage, and the "
       "witness names no boat", "Mail Boat and the fishing boats" in dtext[4] and C.INNER == {"Mail", "Fishing"}
       and not any(b in J[4] for b in ("Mail", "Tender", "Pilot", "fishing")))
    ok("Window 5: the loch landings are listed in order from the mouth, the Narrows Slip is at the Narrows, and the "
       "loch turns south above it (so the chart reading differs from the route reading)",
       [int(x) for x in re.findall(r"(\d+) [A-Z]", D[5]["lines"][0])] == C.LOCH_ORDER
       and [n for n in C.LANDINGS if C.north_of_narrows(n)] != [n for n in C.LANDINGS if C.above_narrows(n)])
    ok("Window 6: the range note lists exactly the villages inside the circle, and Skellan sits on it",
       all(v in D[6]["lines"][1] for v in H.IN_RANGE) and abs(C.dist_light("Skellan") - C.RANGE) < 0.01
       and all(C.dist_light(v) < C.RANGE - 0.4 or C.dist_light(v) > C.RANGE + 0.4 for v in C.HOMES if v != "Skellan"))
    ok("Window 7: the code book page prints the whole alphabet, and the killer's initial starts with a dash",
       all(f"{k} {v}" in dtext[7] for k, v in C.MORSE.items()) and C.MORSE[K["last"][0]].startswith("–"))
    ok("Window 10: the tide table prints the same times the clue uses (first week)",
       all(f"{k} {C.tstr(m)}" in dtext[10] for d in range(1, 8) for m, k in C.tide_events(d)))
    ok("Window 11: the coast note lists the open-coast villages in order from north to south",
       "Bayle, Port Tolland, Carrowby, Lannagh, Selkie Ness" in dtext[11] and "Gannet Head, the mouth of Loch" in dtext[11])
    ok("Window 12: the waybill names exactly the parcel sheds and the letter boxes",
       all(str(n) in D[12]["lines"][0] for n in C.PARCEL_SHEDS) and all(str(n) in D[12]["lines"][1] for n in C.POST_BOXES))
    ok("Window 16: the almanac prints lighting-up times in a.m./p.m. that match the clue",
       all(C.ampm(C.LIGHTING[d]) in dtext[16] for d in range(1, 8)) and "p.m." in dtext[16])
    ok("Window 20: the tally metals note matches the clue (copper 0801–1600)", "Copper: 0801 to 1600" in dtext[20])
    ok("Killer’s own story is consistent with every paper",
       kr["day"] == 2 and kr["boat"] == "Mail" and kr["landing"] in C.PARCEL_SHEDS and C.above_narrows(kr["landing"])
       and C.north_of_narrows(kr["landing"]) and C.rising(kr["day"], kr["time"]) and C.before_lighting(kr["day"], kr["time"])
       and C.LIGHTING[kr["day"]] - kr["time"] >= 60 and C.between_heads(kr["home"]) and C.in_range(kr["home"])
       and "13:38" in C.EPILOGUE[2] and "Ferrach Pier" in C.EPILOGUE[2] and "signing off with a G" in C.EPILOGUE[3] and C.landing_name(kr["landing"]) == "Ferrach Pier")
    ok("The killer’s times sit well inside every window (at least 15 minutes from any tide or lighting-up boundary)",
       all(abs(kr["time"] - m) >= 15 for m, _ in C.tide_events(kr["day"])) and C.LIGHTING[kr["day"]] - kr["time"] >= 15)

    # ---- 7b. the shortlist must not point at the answer
    pool = [r for r, _ in fin]
    attrs = {"boat": lambda r: r["boat"], "village": lambda r: r["home"], "landing": lambda r: r["landing"],
             "hour": lambda r: r["time"] // 60}
    spread = []; bad_attr = []
    for an, fn in attrs.items():
        cnt = {}
        for r in pool:
            cnt[fn(r)] = cnt.get(fn(r), 0) + 1
        kv = fn(kr); kc = cnt.get(kv, 0)
        other = max([v for k, v in cnt.items() if k != kv] or [0])
        top = max(cnt.values()) / len(pool)
        spread.append(f"{an}: killer's value shared by {kc - 1} of {len(pool) - 1} finalists, most common value "
                      f"{max(cnt.values())}/{len(pool)}")
        if not (kc >= 3 and kc <= other and top <= 0.5):
            bad_attr.append(an)
    ok("Finalists don't point at the answer: for boat, village, landing and hour the killer's value is shared by "
       "at least two finalists, is never the single most common value, and no value covers more than half the "
       "shortlist", not bad_attr, "; ".join(spread) + (f"; FAILS: {bad_attr}" if bad_attr else ""))
    names_f = [r["first"] for r in pool]; names_l = [r["last"] for r in pool]
    ok("Finalists all have different first names and different surnames",
       len(set(names_f)) == len(names_f) and len(set(names_l)) == len(names_l))
    rep["facts"]["spread"] = spread

    # ---- 8. hints agree with the clues (level 3 is re-read from its own words)
    h = {k: v[2] for k, v in H.HINTS.items()}
    def listed(text, after):
        part = text.split(after)[1].split(".")[0]
        return [t.strip() for t in re.split(r",| or | and ", part) if t.strip()]
    rise = {int(d): [(C.tmin(a), C.tmin(b)) for a, b in re.findall(r"(\d\d:\d\d)–(\d\d:\d\d)", seg)]
            for d, seg in re.findall(r"(\d+) December ([^;]+)", h["10"])}
    lights = {int(d): C.tmin(t) for t, d in re.findall(r"(\d\d:\d\d) on the (\d+)", h["16"])}
    h3 = {
        "3": lambda r: r["day"] <= max(int(x) for x in re.findall(r"(\d+), (\d+) or (\d+) December", h["3"])[0]),
        "4": lambda r: r["boat"] not in listed(h["4"], "whose boat is"),
        "5": lambda r: r["landing"] in [int(x) for x in listed(h["5"], "His landing is")],
        "6": lambda r: r["home"] in listed(h["6"], "His village is"),
        "7": lambda r: r["last"][0] in listed(h["7"], "The surname begins with"),
        "8": lambda r: "A" in r["first"].upper(),
        "9": lambda r: f"{r['tally']:04d}"[-1] not in "13579",
        "10": lambda r: r["day"] in rise and any(a < r["time"] < b for a, b in rise[r["day"]]),
        "11": lambda r: r["home"] in listed(h["11"], "His village is"),
        "12": lambda r: r["landing"] in [int(x) for x in listed(h["12"], "His landing is")],
        "13": lambda r: len(r["first"]) == 5,
        "14": lambda r: not (sum(map(int, f"{r['tally']:04d}")) <= 15),
        "15": lambda r: r["first"][-1] != r["last"][-1],
        "16": lambda r: r["day"] in lights and r["time"] < lights[r["day"]],
        "17": lambda r: not (r["first"][0].upper() <= r["last"][0].upper()),
        "18": lambda r: "0" not in f"{r['tally']:04d}",
        "19": lambda r: sum(ch in "AEIOU" for ch in r["last"].upper()) == 2,
        "20": lambda r: not (r["tally"] <= 800 or r["tally"] >= 1601),
        "21": lambda r: r["first"][-1].upper() not in "AEIOU",
        "22": lambda r: len(set(r["last"].upper())) == len(r["last"]),
        "23": lambda r: (len(r["first"]) + len(r["last"])) % 2 == 0,
    }
    bad = []
    for cid, rule in h3.items():
        # level-3 hints for the time windows are read on the lines still in after Window 3 (1-3 December)
        pool3 = [r for r in rows if r["day"] <= 3] if cid in ("10", "16") else rows
        a = {r["tally"] for r in pool3 if CLUE[cid]["pred"](r)}
        b = {r["tally"] for r in pool3 if rule(r)}
        if a != b:
            bad.append(f"{cid}: {len(a ^ b)} lines differ")
    ok("Level-3 hints keep exactly the same lines as their windows (all 21; the tide and lamp hints on 1–3 December, "
       "the only dates still in by then)", not bad, "; ".join(bad))
    P = lambda cid, **kw: CLUE[cid]["pred"](dict(dict(C.KILLER), **kw))
    claims = [
        ("G starts with a dash, A with a dot", C.MORSE["G"][0] == "–" and C.MORSE["A"][0] == "·"),
        ("Agnes and Clara contain an A", P("8", first="Agnes") and P("8", first="Clara")),
        ("0472 is even; 0+4+7+2 = 13 (not > 15); 1395 adds to 18", P("9", tally=472) and not P("14", tally=472)
         and P("14", tally=1395) and sum(map(int, "1395")) == 18),
        ("Moira, Grant and Morag have five letters; Ruth and Fergus don't", all(P("13", first=n) for n in ("Moira", "Grant", "Morag"))
         and not P("13", first="Ruth") and not P("13", first="Fergus")),
        ("Angus Ross ends on the same letter twice; Moira Bain doesn't", not P("15", first="Angus", last="Ross")
         and P("15", first="Moira", last="Bain")),
        ("3.46 p.m. is 15:46", C.ampm(C.tmin("15:46")) == "3.46 p.m."),
        ("Sadie Kerr fits Window 17; Ada Muir and Mary Muir don't", P("17", first="Sadie", last="Kerr")
         and not P("17", first="Ada", last="Muir") and not P("17", first="Mary", last="Muir")),
        ("0472 has a nought; 1395 hasn't", not P("18", tally=472) and P("18", tally=1395)),
        ("Moffat and Lindsay have two vowels; Ogilvie has four", P("19", last="Moffat") and P("19", last="Lindsay")
         and C.vowels("Ogilvie") == 4),
        ("Angus and Mary end on a consonant; Effie and Flora don't", P("21", first="Angus") and P("21", first="Mary")
         and not P("21", first="Effie") and not P("21", first="Flora")),
        ("Rennison, Laidlaw and Barclay repeat a letter; Munro doesn't", not P("22", last="Rennison") and not P("22", last="Laidlaw")
         and not P("22", last="Barclay") and P("22", last="Munro")),
        ("Rennison has three Ns (house rules)", "Rennison".upper().count("N") == 3),
        ("Iona Rae has 7 letters, odd", not P("23", first="Iona", last="Rae")),
        ("Tally 0472 digits add up to 13 (house rules)", sum(map(int, "0472")) == 13),
    ]
    ok("Examples and facts quoted in hints and house rules are correct",
       all(v for _, v in claims), "; ".join(f"{k}: {'ok' if v else 'WRONG'}" for k, v in claims))
    reg_names = {name(r) for r in rows}
    ex = ["Sadie Kerr", "Ada Muir", "Mary Muir", "Iona Rae", "Angus Ross", "Moira Bain"]
    ok("Names used as examples in hints are not in the Sound Book", not any(e in reg_names for e in ex),
       ", ".join(e for e in ex if e in reg_names))
    spoil = [f"{cid} level {i + 1}" for cid, hs in H.HINTS.items() for i, hh in enumerate(hs)
             if K["first"] in hh or K["last"] in hh or f"{K['tally']:04d}" in hh or "Ferrach" in hh or "Carrowby" == hh]
    ok("No hint names the killer, his tally or his landing on its own", not spoil, ", ".join(spoil))

    # ---- 9. wording rules
    texts = all_texts()
    rep["texts"] = texts
    hit = stop_hits(texts) + stop_hits(C.FIRST + C.LAST)
    ok("Stop list: no borrowed brands, titles, real lighthouses or islands, and no names or places from calendar A, "
       "cases 1–3 or the party game, in any text or name pool (whole words)", not hit, ", ".join(sorted(set(hit))))
    ok("The word “clue” is not used anywhere in the calendar (evidence / lead instead)",
       not any(re.search(r"\bclues?\b", t.lower()) for t in texts))
    pool_hits = sorted(set(C.FIRST + C.LAST) & (set(NAME_WORDS) | FAMOUS))
    ok("No famous-detective, Christmas-story, lighthouse-history or earlier-character names in the name pools",
       not pool_hits, ", ".join(pool_hits))
    people = [C.VICTIM, "Alma Treleaven", C.SKIPPER, C.TALLYMAN, "Hester Breck", "Drummock", C.PILOT, C.BAKER,
              C.COASTGUARD, "Bosun", "Nan Fairgrieve"]
    toks = {t for p in people for t in p.split()}
    ok("Story characters and the killer's own names are kept out of the random name pools",
       not (toks & set(C.FIRST + C.LAST)) and C.KILLER["first"] not in C.FIRST and C.KILLER["last"] not in C.LAST,
       ", ".join(sorted(toks & set(C.FIRST + C.LAST))))
    missing = {}
    for font, sample in (("Nunito-Regular", texts), ("Kalam-Regular", list(C.JOURNAL.values())),
                         ("CourierPrime-Regular", [dtext[d] for d in dtext]), ("Fraunces-SemiBold", [c["window"] for c in C.CLUES] + [C.TITLE])):
        cmap = set(TTFont(os.path.join(HERE, "fonts", font + ".ttf")).getBestCmap())
        m = sorted({ch for t in sample for ch in t if ord(ch) not in cmap and ch not in "\n"})
        if m:
            missing[font] = m
    ok("Every character in the text exists in the fonts that print it", not missing, repr(missing))
    return rep

def check_pdfs(rep, paths, rows):
    """Text-level checks on the rendered PDFs."""
    import pymupdf as fitz
    def ok(name_, passed, detail=""):
        rep["checks"].append(dict(name=name_, passed=bool(passed), detail=detail))
    K = C.KILLER
    norm = lambda s: re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()
    want = [(str(r["day"]), C.tstr(r["time"]), f"{r['tally']:04d}", r["first"], r["last"], r["home"], r["boat"],
             str(r["landing"])) for r in rows]
    for fmt in ("letter", "a4", "ipad"):
        doc = fitz.open(paths[f"book_{fmt}"])
        pages = [norm(p.get_text()) for p in doc]
        text = " ".join(pages)
        starts = {}
        for i, t in enumerate(pages):
            for d in range(1, 25):
                if f"WINDOW {d} OF 24" in t:
                    starts.setdefault(d, []).append(i)
        ok(f"[{fmt}] each of the 24 windows starts on its own page, in order",
           all(d in starts for d in range(1, 25)) and all(min(starts[d]) < min(starts[d + 1]) for d in range(1, 24))
           and all(sum(f"WINDOW {d} OF 24" in t for d in range(1, 25)) <= 1 for t in pages),
           f"first pages: {[min(starts[d]) + 1 for d in sorted(starts)]}")
        miss = [c["label"] for c in C.CLUES if norm(c["note"]) not in text]
        ok(f"[{fmt}] every window’s question is printed word for word", not miss, ", ".join(miss))
        miss = [d for d, v in C.JOURNAL.items() if norm(v) not in text]
        ok(f"[{fmt}] all 23 journal entries are printed word for word", not miss, str(miss))
        miss = [d for d, v in C.DOCS.items() for line in v.get("lines", []) if norm(line) not in text]
        miss += [d for d, v in C.DOCS.items() for row in v.get("rows", []) if not all(norm(x) in text for x in row)]
        ok(f"[{fmt}] every paper pinned to a window is printed word for word (the text a reader without pictures needs)",
           not miss, str(sorted(set(miss))))
        miss = [cid for cid, hs in H.HINTS.items() for hh in hs if norm(hh) not in text]
        ok(f"[{fmt}] all 63 hints are printed word for word", not miss, ", ".join(miss[:10]))
        ok(f"[{fmt}] the killer's name appears exactly once in the calendar (his line in the Sound Book)",
           text.count(f"{K['first']} {K['last']}") == 1, f"{text.count(K['first'] + ' ' + K['last'])} times")
        cps = all(f"{rep['facts']['checkpoints'][d]:,} lines" in text for d in C.CHECKPOINTS)
        ok(f"[{fmt}] check-ins on Windows 6, 12 and 18 print the counts the code found", cps, str(rep["facts"]["checkpoints"]))
        got = []
        for p in doc:
            lines = {}
            for w in p.get_text("words"):
                lines.setdefault(round(w[3], 0), []).append(w)
            for _, ws in lines.items():
                ws.sort(key=lambda w: w[0])
                t = [w[4] for w in ws]
                if len(t) >= 9 and re.fullmatch(r"\d{1,2}", t[0]) and t[1] == "Dec" and re.fullmatch(r"\d\d:\d\d", t[2]) \
                        and re.fullmatch(r"\d{4}", t[3]):
                    got.append((t[0], t[2], t[3], t[4], t[5], " ".join(t[6:-2]), t[-2], t[-1]))
        ok(f"[{fmt}] the Sound Book in the PDF matches the data line for line (2,400 lines)", got == want,
           f"parsed {len(got)} lines")
        ok(f"[{fmt}] the book has a clickable contents page and bookmarks", len(doc.get_toc()) >= 24,
           f"{len(doc.get_toc())} bookmarks")
        if fmt == "ipad":
            cal = next(i for i, t in enumerate(pages) if "TAP TODAY’S WINDOW" in t)
            targets = {l.get("page") for l in doc[cal].get_links() if l.get("kind") == fitz.LINK_GOTO}
            wins = {min(starts[d]) for d in range(1, 25)}
            ok("[ipad] the first page is the calendar: 24 tappable windows, each opening its own day",
               cal == 0 and wins <= targets and len(targets & wins) == 24,
               f"calendar on page {cal + 1}, {len(targets & wins)} window links (+ {len(targets - wins)} to the cover)")
            back = sum(1 for d in range(1, 25) if any(l.get("page") == cal for l in doc[min(starts[d])].get_links()))
            ok("[ipad] every window page links back to the calendar", back == 24, f"{back} of 24")
        else:
            ok(f"[{fmt}] set-up pages include the envelope template and day numbers 1–24",
               any("ENVELOPE TEMPLATE" in t for t in pages)
               and any("DAY NUMBERS 1 – 24" in t and all(f" {d} " in f" {t} " for d in range(1, 25)) for t in pages))
        fonts = {f[3] for p in doc for f in p.get_fonts()}
        ok(f"[{fmt}] Fraunces, Nunito and Kalam are embedded", all(any(n in f for f in fonts) for n in ("Fraunces", "Nunito", "Kalam")))
        rep.setdefault("pages", {})[f"book_{fmt}"] = len(doc)
        sdoc = fitz.open(paths[f"solution_{fmt}"])
        stext = norm(" ".join(p.get_text() for p in sdoc))
        ok(f"[{fmt}] solution file names the same killer the code found",
           f"{K['first']} {K['last']}" in stext and f"Tally {K['tally']:04d}" in stext)
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
         f"Answer found by the code: **{K['first']} {K['last']}**, tally {K['tally']:04d}, {K['home']}; first crossing "
         f"{K['day']} December at {C.tstr(K['time'])} on {C.BOAT_NAMES[K['boat']]}, put ashore at landing {K['landing']} "
         f"({C.landing_name(K['landing'])}).", "",
         "## Checks", "", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(rep["checks"], 1):
        L.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    L += ["", "## Day by day (the elimination curve)", "", "| Day | Window | Ruled out | Left |", "|---|---|---|---|",
          "| 2 | The Sound Book | 0 | 2,400 |"]
    for w in rep["facts"]["walk"]:
        L.append(f"| {w['day']} | {CLUE[w['id']]['window']} | {w['out']:,} | {w['left']:,} |")
    L += ["", "## Is every window needed?", "", "| Window left out | Lines left |", "|---|---|"]
    for c in C.CLUES:
        L.append(f"| {c['label']} | {rep['facts']['necessity'][c['id']]} |")
    L += ["", "## Readings tested", "", "| Window | Word | Reading | Lines left | Killer kept? | Same answer? |",
          "|---|---|---|---|---|---|"]
    for a in rep["facts"]["alts"]:
        L.append(f"| {a['window']} | {a['word'] or ''} | {a['reading']} | {a['survivors']} | "
                 f"{'yes' if a['killer_kept'] else 'no'} | {'yes' if a['same'] else 'NO'} |")
    L += ["", "## Far-fetched readings (they drop the killer, so they must leave nobody)", "",
          "| Window | Reading | Lines left |", "|---|---|---|"]
    for x in rep["facts"]["far"]:
        L.append(f"| {x['window']} | {x['reading']} | {x['survivors']} |")
    L += ["", "## Finalists (fit every window but one)", "", "| Tally | Traveller | Ruled out only by |", "|---|---|---|"]
    for r, cid in sorted(rep["facts"]["finalists"], key=lambda x: int(x[1])):
        L.append(f"| {r['tally']:04d} | {r['first']} {r['last']} | Window {cid} |")
    L += ["", "## Is the shortlist free of patterns?", ""] + [f"- {x}" for x in rep["facts"].get("spread", [])]
    if rep.get("pages"):
        L += ["", "## Page counts", ""] + [f"- {k}: {v}" for k, v in rep["pages"].items()]
    open(path_md, "w").write("\n".join(L) + "\n")
    slim = dict(checks=rep["checks"], answer=K, necessity=rep["facts"]["necessity"], alts=rep["facts"]["alts"],
                far=rep["facts"]["far"], checkpoints=rep["facts"]["checkpoints"],
                empty_chapters=rep["facts"]["empty_chapters"],
                walk=[{k: v for k, v in w.items() if k != "why"} for w in rep["facts"]["walk"]],
                finalists=[dict(tally=r["tally"], name=f"{r['first']} {r['last']}", clue=c) for r, c in rep["facts"]["finalists"]],
                seal=rep["facts"]["seal"], pages=rep.get("pages"), per_day=rep["facts"]["per_day"])
    json.dump(slim, open(path_json, "w"), indent=1)
    return passed, total

if __name__ == "__main__":
    rows = load()
    rep = check_all(rows)
    for c in rep["checks"]:
        print("PASS" if c["passed"] else "FAIL", "|", c["name"], "|", c["detail"][:400])
    print(rep["facts"]["checkpoints"], rep["facts"]["empty_chapters"])
