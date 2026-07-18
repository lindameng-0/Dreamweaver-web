#!/usr/bin/env python3
"""Convert author uploads in inbox/ into site chapters.

Drop a .docx (export a Google Doc via File > Download > Microsoft Word),
.md, or .txt file into inbox/ and this script turns it into
chapters/NN-slug.md, copies any embedded images to assets/chapters/,
and updates chapters/manifest.json.

Conventions understood:
  - Each "Heading 2" in the doc (or "Heading 1") starts a new chapter,
    and the heading text is that chapter's title. One upload can carry
    a whole batch of chapters; they publish in document order. A doc
    with no headings is treated as a single chapter titled by filename.
  - A line consisting only of dashes/underscores/asterisks (or a real
    horizontal rule in the doc) becomes a ✦ scene break.
  - Italics survive; bold is folded into italics.
  - Images embedded in the doc are carried over, full quality.
  - Optional metadata lines override the defaults. Put them at the top
    of the doc (batch defaults) or right under a chapter heading:
        vigil: VIGIL III — THE MENDING
        folio: 163
    Otherwise vigil is inherited from the previous chapter and folio
    continues automatically.
  - Re-uploading a chapter with the same title updates it in place.

Requires pandoc for .docx input.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
CHAPTERS = ROOT / "chapters"
MEDIA = ROOT / "assets" / "chapters"
MANIFEST = CHAPTERS / "manifest.json"

HR_RE = re.compile(r"^[\s]*[-–—_*]{3,}[\s]*$")
IMG_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)(?:\{[^}]*\})?")
META_RE = re.compile(r"^(title|vigil|folio)\s*[::]\s*(.+)$", re.IGNORECASE)


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "chapter"


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"chapters": []}


def read_chapter_meta(filename):
    meta = {"title": "", "vigil": "", "folio": ""}
    path = CHAPTERS / filename
    if not path.exists():
        return meta
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            break
        m = META_RE.match(line)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
    return meta


def docx_to_markdown(path, media_dir):
    out = subprocess.run(
        ["pandoc", str(path), "-f", "docx", "-t", "gfm", "--wrap=none",
         f"--extract-media={media_dir}"],
        check=True, capture_output=True, text=True,
    )
    return out.stdout


def unescape_pandoc(text):
    # pandoc escapes punctuation in gfm output; asterisks stay meaningful
    return re.sub(r"\\([\[\](){}#.!\"'`~<>|$&%_+-])", r"\1", text)


HTML_IMG_RE = re.compile(r"<img\b[^>]*?/?>", re.IGNORECASE)


def html_imgs_to_markdown(text):
    """pandoc emits <img src=... alt=...> HTML when images carry size
    attributes; fold those (and figure wrappers) back into ![alt](src)."""
    def repl(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        if not src:
            return ""
        return "\n\n![%s](%s)\n\n" % (alt.group(1) if alt else "", src.group(1))
    text = HTML_IMG_RE.sub(repl, text)
    text = re.sub(r"</?figure[^>]*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<figcaption[^>]*>.*?</figcaption>", "", text,
                  flags=re.IGNORECASE | re.DOTALL)
    return text


def normalise_body(md_text, media_dir, slug):
    """markdown-ish text -> list of chapter blocks (strings)."""
    md_text = md_text.replace("\r\n", "\n")
    md_text = html_imgs_to_markdown(md_text)
    # bold -> italics, keep single-star emphasis
    md_text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"*\1*", md_text)
    md_text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", md_text)
    md_text = re.sub(r"__([^_]+)__", r"*\1*", md_text)
    md_text = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"*\1*", md_text)

    blocks = []
    img_count = 0
    for raw in re.split(r"\n\s*\n", md_text):
        chunk = raw.strip()
        if not chunk:
            continue
        # a paragraph that is only dashes (or a markdown hr) = scene break
        if all(HR_RE.match(line) for line in chunk.splitlines()):
            if blocks and blocks[-1] != "***":
                blocks.append("***")
            continue
        # headings from the doc (e.g. pasted title) are ignored as body noise
        if re.match(r"^#{1,6}\s", chunk) and len(chunk.splitlines()) == 1:
            continue

        # pull images out into their own blocks
        pos = 0
        pieces = []
        for m in IMG_RE.finditer(chunk):
            before = chunk[pos:m.start()].strip()
            if before:
                pieces.append(("p", before))
            pieces.append(("img", m.group("alt").strip(), m.group("src")))
            pos = m.end()
        tail = chunk[pos:].strip()
        if tail:
            pieces.append(("p", tail))

        for piece in pieces:
            if piece[0] == "img":
                _, alt, src = piece
                src_path = Path(src)
                if not src_path.is_absolute():
                    src_path = Path(media_dir) / src if not src_path.exists() else src_path
                # pandoc writes absolute-ish paths under media_dir already
                candidates = [Path(src), Path(media_dir) / Path(src).name]
                found = None
                for c in candidates:
                    if c.exists():
                        found = c
                        break
                if not found:
                    hits = list(Path(media_dir).rglob(Path(src).name))
                    found = hits[0] if hits else None
                if not found:
                    continue
                img_count += 1
                dest = MEDIA / f"{slug}-{img_count}{found.suffix.lower()}"
                MEDIA.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(found, dest)
                blocks.append(f"![{alt}]({dest.name})")
            else:
                text = unescape_pandoc(re.sub(r"\s*\n\s*", " ", piece[1])).strip()
                if text:
                    blocks.append(text)

    # drop a paragraph that merely repeats the previous image's caption
    # (pandoc renders docx figure captions as a trailing text line)
    deduped = []
    for block in blocks:
        prev = deduped[-1] if deduped else ""
        m = re.match(r"^!\[(.*)\]\(", prev)
        if m and m.group(1) and block.strip().lower() == m.group(1).strip().lower():
            continue
        deduped.append(block)
    blocks = deduped

    while blocks and blocks[-1] == "***":
        blocks.pop()
    while blocks and blocks[0] == "***":
        blocks.pop(0)
    return blocks


def extract_meta_overrides(blocks):
    meta = {}
    while blocks:
        m = META_RE.match(blocks[0])
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
            blocks.pop(0)
        else:
            break
    return meta


def clean_heading(text):
    """A pandoc heading line's text -> a clean chapter title."""
    text = re.sub(r"\s*\{[^}]*\}\s*$", "", text.strip())  # trailing {#id} attrs
    text = re.sub(r"[*_`]", "", text)                     # emphasis markers
    return unescape_pandoc(text).strip()


