# ADHD Planner — listing video

`adhd_planner_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
41.5 s screen recording of the workbook in Google Sheets.
`adhd_planner_cover_1080.jpg` is the frame at 1.1 s.

## Written against a competitor

Hey Morning sells an all-in-one life planner whose subhead names ADHD as one
audience among several. Their 14.9 s video shows six dense dashboards — a
four-quadrant home, a month calendar, a task board, a habit tracker, a budget,
a meal planner — under one headline that never changes, at a scale where not a
single number is legible on a phone, with hard cuts between screens that look
alike and their one real interaction buried at 12 s.

Their strengths are worth taking: a headline that promises a result rather than
a feature list, and an audience named out loud. Everything else here is the
opposite of their cut, on purpose:

| | them | this |
| --- | --- | --- |
| screens | six, unexplained | three sheets, each captioned |
| captions | one headline for 15 s | seven lines, in the sheet's own words |
| scale | whole dashboards, unreadable | 0.8×–1.4×, every row legible |
| pacing | 1.6–3.7 s, ragged | 1.8–3.0 s plus a 7.3 s uncut opener |
| payoff | one dropdown at 12 s, tiny | three interactions, large, from 7.9 s |
| ground | lavender gradient plus a sticker | the quietest frame of these listings |

The frame is deliberately calm — near-white paper, one mint wash, a thin rule,
no rings and no badge. The product's argument is *three things, not ten*; a busy
frame would contradict it. The mint is the workbook's own `#E0F3EA` section band
and the accent its habit-grid green.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–7.3 s | the Today sheet, held then scrolled, no cuts | 0.5–9.9 s |
| 7.0–8.8 s | **Break it down** — one big task into steps | 11.90 s |
| 8.5–10.5 s | the Energy list, picked | 15.45 s |
| 10.2–12.2 s | the Status list — Parked | 18.30 s |
| 11.9–14.9 s | the Habits grid and the month chart | 37.00 s |

Captions, all lifted from the sheet: *Three things, not ten · Quick wins — two
minutes each · Brain dump. Dopamine menu. · Break one big task into steps · One
row per task — set the energy · Park it — nothing breaks · One per day. No
streaks to lose.* They are timed against the film, not against shots, so three
of them change while the Today sheet is still moving.

The two dropdown shots are cropped to 760 px wide — 1.26× on the way into the
window — because the whole argument against this competitor is that you can read
what is happening. `Break it down` is 680 px, 1.41×.

Tabs switch at 10.8 s (Tasks) and 21.2 s (Habits) in the take, so no shot
crosses them. Sheets raised no toast during this recording; the frames were
checked for it anyway.

## The stitched page

The recording shows one viewport at a time and scrolls in wheel steps, so the
Today sheet is reassembled first. `make_page.py` takes the 28 moments the page
is at REST between steps, aligns each frame to the previous one over their
overlap, and writes every row from the MIDDLE of a viewport — never the bottom
edge, which carries the scrollbar and half-drawn rows, and never the top edge,
where the recording's VP8 encoder leaves a ghost for a few frames after each
step. It then trims the blank tail so the scroll does not end on white, and
scrolls what is left: 1.6 s held at the top, 5.0 s of eased travel, 0.7 s held.

## Rebuilding

```bash
./build_adhd_video.sh <recording.webm> work adhd_planner_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run. The script normalises
the VP8 recording to constant-rate H.264 first — Chrome writes it variable-rate
with no duration header, and seeking it directly gives frames that drift from
the timings above.

The four cuts are the `SHOTS=(start length crop)` table at the top of the build
script, written against a 1862×858 frame with no row-number gutter.
`make_layers_adhd.py` owns everything drawn around the screen; `make_page.py`
owns the page and its scroll.
