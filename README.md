# Dreamweaver — A Novel

A single-page presentation site for the novel **Dreamweaver**, designed in a
light-academia style: parchment grounds, hairline ornaments, arched plates,
and a night-indigo panel drawn from the cover illustration's palette.

## Sections

- **Home** — poster-style hero: the cover illustration in an arched frame,
  with the title set on a curve around the arch
- **Characters** — a full-screen splash-art stage for eight characters,
  one at a time, with a name rail plus arrow, keyboard, and swipe
  navigation. Each entry gets a giant epithet word behind the art, an
  orbit ellipse, a numbered plaque, and a records kicker; splash art
  floats directly on the parchment (white-background art is multiply-
  blended, dark art is background-removed). Characters without art wear
  veiled "yet unveiled" portraits — drop a full-body illustration into
  `assets/characters/` and swap it into the slide when the art exists
- **World** — atlas of the four charted dream provinces, set on a night panel
- **Novel** — synopsis, a manuscript-page excerpt, and a table of contents
  whose chapters open in the reader
- **Reader** (`read.html?ch=N`) — a scrolling chapter reader with drop caps,
  ✦ section breaks, a gold reading-progress bar, and previous/next/contents
  navigation. Chapter text lives in `js/chapters.js` — add a chapter object
  there and it appears in the reader automatically (remember to add its TOC
  row in `index.html`)

## Stack

Static HTML/CSS with a small vanilla-JS file for scroll reveals and nav state.
No build step — open `index.html` or serve the folder:

```sh
python3 -m http.server 8000
```

Type is self-hosted in `assets/fonts/` (no external requests):
[Italiana](https://fonts.google.com/specimen/Italiana) for display,
[Cormorant](https://fonts.google.com/specimen/Cormorant) for text,
[Pinyon Script](https://fonts.google.com/specimen/Pinyon+Script) for accents —
all licensed under the SIL Open Font License.
