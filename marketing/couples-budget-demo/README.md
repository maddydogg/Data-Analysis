# Couples & Family Budget — demo data

`CouplesFamilyBudget_DEMO.xlsx` is the light workbook with a full year of 2026
demo data already in it. Open it, or upload it to Google Sheets, and record.

`make_demo.py` regenerates it; `demo_transactions_couples.csv` is the same 269
rows as plain text, if you would rather paste them into a fresh copy at `A5`.

```bash
python3 make_demo.py CouplesFamilyBudget.xlsx CouplesFamilyBudget_DEMO.xlsx demo_transactions_couples.csv
```

## Why it writes XML instead of using openpyxl

The workbook carries four dashboard charts, and openpyxl drops charts when it
saves. So the script edits the sheet XML directly and only fills cells that
already exist in the template, keeping their styles — dates stay dates, amounts
stay currency, banding, sheet protection, the dropdowns and the charts all
survive untouched.

## What the demo says

Two partners, **Alex** and **Sam**, on `Setup`: incomes 5 200 and 3 800 a month,
split mode **By income**, which gives shares of 57.8% / 42.2%.

| | |
| --- | --- |
| Income (year) | 112 200 |
| Expenses | 66 056 |
| Saved (transfers) | 22 560 |
| Net | 23 584 |

**50 / 30 / 20** — all three rows land on track: needs 47.6% (target 50%),
wants 11.3% (30%), savings 20.1% (20%).

**Split and Settle** — shared spending is deliberately lopsided so the tab has
something to say: Alex paid 32 591.92, Sam paid 15 075.05, and 9 860.00 went
out of the joint account (joint payments are shown but excluded from the split,
which is how the formula works). Alex's fair share is 27 540.92, so the tab
reads **"Sam owes Alex $5,051.00"**. Every shared expense has a Paid by, so the
Check row shows "No errors ✓".

**Savings funds** — Emergency Fund 10 200 / 20 000 (51%), Holiday Fund
5 040 / 6 000 (84%), New Car 7 320 / 25 000 (29%).

**Net worth** — assets 509 460, liabilities 311 500, net worth **197 960**.

**Bill Calendar** — 13 bills across weekly-to-yearly frequencies (Water is
quarterly, home and car insurance yearly) so the "true monthly cost" column
does visible work; total 4 245.98 a month.

The transaction mix per month: two salaries, a bonus in June and December,
shared rent / utilities / groceries / transport / phone / dining, insurance and
the car loan from the joint account, personal shopping, leisure, health and
gifts, three weekend trips, and three standing transfers into the funds.
