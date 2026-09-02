"""Fill Debt Payoff (Light).xlsx with demo data, in place.

The workbook carries a chart, and openpyxl drops charts on save, so this writes
straight into the sheet XML. Every target cell already exists in the template
with its style, so only the value is injected — currency and percent formats,
banding, protection, the Method dropdown and the chart all survive. It also sets
fullCalcOnLoad so Excel recalculates the engine the moment the file opens.

  usage: make_demo_debt.py <source.xlsx> <output.xlsx>
"""
import re, shutil, sys, zipfile
from xml.sax.saxutils import escape

SRC, OUT = sys.argv[1], sys.argv[2]

# Debt, Balance, APR %, Min payment, Custom order  (rows 7..12 on Setup)
DEBTS = [
    ("Store Card",    640,   27.9,  30, 6),
    ("Medical Bill",  1200,   0.0,  50, 5),
    ("Credit Card A", 8900,  25.9, 220, 3),
    ("Credit Card B", 3100,  21.9,  95, 4),
    ("Car Loan",      12800,  7.4, 345, 1),
    ("Student Loan",  9400,   4.9, 205, 2),
]
EXTRA = 400                      # Setup!I4 — extra a month on top of the minimums
PAID  = [640, 600, 2400, 1150, 3900, 2200]   # Debt Tracker C5:C10 — paid so far

def put(xml, ref, value):
    """Fill one existing, pre-styled cell, keeping its style."""
    pat = re.compile(r'<c r="%s"([^>]*?)(/>|>.*?</c>)' % ref, re.S)
    m = pat.search(xml)
    if not m:
        raise KeyError(f"{ref} not found")
    attrs = re.sub(r'\s*t="[^"]*"', "", m.group(1))
    if isinstance(value, (int, float)):
        body = f'<c r="{ref}"{attrs}><v>{value}</v></c>'
    else:
        body = f'<c r="{ref}"{attrs} t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
    return xml[:m.start()] + body + xml[m.end():]

zin = zipfile.ZipFile(SRC)
parts = {n: zin.read(n) for n in zin.namelist()}
zin.close()

# Setup — sheet2
s = parts["xl/worksheets/sheet2.xml"].decode("utf-8")
s = put(s, "I4", EXTRA)
for i, (name, bal, apr, mn, order) in enumerate(DEBTS):
    r = 7 + i
    for col, val in (("A", name), ("B", bal), ("C", apr), ("D", mn), ("E", order)):
        s = put(s, f"{col}{r}", val)
parts["xl/worksheets/sheet2.xml"] = s.encode("utf-8")

# Debt Tracker — sheet4
s = parts["xl/worksheets/sheet4.xml"].decode("utf-8")
for i, paid in enumerate(PAID):
    s = put(s, f"C{5+i}", paid)
parts["xl/worksheets/sheet4.xml"] = s.encode("utf-8")

# make Excel recalculate the engine on open
wbx = parts["xl/workbook.xml"].decode("utf-8")
if "<calcPr" in wbx:
    wbx = re.sub(r'<calcPr([^>]*?)/>', lambda m: '<calcPr' + re.sub(r'\s*fullCalcOnLoad="[^"]*"', "", m.group(1)) + ' fullCalcOnLoad="1"/>', wbx)
else:
    wbx = wbx.replace("</workbook>", '<calcPr fullCalcOnLoad="1"/></workbook>')
parts["xl/workbook.xml"] = wbx.encode("utf-8")

shutil.copy(SRC, OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in parts.items():
        z.writestr(name, data)

# ---------------------------------------------------------------- what it works out to
def simulate(method, months=60):
    """Same arithmetic as the Engine sheet, for reporting the expected result."""
    bal = [d[1] for d in DEBTS]
    score = [(d[1] if method == "Snowball" else 1 - d[2] / 100) + (i + 1) * 1e-5
             for i, d in enumerate(DEBTS)]
    total_int, payoff = 0.0, None
    for m in range(1, months + 1):
        pool = EXTRA + sum(d[3] for d, b in zip(DEBTS, bal) if b == 0)
        live = [s for s, b in zip(score, bal) if b > 0]
        prio = min(live) if live else None
        total_int += sum(b * d[2] / 1200 for b, d in zip(bal, DEBTS))
        bal = [0.0 if b <= 0 else max(0.0, b + b * d[2] / 1200 - (d[3] + (pool if sc == prio else 0)))
               for b, d, sc in zip(bal, DEBTS, score)]
        if payoff is None and sum(bal) <= 0:
            payoff = m
    return payoff, total_int

sm, si = simulate("Snowball")
am, ai = simulate("Avalanche")
total = sum(d[1] for d in DEBTS)
print(f"{OUT}")
print(f"  долгов {len(DEBTS)} на {total:,} · минималки {sum(d[3] for d in DEBTS)}/мес · extra {EXTRA}/мес")
print(f"  Snowball : {sm} мес, проценты ${si:,.0f}")
print(f"  Avalanche: {am} мес, проценты ${ai:,.0f}  → экономия ${si-ai:,.0f} и {sm-am} мес")
print(f"  выплачено {sum(PAID):,} из {total:,} = {sum(PAID)/total:.1%}")
