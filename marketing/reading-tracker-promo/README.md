# Reading Tracker — listing video

`reading_tracker_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
51.5 s screen recording of the workbook in Google Sheets.
`reading_tracker_cover_1080.jpg` is the frame at 1.2 s.

The third dark listing, so the ground moves off navy: a deep plum-indigo, which
reads as evening reading rather than as another finance sheet, with the same
green glow behind the window and the `#7BFFA2` the workbook writes its own
section headers in.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–8.0 s | the Shelf sheet, held then scrolled, no cuts | 5.1–16.2 s |
| 7.7–10.4 s | **the period switch — open, pick, re-count, uncut** | 32.00 s |
| 10.1–12.2 s | the Books log | 35.60 s |
| 12.0–14.9 s | **the status list — open, pick, uncut** | 48.30 s |

Two of the four are uncut before/afters, which is the whole argument: the period
list opens on October (0 books, no rating, 0% of goal), August is picked, and
the shelf comes back with 3 books, 932 pages, 3,3 average and 69% of the year's
goal — with `BOOKS FINISHED BY MONTH`, `BY GENRE`, `BY FORMAT` and `RATINGS AND
SPICE` all repopulated inside the same frame. The last shot does the same on the
Books sheet: the status list opens on `Finished` and lands on `Want to read`.

Seven captions, all lifted from the sheet: *Two sheets. Log a book on Books. ·
Books finished, by month · By genre, by format, by rating · Pick a period… ·
…and the shelf re-counts · One row per book · Reading, finished, did not
finish.* They are timed against the film rather than against shots.

## The Russian toast is not cropped — it is simply not in the film

Sheets floated its **"Преобразовать в таблицу"** toast at x1565-1850 / y768-810
between roughly 40.5 s and 44.0 s of the take, while the Books sheet was on
screen. The other listings steered around such a toast by cropping; here those
seconds were not needed, so no shot goes near them: shot 3 ends at 37.7 s and
shot 4 starts at 48.3 s. The gap is 10.6 s of unused recording.

## The stitched page

The Shelf sheet is long: 812 px of viewport and 994 px of scroll under it. The
take scrolls it down between 5.1 s and 16.2 s and then back up, so only the
downward pass is used. `make_page.py` takes the 38 moments that pass is at rest,
aligns each frame to the previous one over their overlap, and writes every row
from the MIDDLE of a viewport — never the bottom edge, which carries the
scrollbar and half-drawn rows, and never the top edge, where the recording's VP8
encoder leaves a ghost for a few frames after each step. It trims the blank tail
and scrolls what is left: 1.6 s held, 5.7 s of eased travel, 0.7 s held.

## Rebuilding

```bash
./build_reading_video.sh <recording.webm> work reading_tracker_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1862×853** — an odd height, which libx264 refuses — so the
normalising pass crops it to 852 on the way in. The three cuts are the
`SHOTS=(start length crop)` table at the top of the build script;
`make_layers_reading.py` owns everything drawn around the screen and
`make_page.py` owns the page and its scroll.
