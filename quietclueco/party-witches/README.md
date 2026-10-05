# Murder at the Lantern Supper — QuietClueCo murder mystery party

A Halloween murder mystery party for 6–12 players in Morrowmere, the witch village of case No. 3, with a new victim and a
new killer. 6 core roles + up to 6 extra, 3 rounds, 2–3 hours, no acting, the host can play. Spooky, not gory.

Story: at the Hearth Circle’s Lantern Supper at Larkwell Hall, the Lantern Keeper Rowena Heatherly is found in the Still
Room at a quarter to eleven, a green glass of blackberry cordial empty beside her. The foxglove went into the glass while
she was upstairs in the Lantern Room.

## Files

| Path | What it is |
|---|---|
| `print/…_HOST-GUIDE_US-Letter.pdf`, `…_A4.pdf` | Host guide (17 pages in US Letter, 16 in A4): welcome, how it works, before the party, what to print (page by page, per role and per guest count), casting for 6–12, guests, players and the host, the evening, plan of the house, round scripts, FAQ, and the SEALED SOLUTION at the back |
| `print/…_PLAYER-KIT_US-Letter.pdf`, `…_A4.pdf` | Player kit (65 pages): printing guide, house rules, plan of Larkwell Hall, 12 booklets × 4 pages, 11 evidence cards, detective’s notes, accusation sheets, 13 name badges, potion menu, 4 awards |
| `invitations/` | Fillable 5x7 invitation, 12 fillable character invitations, 13 phone PNGs, README |
| `delivery/` | The 5 files for Etsy (4 PDFs + INVITATIONS.zip), each under 20 MB |
| `listing/mockups/` | 10 listing images, 2000×2000 JPG, plus an overview |
| `listing/video/` | Old-film trailer (13.5 s) and kit presentation (14 s), 1080×1080, no sound |
| `listing/etsy_listing.md` | Title, description, price note, 30 tag candidates with Listadum data |
| `research.md` | Research of 5 competing party games and the format we chose |
| `verification_report.md` / `.json` | Code checks of the logic, the timeline, the texts and the PDFs (includes the true timeline: spoiler) |
| `listing/spoiler_check.md` | Spoiler and format checks of every image and video frame |
| `out/` | Archives (not in git): files-for-sale ZIP, mockups ZIP, both videos |
| `src/` | `case.py` (story, house, timeline, booklets, cards), `verify.py`, `render.py`, `invitations.py`, `build.py` |
| `listing/src/` | `party_art.py` (poster art), `mockups.py`, `video.py`, `build_listing.py`, `party_listing.py`, `poster.py`, `kit.py` |

## Rebuild

```bash
pip install reportlab pymupdf pillow imageio-ffmpeg
cd src && python3 build.py                      # checks, art, PDFs, invitations, delivery
cd ../listing/src && python3 build_listing.py   # mockups, videos, archives, spoiler check
```

## What the code checks

- **Solver.** Reads only the structured claims on the cards and in the booklets. Rules: cards are true; nobody lies about
  where someone else was; your own account never clears you. A stricter reading (the killer’s whole booklet untrusted) is
  tested too.
- **Unique answer** under every reading of the time window and of the place words on the plan, both rule readings and every
  guest count from 6 to 12.
- **Curve:** 6 suspects → 4 after Round 1 → 2 after Round 2 → 1 after Round 3.
- **Every key clue needed:** cards 1, 2 and 9, Isadora’s Round 1 alibi for Silas and Rufus’s Round 2 account of Cordelia.
  All of them belong to core roles or the table.
- **Extra roles:** removing every line of the 6 extra roles changes nothing.
- **Character–time–place table:** every booklet line and card matches the true timeline (who was where, who could see whom
  from where); only the killer gives a false account, and only of her own whereabouts.
- **Print list:** the page numbers the host guide prints (every booklet, the table items, the sealed pages) match
  the player kit and the guide itself; the guide is laid out twice so its own page numbers are settled.
- **No solution in the player kit**; in the host guide only after the sealed page. Stop list (films, books, other party
  games, real witch trials), no gore, nothing from case No. 3’s solution.

## Answer (spoiler)

<details><summary>Show</summary>

Clementine Reed, the candlemaker, at a quarter past ten, through the herb garden; the green wax on the rim of the glass.

</details>
