# Paycheck Budget — demo data and listing video

`paycheck_budget_promo_1500.mp4` is a 14.8 s listing video for the Paycheck
Budget workbook, cut in the same shape as the reference ad: title, a feature
list that grows shot by shot, the sheet running inside a laptop, a pill and a
round badge over the screen, and a footer strip.

`PaycheckBudget_Light_DEMO.xlsx` is the same workbook with one month of demo
data in it — open it, or upload it to Google Sheets, and record your own take.
`paycheck_budget_cover.jpg` is the frame at 13.6 s, for the listing thumbnail.

There was no screen recording to cut, so the "recording" is synthesised: every
sheet is rendered headlessly by LibreOffice from the demo workbook, and the pan,
the zoom, the cursor and the dropdown are composited on top in Pillow. Nothing
on screen is drawn by hand — the pixels are the workbook's own output, at 200
dpi, which is why the numbers on camera add up.

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
deliberately small and positive: it reads as a month that balanced.

Rent is the one large expense, so `Spending by category` has a shape; two funds
are far from their target and one is close, so the Savings tab is not a row of
identical bars.

## The cut

| | shot | new line in the list |
| ---: | --- | --- |
| 0.0 s | Start Here | 8 ready-to-use tabs |
| 1.5 s | Setup | Set it up once |
| 3.3 s | Paycheck Budget, scrolling through the split | Split across Paycheck 1 & 2 |
| 5.3 s | Transactions, scrolling the log | One log for everything |
| 7.2 s | **Bill Calendar — the interaction** | True monthly cost of each bill |
| 10.2 s | Savings | Sinking funds & debt payoff |
| 11.2 s | Debt | |
| 12.2 s | Dashboard | |

Shots cross-fade over 0.22 s. Total 14.8 s, under Etsy's 15 s ceiling; 1500×1124
(4:3, the reference's ratio), H.264, ~3 MB, no audio.

The Bill Calendar shot is the one that sells the product. The cursor opens the
Frequency dropdown on the Gym row, walks down to `Monthly`, clicks — and the
sheet under it is swapped for a second render where that cell really is Monthly,
so `Monthly cost` falls from **$104.00 to $24.00** and the total from
**$2,033.96 to $1,953.96**, both flashed in amber for a beat. Two real renders,
not a drawn number.

The dropdown lands on the cell because `render_sheets.py` reads the cell's
position out of the PDF text layer (`search_for`) rather than guessing pixels.
That shot holds its zoom still so the overlay cannot drift.

## Rebuilding

```bash
./build_paycheck.sh "Paycheck Budget  Light.xlsx"
```

Needs `libreoffice-calc` (headless) and `python3` with `openpyxl pymupdf pillow
numpy imageio-ffmpeg`. Montserrat and Inter are fetched from Google Fonts into
`work/fonts` on first run. The steps run standalone too:

| | |
| --- | --- |
| `make_demo_paycheck.py src.xlsx out.xlsx` | writes the demo month into a copy |
| `render_sheets.py demo.xlsx` | LibreOffice → PDF → cropped PNG per sheet, + cell geometry |
| `make_video.py` | composites `work/frames/f_%04d.png` |

`render_sheets.py` builds its own LibreOffice profile with `OOXMLRecalcMode=0`.
Without it LibreOffice keeps Excel's cached values and every sheet renders as
zeros, because openpyxl writes formulas without results.

## Two notes on the workbook itself

`Dashboard!A4` holds the label `Month`, but column A is the 2-character gutter
and B4 carries the value, so the label renders clipped to `M`. The generator
clears that cell in the demo copy to keep it off camera — worth giving the label
a wider home in the template.

The footer strip claims only what the workbook itself says: Sheets and Excel, 8
tabs, and that the maths is already done. There is no brand line and no star
rating in it — add yours in `make_bg()` in `make_video.py`.
