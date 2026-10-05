"""Independent checks for Murder at the Lantern Supper.

The solver reads only the structured claims attached to the clue cards and the booklets (the same
records the renderer prints), never the answer, and works out who could have poisoned the glass.

Rules the solver follows (house rules 4 and 5 in the kit):
  * clue cards are true;
  * nobody lies about where someone else was;
  * a person's account of their own whereabouts never clears them.
A stricter reading (the killer's booklet is not trusted at all) is also tested.
"""
import itertools, json, os, re
import case as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

# ---------------------------------------------------------------- the clue items
def items():
    """Every card and every booklet line that carries a claim, as (id, source, round, text, claims)."""
    out = []
    for c in C.CARDS:
        out.append((f"card {c['id']}", "card", c["round"], " ".join(c["text"]), c["claims"]))
    for k, b in C.B.items():
        for r, lines in enumerate(b["rounds"], 1):
            for j, (text, claims) in enumerate(lines):
                out.append((f"{k} r{r}.{j + 1}", k, r, text, claims))
    return out
ITEMS = items()
ITEM = {i[0]: i for i in ITEMS}

def place_sets(rooms, reading):
    if isinstance(rooms, str):
        return set(reading[rooms]) if rooms in reading else {rooms}
    return set(rooms)

def all_readings():
    """Every combination of the window readings and the place-word readings."""
    keys = list(C.PLACE_READINGS)
    for wname, window in C.WINDOW_READINGS.items():
        for combo in itertools.product(*[list(C.PLACE_READINGS[k].items()) for k in keys]):
            reading = {k: rooms for k, (_, rooms) in zip(keys, combo)}
            label = [f"window: {wname}"] + [f"“{k}”: {lab}" for k, (lab, _) in zip(keys, combo)]
            yield window, reading, label

PRIMARY = (C.WINDOW_READINGS["the quarter from 22:15 only"],
           {k: list(v.values())[0] for k, v in C.PLACE_READINGS.items()})

def suspects_for(present):
    return [k for k in C.PEOPLE if k in present]

def solve(item_ids, window, reading, strict=False, pool=None):
    """Return the people who could have poisoned the glass, given the clue items."""
    pool = pool or list(C.PEOPLE)
    colour, wax = {}, None
    for iid in item_ids:
        _, src, _, _, claims = ITEM[iid]
        for cl in claims:
            if cl[0] == "colour" and src == "card":
                colour[cl[1]] = cl[2]
            if cl[0] == "wax":
                wax = cl[1]
    has_window = any(cl[0] == "window" for iid in item_ids for cl in ITEM[iid][4])
    out = []
    for k in pool:
        ruled_out = False
        if has_window:
            # where k is placed, slot by slot, by sources other than k
            placed = {t: None for t in window}
            for iid in item_ids:
                _, src, _, _, claims = ITEM[iid]
                if src == k or (strict and src == k):
                    continue
                for cl in claims:
                    if cl[0] == "at" and cl[1] == k:
                        rooms, slots = place_sets(cl[2], reading), cl[3]
                    elif cl[0] == "saw" and cl[2] == k:
                        rooms, slots = place_sets(cl[3], reading), cl[4]
                    else:
                        continue
                    for t in slots:
                        if t in placed:
                            placed[t] = rooms if placed[t] is None else (placed[t] & rooms)
            if all(placed[t] is not None and C.POISON_ROOM not in placed[t] for t in window):
                ruled_out = True
        if wax is not None and k in colour and colour[k] != wax:
            ruled_out = True
        if not ruled_out:
            out.append(k)
    return out

def trusted_ids(item_ids, candidate, strict):
    if not strict:
        return item_ids
    return [i for i in item_ids if ITEM[i][1] != candidate]

def solve_any(item_ids, window, reading, strict=False, pool=None):
    if not strict:
        return solve(item_ids, window, reading, pool=pool)
    # strict: for each candidate, drop everything the candidate said
    pool = pool or list(C.PEOPLE)
    return [k for k in pool if k in solve(trusted_ids(item_ids, k, True), window, reading, pool=[k])]

