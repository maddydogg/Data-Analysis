"""Fill CouplesFamilyBudget.xlsx with a year of demo data, in place.

openpyxl would drop the four dashboard charts on save, so this writes straight
into the sheet XML instead: every target cell already exists in the template
with its style, so only the value is injected and the date/currency formats,
banding, protection, charts and validations all survive.

  usage: make_demo.py <source.xlsx> <output.xlsx> [demo_transactions.csv]
"""
import csv, datetime as dt, random, re, shutil, sys, zipfile
from xml.sax.saxutils import escape

SRC, OUT = sys.argv[1], sys.argv[2]
CSV_OUT = sys.argv[3] if len(sys.argv) > 3 else None
YEAR = 2026
random.seed(11)

A, B = "Alex", "Sam"                 # partner names
INC_A, INC_B = 5200, 3800            # monthly income each -> 57.8% / 42.2% split

# ---------------------------------------------------------------- transactions
rows = []
def add(month, day, typ, cat, acct, amount, paid, share, note=""):
    import calendar
    day = min(day, calendar.monthrange(YEAR, month)[1])
    rows.append([dt.date(YEAR, month, day), typ, cat, acct, round(amount, 2), paid, share, note])

def jit(x, p=0.12): return round(x * random.uniform(1 - p, 1 + p), 2)

GIFTS   = {2: 140, 5: 180, 6: 220, 9: 160, 11: 190, 12: 420}
HEALTH  = {1: 90, 3: 120, 5: 70, 7: 140, 9: 85, 11: 110}
TRIPS   = {4: 520, 8: 780, 12: 640}
BONUS   = {6: 1800, 12: 2400}

for m in range(1, 13):
    # income
    add(m, 1,  "Income", "Salary", "Checking", INC_A, A, "Personal", "Monthly pay")
    add(m, 1,  "Income", "Salary", "Checking", INC_B, B, "Personal", "Monthly pay")
    if m in BONUS:
        add(m, 20, "Income", "Side income", "Checking", BONUS[m], A, "Personal", "Bonus")

    # shared — Alex pays
    add(m, 1,  "Expense", "Rent or Mortgage",   "Checking",    2400.00,   A, "Shared", "Rent")
    add(m, 9,  "Expense", "Transport",          "Credit Card", jit(180),  A, "Shared", "Fuel and transit")
    add(m, 7,  "Expense", "Subscriptions",      "Credit Card", 46.99,     A, "Shared", "Streaming + cloud")
    add(m, 11, "Expense", "Dining out",         "Credit Card", jit(95),   A, "Shared", "Date night")
    # shared — Sam pays
    add(m, 4,  "Expense", "Utilities",          "Checking",    jit(210, .25), B, "Shared", "Electric and gas")
    add(m, 6,  "Expense", "Groceries",          "Credit Card", jit(320),  B, "Shared", "Weekly shop")
    add(m, 19, "Expense", "Groceries",          "Credit Card", jit(320),  B, "Shared", "Weekly shop")
    add(m, 8,  "Expense", "Phone and Internet", "Checking",    110.00,    B, "Shared", "Fibre + mobiles")
    add(m, 23, "Expense", "Transport",          "Credit Card", jit(180),  B, "Shared", "Fuel and transit")
    add(m, 24, "Expense", "Dining out",         "Credit Card", jit(95),   B, "Shared", "Lunch out")
    # shared — paid from the joint account
    add(m, 3,  "Expense", "Insurance",          "Checking",    240.00, "Joint", "Shared", "Home + car")
    add(m, 12, "Expense", "Debt",               "Checking",    420.00, "Joint", "Shared", "Car loan")

    # personal — each pays their own
    add(m, 15, "Expense", "Shopping",        "Credit Card", jit(150), A, "Personal", "Clothes")
    add(m, 21, "Expense", "Fun and Leisure", "Credit Card", jit(150), A, "Personal", "Gym + hobbies")
    add(m, 16, "Expense", "Shopping",        "Credit Card", jit(110), B, "Personal", "Clothes")
    add(m, 22, "Expense", "Fun and Leisure", "Credit Card", jit(150), B, "Personal", "Gym + hobbies")
    if m in HEALTH:
        add(m, 17, "Expense", "Health", "Checking", HEALTH[m], (A if m % 2 else B), "Personal", "Pharmacy")
    if m in GIFTS:
        add(m, 14, "Expense", "Gifts", "Credit Card", GIFTS[m], (B if m % 2 else A), "Personal", "Present")
    if m in TRIPS:
        add(m, 26, "Expense", "Fun and Leisure", "Credit Card", TRIPS[m], "Joint", "Shared", "Weekend away")

    # transfers into the savings funds — these feed Savings & Net Worth
    add(m, 2, "Transfer", "Emergency Fund", "Savings", 850.00, "Joint", "Shared", "Auto transfer")
    add(m, 2, "Transfer", "Holiday Fund",   "Savings", 420.00, "Joint", "Shared", "Auto transfer")
    add(m, 2, "Transfer", "New Car",        "Savings", 610.00, "Joint", "Shared", "Auto transfer")

rows.sort(key=lambda r: r[0])

if CSV_OUT:
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow([r[0].isoformat()] + r[1:])

