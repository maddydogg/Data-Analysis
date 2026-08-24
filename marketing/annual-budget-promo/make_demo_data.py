"""Generate a year of realistic demo transactions for AnnualBudgetSpreadsheet.xlsx.

Writes demo_transactions.csv — paste it into the Transactions tab at cell A5.
Every category is one of the 17 names the built-in dropdown allows, so no cell
picks up a validation warning marker on screen.
"""
import csv, random, calendar, os, sys

YEAR = 2026
random.seed(7)
OUT = sys.argv[1] if len(sys.argv) > 1 else "demo_transactions.csv"

rows = []
def add(month, day, typ, cat, acct, amount, note=""):
    day = min(day, calendar.monthrange(YEAR, month)[1])
    rows.append([f"{YEAR}-{month:02d}-{day:02d}", typ, cat, acct, f"{amount:.2f}", note])

def jitter(base, pct=0.14):
    return round(base * random.uniform(1 - pct, 1 + pct), 2)

SIDE   = {2: 320, 4: 480, 6: 260, 9: 640, 11: 410}
SHOP   = {1: 180, 2: 240, 3: 310, 4: 195, 5: 260, 6: 340, 7: 210, 8: 175,
          9: 290, 10: 225, 11: 380, 12: 420}
GIFTS  = {2: 70, 5: 95, 6: 130, 9: 80, 11: 110, 12: 260}
HEALTH = {1: 45, 3: 60, 5: 40, 8: 95, 10: 45, 12: 55}
TRIPS  = {3: 260, 7: 420, 10: 310}
# uneven transfers so "Saved by Month" is a real shape, not a flat line
SAVED  = {1: 900, 2: 900, 3: 700, 4: 1000, 5: 900, 6: 1200,
          7: 600, 8: 900, 9: 1100, 10: 900, 11: 800, 12: 1400}

for m in range(1, 13):
    # income
    add(m, 15, "Income", "Salary", "Checking", 2250.00, "Paycheck")
    add(m, 28, "Income", "Salary", "Checking", 2250.00, "Paycheck")
    if m in SIDE:
        add(m, 21, "Income", "Side income", "Checking", SIDE[m], "Freelance")
    # fixed needs
    add(m, 1,  "Expense", "Rent or Mortgage",   "Checking",    1250.00, "Rent")
    add(m, 4,  "Expense", "Utilities",          "Checking",    jitter(128, 0.28), "Electric + water")
    add(m, 6,  "Expense", "Insurance",          "Checking",    88.00,  "Home + contents")
    add(m, 8,  "Expense", "Phone and Internet", "Checking",    65.00,  "Fibre + mobile")
    add(m, 12, "Expense", "Debt",               "Checking",    220.00, "Loan payment")
    # variable needs
    for d, base in ((5, 118), (12, 96), (19, 132), (26, 88)):
        add(m, d, "Expense", "Groceries", random.choice(["Checking", "Credit Card"]), jitter(base, 0.22), "Weekly shop")
    add(m, 9,  "Expense", "Transport", "Checking", jitter(85, 0.3), "Fuel / transit")
    add(m, 23, "Expense", "Transport", "Credit Card", jitter(45, 0.35), "Fuel / transit")
    if m in HEALTH:
        add(m, 17, "Expense", "Health", "Checking", HEALTH[m], "Pharmacy")
    # wants
    add(m, 7,  "Expense", "Subscriptions",   "Credit Card", 27.97, "Streaming")
    add(m, 10, "Expense", "Subscriptions",   "Credit Card", 15.99, "Cloud + music")
    add(m, 11, "Expense", "Dining out",      "Credit Card", jitter(62, 0.35), "Dinner out")
    add(m, 24, "Expense", "Dining out",      "Credit Card", jitter(38, 0.4),  "Lunch")
    add(m, 27, "Expense", "Dining out",      "Credit Card", jitter(45, 0.4),  "Brunch")
    add(m, 18, "Expense", "Fun and Leisure", "Credit Card", jitter(88, 0.35), "Cinema / gym")
    if m in TRIPS:
        add(m, 22, "Expense", "Fun and Leisure", "Credit Card", TRIPS[m], "Weekend away")
    if m in SHOP:
        add(m, 20, "Expense", "Shopping", "Credit Card", SHOP[m], "Clothes / home")
    if m in GIFTS:
        add(m, 14, "Expense", "Gifts", "Credit Card", GIFTS[m], "Birthday")
    # money moved to savings
    add(m, 16, "Transfer", "Savings", "Savings", SAVED[m], "Monthly transfer")

rows.sort(key=lambda r: r[0])
with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerows(rows)

inc = sum(float(r[4]) for r in rows if r[1] == "Income")
exp = sum(float(r[4]) for r in rows if r[1] == "Expense")
tra = sum(float(r[4]) for r in rows if r[1] == "Transfer")
NEEDS = {"Rent or Mortgage", "Utilities", "Groceries", "Transport", "Health",
         "Insurance", "Phone and Internet", "Debt"}
needs = sum(float(r[4]) for r in rows if r[1] == "Expense" and r[2] in NEEDS)
wants = exp - needs
print(f"{OUT}: {len(rows)} строк за {YEAR}")
print(f"  доход {inc:,.0f}   расходы {exp:,.0f}   переводы в сбережения {tra:,.0f}   net {inc-exp-tra:,.0f}")
print(f"  50/30/20 факт: needs {needs:,.0f} ({needs/exp:.0%})  wants {wants:,.0f} ({wants/exp:.0%})  savings {tra:,.0f}")
print(f"  при Setup!J4 = 4700 цели: needs {4700*12*0.5:,.0f}  wants {4700*12*0.3:,.0f}  savings {4700*12*0.2:,.0f}")
