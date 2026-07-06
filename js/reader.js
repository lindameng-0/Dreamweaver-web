/* Dreamweaver — chapter reader */

(function () {
  "use strict";

  var chapters = window.DW_CHAPTERS || [];
  var ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
               "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"];

  /* which chapter? (?ch=N, 1-based) */
  var n = parseInt(new URLSearchParams(location.search).get("ch"), 10);
  if (isNaN(n) || n < 1 || n > chapters.length) n = 1;
  var i = n - 1;
  var ch = chapters[i];

  document.title = ch.title + " — Dreamweaver";

  /* header */
  document.getElementById("crumb-vigil").textContent = ch.vigilShort;
  document.getElementById("ch-kicker").textContent =
    ch.vigil + "  ·  CHAPTER " + ROMAN[i] + "  ·  FOLIO " + ch.folio;
  document.getElementById("ch-title").textContent = ch.title;

  /* body */
  var body = document.getElementById("ch-body");
  ch.paras.forEach(function (para) {
    if (para === "---") {
      var brk = document.createElement("p");
      brk.className = "chapter-break";
      brk.setAttribute("aria-hidden", "true");
      brk.textContent = "✦";
      body.appendChild(brk);
    } else {
      var p = document.createElement("p");
      p.textContent = para;
      body.appendChild(p);
    }
  });

  /* prev / next */
  var prev = document.getElementById("nav-prev");
  var next = document.getElementById("nav-next");

  if (i > 0) {
    prev.href = "read.html?ch=" + i;
    prev.querySelector(".ch-nav-title").textContent = chapters[i - 1].title;
  } else {
    prev.classList.add("is-disabled");
    prev.removeAttribute("href");
    prev.setAttribute("aria-disabled", "true");
    prev.querySelector(".ch-nav-title").textContent = "This is the first chapter";
  }

  if (i < chapters.length - 1) {
    next.href = "read.html?ch=" + (i + 2);
    next.querySelector(".ch-nav-title").textContent = chapters[i + 1].title;
  } else {
    next.classList.add("is-disabled");
    next.removeAttribute("href");
    next.setAttribute("aria-disabled", "true");
    next.querySelector(".ch-nav-title").textContent = "Vigil III — forthcoming";
    document.getElementById("ch-finis").textContent = "finis vigiliae secundae";
  }

  /* gold reading-progress bar */
  var bar = document.getElementById("read-progress-bar");
  var ticking = false;
  function paint() {
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    var p = max > 0 ? Math.min(1, Math.max(0, doc.scrollTop / max)) : 0;
    bar.style.transform = "scaleX(" + p + ")";
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(paint); }
  }, { passive: true });
  paint();
})();
