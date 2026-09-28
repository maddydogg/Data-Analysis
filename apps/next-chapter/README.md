# Next Chapter — book tracker app

Offline book tracker built on the Next Step / Until Payday template: one HTML
file, installable to the home screen, data kept only on the device, a free
demo that hands off to the Etsy listing.

```bash
python3 build.py          # writes dist/next-chapter-demo and dist/next-chapter
```

Each `dist/` folder is ready for Cloudflare Pages as is. Before publishing:

- set `FULL_URL` in `src/index.html` to the Etsy listing of the full version;
- paste the Cloudflare Web Analytics beacon where the comment in `<head>` says;
- rebuild.

## Who it is for

Women aged roughly 20–40 who read romance, romantasy and cozy fantasy.
Goodreads' audience is about 60% women, with 25–34 the largest age group; the
BookTok audience is mostly women in their twenties. The shop's own book-tracker
tags (romantasy tracker, spice tracker, tbr list) point at the same reader.
That is why the default look is warm paper, there is a Romantasy theme, and
spice ratings are built in — with a switch to hide them.

## What the reviews asked for, and what answers it

| Reviews say | In the app |
| --- | --- |
| "Nice to visually see all my books and the statistics" | Stats tab: books, pages, hours listened, average rating and spice, books by month, format split, moods, favourites |
| Wished it tracked how many hours a book took | Optional minutes per reading session; total reading time per year |
| Wanted a tab to track book series | Series shelf: books in order, what's read, what's next |
| Goodreads has no DNF shelf | DNF is a shelf, records where you stopped, counts in stats |
| Goodreads only allows whole stars; StoryGraph's quarter stars are loved | Quarter-star rating slider |
| StoryGraph reviews are quick: tick boxes, drop-downs | Review in taps: rating, spice 0–5, mood chips, one-line note |
| StoryGraph is slow, needs restarts; Goodreads crashes and loses reviews | One local file, no server, opens instantly, works offline |
| StoryGraph mass import is painful | One-tap import of a Goodreads or StoryGraph CSV: shelves, ratings, dates, series parsed from titles |
| Goodnotes is slow | Not a PDF: a real app on the phone |
| Readers leaving Amazon-owned Goodreads | No account, nothing uploaded; backup file is theirs |
| Spice ratings wanted (a spice-only app exists for this) | Spice built in, next to rating and mood |

## Demo

15 books (manual or imported), everything else unlocked. Backup from the demo
restores into the full version.
