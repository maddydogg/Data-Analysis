# Budget Planner — listing video

`budget_planner_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
48.9 s screen recording. `budget_planner_cover_1080.jpg` is the frame at 1.2 s.

The product's claim is that everything lives on one page, so the film is built
to prove it rather than to contradict it: it opens on the whole page and then
travels down it in **one uncut move**. Cutting the page into six close-ups —
the first version of this video — says the opposite of what the listing is
selling, however pretty the crops are.

| | | |
| ---: | --- | ---: |
| 0.0–9.7 s | the page: held at the top, then scrolled to the bottom, no cuts | one take |
| 9.5–10.8 s | the Month list open | 29.45 s |
| 10.6–12.3 s | April — the whole page has re-done itself | 31.45 s |
| 12.0–13.5 s | the Log | 34.90 s |
| 13.3–14.9 s | the Log — a Category list, picked | 39.60 s |

Four captions ride over the scroll and the switch — *Everything on one page ·
Plan vs actual · bills · funds · debts · One screen. No tab hopping. · Pick a
month… · …and the whole page re-does itself · The second sheet is just the log*
— timed against the film, not against shots, so a line can change while the page
keeps moving under it.

The month pair and the wide Log shot are framed at the page's full width, the
same scale as the scroll, so no cut ever changes the zoom. Switching to April
takes expenses from $3 228 to $3 159 and left-to-spend from $802 to $871, and
every plan-vs-actual row and chart bar recomputes — all of it inside one frame,
which is the point.

## The stitched page

The recording only ever shows one viewport, and it scrolls in jumps, so the page
is reassembled first. `make_page.py` takes one monotonic scroll pass (21
viewports between 0.0 s and 13.8 s), aligns each frame to the previous one by
minimising the difference over their overlap, and writes every row from the last
viewport that had it near the top — never from a viewport's bottom edge, which
carries the scrollbar and half-drawn rows. That yields a 1470×1562 page, which
the script then scrolls at 30 fps: 2.4 s held at the top, 6.4 s of eased travel
over the 735 px span, 0.9 s held at the bottom.

Aligning against the previous frame rather than against the first one matters:
absolute matching mis-measured the deep positions by up to 16 px and left the
bottom of the page ghosted.

## Rebuilding

```bash
./build_budget_video.sh <recording.webm> work budget_planner_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run. The script normalises
the VP8 recording to constant-rate H.264 first — Chrome writes it variable-rate
with no duration header, and seeking it directly gives frames that drift from
the timings above.

Sheets floats its Russian **"Преобразовать в таблицу"** toast over the Log from
36.5 s at x980-1260 / y760-800. The shop sells in English, so the wide Log shot
ends at 36.45 s, just before it appears, and the close one stops at x950.
Nothing is painted over.

`make_layers_budget.py` owns everything drawn around the screen — title,
captions, the two tab pills, footer, progress bar. `make_page.py` owns the page
and its scroll. The four cuts are the `SHOTS=(start length crop)` table in the
build script, written against a 1862×850 frame with no row-number gutter.
