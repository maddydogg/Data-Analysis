# Budget Planner — listing video

`budget_planner_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
48.9 s screen recording of the workbook in Google Sheets. Ten shots, cross-faded
over 0.28 s, in the same frame as the other listings.
`budget_planner_cover_1080.jpg` is the frame at 1.0 s, for the thumbnail.

This product is one white page with a bright green chart, so its ground is the
lightest of the three listings: near-white paper, one green sweep low-left and a
cooler one top-right, and the workbook's own `#7DFFA4` as the accent. The debt
listing owns the mint-and-cream mesh; the paycheck listing owns the blue-grey
paper. Two tab pills, because the product is two sheets and says so on its face.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 1 | The whole page — income, expenses, saved, left to spend | 0.55 s |
| 2 | Plan vs actual, category by category | 19.60 s |
| 3 | Spending by category | 0.60 s |
| 4 | Bills and subscriptions, at their true monthly cost | 6.30 s |
| 5 | Savings funds against their targets | 8.55 s |
| 6 | Debt payoff, smallest balance first | 11.40 s |
| 7 | **the Month list open** | 29.45 s |
| 8 | **April — the page has re-done itself** | 31.45 s |
| 9 | The Log | 34.90 s |
| 10 | The Log — a Category list, picked | 39.60 s |

Shots 7 and 8 are the pair that sells it. The cursor opens the Month list and
picks April; the header becomes April 2026, expenses go $3 228 → $3 159, and
every row of plan-vs-actual and every bar of the chart re-computes. The switch
lands at 31.1 s in the take and settles by 31.4 s, so shot 7 ends before it and
shot 8 opens on the finished page.

Lengths run 1.55–1.97 s rather than one fixed length, because the take does. The
page is scrolled at 2.6 / 5.2 / 10.7 / 13.3 s and the Log opens at 34.4 s, so no
shot crosses those; shots 1 and 3 are both taken from the first still stretch,
at different crops.

Sheets floats its Russian **"Преобразовать в таблицу"** toast over the Log from
36.5 s, at x980-1260 / y760-800. The shop sells in English, so both Log crops
stop at x950 and the toast never enters frame. Nothing is painted over.

Two crops also have to stop short of the Sheets tab strip, which sits at y820 in
this recording — the savings shot ends at y812 and the debt shot at y842.

## Rebuilding

```bash
./build_budget_video.sh <recording.webm> work budget_planner_promo_1080.mp4
```

Needs `python3` with `pillow` and `imageio-ffmpeg`. Playfair Display and
Montserrat are fetched into `work/fonts` on first run. The script normalises the
VP8 recording to constant-rate H.264 first — Chrome writes it variable-rate with
no duration header, and seeking it directly gives frames that drift from the
timings above.

The shot table is `SHOTS=(start length crop)` at the top of the script, written
against one specific take: a 1862×850 frame with no row-number gutter.
`make_layers_budget.py` owns everything drawn around the screen — title,
captions, tab pills, footer, progress bar.
