# Debt Payoff (Light) — demo data

`DebtPayoff_Light_DEMO.xlsx` is your workbook with a demo plan already in it.
Open it, or upload it to Google Sheets, and record.

`make_demo_debt.py` regenerates it. The workbook carries a chart and openpyxl
drops charts on save, so the script writes into the sheet XML and only fills
cells that already exist in the template — currency and percent formats, the
banding, sheet protection, the Method dropdown and the chart all survive. It
also sets `fullCalcOnLoad` so Excel recalculates the engine on open.

```bash
python3 make_demo_debt.py "Debt Payoff  Light.xlsx" DebtPayoff_Light_DEMO.xlsx
```

## The plan the demo describes

Six debts, `$36,040` total, minimums `$945` a month, `$400` extra, start
`2026-08-01`, method **Snowball**.

| Debt | Balance | APR | Min | Custom order |
| --- | ---: | ---: | ---: | ---: |
| Store Card | 640 | 27.9 | 30 | 6 |
| Medical Bill | 1 200 | 0.0 | 50 | 5 |
| Credit Card A | 8 900 | 25.9 | 220 | 3 |
| Credit Card B | 3 100 | 21.9 | 95 | 4 |
| Car Loan | 12 800 | 7.4 | 345 | 1 |
| Student Loan | 9 400 | 4.9 | 205 | 2 |

Running the same arithmetic as the Engine sheet, the Dashboard should read:

| | |
| --- | --- |
| Debt-free date | **Jun 2029** (34 months from the start date) |
| Total debt | $36 040 |
| Total interest | ≈ $6 290 |
| Paid so far / progress | $10 890 → **30.2 %** |
| Snowball vs Avalanche | 34 mo / $6 290 versus 33 mo / $5 546 |
| The comparison line | *"Avalanche would save you $744 in interest."* |

Payoff order comes out different under each method, which is the point of the
product — Snowball runs Store Card, Medical Bill, Credit Card B, Credit Card A,
Student Loan, Car Loan; Avalanche runs Store Card, Credit Card A, Credit Card B,
Car Loan, Student Loan, Medical Bill; the Custom column is filled with a third
order (largest balance first) so switching the method to Custom also does
something visible.

Every minimum payment is comfortably above its debt's monthly interest, so the
"this debt never pays off" warning never fires, and the balance curve reaches
zero well inside the engine's 60-month window.

The rows are deliberately not typed in payoff order — the Dashboard sorts them
for you, and the difference between the Setup table and the PAYOFF ORDER list
reads on camera.

## Shot list for the recording

Nine or ten shots, 5–8 seconds each, one continuous take, English UI, gridlines
off, `Ctrl+Shift+F` to hide the Sheets menus.

1. **Setup** — the debt table, filled.
2. **Setup** — open the Method dropdown (Snowball / Avalanche / Custom), hold it open.
3. **Dashboard** — the KPI row: debt-free date, months to go, total debt, total interest.
4. **Dashboard** — the payoff order list.
5. **Dashboard** — the balance-over-time chart.
6. **Dashboard** — Snowball vs Avalanche table and the sentence under it.
7. **The money shot** — switch Method to Avalanche on Setup, go back to the
   Dashboard, let the numbers land. Do it slowly, this is the one that sells.
8. **Debt Tracker** — paid so far, remaining, the % column.
9. **Setup** — change Extra / month from 400 to 800, back to the Dashboard, watch
   the debt-free date move in. Leave it as the last beat, or set it back to 400.
10. **Start Here** — optional, for a "how it works" shot.
