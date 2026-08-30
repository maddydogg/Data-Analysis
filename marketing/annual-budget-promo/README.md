# Annual Budget — Etsy listing video

`budget_promo_1080.mp4` — 1080×1080, 30 fps, 14.9 s, no audio. Cut from a 79 s
screen recording of the Google Sheets template.

| file | what it is |
| --- | --- |
| `budget_promo_1080.mp4` | the finished video (light theme) |
| `budget_dark_promo_1080.mp4` | second cut, from the dark-theme recording |
| `budget_dark_cover_1080.jpg` | still from the dark cut |
| `build_dark.sh`, `make_layers_dark.py` | build + layers for the dark cut |
| `budget_couple_promo_1080.mp4` | third cut — the couples edition (Split and Settle) |
| `budget_couple_cover_1080.jpg` | still from the couples cut |
| `build_couple.sh`, `make_layers_couple.py` | build + layers for the couples cut |
| `budget_cover_1080.jpg` | still frame, usable as a listing image |
| `build.sh` | rebuilds the video from the raw recording |
| `make_layers.py` | renders the design layers (background, window, captions, tab pills) |
| `SHOOTING_SCRIPT.md` | the script the recording was shot from |
| `make_demo_data.py`, `demo_transactions.csv` | a year of demo transactions for the workbook |

## Design

Deliberately not the Reading Tracker frame. Instead of a laptop mockup and a
circular badge this one uses a browser window (title bar, address pill, a small
`UPDATES ITSELF` chip), a strip of all nine tab names under the window where the
tab being shown lights up, and a progress bar that fills across the bottom over
the 14.9 s.

Palette comes from `AnnualBudgetSpreadsheet.xlsx` and from the recording itself:
background runs from a tint of `EAF5EE` to a shade of `DFF3EA` (the mint used for
section headers on every sheet), type is `33566B`, the lit tab pill is `33566B`
with mint text, and the progress bar picks up the `78FAA0` green of the charts.

## The ten shots

| in video | from raw | shot | caption | tab lit |
| --- | --- | --- | --- | --- |
| 0.00–1.76 | 1.0 s | Setup — income, categories, accounts | Set it up once | Setup |
| 1.46–3.22 | 17.2 s | Transactions, category dropdown open | Log it once — the year fills in | Transactions |
| 2.92–4.68 | 21.6 s | Annual Dashboard — KPIs and month table | Your whole year on one screen | Dashboard |
| 4.38–6.14 | 28.0 s | Spending by Category doughnut | See where the money actually goes | Dashboard |
| 5.84–7.60 | 34.1 s | Income vs Expenses by month | Charts build themselves | Dashboard |
| 7.30–9.06 | 38.5 s | 50 / 30 / 20 Rule | 50 / 30 / 20, checked for you | 50-30-20 |
| 8.76–10.52 | 43.2 s | Spending Tracker | Every category, ranked | Spending |
| 10.22–11.98 | 50.8 s | Month View, month picker open | Any month on its own | Month View |
| 11.68–13.44 | 61.6 s | Bill Calendar, frequency dropdown | The true cost of every bill | Bills |
| 13.14–14.90 | 77.0 s | Savings & Net Worth | Savings goals and net worth | Net Worth |

Shots cross-fade over 0.30 s; the video opens and closes on a white fade so it
loops cleanly in Etsy's player.

## The Russian frames

From 62.6 s to 71.4 s of the recording Sheets shows a Russian
"Преобразовать в таблицу" toast, to the right of x=820 in the frame. The Bill
Calendar shot is taken at 61.6 s and its crop stops at x=820, so the toast is
outside the picture — the dropdown moment is kept, the toast never enters frame.

## Rebuild

```bash
./fetch_fonts.sh /tmp/promo/fonts        # from ../book-tracker-promo
./build.sh /path/to/Screen_recording.webm /tmp/promo budget_promo_1080.mp4
```

Captions live in `SCENES` in `make_layers.py`; shot timings and crops are the
`cut` lines in `build.sh`.


## Dark cut