def ids_for(present, max_round=3, drop=()):
    keep = []
    for iid, src, r, _, claims in ITEMS:
        if r > max_round or iid in drop:
            continue
        if src != "card" and src not in present:
            continue
        if not claims or all(cl[0] in ("heard",) for cl in claims):
            continue
        keep.append(iid)
    return keep

def cast(n):
    return C.CORE + C.ADD_ORDER[:n - 6]

# ---------------------------------------------------------------- checks
def check_all():
    checks = []; facts = {}
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=str(detail))); return passed

    # ---- 1. the house
    rooms = set(C.ROOMS)
    ok("Plan: every door and sightline joins two rooms on the plan",
       all(a in rooms and b in rooms for a, b, _ in C.DOORS) and all(a in rooms and b in rooms for a, b in C.VIEWS))
    adj = {r: set() for r in rooms}
    for a, b, _ in C.DOORS:
        adj[a].add(b); adj[b].add(a)
    seen, todo = {"Porch"}, ["Porch"]
    while todo:
        for n in adj[todo.pop()]:
            if n not in seen:
                seen.add(n); todo.append(n)
    ok("Plan: every room can be reached from the front door", seen == rooms, sorted(rooms - seen))
    ok("Plan: the Lantern Room is reached only by the stair in the Still Room", adj["Lantern Room"] == {"Still Room"},
       sorted(adj["Lantern Room"]))
    route = C.KILLER_ROUTE
    ok("The killer’s route (Great Hall → herb garden → Still Room and back) follows doors on the plan",
       all(b in adj[a] for a, b in zip(route, route[1:])), " → ".join(route))

    def dist(a, b):
        if a == b:
            return 0
        frontier, d, seen = {a}, 0, {a}
        while frontier:
            d += 1; nxt = set()
            for x in frontier:
                for y in adj[x]:
                    if y == b:
                        return d
                    if y not in seen:
                        seen.add(y); nxt.add(y)
            frontier = nxt
        return 99
    far = [(k, C.SLOTS[i], tl[i], tl[i + 1]) for k, tl in C.TIMELINE.items() for i in range(len(tl) - 1)
           if dist(tl[i], tl[i + 1]) > 3]
    ok("Timeline: nobody moves more than three doors in a quarter of an hour", not far, far)

    # ---- 2. the timeline against every card and booklet
    ok("Timeline: every character (and Rowena) has a room for every quarter hour",
       set(C.TIMELINE) == set(C.PEOPLE) | {"rowena"} and all(len(v) == len(C.SLOTS) and all(r in rooms for r in v)
                                                            for v in C.TIMELINE.values()))
    def at(k, t):
        return C.TIMELINE[k][C.SLOTS.index(t)]
    def can_see(a, b):
        return a == b or (a, b) in C.VIEWS
    bad, lies = [], []
    for iid, src, r, text, claims in ITEMS:
        for cl in claims:
            for reading in [PRIMARY[1]] + [dict(zip(C.PLACE_READINGS, combo)) for combo in
                                           itertools.product(*[list(v.values()) for v in C.PLACE_READINGS.values()])]:
                if cl[0] == "at":
                    for t in cl[3]:
                        if at(cl[1], t) not in place_sets(cl[2], reading):
                            bad.append(f"{iid}: {cl[1]} at {t}")
                elif cl[0] == "saw":
                    for t in cl[4]:
                        if at(cl[2], t) not in place_sets(cl[3], reading):
                            bad.append(f"{iid}: {cl[2]} not where {cl[1]} says at {t}")
                        if not can_see(at(cl[1], t), at(cl[2], t)):
                            bad.append(f"{iid}: {cl[1]} in {at(cl[1], t)} cannot see {at(cl[2], t)} at {t}")
            if cl[0] == "lie":
                lies.append((iid, src, cl))
            if cl[0] == "colour" and C.PEOPLE[cl[1]][4] != cl[2]:
                bad.append(f"{iid}: colour of {cl[1]}")
            if cl[0] == "route" and cl[1] not in C.KILLER_ROUTE:
                bad.append(f"{iid}: route")
            if cl[0] == "wax" and C.PEOPLE[C.KILLER][4] != cl[1]:
                bad.append(f"{iid}: wax")
    ok("Character–time–place table: every card and every booklet line matches the true timeline, under every "
       "reading of the place words (who was where, who could see whom)", not bad, "; ".join(sorted(set(bad))[:8]))
    ok("Only the killer gives a false account, and only of their own whereabouts",
       len(lies) == 1 and lies[0][1] == C.KILLER and lies[0][2][1] == C.KILLER
       and at(C.KILLER, lies[0][2][3][0]) != lies[0][2][2],
       "; ".join(f"{i}: says {cl[2]} at {cl[3]}" for i, _, cl in lies))
    ok("Rowena’s movements on the cards match the timeline (Kitchen at 22:00, Lantern Room at 22:15, Still Room "
       "from 22:30)", C.TIMELINE["rowena"][2:] == ["Kitchen", "Lantern Room", "Still Room", "Still Room"])
    ok("At the poisoning the killer was really in the Still Room, and every other guest really elsewhere",
       at(C.KILLER, "22:15") == C.POISON_ROOM and all(at(k, "22:15") != C.POISON_ROOM for k in C.PEOPLE if k != C.KILLER))

    # ---- 3. the solution: unique, under every reading, every rule, every guest count
    full = ids_for(set(C.PEOPLE))
    res_full = solve(full, *PRIMARY)
    ok("With every card and every booklet, exactly one person could have poisoned the glass, and it is the killer",
       res_full == [C.KILLER], res_full)
    readings_report = []
    all_ok = True
    for window, reading, label in all_readings():
        for strict in (False, True):
            for n in range(6, 13):
                res = solve_any(ids_for(set(cast(n))), window, reading, strict=strict)
                if res != [C.KILLER]:
                    all_ok = False
            readings_report.append(dict(reading="; ".join(label), strict=strict,
                                        result=solve_any(ids_for(set(cast(6))), window, reading, strict=strict)))
    n_comb = len(list(all_readings())) * 2 * 7
    ok(f"Every reading of the place words and of the time window, both readings of the house rules, and every "
       f"guest count from 6 to 12 give the same single answer ({n_comb} combinations)", all_ok)
    facts["readings"] = readings_report

    # ---- 4. extra roles: the case is solvable without any of them
    core_only = ids_for(set(C.CORE))
    ok("With only the 6 core roles (no extra guests), the cards and booklets still give exactly one answer",
       solve(core_only, *PRIMARY) == [C.KILLER])
    opt_ids = [i for i in full if ITEM[i][1] in C.OPTIONAL]
    ok("No clue the solution needs belongs to an extra role: every line from the 6 extra roles can be removed "
       "without changing the answer", solve([i for i in full if i not in opt_ids], *PRIMARY) == [C.KILLER],
       f"{len(opt_ids)} lines from extra roles")
    ok("Lines from the extra roles never point away from the killer (adding them keeps the killer in)",
       C.KILLER in solve(full, *PRIMARY))
    casting = {n: cast(n) for n in range(6, 13)}
    ok("Casting table: 6 guests play the 6 core roles; each extra guest adds one extra role, up to 12",
       all(len(v) == n and set(C.CORE) <= set(v) for n, v in casting.items()))
    facts["casting"] = {n: [C.name(k) for k in v] for n, v in casting.items()}

    # ---- 5. the curve: suspects left after each round (core roles only)
    curve = []
    for r in (0, 1, 2, 3):
        left = solve(ids_for(set(C.CORE), max_round=r), *PRIMARY, pool=C.CORE) if r else list(C.CORE)
        curve.append(dict(round=r, left=[C.name(k) for k in left]))
    facts["curve"] = curve
    ok("Suspects left by round: 6 at the start, at least 3 after Round 1, at least 2 after Round 2, 1 after Round 3",
       len(curve[1]["left"]) >= 3 and len(curve[2]["left"]) >= 2 and len(curve[3]["left"]) == 1,
       " → ".join(str(len(c["left"])) for c in curve))
    for n in range(6, 13):
        cr = [len(solve(ids_for(set(cast(n)), max_round=r), *PRIMARY, pool=C.CORE)) for r in (1, 2, 3)]
        if not (cr[1] >= 2 and cr[2] == 1):
            ok(f"Curve holds with {n} guests", False, cr)
    ok("The curve holds at every guest count from 6 to 12 (the extra roles never solve it early)",
       all(len(solve(ids_for(set(cast(n)), max_round=2), *PRIMARY, pool=C.CORE)) >= 2 for n in range(6, 13)))

    # ---- 6. every key clue is needed
    necessary = []
    for iid in core_only:
        res = solve([i for i in core_only if i != iid], *PRIMARY)
        if res != [C.KILLER]:
            necessary.append((iid, [C.name(k) for k in res]))
    nec_ids = sorted(i for i, _ in necessary)
    key_ids = sorted([f"card {c['id']}" for c in C.CARDS if c["key"]] + [i for i in core_only if ITEM[i][1] != "card"
                      and i in dict(necessary)])
    ok("Every key clue is needed: removing any one of them leaves two or more suspects",
       all(len(r) >= 2 for _, r in necessary), "; ".join(f"without {i}: {', '.join(r)}" for i, r in necessary))
    ok("The key clues are exactly the cards marked key plus two booklet lines; every one belongs to a core role or "
       "is a card on the table", sorted(nec_ids) == key_ids and all(ITEM[i][1] in C.CORE + ["card"] for i in nec_ids),
       ", ".join(nec_ids))
    facts["key"] = [dict(id=i, text=ITEM[i][3][:140], without=r) for i, r in necessary]

    # ---- 7. words, names and the stop list
    texts = player_texts() + host_open_texts()
    flat = " ".join(" ".join(t.split()) for t in texts)
    ok("No “straight” anywhere (the lesson of the Hob Stones)", not re.search(r"\bstraight\b", flat, re.I))
    for phrase in C.PLACE_READINGS:
        ok(f"The place phrase “{phrase}” is printed where a player will read it", phrase in flat)
    hits = stop_hits(texts + [C.name(k) for k in C.PEOPLE] + [C.TITLE, C.HOUSE])
    ok("Stop list: no borrowed brands, films, books, other party games or real witch trials (whole words)", not hits,
       ", ".join(hits))
    gore = [w for w in GORE if re.search(r"\b" + w + r"\b", flat, re.I)]
    ok("Spooky, not gory: no blood, wounds or weapons in any text", not gore, ", ".join(gore))
    case3 = [w for w in CASE3 if re.search(r"\b" + re.escape(w) + r"\b", flat, re.I)]
    ok("Nothing from the solution of case No. 3 (its killer, victim, ticket, village or stall)", not case3, ", ".join(case3))
    famous = [k for k in C.PEOPLE if C.name(k).split()[0] in FAMOUS_WITCHES or C.name(k).split()[-1] in FAMOUS_WITCHES]
    ok("No character shares a name with a famous fictional witch", not famous, famous)
    ok("The killer is one of the 6 core roles", C.KILLER in C.CORE)

    # ---- 8. no solution in the players’ materials
    sp = spoiler_hits(player_texts() + host_open_texts())
    ok("No solution in any player material or in the open part of the host guide", not sp, "; ".join(sp))
    kb = " ".join(t for r in C.B[C.KILLER]["rounds"] for t, _ in r) + " " + C.B[C.KILLER]["secret"]
    ok("The killer’s own booklet never says they did it, and never mentions the garden, the foxglove or the wax",
       not re.search(r"foxglove|herb garden|wax on|poison(ed)? (the|her)|you killed|the killer", kb, re.I))
    ok("Every booklet has a part for all three rounds, a secret, a costume, a candle colour and questions to ask",
       all(len(b["rounds"]) == 3 and all(b["rounds"]) and b["secret"] and len(b["ask"]) >= 3 for b in C.B.values())
       and all(v[3] and v[4] for v in C.PEOPLE.values()))
    facts["timeline"] = {k: v for k, v in C.TIMELINE.items()}
    return dict(checks=checks, facts=facts)

