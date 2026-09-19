# Job Invoice — listing video

`job_invoice_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
32.9 s screen recording of the workbook in Google Sheets.
`job_invoice_cover_1080.jpg` is the frame at 1.2 s.

## The ground is the file's own palette

Asked for, and taken literally. The workbook draws its section headers as
full-width bands of `#E0F3E8`, writes those headers in the slate `#3E5058` and
its values in a steel blue near `#38566A`. So the frame is built the way the
sheet is — mint bands separated by paper, one of them carrying the title — and
there is no colour in it the file does not already use. The accent `#2D6A57` is
that same mint taken down to where type can sit on it.

That band device belongs to this listing alone: the mesh is the debt video's,
the blue-grey paper the paycheck one's, the green sweeps the budget planner's,
the single mint wash the ADHD planner's, the ledger ruling the bookkeeping
one's and the manila docket the estimate one's.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–3.3 s | **the whole Setup sheet, held — it fits one screen** | 0.8 / 2.2 s (stitched) |
| 3.0–6.0 s | **a line switched to a flat price, uncut** | 10.40 s |
| 5.7–8.7 s | **the rate type picked, uncut** | 20.95 s, 0.8× |
| 8.4–14.9 s | **the whole Invoice, one move, to BALANCE DUE** | 4.6 + 23.0→31.8 s (stitched) |

All four shots are uncut. The two middle ones are the sheet doing the pricing
inside a single frame, because cutting between a before and an after is what
makes a viewer doubt it happened:

* **Flat price.** The rate type list is open on *After hours*; *Flat rate* is
  picked; the Rate column empties, the **Fixed price cell turns amber** because
  that is what the sheet now needs, and `Labour subtotal 702.50 → 477.50`.
* **Rate type.** The list opens again, *Weekend* is picked, and the rate
  `65.00 → 95.00`, the line amount `260.00 → 380.00` and
  `Labour subtotal 640.00 → 760.00` all move at once. The take leaves only
  eight tenths of a second on the new number before it starts scrolling, so
  this shot alone runs at 0.8×.

Six captions, lifted from the sheet: *Fill this in once — everything reads from
here · Switch a line to a flat price… · …and it asks for the price, not the
hours · Pick the rate type — the subtotal moves with it · One page per job ·
Deposit off. Balance due, ready to send.*

## The two stitched pages, and two things `make_page.py` learned here

**The Setup sheet is held, not scrolled.** Stitched it is 851 px against the
window's own 877, so it fits — and when the claim is that the whole setup is one
screen, the honest shot is the whole screen. `make_page.py` now centres a page
shorter than the viewport and holds it instead of scrolling into white.

**The Invoice's header comes from a different moment than its body.** The take
only ever shows the top of the invoice *before* the rate types are edited, and
the body only *after*. Stitched naively, one uncut shot would carry a Labour
subtotal of 702.50 at the top and 760.00 in the totals. `PAGE_HEAD="4.6,150"`
takes the first 150 px from 4.6 s and everything below from the final pass, so
the page is consistent end to end.

Otherwise the method is the usual one: the pass is the take's own resting
moments between wheel steps (2 for the Setup, 21 for the Invoice), each frame
aligned to the previous over their overlap, every row written from the MIDDLE of
a viewport — never the bottom edge, which carries the scrollbar and half-drawn
rows, and never the top edge, where the recording's VP8 encoder leaves a ghost
for a few frames after each step.

## No Russian anywhere in the film

The recording is cropped to the grid area, which puts Sheets' own sheet-tab
strip and its toasts at y ≥ 818 — below every crop the film uses. The stitched
pages stop at 762 px and the two dropdown shots at 764 px. The workbook is
English throughout: *Redline Home Repairs*, `INV-2003`, `JOB-1001`, and the rate
types *Standard · After hours · Weekend · Flat rate*.

## Rebuilding

```bash
./build_invoice_video.sh <recording.webm> work job_invoice_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1860×849** — an odd height, which libx264 refuses — so the
normalising pass crops it to 848 on the way in. The two passes are the inline
`"0.8,2.2"` and `INV=` at the top of the build script, the two straight cuts are
the `-ss`/`-t`/`crop` lines beside them; `make_layers_invoice.py` owns
everything drawn around the screen and `make_page.py` owns the pages.