def extract_meta_lines(lines):
    """Pull title/vigil/folio lines out of a list of raw lines."""
    meta = {}
    for line in lines:
        m = META_RE.match(line.strip())
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
    return meta


def split_into_chapters(md_text):
    """Split a document into chapters at its heading lines.

    Google Docs "Heading 2" exports as an H2 (## Title); "Heading 1" as
    an H1 (# Title). We split on H2 when any are present, otherwise H1.
    Returns (preamble_lines, [(title, body_md), ...]) — or None when the
    document has no headings at all (a single-chapter upload).
    """
    lines = md_text.replace("\r\n", "\n").split("\n")
    if any(re.match(r"^##\s+\S", ln) for ln in lines):
        pat = re.compile(r"^##\s+(.*)$")
    elif any(re.match(r"^#\s+\S", ln) for ln in lines):
        pat = re.compile(r"^#\s+(.*)$")
    else:
        return None

    preamble, sections = [], []
    cur_title, cur_lines, started = None, [], False
    for ln in lines:
        m = pat.match(ln)
        if m:
            if started:
                sections.append((cur_title, "\n".join(cur_lines)))
            else:
                preamble, started = cur_lines, True
            cur_title, cur_lines = clean_heading(m.group(1)), []
        else:
            cur_lines.append(ln)
    if started:
        sections.append((cur_title, "\n".join(cur_lines)))

    sections = [(t, b) for (t, b) in sections if t or b.strip()]
    return preamble, sections