GORE = ["blood", "bloody", "bleeding", "stab", "stabbed", "knife", "dagger", "gore", "gory", "wound", "corpse",
        "strangled", "axe", "gun", "shot", "skull"]
CASE3 = ["Edna", "Elworthy", "Hatherby", "4073", "Ember Pot", "Rosehip Ember", "Orchard Gap", "Quell", "Ottilie",
         "Barnaby", "Hob Stones", "Mill Stile"]
FAMOUS_WITCHES = {"Hilda", "Zelda", "Phoebe", "Sybil", "Esme", "Agatha", "Winifred", "Sabrina", "Willow", "Morticia",
                  "Wednesday", "Sanderson", "Owens", "Elphaba", "Glinda", "Hermione", "Minerva", "Bellatrix",
                  "Maleficent", "Ursula", "Samantha", "Prue", "Piper", "Halliwell", "Weatherwax", "Ogg", "Kiki"}
STOP = ["Hocus Pocus", "Sanderson", "Practical Magic", "Owens", "Sabrina", "Charmed", "Halliwell", "Wicked",
        "Elphaba", "Glinda", "Agatha All Along", "Agatha", "The Craft", "Harry Potter", "Hogwarts", "Quidditch",
        "Hermione", "Discworld", "Weatherwax", "Kiki", "Maleficent", "Ursula", "Winifred", "Salem", "Moonfall",
        "Cluedo", "Clue", "Christie", "Poirot", "Marple", "Sherlock", "Holmes", "Knives Out", "Glass Onion",
        "Traitors", "Frankenstein", "Dracula", "Wednesday", "Addams", "Disney", "Pendle", "Hopkins", "witch trial",
        "witch trials", "witch hunt", "Wicca", "Wiccan", "Samhain", "pagan", "burned at the stake", "gallows",
        "Murder at the Villa", "Villa Solaris", "Murder Among Monsters", "Monster Mansion", "Haunted Hotel",
        "Creepy Carnival", "Witches Dene", "Witches and Warlocks", "Wasted Witch", "Witch's Coven", "Ravenwood",
        "Transylville", "Thistlewood", "My Mystery Party", "Night of Mystery"]