# ---------------------------------------------------------------- other tabs
BILLS = [("Rent or Mortgage", 2400, "Monthly", 1, "Yes"), ("Electricity", 130, "Monthly", 8, "Yes"),
         ("Water", 210, "Quarterly", 12, "No"),           ("Internet", 60, "Monthly", 15, "Yes"),
         ("Mobile phones", 50, "Monthly", 15, "Yes"),     ("Council tax", 195, "Monthly", 20, "Yes"),
         ("Home insurance", 240, "Yearly", 3, "No"),      ("Car insurance", 620, "Yearly", 9, "No"),
         ("Netflix", 15.99, "Monthly", 18, "Yes"),        ("Spotify", 11.99, "Monthly", 22, "Yes"),
         ("Gym", 39, "Monthly", 1, "Yes"),                ("Childcare", 480, "Monthly", 5, "Yes"),
         ("Car loan payment", 420, "Monthly", 25, "Yes")]
FUNDS  = [("Emergency Fund", 20000), ("Holiday Fund", 6000), ("New Car", 25000)]
ASSETS = [("Checking", 6400), ("Savings", 22560), ("Investments", 42000), ("Car", 18500), ("Home", 420000)]
LIABS  = [("Mortgage", 298000), ("Car loan", 11200), ("Credit card", 2300)]

# ---------------------------------------------------------------- xml injection
EPOCH = dt.date(1899, 12, 30)

def put(xml, ref, value):
    """Fill one existing (empty, pre-styled) cell, keeping its style."""
    row = int(re.match(r"[A-Z]+(\d+)", ref).group(1))
    pat = re.compile(r'<c r="%s"([^>]*?)(/>|>.*?</c>)' % ref, re.S)
    m = pat.search(xml)
    if not m:
        raise KeyError(f"{ref} not found")
    attrs = re.sub(r'\s*t="[^"]*"', "", m.group(1))
    if isinstance(value, dt.date):
        body = f'<c r="{ref}"{attrs}><v>{(value - EPOCH).days}</v></c>'
    elif isinstance(value, (int, float)):
        body = f'<c r="{ref}"{attrs}><v>{value}</v></c>'
    else:
        body = f'<c r="{ref}"{attrs} t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
    return xml[:m.start()] + body + xml[m.end():]

zin = zipfile.ZipFile(SRC)
parts = {n: zin.read(n) for n in zin.namelist()}
zin.close()

# Setup — the couple block
s = parts["xl/worksheets/sheet2.xml"].decode("utf-8")
for ref, val in (("N3", A), ("N4", B), ("N11", INC_A), ("N12", INC_B)):
    s = put(s, ref, val)
parts["xl/worksheets/sheet2.xml"] = s.encode("utf-8")

# Transactions
s = parts["xl/worksheets/sheet3.xml"].decode("utf-8")
for i, r in enumerate(rows):
    n = 5 + i
    for col, val in zip("ABCDEFGH", r):
        if val == "":
            continue
        s = put(s, f"{col}{n}", val)
parts["xl/worksheets/sheet3.xml"] = s.encode("utf-8")

# Bill Calendar
s = parts["xl/worksheets/sheet9.xml"].decode("utf-8")
for i, (name, amt, freq, due, paid) in enumerate(BILLS):
    n = 5 + i
    for col, val in (("A", name), ("B", amt), ("C", freq), ("F", due), ("G", paid)):
        s = put(s, f"{col}{n}", val)
parts["xl/worksheets/sheet9.xml"] = s.encode("utf-8")

# Savings & Net Worth
s = parts["xl/worksheets/sheet10.xml"].decode("utf-8")
for i, (name, target) in enumerate(FUNDS):
    s = put(s, f"A{6+i}", name); s = put(s, f"B{6+i}", target)
for i, (name, val) in enumerate(ASSETS):
    s = put(s, f"G{6+i}", name); s = put(s, f"H{6+i}", val)
for i, (name, val) in enumerate(LIABS):
    s = put(s, f"I{6+i}", name); s = put(s, f"J{6+i}", val)
parts["xl/worksheets/sheet10.xml"] = s.encode("utf-8")

shutil.copy(SRC, OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in parts.items():
        z.writestr(name, data)

# ---------------------------------------------------------------- what it adds up to
inc = sum(r[4] for r in rows if r[1] == "Income")
exp = sum(r[4] for r in rows if r[1] == "Expense")
tra = sum(r[4] for r in rows if r[1] == "Transfer")
share_a = INC_A / (INC_A + INC_B)
paid_a = sum(r[4] for r in rows if r[1] == "Expense" and r[6] == "Shared" and r[5] == A)
paid_b = sum(r[4] for r in rows if r[1] == "Expense" and r[6] == "Shared" and r[5] == B)
paid_j = sum(r[4] for r in rows if r[1] == "Expense" and r[6] == "Shared" and r[5] == "Joint")
pool = paid_a + paid_b
diff = paid_a - pool * share_a
NEEDS = {"Rent or Mortgage", "Utilities", "Groceries", "Transport", "Health",
         "Insurance", "Phone and Internet", "Debt"}
needs = sum(r[4] for r in rows if r[1] == "Expense" and r[2] in NEEDS)
wants = exp - needs
print(f"{len(rows)} строк, {YEAR}")
print(f"  доход {inc:,.0f}   расходы {exp:,.0f}   переводы {tra:,.0f}   net {inc-exp-tra:,.0f}")
print(f"  50/30/20: needs {needs/inc:.1%} (цель 50%)  wants {wants/inc:.1%} (30%)  savings {tra/inc:.1%} (20%)")
print(f"  общие расходы: {A} {paid_a:,.2f} · {B} {paid_b:,.2f} · Joint {paid_j:,.2f} (в дележ не идёт)")
print(f"  доля {A} {share_a:.1%} → справедливо {pool*share_a:,.2f}")
print(f"  ИТОГ: {B} owes {A} ${diff:,.2f}" if diff > 0 else f"  ИТОГ: {A} owes {B} ${-diff:,.2f}")
