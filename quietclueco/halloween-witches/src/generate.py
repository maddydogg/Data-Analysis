"""Build the Visitor Log for Full Moon over Morrowmere.

Deterministic (seeded). Steps:
1. 6,000 random visitors, ticket numbers 0001-6000, unique full names.
2. Plant the killer.
3. Plant near-miss visitors ("finalists"): each one fits every clue except one, and fails
   that clue under every reading we test, so every clue is needed to reach the answer.
   Finalists are spread evenly over entrances, villages, stalls and entry hours (the killer's
   own value counts as already used), so the shortlist has no pattern that points at the answer.
4. Re-roll any other visitor who could survive under some reading of the clues.
"""
import csv, json, random, os
from itertools import product
import case as C

GROUP = {"1": "name", "2": "name", "3": "name", "4": "name", "5": "name", "12": "name",
         "F": "name", "6": "ticket", "7": "ticket", "8": "entry", "B": "entry", "C": "entry",
         "A": "gate", "9": "town", "E": "town", "10": "stall", "11": "stall", "D": "stall"}
GROUP_ATTRS = {"name": ("first", "last"), "ticket": ("ticket",), "entry": ("entry",),
               "gate": ("gate",), "town": ("town",), "stall": ("stall",)}
CLUE = {c["id"]: c for c in C.CLUES}
# planted finalists per clue (a few clues get two)
DECOYS_PER_CLUE = {cid: 1 for cid in CLUE}
DECOYS_PER_CLUE.update({"B": 2, "D": 2, "F": 2, "3": 2, "E": 2, "A": 2})
# what "the same value" means for the diversity rule
SPREAD = {"gate": [lambda p: p["gate"]], "town": [lambda p: p["town"]],
          "stall": [lambda p: C.lane_of(p["stall"]), lambda p: p["stall"]],
          "entry": [lambda p: p["entry"] // 60]}

def readings(c):
    return [c["pred"]] + [a[1] for a in c["alts"]]

def robust_pass(c, r):
    return all(p(r) for p in readings(c))

def robust_fail(c, r):
    return not any(p(r) for p in readings(c))

def seal(r):
    return (r["ticket"] * 7 + len(r["first"]) + len(r["last"])) % 1000

def entry_weight(m):
    # quiet at opening, busiest 18:00-19:30, tailing off before last entry
    h = m / 60
    return 0.5 + 2.2 * max(0, 1 - abs(h - 18.7) / 2.2)

def build():
    rng = random.Random(C.SEED)
    K = dict(C.KILLER)
    minutes = list(range(C.tmin(C.OPEN_FROM), C.tmin(C.LAST_ENTRY) + 1))
    mweights = [entry_weight(m) for m in minutes]
    used_names = {(K["first"], K["last"])}

    def rand_name():
        while True:
            n = (rng.choice(C.FIRST), rng.choice(C.LAST))
            if n not in used_names:
                used_names.add(n); return n

    def rand_attrs(r):
        r["town"] = rng.choices(C.TOWNS, C.TOWN_WEIGHTS)[0]
        r["gate"] = rng.choices(C.GATES, C.GATE_WEIGHTS)[0]
        r["entry"] = rng.choices(minutes, mweights)[0]
        r["stall"] = rng.randint(1, 36)
        return r

    recs = {}
    for t in range(1, C.N_VISITORS + 1):
        if t == K["ticket"]:
            recs[t] = K; continue
        f, l = rand_name()
        recs[t] = rand_attrs(dict(ticket=t, first=f, last=l))

    # ---- candidate domains per group, as partial records
    names = [dict(first=f, last=l) for f, l in product(C.FIRST, C.LAST)]
    domains = {"name": names,
               "entry": [dict(entry=m) for m in minutes],
               "gate": [dict(gate=g) for g in C.GATES],
               "town": [dict(town=t) for t in C.TOWNS],
               "stall": [dict(stall=s) for s in C.STALLS]}

    def ok_group(group, part, fail_id=None):
        r = dict(K); r.update(part)
        for cid, g in GROUP.items():
            if g != group:
                continue
            c = CLUE[cid]
            if cid == fail_id:
                if not robust_fail(c, r):
                    return False
            elif not robust_pass(c, r):
                return False
        return True

    decoys = {}
    decoy_firsts, decoy_lasts = {K["first"]}, {K["last"]}   # finalists get distinct names
    used = {g: [{fn(K): 1} for fn in fns] for g, fns in SPREAD.items()}   # how often each value is on the shortlist

    def spread(g, opts):
        """Keep only the options whose value is least used so far; ties go to values that
        are not the killer's, so the killer's value never becomes the most common one."""
        if g not in SPREAD:
            return opts
        fns = SPREAD[g]
        key = lambda p: tuple(x for i, fn in enumerate(fns)
                              for x in (used[g][i].get(fn(p), 0), fn(p) == fn(K)))
        best = min(key(p) for p in opts)
        return [p for p in opts if key(p) == best]
    taken = {K["ticket"]}
    kseal = seal(K)
    for cid, n in DECOYS_PER_CLUE.items():
        for _ in range(n):
            for attempt in range(500):
                fail_group = GROUP[cid]
                # ticket
                tick_ok = [t for t in range(1, C.N_VISITORS + 1) if t not in taken
                           and ok_group("ticket", dict(ticket=t), cid if fail_group == "ticket" else None)]
                t = rng.choice(tick_ok)
                r = dict(ticket=t)
                for g in ("name", "entry", "gate", "town", "stall"):
                    opts = [p for p in domains[g]
                            if ok_group(g, p, cid if fail_group == g else None)]
                    if g == "name":
                        opts = [p for p in opts if (p["first"], p["last"]) not in used_names]
                        # prefer names no other finalist uses, so the shortlist doesn't look samey
                        for strict in ((decoy_firsts, decoy_lasts), (set(), decoy_lasts)):
                            fresh = [p for p in opts if p["first"] not in strict[0] and p["last"] not in strict[1]]
                            if fresh:
                                opts = fresh; break
                    r.update(rng.choice(spread(g, opts)))
                if seal(r) != kseal:
                    break
            used_names.discard((recs[t]["first"], recs[t]["last"]))
            used_names.add((r["first"], r["last"]))
            recs[t] = r
            decoy_firsts.add(r["first"]); decoy_lasts.add(r["last"])
            for g, fns in SPREAD.items():
                for i, fn in enumerate(fns):
                    used[g][i][fn(r)] = used[g][i].get(fn(r), 0) + 1
            taken.add(t)
            decoys.setdefault(cid, []).append(t)

    # ---- every other visitor must fail at least one clue under every reading
    rerolled = 0
    for t, r in recs.items():
        if t in taken:
            continue
        while not any(robust_fail(c, r) for c in C.CLUES):
            rerolled += 1
            used_names.discard((r["first"], r["last"]))
            r["first"], r["last"] = rand_name()
            rand_attrs(r)

    rows = sorted(recs.values(), key=lambda r: (r["entry"], r["ticket"]))
    meta = dict(decoys=decoys, rerolled=rerolled, killer=K["ticket"], seal=f"{kseal:03d}")
    return rows, meta

def save(rows, meta, outdir):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "visitor_log.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry", "ticket", "first", "last", "town", "gate", "stall"])
        for r in rows:
            w.writerow([C.tstr(r["entry"]), f"{r['ticket']:04d}", r["first"], r["last"],
                        r["town"], r["gate"], r["stall"]])
    json.dump(meta, open(os.path.join(outdir, "generator_meta.json"), "w"), indent=1)

if __name__ == "__main__":
    rows, meta = build()
    save(rows, meta, os.path.join(os.path.dirname(__file__), "data"))
    print(len(rows), "visitors;", meta)