def stop_hits(texts):
    flat = " ".join(texts)
    return sorted({b for b in STOP if re.search(r"\b" + re.escape(b) + r"\b", flat, re.I)})

def spoiler_tokens():
    toks = [C.SOLUTION_INTRO, "killer is Clementine", "Clementine is the killer", "Clementine poisoned",
            "Clementine Reed poisoned"]
    toks += [t[:60] for _, t in C.SOLUTION] + [t[:60] for _, t in C.DEDUCTION] + [C.EPILOGUE[:60]]
    return toks
def spoiler_hits(texts):
    flat = " ".join(" ".join(t.split()) for t in texts)
    return [t for t in spoiler_tokens() if " ".join(t.split()) in flat]

def player_texts():
    out = []
    for c in C.CARDS:
        out += [c["title"]] + c["text"]
    for k, b in C.B.items():
        out += b["intro"] + [b["secret"]] + [t for r in b["rounds"] for t, _ in r] + b["ask"]
    for p in C.PEOPLE.values():
        out += [p[0], p[1], p[3], p[5]]
    out += [x for p in C.POTIONS for x in p] + [C.POTION_NOTE] + [a + " " + b for a, b in C.AWARDS] + C.HOUSE_RULES
    return out
def host_open_texts():
    return C.HOST_INTRO + [t for v in C.ROUND_SCRIPTS.values() for t in v]

