# Reseller Tracker (dark) — listing video

`reseller_dark_promo_1080.mp4` is the 14.9 s Etsy listing video, cut from one
64.1 s screen recording of the workbook in Google Sheets.
`reseller_dark_cover_1080.jpg` is the frame at 1.0 s.

This is the dark edition of the workbook `../reseller-tracker-promo` sells —
the same settings, not the UK ones: `$`, tax year starting 1 January, 0.700 a
mile, and the US platform fee table.

## Same film, dark key

The frame keeps the light listing's device — vertical column bands, the sheet's
own *"blue columns are yours, green ones calculate"* made into the ground — and
only changes key, to this edition's own colours: the page's `#0C1020`, its
banded rows `#14182C`, its section green `#143824`, and the `#78FCA0` it writes
its headers and its chart bars in. A green glow sits behind the window, the way
the other dark listings in the shop are lit.

Same structure, dark key, is what makes a pair read as one product in two skins
rather than as two products. The film shows the same five sheets in the same
order for the same reason.

## The cut

| | shot | from the take |
| ---: | --- | ---: |
| 0.0–3.1 s | Setup — the platform fee table every later number works from | 10.00 s |
| 2.8–5.8 s | Inventory & Sales — one row per item, blue in, green out | 19.85 s |
| 5.5–8.1 s | Lots — the Source list, and 45.00 for a bin of ten still 4.50 each | 26.45 s |
| 7.9–11.4 s | Dashboard — the year live, and the two-series chart beside it | 46.20 s |
| 11.2–14.9 s | Tax Summary — net profit, then the mileage off it | 62.90 s |

The numbers the film lands on: `Revenue 5,098.18 · Net profit 728.19 · 108
items at 20.54 each · 32 days to sell` on the dashboard, and on the tax page
`Total expenses 1,490.32 → NET PROFIT 728.19 → 573.0 miles → 401.10 off →
327.09 after mileage`.

Six captions: *Your platforms and their fees — once · One row per item · Blue
is yours. Green calculates. · A box for one price? Cost per item, done. · Every
number, live on one dashboard · Net profit, and the mileage on top.*

## The Russian toast is not cropped — it is simply not in the film

Sheets floated its **"Преобразовать в таблицу"** toast over the Setup sheet at
x 925–1170 / y 483–527, from **5.0 s to 7.7 s** of the take. The other listings
steered around such a toast by cropping; here the take is long enough that no
shot needs those seconds at all. The Setup shot starts at **10.00 s**, two and
a third seconds after the toast is gone — and also clear of the Yes/No list
that was open over the fee table at 9.0 s.

Checked rather than assumed: a sweep of every frame of the take for a
toast-shaped white pill inside the grid found exactly one run, 5.0–7.7 s, and
none of the five source windows touches it. The only solid white block left in
the finished film is the Lots *Source* menu — *Thrift store, Garage sale,
Estate sale, Flea market, Retail clearance, Online arbitrage, Wholesale lot,
Auction, Own items, Other* — which is English. Sheets' own tab strip stays
light even in dark mode, and it sits at y ≥ 792, below every crop: the five
shots stop at 673, 630, 616, 706 and 772 px.

## Nothing is stitched

The take reads the sheets the way anyone reads a spreadsheet — scroll, stop,
look — and every sheet here fits a screen at the right stop, so all five shots
are the stops themselves, slowed to the time it takes to read them.
`make_page.py` is carried in the folder unused, for the next take that needs a
page longer than its window.

## Rebuilding

```bash
./build_dark_video.sh <recording.webm> work reseller_dark_promo_1080.mp4
```

Needs `python3` with `pillow`, `numpy` and `imageio-ffmpeg`. Playfair Display
and Montserrat are fetched into `work/fonts` on first run.

This take is **1855×847** — both dimensions odd, which libx264 refuses — so the
normalising pass crops it to 1854×846 on the way in. The grid area is 772 px.
The five shots are the `SHOTS=(id start length crop speed)` table at the top of
the build script; `make_layers_dark.py` owns everything drawn around the screen.
