# Estimate & Invoice — listing video

`estimate_invoice_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
43.0 s screen recording of the workbook in Google Sheets.
`estimate_invoice_cover_1080.jpg` is the frame at 1.2 s.

The seventh listing, so the ground moves again: a manila job docket. Kraft paper
with the fibre still in it, a label band across the head where the title is
written, a folded corner bottom right, and the deep teal `#0F5E52` the workbook
writes its own section headers in. Nothing here is a finance sheet's ground —
it is the thing a trade carries the job on.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–5.4 s | **the whole Estimate, one move, no cuts** | 6.2→3.4 s (stitched) |
| 5.1–7.7 s | **the rate type — open, pick, re-price, uncut** | 12.60 s, 0.81× |
| 7.4–11.9 s | **the whole Invoice, one move, landing on BALANCE DUE** | 22.9→30.2 s (stitched) |
| 11.7–14.9 s | **the Job Log — three jobs filed, KPIs recount, uncut** | 35.10 s |

All four shots are uncut, and two of them are whole pages travelling past in one
continuous move. That is the listing's argument made literally: a job is quoted
on one page, invoiced on one page and filed on one row, so the film never chops
a page into close-ups and never cuts between a before and an after.

The middle shot is the one that shows the sheet doing the arithmetic. The rate
type list is open on *After hours*; *Weekend* is picked; the rate goes 90.00 →
95.00, the line amount 135.00 → 142.50 and **Labour subtotal 797.50 → 805.00** —
all inside a single frame, because cutting there is exactly what makes a viewer
doubt the sheet did the work. The take only holds the open list for four tenths
of a second, which is less than it takes to read four rate types and then watch
a number move, so this shot alone runs at 0.81×.

The closer does the same on the Job Log: three statuses are set and the KPI row
above recounts, `OPEN VALUE 1,210.00 → 790.00`, with `INVOICED`, `PAID` and
`OUTSTANDING` moving with it.

Six captions, all lifted from the sheet: *Everything for one job, on one page ·
Labour, materials, totals — one sheet · Pick the rate type. It re-prices
itself. · The same job, now an invoice · Deposit off. Balance due, ready to
send. · Mark it invoiced — the job log keeps score.* They are timed against the
film rather than against shots, so a line can change while a page keeps moving
under it.

## The two stitched pages

Neither the Estimate nor the Invoice fits a viewport: 805 px of grid against
1,583 px and 1,636 px of page. The take wheels **up** through the Estimate
(6.2 s → 3.4 s) and **down** through the Invoice (22.9 s → 30.2 s), so each pass
is read in its own direction. `make_page.py` takes the moments a pass is at rest
between wheel steps — 7 of them for the Estimate, 15 for the Invoice — aligns
each frame to the previous one over their overlap, and writes every row from the
MIDDLE of a viewport: never the bottom edge, which carries the scrollbar and
half-drawn rows, and never the top edge, where the recording's VP8 encoder
leaves a ghost for a few frames after each step. It trims the blank tail and
scrolls what is left.

This take wheels in long steps — up to 280 px between rests, against the 130 the
earlier takes needed — so this copy of `make_page.py` searches the alignment out
to 320 px and reads a 805 px grid.

## No Russian anywhere in the film

The seller works the US market, so nothing Cyrillic may reach a frame. The
recording is cropped to the grid area, which puts Sheets' own sheet-tab strip
and its toasts at y ≥ 812 — below every crop the film uses. The stitched pages
stop at 761 px (805 grid less the 44 px bottom edge), the rate-type shot stops
at 790 px, and the Job Log shot stops at 733 px. The workbook itself is English
throughout: *Redline Home Repairs*, `EST-1001`, `INV-2003`, and the rate types
*Standard · After hours · Weekend · Flat rate*.

## Rebuilding

```bash
./build_estimate_video.sh <recording.webm> work estimate_invoice_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1862×844** — both dimensions even — so the normalising pass only
fixes the frame rate and the missing duration header. The two rest-frame passes
are `EST=` and `INV=` at the top of the build script, the two straight cuts are
the `-ss`/`-t`/`crop` lines beside them; `make_layers_estimate.py` owns
everything drawn around the screen and `make_page.py` owns the pages and their
scrolls.
