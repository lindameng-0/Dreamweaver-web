# Dreamweaver — A Novel

A single-page presentation site for the novel **Dreamweaver**, designed in a
light-academia style: parchment grounds, hairline ornaments, arched plates,
and a night-indigo panel drawn from the cover illustration's palette.

## Sections

- **Home** — poster-style hero: the cover illustration in an arched frame,
  with the title set on a curve around the arch
- **Characters** — a full-screen splash-art stage for eight characters,
  one at a time, with a name rail plus arrow, keyboard, and swipe
  navigation. Characters with finished art blend straight into the page
  (the stage fades to charcoal for night-mood characters); the rest wear
  veiled "yet unveiled" portraits — drop a full-body illustration into
  `assets/characters/` and swap it into the slide when the art exists
- **World** — atlas of the four charted dream provinces, set on a night panel
- **Novel** — synopsis, a manuscript-page excerpt, and the table of contents

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