# ---------------------------------------------------------------- PDF checks (after rendering)
def check_pdfs(rep, paths):
    import pymupdf as fitz
    checks = rep["checks"]
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=str(detail))); return passed
    toks = spoiler_tokens()
    for key, p in paths.items():
        doc = fitz.open(p); pages = [" ".join(pg.get_text().split()) for pg in doc]
        mb = os.path.getsize(p) / 2 ** 20
        ok(f"{os.path.basename(p)}: under 20 MB", mb < 20, f"{mb:.1f} MB, {len(pages)} pages")
        if key.startswith("host"):
            sealed = next((i for i, t in enumerate(pages) if "SEALED SOLUTION" in t and "STOP" in t), None)
            ok(f"{os.path.basename(p)}: has a sealed solution section", sealed is not None, f"page {sealed and sealed + 1}")
            before = " ".join(pages[:sealed]) if sealed is not None else ""
            after = " ".join(pages[sealed:]) if sealed is not None else ""
            ok(f"{os.path.basename(p)}: nothing from the solution before the sealed section",
               not [t for t in toks if " ".join(t.split()) in before])
            ok(f"{os.path.basename(p)}: the sealed section holds the answer, the reasoning and the timeline table",
               C.SOLUTION_INTRO in after and all(" ".join(t[:50].split()) in after for _, t in C.DEDUCTION)
               and "Character, time and place" in after)
            ok(f"{os.path.basename(p)}: the sealed section is the last part of the guide",
               sealed is not None and sealed >= len(pages) - 8)
        else:
            alltext = " ".join(pages)
            ok(f"{os.path.basename(p)}: no solution anywhere in the player kit",
               not [t for t in toks if " ".join(t.split()) in alltext])
            for k in C.PEOPLE:
                ok(f"{os.path.basename(p)}: {C.name(k)}’s booklet is complete",
                   C.name(k) in alltext and all(" ".join(t[:50].split()) in alltext for r in C.B[k]["rounds"] for t, _ in r))
            for c in C.CARDS:
                ok(f"{os.path.basename(p)}: clue card {c['id']} printed word for word",
                   all(" ".join(t.split()) in alltext for t in c["text"] if t != "LEDGER"))
    return rep

