"""Build the Lantern Register for The Windows at Quillon's.

Deterministic (seeded). Steps:
1. 2,400 random shoppers, pass numbers 0001-2400, unique full names.
2. Plant the killer.
3. Plant near-miss shoppers ("finalists"): each one fits every clue except one, and fails that
   clue under every reading we test, so every window is needed. More finalists sit on the last
   windows, so several passes are still in until the final days. Finalists are spread evenly over
   doors, districts, tills and entry hours (the killer's own value counts as already used), so the
   shortlist has no pattern that points at the answer.
4. Re-roll any other shopper who could survive under some reading of the clues.
"""
import csv, json, random, os
from itertools import product
import case as C

GROUP = {c["id"]: c["group"] for c in C.CLUES}
GROUP_ATTRS = {"name": ("first", "last"), "ticket": ("ticket",), "entry": ("entry",),
               "gate": ("gate",), "town": ("town",), "stall": ("stall",)}
CLUE = {c["id"]: c for c in C.CLUES}
# planted finalists per window: one each, two on the last windows so the end stays open
DECOYS_PER_CLUE = {cid: 1 for cid in CLUE}
DECOYS_PER_CLUE.update({"4": 2, "19": 2, "20": 2, "21": 2, "22": 2, "23": 2, "17": 2, "15": 2, "13": 2})
SPREAD = {"gate": [lambda p: p["gate"]], "town": [lambda p: p["town"]],
          "stall": [lambda p: p["stall"]],
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
    # a steady trickle from opening, busiest 18:00-20:00, thinning before the curtain
    h = m / 60
    return 0.6 + 2.0 * max(0, 1 - abs(h - 19.0) / 2.4)

def town_weights():
    return [C.DISTRICT_WEIGHTS.get(d, 6) for d in C.DISTRICTS]

def till_weights():
    busy = {1: 9, 9: 7, 20: 7, 14: 7, 4: 6, 6: 5, 5: 6, 10: 6, 11: 5}
    return [busy.get(n, 4) for n in C.DEPTS]

def shortlist_ok(recs, K):
    """Same rule as verify.py: for door, district, till and entry hour the killer's value is shared by at
    least two finalists, is not the single most common value, and no value covers more than half;
    finalists have distinct first names and surnames."""
    fin = [r for r in recs.values() if sum(not c["pred"](r) for c in C.CLUES) == 1]
    for fn in (lambda r: r["gate"], lambda r: r["town"], lambda r: r["stall"], lambda r: r["entry"] // 60):
        cnt = {}
        for r in fin + [K]:
            cnt[fn(r)] = cnt.get(fn(r), 0) + 1
        kc = cnt[fn(K)]; other = max([v for k, v in cnt.items() if k != fn(K)] or [0])
        if not (kc >= 3 and kc <= other and max(cnt.values()) / len(fin + [K]) <= 0.5):
            return False
    return len({r["first"] for r in fin}) == len(fin) and len({r["last"] for r in fin}) == len(fin)

def build():
    for salt in range(200):
        rows, meta = build_once(salt)
        recs = {r["ticket"]: r for r in rows}
        if shortlist_ok(recs, recs[C.KILLER["ticket"]]):
            meta["salt"] = salt
            return rows, meta
    raise RuntimeError("no balanced shortlist found")

def build_once(salt):
    rng = random.Random(C.SEED * 1000 + salt)
    K = dict(C.KILLER)
    minutes = list(range(C.tmin(C.OPEN_FROM), C.tmin(C.LAST_ENTRY) + 1))
    mweights = [entry_weight(m) for m in minutes]
    tw, sw = town_weights(), till_weights()
    used_names = {(K["first"], K["last"])}

    def rand_name():
        while True:
            n = (rng.choice(C.FIRST), rng.choice(C.LAST))
            if n not in used_names:
                used_names.add(n); return n

    def rand_attrs(r):
        r["town"] = rng.choices(C.DISTRICTS, tw)[0]
        r["gate"] = rng.choices(C.DOORS, C.DOOR_WEIGHTS)[0]
        r["entry"] = rng.choices(minutes, mweights)[0]
        r["stall"] = rng.choices(list(C.DEPTS), sw)[0]
        return r

    recs = {}
    for t in range(1, C.N_PASSES + 1):
        if t == K["ticket"]:
            recs[t] = K; continue
        f, l = rand_name()
        recs[t] = rand_attrs(dict(ticket=t, first=f, last=l))

    names = [dict(first=f, last=l) for f, l in product(C.FIRST, C.LAST)]
    domains = {"name": names,
               "entry": [dict(entry=m) for m in minutes],
               "gate": [dict(gate=g) for g in C.DOORS],
               "town": [dict(town=t) for t in C.DISTRICTS],
               "stall": [dict(stall=s) for s in C.DEPTS]}

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
    decoy_firsts, decoy_lasts = {K["first"]}, {K["last"]}
    used = {g: [{fn(K): 1} for fn in fns] for g, fns in SPREAD.items()}

    def spread(g, opts):
        if g not in SPREAD:
            return opts
        fns = SPREAD[g]
        key = lambda p: tuple(x for i, fn in enumerate(fns)
                              for x in (used[g][i].get(fn(p), 0), fn(p) == fn(K)))
        # least-used values first, ties broken at random, so that attributes are not chosen in lockstep
        # (which would make the shortlist fall into tidy groups)
        cnt = lambda p: sum(used[g][i].get(fn(p), 0) for i, fn in enumerate(fns))
        best = min(cnt(p) for p in opts)
        return [p for p in opts if cnt(p) == best]

    taken = {K["ticket"]}
    kseal = seal(K)
    for cid, n in DECOYS_PER_CLUE.items():
        for _ in range(n):
            for attempt in range(500):
                fail_group = GROUP[cid]
                tick_ok = [t for t in range(1, C.N_PASSES + 1) if t not in taken
                           and ok_group("ticket", dict(ticket=t), cid if fail_group == "ticket" else None)]
                if not tick_ok:
                    raise RuntimeError(f"no ticket fits for clue {cid}")
                t = rng.choice(tick_ok)
                r = dict(ticket=t)
                for g in ("name", "entry", "gate", "town", "stall"):
                    opts = [p for p in domains[g]
                            if ok_group(g, p, cid if fail_group == g else None)]
                    if g == "name":
                        opts = [p for p in opts if (p["first"], p["last"]) not in used_names]
                        for strict in ((decoy_firsts, decoy_lasts), (set(), decoy_lasts), (set(), set())):
                            fresh = [p for p in opts if p["first"] not in strict[0] and p["last"] not in strict[1]]
                            if fresh:
                                opts = fresh; break
                    if not opts:
                        raise RuntimeError(f"no {g} option for clue {cid}")
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
    with open(os.path.join(outdir, "lantern_register.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry", "ticket", "first", "last", "town", "gate", "stall"])
        for r in rows:
            w.writerow([C.tstr(r["entry"]), f"{r['ticket']:04d}", r["first"], r["last"],
                        r["town"], r["gate"], r["stall"]])
    json.dump(meta, open(os.path.join(outdir, "generator_meta.json"), "w"), indent=1)

if __name__ == "__main__":
    rows, meta = build()
    save(rows, meta, os.path.join(os.path.dirname(__file__), "data"))
    print(len(rows), "passes;", meta)
