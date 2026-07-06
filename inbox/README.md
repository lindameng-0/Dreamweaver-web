# ✦ The Inbox — how to publish a chapter

Drop a chapter file into this folder and it becomes a page on the site,
automatically, in about two minutes. No code involved.

## From Google Docs (the usual way)

1. In your Google Doc: **File → Download → Microsoft Word (.docx)**
2. On GitHub, open this `inbox/` folder → **Add file → Upload files**
3. Drag the `.docx` in and press **Commit changes**

That's it. The converter runs, the chapter appears in the table of
contents, and the site redeploys on its own.

## What the converter understands

- **The filename becomes the title** — name the file
  `The Loomkeeper's Price.docx` and that is the chapter title.
- **A line of dashes** (`--------`, any number, or a real horizontal
  rule) becomes the ✦ scene break.
- **Images in the doc are carried over** and framed like plates,
  in the order they appear.
- *Italics* survive; **bold** is folded into italics.
- Chapters are appended in order. The **vigil** is inherited from the
  previous chapter and the **folio** number continues automatically.

## Optional overrides

To control the metadata, put any of these on the first lines of the doc
itself (they are removed from the published text):

```
title: The Loomkeeper's Price
vigil: VIGIL III — THE MENDING
folio: 163
```

Starting a new vigil? Just set `vigil:` once — later chapters inherit it.

## Updating a chapter

Re-upload a doc with the **same title** and it replaces that chapter
(images included). Plain `.md` / `.txt` files work too.

## Notes

- PDFs are not supported — export the Google Doc as `.docx` instead
  (PDF text extraction mangles paragraphs and drops images).
- Only people with write access to this repository can upload, so the
  inbox is yours alone.
