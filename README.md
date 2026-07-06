# Dreamweaver — A Novel

A single-page presentation site for the novel **Dreamweaver**, designed in a
light-academia style: parchment grounds, hairline ornaments, arched plates,
and a night-indigo panel drawn from the cover illustration's palette.

## Sections

- **Home** — poster-style hero: the cover illustration in an arched frame,
  with the title set on a curve around the arch
- **Characters** — dramatis personæ with watercolour-wash plates
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