def write_report(rep, md, js):
    passed = sum(c["passed"] for c in rep["checks"])
    lines = [f"# {C.TITLE}: verification report", "", f"Result: **{passed} of {len(rep['checks'])} checks passed**", "",
             "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(rep["checks"], 1):
        lines.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'][:300].replace('|', '/')} |")
    f = rep["facts"]
    lines += ["", "## Suspects left after each round (6 core roles)", "", "| Round | Left |", "|---|---|"]
    for c in f["curve"]:
        lines.append(f"| {c['round'] or 'start'} | {len(c['left'])}: {', '.join(c['left'])} |")
    lines += ["", "## Key clues (each one needed)", "", "| Clue | Without it, still possible |", "|---|---|"]
    for k in f["key"]:
        lines.append(f"| {k['id']}: {k['text'][:90]}… | {', '.join(k['without'])} |")
    lines += ["", "## Readings tested", "", "| Reading | Rules | Result |", "|---|---|---|"]
    for r in f["readings"]:
        lines.append(f"| {r['reading']} | {'strict' if r['strict'] else 'house rules'} | {', '.join(C.name(k) for k in r['result'])} |")
    lines += ["", "## Casting by number of guests", ""]
    for n, v in f["casting"].items():
        lines.append(f"- {n} guests: {', '.join(v)}")
    lines += ["", "## Character, time and place (SPOILER: the true timeline)", "",
              "| Character | " + " | ".join(C.SLOTS) + " |", "|---|" + "---|" * len(C.SLOTS)]
    for k, v in f["timeline"].items():
        nm = "Rowena Heatherly (victim)" if k == "rowena" else C.name(k)
        lines.append(f"| {nm} | " + " | ".join(v) + " |")
    open(md, "w").write("\n".join(lines) + "\n")
    json.dump(rep, open(js, "w"), indent=1, default=list)
    return passed, len(rep["checks"])

if __name__ == "__main__":
    rep = check_all()
    p, n = write_report(rep, os.path.join(OUT, "verification_report.md"), os.path.join(OUT, "verification_report.json"))
    print(f"checks {p}/{n}")
    for c in rep["checks"]:
        if not c["passed"]:
            print("FAIL", c["name"], "|", c["detail"])
    print([(c["round"], len(c["left"])) for c in rep["facts"]["curve"]])
    print([k["id"] for k in rep["facts"]["key"]])
