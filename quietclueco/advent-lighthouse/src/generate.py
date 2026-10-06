"""Build the Sound Book for The Keeper of Candleholm.

Deterministic (seeded). Steps:
1. 2,400 random travellers, tallies 0001-2400 drawn at random, unique full names. First crossings
   bunch up at the start of the month (regulars get their tally on the first days) and pick up again
   before Christmas.
2. Plant the killer.
3. Plant near-miss travellers ("finalists"): each one fits every clue except one, and fails that
   clue under every reading we test (the far-fetched ones too), so every window is needed and a
   far-fetched reading leaves nobody. More finalists sit on the last windows, so several lines are
   still in until the final days. Finalists are spread over boats, villages, landings and hours (the
   killer's own value counts as already used), so the shortlist has no pattern that points at the
   answer.
4. Re-roll any other traveller who could survive under some reading of the clues.
"""
import csv, json, random, os
from itertools import product
import case as C

GROUP = {c["id"]: c["group"] for c in C.CLUES}
CLUE = {c["id"]: c for c in C.CLUES}
DECOYS_PER_CLUE = {cid: 1 for cid in CLUE}
DECOYS_PER_CLUE.update({"4": 2, "13": 2, "15": 2, "17": 2, "19": 2, "20": 2, "21": 2, "22": 2, "23": 2})
SPREAD = {"boat": [lambda p: p["boat"]], "home": [lambda p: p["home"]], "landing": [lambda p: p["landing"]],
          "when": [lambda p: p["time"] // 60]}

def readings(c):
    return [c["pred"]] + [a[1] for a in c["alts"]]

def robust_pass(c, r):
    return all(p(r) for p in readings(c))

def robust_fail(c, r):
    return not any(p(r) for p in readings(c) + [f[1] for f in c["far"]])

def seal(r):
    return (r["tally"] * 4 + len(r["first"]) + len(r["last"])) % 1000

DAY_WEIGHTS = {1: 520, 2: 330, 3: 230}
DAY_WEIGHTS.update({d: 72 - 2 * (d - 4) for d in range(4, 18)})
DAY_WEIGHTS.update({18: 64, 19: 72, 20: 80, 21: 86, 22: 80, 23: 66})

def time_weight(m):
    # a few early boats, busiest late morning to early afternoon, a thin evening run
    h = m / 60
    return 0.5 + 2.0 * max(0, 1 - abs(h - 12.0) / 4.0)

def build():
    for salt in range(400):
        rows, meta = build_once(salt)
        recs = {r["tally"]: r for r in rows}
        if shortlist_ok(recs, recs[C.KILLER["tally"]]):
            meta["salt"] = salt
            return rows, meta
    raise RuntimeError("no balanced shortlist found")

def shortlist_ok(recs, K):
    """Same rule as verify.py: for boat, village, landing and hour the killer's value is shared by at least
    two finalists, is not the single most common value, and no value covers more than half; finalists have
    distinct first names and surnames."""
    fin = [r for r in recs.values() if sum(not c["pred"](r) for c in C.CLUES) == 1]
    for fn in (lambda r: r["boat"], lambda r: r["home"], lambda r: r["landing"], lambda r: r["time"] // 60):
        cnt = {}
        for r in fin + [K]:
            cnt[fn(r)] = cnt.get(fn(r), 0) + 1
        kc = cnt[fn(K)]; other = max([v for k, v in cnt.items() if k != fn(K)] or [0])
        if not (kc >= 3 and kc <= other and max(cnt.values()) / len(fin + [K]) <= 0.5):
            return False
    return len({r["first"] for r in fin}) == len(fin) and len({r["last"] for r in fin}) == len(fin)

def build_once(salt):
    rng = random.Random(C.SEED * 1000 + salt)
    K = dict(C.KILLER)
    minutes = list(range(C.tmin(C.FIRST_BOAT), C.tmin(C.LAST_BOAT) + 1))
    mweights = [time_weight(m) for m in minutes]
    days = C.DAYS; dweights = [DAY_WEIGHTS[d] for d in days]
    homes = C.HOMES; hweights = [C.VILLAGE_WEIGHTS[v] for v in homes]
    lands = list(C.LANDINGS); lweights = [C.LANDING_WEIGHTS[n] for n in lands]
    used_names = {(K["first"], K["last"])}

    def rand_name():
        while True:
            n = (rng.choice(C.FIRST), rng.choice(C.LAST))
            if n not in used_names:
                used_names.add(n); return n

    def rand_attrs(r):
        r["day"] = rng.choices(days, dweights)[0]
        r["time"] = rng.choices(minutes, mweights)[0]
        r["home"] = rng.choices(homes, hweights)[0]
        r["boat"] = rng.choices(C.BOATS, C.BOAT_WEIGHTS)[0]
        r["landing"] = rng.choices(lands, lweights)[0]
        return r

    recs = {}
    for t in range(1, C.N_ROWS + 1):
        if t == K["tally"]:
            recs[t] = K; continue
        f, l = rand_name()
        recs[t] = rand_attrs(dict(tally=t, first=f, last=l))

    names = [dict(first=f, last=l) for f, l in product(C.FIRST, C.LAST)]
    domains = {"name": names,
               "when": [dict(day=d, time=m) for d in days for m in minutes],
               "boat": [dict(boat=b) for b in C.BOATS],
               "home": [dict(home=v) for v in homes],
               "landing": [dict(landing=n) for n in lands]}

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

    decoy_firsts, decoy_lasts = {K["first"]}, {K["last"]}
    used = {g: [{fn(K): 1} for fn in fns] for g, fns in SPREAD.items()}

    def spread(g, opts):
        if g not in SPREAD:
            return opts
        fns = SPREAD[g]
        cnt = lambda p: sum(used[g][i].get(fn(p), 0) for i, fn in enumerate(fns))
        best = min(cnt(p) for p in opts)
        return [p for p in opts if cnt(p) == best]

    taken = {K["tally"]}; decoys = {}
    kseal = seal(K)
    opt_cache = {}
    for cid, n in DECOYS_PER_CLUE.items():
        for _ in range(n):
            for attempt in range(500):
                fail_group = GROUP[cid]
                tick_ok = [t for t in range(1, C.N_ROWS + 1) if t not in taken
                           and ok_group("tally", dict(tally=t), cid if fail_group == "tally" else None)]
                if not tick_ok:
                    raise RuntimeError(f"no tally fits for clue {cid}")
                t = rng.choice(tick_ok)
                r = dict(tally=t)
                for g in ("name", "when", "boat", "home", "landing"):
                    key = (g, cid if fail_group == g else None)
                    if key not in opt_cache:
                        opt_cache[key] = [p for p in domains[g] if ok_group(g, p, key[1])]
                    opts = opt_cache[key]
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

    rows = sorted(recs.values(), key=lambda r: (r["day"], r["time"], r["tally"]))
    meta = dict(decoys=decoys, rerolled=rerolled, killer=K["tally"], seal=f"{kseal:03d}")
    return rows, meta

COLUMNS = ["day", "time", "tally", "first", "last", "home", "boat", "landing"]

def save(rows, meta, outdir):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "sound_book.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([r["day"], C.tstr(r["time"]), f"{r['tally']:04d}", r["first"], r["last"], r["home"],
                        r["boat"], r["landing"]])
    json.dump(meta, open(os.path.join(outdir, "generator_meta.json"), "w"), indent=1)

def load(outdir):
    rows = []
    with open(os.path.join(outdir, "sound_book.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(dict(day=int(r["day"]), time=C.tmin(r["time"]), tally=int(r["tally"]), first=r["first"],
                             last=r["last"], home=r["home"], boat=r["boat"], landing=int(r["landing"])))
    return rows

if __name__ == "__main__":
    import time
    t0 = time.time()
    rows, meta = build()
    save(rows, meta, os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
    print(len(rows), "lines;", meta, f"{time.time() - t0:.1f}s")
