# Paycheck Budget — demo data and listing video

`paycheck_budget_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
38.6 s screen recording of the workbook in Google Sheets. Same paper frame as
the other listings, keyed to this workbook's own palette — the mint DFF3EA of
its section headers, the pale blue E7ECFA of its cards and the 3E7CC0 its input
cells are written in. No green anywhere, so it reads as a sibling of the debt
listing rather than a copy of it.

`paycheck_budget_cover_1080.jpg` is the frame at 2.4 s, for the thumbnail.

`PaycheckBudget_Light_DEMO.xlsx` and `PaycheckBudget_Dark_DEMO.xlsx` are the
workbooks with the demo month already in them — the light one is the file the
take was recorded from. Both editions carry the identical structure (same eight
sheets, same formulas, same input cells), so one generator fills either and both
land on the same numbers; only the styling differs. `make_demo_paycheck.py`
regenerates them from a clean template.

## The month the demo describes

July 2026. Month start `2026-07-01`, paychecks on the 3rd and the 17th.

| | |
| --- | ---: |
| Paycheck 1 / Paycheck 2 | $2,100.00 each |
| Extra income (freelance, 22 Jul) | $320.00 |
| Planned across 12 categories | $3,325.00 |
| 42 logged transactions | income, expense and transfer |
| Transfers to five sinking funds | $1,230.00 |
| Three debts, $26,450 borrowed | $16,570.00 remaining |

Which lands the Dashboard on **income $4,520.00 · expenses $3,208.68 · saved
$1,230.00 · left $81.32**, and bills at **$2,033.96 a month**. The left-over is
small and positive on purpose: it reads as a month that balanced.

Rent is the one large expense, so `Spending by category` has a shape; two funds
sit far from target and one is close, so Savings is not a row of identical bars.

## The cut

Ten shots, cross-faded over 0.28 s. Lengths vary between 1.52 s and 1.80 s
because the take does — a shot is as long as its window in the recording allows,
and the ten add up to exactly 14.9 s.

| | shot | from the take |
| ---: | --- | ---: |
| 1 | Setup — paychecks, categories, funds, debts | 0.60 s |
| 2 | Dashboard — income, expenses, saved, left | 5.20 s |
| 3 | Dashboard — spending by category and the chart | 8.30 s |
| 4 | Paycheck Budget — planned vs actual, % used | 11.60 s |
| 5 | Transactions — the log | 15.00 s |
| 6 | Transactions — **the Account dropdown, picked** | 16.85 s |
| 7 | Transactions — **the Category dropdown, picked** | 25.55 s |
| 8 | Bill Calendar — weekly and yearly bills as a monthly cost | 29.95 s |
| 9 | Savings — five funds against their targets | 34.05 s |
| 10 | Debt — three debts, smallest first | 36.20 s |

Shots 6 and 7 are the ones that sell it: the cursor opens a real data-validation
list and picks from it, and the cell changes on camera. Nothing is sped up or
re-timed.

Three things the shot list steers around, all read off the take rather than
guessed:

- Sheets floats a Russian **"Преобразовать в таблицу"** toast — at y 777 from
  17 s and at y 455–500 from 31.5 s. Every crop is sized to keep it out of
  frame; that is why the Bill Calendar shot is the short one, ending at 31.47 s.
- The tab switches land at 2.6 / 10.5 / 14.8 / 29.9 / 34.0 / 35.8 s, so no shot
  may cross them.
- The Dashboard is scrolled between 4 s and 7.3 s, so shot 2 is taken before it
  and shot 3 after.

## Rebuilding

```bash
./build_paycheck_video.sh <recording.webm> work paycheck_budget_promo_1080.mp4
```

Needs `python3` with `pillow` and `imageio-ffmpeg`; Playfair Display and
Montserrat are fetched into `work/fonts` on first run. The script normalises the
VP8 recording to constant-rate H.264 first — Chrome writes it variable-rate with
no duration header, and seeking it directly gives frames that drift from the
timings above.

Changing the workbook means re-recording, and the shot table is written against
one specific take: `SHOTS=(start length crop)` at the top of the script, with a
1844×852 frame and no row-number gutter. `make_layers_paycheck.py` owns
everything drawn around the screen — title, captions, tab pills, footer.

To regenerate the demo workbook:

```bash
python3 make_demo_paycheck.py "Paycheck Budget  Light.xlsx" PaycheckBudget_Light_DEMO.xlsx
python3 make_demo_paycheck.py "Paycheck Budget  Dark.xlsx"  PaycheckBudget_Dark_DEMO.xlsx
```

It writes only into cells the template already has, and sets `fullCalcOnLoad` so
Excel recalculates the engine on open (openpyxl writes formulas without cached
results; Google Sheets computes them anyway). Add `--page-setup` for the
one-page-per-sheet printing that headless rendering wants — the delivered demo
workbooks keep the template's own page setup.

## One note on the workbook itself

`Dashboard!A4` holds the label `Month`, but column A is the 2-character gutter
and B4 carries the value, so the label renders clipped to `M`. The generator
clears that cell in the demo copy to keep it off camera — worth giving the label
a wider home in the template.
