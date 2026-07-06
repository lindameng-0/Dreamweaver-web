#!/usr/bin/env python3
"""Convert author uploads in inbox/ into site chapters.

Drop a .docx (export a Google Doc via File > Download > Microsoft Word),
.md, or .txt file into inbox/ and this script turns it into
chapters/NN-slug.md, copies any embedded images to assets/chapters/,
and updates chapters/manifest.json.

Conventions understood:
  - A line consisting only of dashes/underscores/asterisks (or a real
    horizontal rule in the doc) becomes a ✦ scene break.
  - Italics survive; bold is folded into italics.
  - Images embedded in the doc are carried over, full quality.
  - Optional first lines in the doc override metadata:
        title: The Loomkeeper's Price
        vigil: VIGIL III — THE MENDING
        folio: 163
    Otherwise: title comes from the filename, vigil is inherited from
    the latest chapter, folio continues from the previous chapter.
  - Re-uploading a doc with the same title updates that chapter.

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


def process(path):
    manifest = load_manifest()
    files = manifest.get("chapters", [])

    stem = path.stem
    num_match = re.match(r"^(\d+)[\s.\-–—_]*(.*)$", stem)
    filename_title = (num_match.group(2) if num_match and num_match.group(2) else stem).strip()

    with tempfile.TemporaryDirectory() as media_dir:
        ext = path.suffix.lower()
        if ext == ".docx":
            md = docx_to_markdown(path, media_dir)
        elif ext in (".md", ".txt", ".markdown"):
            md = path.read_text(encoding="utf-8")
        else:
            print(f"skip (unsupported type): {path.name}")
            return None

        # metadata defaults from the latest chapter
        prev_meta = read_chapter_meta(files[-1]) if files else {}
        title_guess = filename_title or "Untitled Chapter"
        slug = slugify(title_guess)

        blocks = normalise_body(md, media_dir, slug)
        overrides = extract_meta_overrides(blocks)

        title = overrides.get("title") or title_guess
        slug = slugify(title)
        vigil = overrides.get("vigil") or prev_meta.get("vigil") or "VIGIL I — THE COMMISSION"
        folio = overrides.get("folio")
        if not folio:
            try:
                folio = str(int(prev_meta.get("folio", "0")) + 24)
            except ValueError:
                folio = ""

    if not blocks:
        print(f"skip (no content found): {path.name}")
        return None

    # update an existing chapter when the slug matches, else append
    existing = None
    for f in files:
        if re.sub(r"^\d+-", "", f).rsplit(".", 1)[0] == slug:
            existing = f
            break

    if existing:
        out_name = existing
        old = read_chapter_meta(existing)
        vigil = overrides.get("vigil") or old.get("vigil") or vigil
        folio = overrides.get("folio") or old.get("folio") or folio
    else:
        out_name = f"{len(files) + 1:02d}-{slug}.md"
        files.append(out_name)

    body = "\n\n".join(blocks)
    content = f"title: {title}\nvigil: {vigil}\nfolio: {folio}\n\n{body}\n"
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    (CHAPTERS / out_name).write_text(content, encoding="utf-8")

    manifest["chapters"] = files
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    path.unlink()
    action = "updated" if existing else "published"
    print(f"{action}: {title!r} -> chapters/{out_name}")
    return title


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
    done = [t for t in (process(p) for p in uploads) if t]
    print(f"processed {len(done)} chapter(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