def process(path):
    manifest = load_manifest()
    files = manifest.get("chapters", [])

    stem = path.stem
    num_match = re.match(r"^(\d+)[\s.\-–—_]*(.*)$", stem)
    filename_title = (num_match.group(2) if num_match and num_match.group(2) else stem).strip()

    # ── parse the upload into one or more chapters (while media dir lives) ──
    with tempfile.TemporaryDirectory() as media_dir:
        ext = path.suffix.lower()
        if ext == ".docx":
            md = docx_to_markdown(path, media_dir)
        elif ext in (".md", ".txt", ".markdown"):
            md = path.read_text(encoding="utf-8")
        else:
            print(f"skip (unsupported type): {path.name}")
            return []

        split = split_into_chapters(md)
        if split is None:
            sections, batch_meta = [(None, md)], {}
        else:
            preamble, sections = split
            batch_meta = extract_meta_lines(preamble)

        built = []
        for heading_title, body_md in sections:
            prov_title = heading_title or filename_title or "Untitled Chapter"
            blocks = normalise_body(body_md, media_dir, slugify(prov_title))
            overrides = extract_meta_overrides(blocks)
            if not blocks:
                continue
            title = overrides.get("title") or heading_title or filename_title or "Untitled Chapter"
            built.append({"title": title, "overrides": overrides, "blocks": blocks})

    if not built:
        print(f"skip (no content found): {path.name}")
        return []

    # ── write each chapter, chaining vigil/folio from the previous one ──
    prev_meta = read_chapter_meta(files[-1]) if files else {}
    running_vigil = batch_meta.get("vigil") or prev_meta.get("vigil") or "VIGIL I — THE COMMISSION"
    have_folio = bool(batch_meta.get("folio") or prev_meta.get("folio"))
    try:
        running_folio = int(batch_meta.get("folio") or prev_meta.get("folio") or 0)
    except ValueError:
        running_folio = 0

    results = []
    for item in built:
        title, overrides, blocks = item["title"], item["overrides"], item["blocks"]
        slug = slugify(title)

        existing = None
        for f in files:
            if re.sub(r"^\d+-", "", f).rsplit(".", 1)[0] == slug:
                existing = f
                break
        old = read_chapter_meta(existing) if existing else {}

        vigil = overrides.get("vigil") or (old.get("vigil") if existing else "") or running_vigil
        running_vigil = vigil

        if overrides.get("folio"):
            folio = overrides["folio"]
        elif existing and old.get("folio"):
            folio = old["folio"]
        elif not have_folio:
            folio = "1"
        else:
            folio = str(running_folio + 24)
        try:
            running_folio, have_folio = int(folio), True
        except ValueError:
            pass

        if existing:
            out_name = existing
        else:
            out_name = f"{len(files) + 1:02d}-{slug}.md"
            files.append(out_name)

        body = "\n\n".join(blocks)
        content = f"title: {title}\nvigil: {vigil}\nfolio: {folio}\n\n{body}\n"
        CHAPTERS.mkdir(parents=True, exist_ok=True)
        (CHAPTERS / out_name).write_text(content, encoding="utf-8")
        print(f"{'updated' if existing else 'published'}: {title!r} -> chapters/{out_name}")
        results.append(title)

    manifest["chapters"] = files
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    path.unlink()
    return results


def main():
    if not INBOX.exists():
        print("no inbox directory")
        return 0
    uploads = sorted(p for p in INBOX.iterdir()
                     if p.is_file() and not p.name.startswith(".")
                     and p.name.lower() != "readme.md")
    if not uploads:
        print("inbox empty")
        return 0
    done = []
    for p in uploads:
        done.extend(process(p))
    print(f"processed {len(done)} chapter(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
