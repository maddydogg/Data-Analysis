# Annual Budget — Etsy listing video

`budget_promo_1080.mp4` — 1080×1080, 30 fps, 14.9 s, no audio. Cut from a 79 s
screen recording of the Google Sheets template.

| file | what it is |
| --- | --- |
| `budget_promo_1080.mp4` | the finished video |
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
