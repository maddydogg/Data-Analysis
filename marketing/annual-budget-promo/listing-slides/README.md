# Listing slides — 2000×2000

Six Etsy listing images, rendered in both themes:
`light_slide_01…06.png` and `dark_slide_01…06.png`, plus two contact sheets.

| # | slide | what it does |
| --- | --- | --- |
| 01 | The Annual Budget | hero — name, promise, the dashboard, three claim chips |
| 02 | Nine tabs, one file | the nine tabs as a 3×3 grid with one line each |
| 03 | Three steps, then it runs itself | setup → log → read, with a screenshot per step |
| 04 | Your whole year at a glance | four dashboard blocks, captioned |
| 05 | Details that save the most time | five mechanics, with the bill calendar and month view |
| 06 | Everything, in one file | what the buyer gets, plus the workbook's own disclaimer |

## Why it looks the way it does

It reuses the system already built for the promo video rather than the layout of
any competitor listing: the same browser-window frame, the same mint palette
read out of `AnnualBudgetSpreadsheet.xlsx` (`DFF3EA`, `33566B`), the same
Playfair + Montserrat pairing.

Where the Hey Morning listings centre a heavy grotesque headline over a laptop
mockup, put a circular sticker badge on the screen and close with a star row and
a customer count, these slides are left-aligned and editorial: an eyebrow, a
serif headline, a numbered index in the footer, cards and chips instead of
stickers. No stars, no customer count, no laptop — nothing that would only make
sense as a copy of someone else's page.

Every claim comes from the workbook itself: the tab names and their one-line
descriptions are the Start Here sheet's own wording, "formulas are protected,
only the blue cells are yours" and "an organisation tool, not financial advice"
are quoted from it.

## Rebuild

```bash
python3 ../make_listing_slides.py <out-dir> <fonts-dir> <shots-dir> light
python3 ../make_listing_slides.py <out-dir> <fonts-dir> <shots-dir> dark
```

`shots-dir` holds `light_*.png` / `dark_*.png` crops pulled from the two screen
recordings; the `cut` lines in `build.sh` and `build_dark.sh` list the exact
timecodes and crops used.
