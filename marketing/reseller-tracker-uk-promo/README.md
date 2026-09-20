# Reseller Tracker (UK) — listing video

`reseller_uk_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
45.5 s screen recording of the workbook in Google Sheets.
`reseller_uk_cover_1080.jpg` is the frame at 1.0 s.

This is the UK edition of the workbook `../reseller-tracker-promo` sells, so the
frame has to read as that listing's sibling and never as a duplicate of it.

## The ground, and what separates it from the US one

Keyed to the file, as always — and the difference is in the file. The UK
Dashboard draws profit as **two** series, `#78E3A4` for profit on items and the
slate `#395668` for net profit, where the US one draws a single mint bar. So
the ground here is bar **pairs** in those two colours, and the whole frame is
keyed to the slate rather than to the mint, which is what tells the two
listings apart at thumbnail size.

Everything else UK is said in words rather than drawn: **pounds, the 6 April
tax year, HMRC mileage** in the kicker, `06 APR 2026 — 05 APR 2027` on the
window chip, and `mileage at 45p` in the footer.

Bar pairs belong to this listing alone: the US tracker's ground is flat column
bands, the light edition's a single-series chart, the invoice's horizontal
section bands, the estimate's a manila docket.

## The cut

The film leads with what actually differs and lets the rest follow.

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–3.1 s | **Setup — the UK shot: £, day 6 / month 4, 0.450, UK platform fees** | 3.80 s |
| 2.8–5.8 s | Inventory & Sales — one row per item, blue in, green out | 10.42 s |
| 5.5–8.1 s | Lots, at speed — the Source list, and a box of ten at 4.50 each | 19.10 s |
| 7.9–11.5 s | Dashboard — 06 Apr 2026 to 05 Apr 2027, and a chart running Apr→Mar | 34.05 s |
| 11.2–14.9 s | Tax Summary — net profit, then the mileage off it | 44.45 s |

The Setup shot is the listing's whole reason to exist and every UK mark in it
is legible: the sheet's own footnotes read *"UK: tax year starts 6 April (day 6,
month 4)"*, *"Ireland: 1 January (day 1, month 1)"* and *"0.45 is the HMRC rate
for the first 10,000 business miles by car. Check yours."* Beside them the
platform table — **Vinted 0%, eBay (private) 0%, eBay (business) 15.9% + 0.48,
Depop 2.9% + 0.30, Whatnot 10.9%, Etsy 10.5% + 0.36, car boot / cash 0%** —
under the note *"UK rates as of 2026. eBay business incl. VAT."*

The Dashboard tab opens at 33.1 s in the take, but Sheets does not draw the
sheet until 34.0 — nine tenths of a second of blank white while it loads. That
is not in the film: the shot starts at 34.05, once the sheet is on screen, and
holds it. No frame of the film shows an empty window.

The Lots shot is the only one played near speed, because something happens in
it: the Source list opens and the sources are the British ones — charity shop,
car boot sale, jumble sale, house clearance — while 45.00 for a bag of ten tees
stays 4.50 an item.

The numbers the film lands on: `Net profit 1,898.00` on the dashboard, and on
the tax page `Total expenses 900.88 → NET PROFIT 1,898.00 → 372.2 miles →
167.49 off → Profit after mileage 1,730.51`.

Seven captions: *Pounds, 6 April, HMRC mileage · eBay, Vinted, Depop, Etsy —
the fees are in · One row per item — blue is yours, green calculates · A
car-boot box for one price → cost per item · Your tax year, 6 April to 5 April
· Net profit, live · And the mileage deduction on top.*

## Nothing is stitched

The take reads the sheets the way anyone reads a spreadsheet — scroll, stop,
look — and every sheet here fits a screen at the right stop. So four shots are
the stops themselves, slowed to the time it takes to read them, and the fifth
is the Lots interaction at 0.77×. `make_page.py` is carried in the folder
unused, for the next take that needs a page longer than its window.

## No Russian anywhere in the film

The recording is cropped to the grid area, which puts Sheets' own sheet-tab
strip and its toasts at y ≥ 824 — below every crop the film uses. The five
shots stop at 673, 630, 596, 706 and 758 px. The workbook is English
throughout.

## Rebuilding

```bash
./build_uk_video.sh <recording.webm> work reseller_uk_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1862×848** — both dimensions even — so the normalising pass only
fixes the frame rate and the missing duration header. The five shots are the
`SHOTS=(id start length crop speed)` table at the top of the build script;
`make_layers_uk.py` owns everything drawn around the screen.
