# ✦ The Inbox — how to publish a chapter

Drop a chapter file into this folder and it becomes a page on the site,
automatically, in about two minutes. No code involved.

## From Google Docs (the usual way)

1. In your Google Doc: **File → Download → Microsoft Word (.docx)**
2. On GitHub, open this `inbox/` folder → **Add file → Upload files**
3. Drag the `.docx` in and press **Commit changes**

That's it. The converter runs, the chapter appears in the table of
contents, and the site redeploys on its own.

## One document, many chapters

Put several chapters in a single doc by giving each chapter title the
**Heading 2** style (the style dropdown in the Google Docs toolbar).
Everything under a heading, up to the next one, becomes that chapter's
body. They publish in the order they appear:

```
Heading 2  →  The Loomkeeper's Price
   (prose, dashes, images…)

Heading 2  →  The Warp and the Weft
   (prose…)

Heading 2  →  What the Thread Remembered
   (prose…)
```

A book title in **Heading 1** at the very top is fine — it is ignored,
not treated as a chapter. A doc with **no headings** is published as a
single chapter, titled by the file name.

## What the converter understands

- **Chapter titles come from Heading 2** (or the file name, for a
  headingless single-chapter doc).
- **A line of dashes** (`--------`, any number, or a real horizontal
  rule) becomes the ✦ scene break.
- **Images in the doc are carried over** and framed like plates,
  in the order they appear.
- *Italics* survive; **bold** is folded into italics.
- Chapters publish in document order. The **vigil** is inherited from
  the previous chapter and the **folio** number continues automatically.

## Optional overrides

To control the metadata, add any of these lines — at the very top of the
doc (defaults for the whole upload) or right under a chapter's Heading 2
(that chapter only). They are removed from the published text:

```
vigil: VIGIL III — THE MENDING
folio: 163
```

Starting a new vigil? Set `vigil:` once under the first chapter of it —
later chapters in the same upload inherit it automatically.

## Updating a chapter

Re-upload a doc with the **same title** and it replaces that chapter
(images included). Plain `.md` / `.txt` files work too.

## Notes

- PDFs are not supported — export the Google Doc as `.docx` instead
  (PDF text extraction mangles paragraphs and drops images).
- Only people with write access to this repository can upload, so the
  inbox is yours alone.
