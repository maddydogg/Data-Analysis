# Debt Payoff — demo data and listing video

`DebtPayoff_Light_DEMO.xlsx` and `DebtPayoff_Dark_DEMO.xlsx` are your workbooks
with the demo plan already in them. Open one, or upload it to Google Sheets, and
record.

Both editions carry the identical structure — same six sheets, same engine
formulas, same input cells — so one generator fills either, and both land on the
same numbers. Only the styling differs.

`make_demo_debt.py` regenerates it. The workbook carries a chart and openpyxl
drops charts on save, so the script writes into the sheet XML and only fills
cells that already exist in the template — currency and percent formats, the
banding, sheet protection, the Method dropdown and the chart all survive. It
also sets `fullCalcOnLoad` so Excel recalculates the engine on open.

```bash
python3 make_demo_debt.py "Debt Payoff  Light.xlsx" DebtPayoff_Light_DEMO.xlsx
python3 make_demo_debt.py "Debt Payoff  Dark.xlsx"  DebtPayoff_Dark_DEMO.xlsx
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


## The listing video

`debt_payoff_promo_1080.mp4` — 1080×1080, 30 fps, 14.9 s, no audio, cut from the
37.2 s recording of the demo file. Same frame as the budget videos (paper ground
built from the sheet's own palette, browser window, tab strip, progress bar), so
the two products read as one shop.

Ten shots at 1.742 s with 0.28 s cross-fades. The order is a story rather than a
tour: enter the debts, pick a method, read the plan, then prove the plan is live
by changing the method and watching every number move.

| in video | from raw | shot | caption |
| --- | --- | --- | --- |
| 0.00–1.74 | 0.4 s | Setup — the six debts | List your debts once |
| 1.46–3.20 | 2.6 s | Setup — Method dropdown open | Snowball, Avalanche or your own order |
| 2.93–4.67 | 13.0 s | Dashboard — Jun 2029, 34 months, $36 040, $6 290 | Your debt-free date, worked out |
| 4.39–6.13 | 21.4 s | Dashboard — total paid, paid so far, 30.2 % | What it costs — and how far you are |
| 5.85–7.59 | 15.4 s | Dashboard — payoff order | The order to pay them in |
| 7.31–9.05 | 17.4 s | Dashboard — balance over time | The balance falling to zero |
| 8.77–10.51 | 19.2 s | Dashboard — Snowball vs Avalanche + the verdict | Avalanche saves $744 — it tells you |
| 10.24–11.98 | 29.8 s | Setup — switching the method to Custom | Change the method… |
| 11.70–13.44 | 32.4 s | Dashboard — Custom: Jul 2029, 35 months, $8 662 | …and the whole plan recalculates |
| 13.16–14.90 | 25.4 s | Debt Tracker — paid so far, remaining, % paid | Log payments, watch each debt shrink |

The pair at 10.24 → 13.44 is the point of the whole cut: the method changes on
Setup and the Dashboard comes back with a different date, a different interest
total and a different payoff order. The competitor's debt video shows three
strategies as static tables; this one shows the sheet recalculating.

Nothing had to be cut for defects — the take carries no Sheets toast and no
tab-switch flashes. This recording is 1622×720 with no row-number gutter, so
crops start at x=0.

Copy on the frame: `SNOWBALL · AVALANCHE · CUSTOM · GOOGLE SHEETS & EXCEL`
(eyebrow), `Debt Payoff Plan` (headline), `DOES THE MATH` (window chip),
`PICK A METHOD — IT WORKS OUT THE ORDER, THE DATE AND THE INTEREST` and
`4 tabs · snowball, avalanche or your own order · yours to edit` (footer).

### Rebuild

```bash
./build_debt.sh /path/to/Screen_recording.webm /tmp/debt debt_payoff_promo_1080.mp4
```
