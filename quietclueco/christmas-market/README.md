# Snowfall at Ember Square — QuietClueCo case No. 1

A cozy "find the killer" elimination puzzle set at a Christmas market. There are 6,000 visitors, 18 clues and one killer. It plays with 1–4 players and takes about 90–150 minutes.

## Files

| Path | What it is |
|---|---|
| `print/snowfall-at-ember-square_print-US-Letter.pdf` | Case book for printing, US Letter (138 pages) |
| `print/snowfall-at-ember-square_print-A4.pdf` | Case book for printing, A4 (129 pages) |
| `ipad/snowfall-at-ember-square_iPad.pdf` | Case book for Goodnotes / Notability, 768×1024 portrait, clickable contents and bookmarks (117 pages) |
| `solution/…_SOLUTION_print-US-Letter.pdf`, `…_SOLUTION_print-A4.pdf`, `…_SOLUTION_iPad.pdf` | "The Envelope": answer, epilogue, step-by-step solution, finalists, and the elimination index for all 6,000 tickets |
| `verification_report.md` / `.json` | Code verification report |
| `previews/<version>/page-NNN.png` | PNG preview of every page of every PDF |
| `src/` | Generator source: `case.py` (story, world, clues), `hints.py`, `generate.py` (visitor log), `verify.py` (checks), `render.py` (PDF drawing), `build.py` (runs everything) |
| `src/data/visitor_log.csv` | The 6,000-line Visitor Log exactly as printed |
| `src/fonts/` | Fraunces, Nunito, Caveat and Courier Prime (SIL Open Font License, from Google Fonts) |

## Rebuild

```bash
pip install reportlab pymupdf fonttools pillow
cd src && python3 build.py          # add --no-previews to skip the PNGs
```

The build is deterministic because the generator is seeded. It exits with a non-zero code if any check fails.

## Answer (spoiler)

<details><summary>Show</summary>

Hazel Russell, ticket 3857, from Marrowby. She entered at 19:23 through the South Gate, and her last stall was 22. The Sealed Check number is 011.
</details>
