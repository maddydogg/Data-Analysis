# Bookkeeping — listing video

`bookkeeping_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
44.7 s screen recording of the workbook in Google Sheets.
`bookkeeping_cover_1080.jpg` is the frame at 1.2 s.

This one sells to someone who has to hand numbers to an accountant, so the frame
is the most businesslike of the listings: warm paper **ruled like a ledger**
rather than gridded like a spreadsheet, a red margin line down the left, deep
graphite-green type. The mint is the workbook's own `#DBF5EA` section band and
the accent the green its chart bars are drawn in. The other four listings own
the looks it avoids — the debt one the mint-and-cream mesh, the paycheck one
blue-grey paper, the budget one green sweeps, the ADHD one an almost empty page.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–8.6 s | the Books sheet, held then scrolled, no cuts | 0.1–12.6 s |
| 8.3–10.8 s | **the period switch — open, pick, recompute, uncut** | 21.80 s |
| 10.5–12.6 s | the Log | 32.90 s |
| 12.3–14.9 s | the Log — Income, Expense or Mileage | 34.20 s |

The period shot is the one that matters and it is deliberately **one shot, not
two**: the list opens on `Whole year`, July is picked, and income goes
$56 857 → $5 262, net profit $34 742 → $3 137, set-aside $8 685,50 → $784,25,
mileage 1 274 miles → 177 — all inside a single continuous frame. Cutting
between "before" and "after" is exactly what makes a viewer doubt that a sheet
really did the work. Its caption changes under it instead: *Pick a period…* then
*…and the page re-does itself*.

Seven captions, all lifted from the sheet: *Two sheets. Log it once. · Month by
month, quarter by quarter · What your accountant asks for · Pick a period… ·
…and the page re-does itself · One row per transaction · Income, expense — or a
mileage trip.* They are timed against the film rather than against shots.

The take switches to the Log at 32.6 s, so nothing crosses it. The list shot is
cropped to 800 px — 1.2× on the way into the window — so the three options read.

## The stitched page

The Books sheet is long: 812 px of viewport and 997 px of scroll under it. The
recording shows one viewport at a time and scrolls in wheel steps, then scrolls
back up, so only the downward pass is used. `make_page.py` takes the 42 moments
that pass is at rest, aligns each frame to the previous one over their overlap,
and writes every row from the MIDDLE of a viewport — never the bottom edge,
which carries the scrollbar and half-drawn rows, and never the top edge, where
the recording's VP8 encoder leaves a ghost for a few frames after each step. It
trims the blank tail and scrolls what is left: 1.8 s held, 6.1 s of eased
travel, 0.7 s held.

## Rebuilding

```bash
./build_books_video.sh <recording.webm> work bookkeeping_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run. The script normalises
the VP8 recording to constant-rate H.264 first — Chrome writes it variable-rate
with no duration header, and seeking it directly gives frames that drift from
the timings above.

The three cuts are the `SHOTS=(start length crop)` table at the top of the build
script, written against a **1450×856** frame — this take was recorded in a
narrower window than the others, so its crops are not interchangeable with
theirs. `make_layers_books.py` owns everything drawn around the screen;
`make_page.py` owns the page and its scroll.

## One note on the workbook

The sheet says it plainly and so should the listing: *not tax advice — a
record-keeping tool, and the set-aside percentage is your own estimate.* Nothing
in the video claims otherwise; the footer sells what it does, which is that you
log a transaction once and the page does the arithmetic your accountant asks
for.
