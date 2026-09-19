# Reseller Tracker — listing video

`reseller_tracker_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
46.1 s screen recording of the workbook in Google Sheets.
`reseller_tracker_cover_1080.jpg` is the frame at 1.2 s.

## The ground is the file's own column coding

The workbook prints one sentence under its own title: *Blue columns are yours,
green ones calculate.* So the ground is columns — wide, faint vertical bands
alternating its input blue `#F0F3FA` and its computed mint `#E0F3E8`, closed by
hairlines, exactly the way the sheet codes itself. The accent `#265674` is the
steel blue its input cells are written in, which is what keeps this frame apart
from the mint-and-green one the invoice listing uses.

Columns belong to this listing alone: horizontal section bands are the invoice
video's, the manila docket the estimate one's, the ledger ruling the
bookkeeping one's, the mesh debt's, the sweeps the budget planner's and the
single mint wash the ADHD planner's.

## The cut

The take walks eight sheets in 46 s — four times more than fits. The film keeps
the five that carry the argument, in the order a seller meets them.

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–2.6 s | Setup — the platform fee table, and a fee switched on a dropdown | 0.40 s |
| 2.3–5.2 s | Inventory & Sales — rows under the frozen header, settling | 9.40 s, 0.86× |
| 4.9–7.4 s | Lots — one box, 45.00 for 10 tees, **4.50 an item, worked out** | 18.60 s |
| 7.2–9.8 s | Dashboard — **WHERE TO BUY**, ROI by source | 36.10 s, 0.65× |
| 9.5–14.9 s | **Tax Summary, whole, one uncut move** | 39.6→45.0 s (stitched) |

The Setup shot carries its own small before/after, uncut: the *Fee on shipping?*
list opens on Depop and the answer goes Yes → No. The numbers that matter are
the ones the sheet reaches on its own — Garage sale at **227.6% ROI** against
retail clearance at 125%, and a tax page that ends `NET PROFIT 698.03`,
`Mileage 573.0 mi → 401.10`, `Profit after mileage 296.93`.

Two shots are slowed, for the same reason each time: the take does not hold
them long enough to read. The Inventory settle runs at 0.86×, and the Dashboard
— which the take holds for 1.7 s — at 0.65×.

Seven captions, lifted from the sheet: *Your platforms and their fees — once ·
One row per item · Blue is yours. Green calculates. · A box for one price? Cost
per item, done. · It tells you where to buy · Every figure the tax return needs
· Net profit — and the mileage on top.*

## The stitched page

Four of the five sheets fit one screen, so they are shot as they are. The Tax
Summary does not — 1,283 px of it against a 676 px viewport — and it is the one
sheet here with no frozen header, so the whole page is stitched out of the
take's eight resting moments between wheel steps and scrolled in one move from
the tax year down to the profit after mileage. `make_page.py` aligns each frame
to the previous over their overlap and writes every row from the MIDDLE of a
viewport: never the bottom edge, which carries the scrollbar and half-drawn
rows, and never the top edge, where the recording's VP8 encoder leaves a ghost
for a few frames after each step.

This take has a **676 px grid area** — the shortest of the recordings so far —
so this copy of `make_page.py` reads that height and searches the alignment out
to 220 px.

Inventory & Sales, Expenses and the Dashboard all freeze their header rows, so
their bodies scroll under a fixed head. None of them is stitched here; they are
each short enough to shoot whole.

## No Russian anywhere in the film

The recording is cropped to the grid area, which puts Sheets' own sheet-tab
strip and its toasts at y ≥ 694 — below every crop the film uses. The four
straight shots stop at 588, 568, 568 and 656 px, and the stitched page at 632.
The workbook is English throughout, down to the platform names.

## Rebuilding

```bash
./build_reseller_video.sh <recording.webm> work reseller_tracker_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1862×718** — both dimensions even — so the normalising pass only
fixes the frame rate and the missing duration header. The four straight shots
are the `SHOTS=(id start length crop speed)` table at the top of the build
script and the fifth is `TAX=`; `make_layers_reseller.py` owns everything drawn
around the screen and `make_page.py` owns the page and its scroll.
