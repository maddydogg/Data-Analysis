# Simple Reseller Tracker — listing video

`reseller_simple_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
23.2 s screen recording of the workbook in Google Sheets.
`reseller_simple_cover_1080.jpg` is the frame at 1.2 s.

This is the two-sheet light edition of the same family as
`../reseller-tracker-promo`, so it carries a different listing title —
**Simple Reseller Tracker** — even though the sheet writes "Reseller Tracker"
at the top of itself. Two listings in one shop cannot share a name.

## The ground is the file's own chart

The one thing in this workbook that is not a table is its *Profit by month*
chart, drawn in `#78E3A4`. So the ground is that chart: twelve faint bars along
the foot of the frame at the heights the demo year actually reaches — 33.71 in
January up to 191.00 in April — with the last three still at zero, because the
year is not over. The paper is its section mint `#E0F3E8` opened up and the
pills are filled with the chart green itself.

Bars belong to this listing alone: the full tracker's frame is vertical column
bands, the invoice's horizontal section bands, the estimate's a manila docket.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–3.6 s | Items — the rows come to rest under the frozen header | 3.30 s, 0.56× |
| 3.3–6.5 s | **the beat, uncut: pick a platform, the fee and the profit fill in** | 7.60 s, 0.75× |
| 6.2–9.3 s | Summary head — profit, sales, stock, beside the fee table behind them | 11.10 s |
| 9.1–12.2 s | BY MONTH — every month and the year | 17.00 s |
| 11.9–14.9 s | BY PLATFORM — which platform actually pays | 20.00 s |

The middle shot is the whole argument in one frame, with no cut in it: the
Platform list is open on *Vinted*, which charges nothing, *Poshmark* is picked,
and **Fees goes 0.00 → 3.47 while Profit goes 13.11 → 9.64**. The row above it
did the same thing a moment earlier — 16.00 → 13.72 — and both are in shot. It
is exactly what the sheet promises under its own title: *Add Sold for when it
sells and the fees and profit fill in. Fees are set on Summary.*

The numbers the Summary reaches on its own: `TOTAL 50 items · 1,815.92 sold ·
193.24 in fees · 960.73 profit`, and by platform, Mercari at 279.92 against
Whatnot at 99.28 on much the same number of items.

Seven captions, lifted from the sheet: *Two sheets — type in the blue cells ·
One row per item, sold or not · Pick the platform… · …and the fee and the
profit fill in · Profit, sales, stock — and the fees behind them · Every month,
totalled · And which platform actually pays.*

## Nothing is stitched here

Both sheets freeze their head, and the take reads them the way anyone reads a
spreadsheet: scroll, stop, look. Neither sheet is longer than the thing it has
to say once you are at the right stop, so four of the five shots are the stops
themselves, slowed to the time it takes to read them, and the fifth is the beat
at 0.75×. The take also pans sideways twice mid-scroll, which is another reason
a single stitched travel would not have been honest to it.

`make_page.py` is still here, and gained `GRID_Y` while this listing was cut —
the first row of the grid that actually scrolls, for a sheet that freezes its
title band. It is unused by this build and kept for the next take that needs it.

## No Russian anywhere in the film

The recording is cropped to the grid area, which puts Sheets' own sheet-tab
strip and its toasts at y ≥ 694 — below every crop the film uses. The five
shots stop at 630, 623, 580, 580 and 522 px. The workbook is English
throughout, down to the platform names.

## Rebuilding

```bash
./build_simple_video.sh <recording.webm> work reseller_simple_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1862×718** — both dimensions even — so the normalising pass only
fixes the frame rate and the missing duration header. The five shots are the
`SHOTS=(id start length crop speed)` table at the top of the build script;
`make_layers_simple.py` owns everything drawn around the screen.
