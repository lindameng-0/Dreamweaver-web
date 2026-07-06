/* Dreamweaver — shared chapter file format.
 *
 * A chapter file is plain text:
 *
 *   title: The Unslept Tailor
 *   vigil: VIGIL I — THE COMMISSION
 *   folio: 1
 *
 *   Paragraphs separated by blank lines.
 *
 *   ***
 *
 *   A line of *** makes a ✦ scene break. *asterisks* make italics.
 *
 *   ![A caption for the plate](marker-post.jpg)
 *
 *   An image line drops an illustration between paragraphs. Bare
 *   filenames resolve to assets/chapters/; paths with a slash are
 *   used as written.
 */

window.DWFormat = (function () {
  "use strict";

  var IMG_RE = /^!\[(.*?)\]\((.+?)\)$/;

  function parse(text) {
    var meta = { title: "", vigil: "", folio: "" };
    var lines = text.replace(/\r\n/g, "\n").split("\n");
    var i = 0;

    for (; i < lines.length; i++) {
      var line = lines[i];
      if (line.trim() === "") { if (meta.title || meta.vigil) { i++; break; } else continue; }
      var m = line.match(/^(title|vigil|folio):\s*(.*)$/i);
      if (m) meta[m[1].toLowerCase()] = m[2].trim();
      else break;
    }

    var blocks = [];
    var body = lines.slice(i).join("\n");
    body.split(/\n\s*\n/).forEach(function (raw) {
      var block = raw.trim();
      if (!block) return;
      if (/^\*{3,}$/.test(block)) { blocks.push({ type: "break" }); return; }
      var img = block.match(IMG_RE);
      if (img) {
        var src = img[2].trim();
        if (src.indexOf("/") === -1) src = "assets/chapters/" + src;
        blocks.push({ type: "img", caption: img[1].trim(), src: src });
        return;
      }
      blocks.push({ type: "p", text: block.replace(/\s*\n\s*/g, " ") });
    });

    return { meta: meta, blocks: blocks };
  }

  /* "VIGIL I — THE COMMISSION" → "VIGIL I" */
  function vigilShort(vigil) {
    return (vigil || "").split("—")[0].trim();
  }

  /* append a paragraph's text with *italics* as real <em> nodes */
  function appendRich(el, text) {
    text.split(/\*([^*\n]+)\*/g).forEach(function (part, idx) {
      if (!part) return;
      if (idx % 2 === 1) {
        var em = document.createElement("em");
        em.textContent = part;
        el.appendChild(em);
      } else {
        el.appendChild(document.createTextNode(part));
      }
    });
  }

  function render(blocks, container) {
    container.textContent = "";
    blocks.forEach(function (block) {
      if (block.type === "break") {
        var brk = document.createElement("p");
        brk.className = "chapter-break";
        brk.setAttribute("aria-hidden", "true");
        brk.textContent = "✦";
        container.appendChild(brk);
      } else if (block.type === "img") {
        var fig = document.createElement("figure");
        fig.className = "chapter-figure";
        var img = document.createElement("img");
        img.src = block.src;
        img.alt = block.caption;
        img.loading = "lazy";
        fig.appendChild(img);
        if (block.caption) {
          var cap = document.createElement("figcaption");
          cap.textContent = block.caption;
          fig.appendChild(cap);
        }
        container.appendChild(fig);
      } else {
        var p = document.createElement("p");
        appendRich(p, block.text);
        container.appendChild(p);
      }
    });
  }

  return { parse: parse, render: render, vigilShort: vigilShort };
})();