A second 14.9 s video, `budget_dark_promo_1080.mp4`, built from the 62 s
recording of the workbook in its dark theme. Same structure — ten shots, browser
window, tab strip, progress bar — with the frame flipped to match the sheet:
background gradient `#161F38` → `#090D1A`, accent `#7BFFA2` (the green of the
sheet's headings and chart bars), type `#EAF3F0`, and the opening and closing
fades on the page's own dark ground instead of white.

| in video | from raw | shot | caption |
| --- | --- | --- | --- |
| 0.00–1.76 | 3.2 s | Setup | Set it up once |
| 1.46–3.22 | 9.4 s | Transactions, account dropdown open | Log it once — the year fills in |
| 2.92–4.68 | 15.5 s | Annual Dashboard — KPIs + month table | Your whole year on one screen |
| 4.38–6.14 | 20.6 s | 50/30/20 table + Spending by Category | See where the money actually goes |
| 5.84–7.60 | 28.0 s | Income vs Expenses by month | Charts build themselves |
| 7.30–9.06 | 33.5 s | 50 / 30 / 20 Rule | 50 / 30 / 20, checked for you |
| 8.76–10.52 | 36.8 s | Spending Tracker | Every category, ranked |
| 10.22–11.98 | 44.6 s | Month View, month picker open | Any month on its own |
| 11.68–13.44 | 53.2 s | Bill Calendar, frequency changed | The true cost of every bill |
| 13.14–14.90 | 60.2 s | Savings & Net Worth | Savings goals and net worth |

Defects kept out of frame:

- the Russian "Преобразовать в таблицу" toast, on screen 1.5–3.0 s and
  52.0–59.0 s — the Setup shot starts after it clears, and the Bill Calendar
  shot is cropped to x<836 while the toast sits at x 867–1131;
- the white flashes while tabs switch at 39.0 s and 49.5 s — no shot spans them;
- the light row-number gutter and column-letter strip — every crop starts at
  x=56, y≥28.


## Couples cut

`budget_couple_promo_1080.mp4` — 14.9 s, from the 41.8 s recording of the
edition that adds **Split and Settle** plus `Paid by` and `Share` columns on
Transactions. That feature leads the story, so this cut runs eleven shots of
1.61 s with 0.28 s cross-fades instead of ten of 1.76 s, the tab strip carries
ten tabs, and the header reads FOR COUPLES & HOUSEHOLDS with the footer line
"one log feeds the whole year — and splits it fairly".

| in video | from raw | shot | caption | tab lit |
| --- | --- | --- | --- | --- |
| 0.00–1.61 | 3.0 s | Transactions — Paid by / Share columns | Mark who paid and what's shared | Transactions |
| 1.33–2.94 | 5.5 s | Transactions — category dropdown open | Dropdowns do the typing | Transactions |
| 2.66–4.27 | 8.5 s | Annual Dashboard — KPIs + month table | Your whole year on one screen | Dashboard |
| 3.99–5.60 | 13.5 s | Spending by Category doughnut | See where the money actually goes | Dashboard |
| 5.32–6.93 | 16.5 s | Income vs Expenses + Saved by Month | Charts build themselves | Dashboard |
| 6.65–8.26 | 19.4 s | 50 / 30 / 20 Rule | 50 / 30 / 20, checked for you | 50-30-20 |
| 7.97–9.58 | 21.8 s | Spending Tracker | Every category, ranked | Spending |
| 9.30–10.91 | 24.5 s | Split and Settle — "Sam owes Alex $6,030.25" | Split by income — who owes whom | Split & Settle |
| 10.63–12.24 | 28.5 s | Month View — month picker open | Any month on its own | Month View |
| 11.96–13.57 | 31.6 s | Bill Calendar | The true cost of every bill | Bills |
| 13.29–14.90 | 39.3 s | Savings & Net Worth | Savings goals and net worth | Net Worth |

Defects kept out of frame: the Russian "Преобразовать в таблицу" toast, on
screen 1.5–2.5 s and 33.5–39.0 s — no shot overlaps either window. This
recording has no row-number gutter, so crops start at x=0 rather than x=56.
