/* Dreamweaver — chapter reader (loads chapters/<file> per manifest order) */

(function () {
  "use strict";

  var ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
               "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
               "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX"];

  function fetchChapter(file) {
    return fetch("chapters/" + file, { cache: "no-cache" })
      .then(function (res) {
        if (!res.ok) throw new Error("chapter fetch failed: " + res.status);
        return res.text();
      })
      .then(window.DWFormat.parse);
  }

  fetch("chapters/manifest.json", { cache: "no-cache" })
    .then(function (res) {
      if (!res.ok) throw new Error("manifest fetch failed: " + res.status);
      return res.json();
    })
    .then(function (manifest) {
      var files = manifest.chapters || [];
      if (!files.length) throw new Error("no chapters in manifest");

      var n = parseInt(new URLSearchParams(location.search).get("ch"), 10);
      if (isNaN(n) || n < 1 || n > files.length) n = 1;
      var i = n - 1;

      return Promise.all([
        fetchChapter(files[i]),
        i > 0 ? fetchChapter(files[i - 1]) : null,
        i < files.length - 1 ? fetchChapter(files[i + 1]) : null
      ]).then(function (loaded) {
        var ch = loaded[0], prevCh = loaded[1], nextCh = loaded[2];

        document.title = ch.meta.title + " — Dreamweaver";

        var crumb = document.querySelector(".reader-crumb");
        if (crumb) {
          crumb.textContent = "DREAMWEAVER";
          if (ch.meta.vigil) {
            crumb.textContent += " · " + window.DWFormat.vigilShort(ch.meta.vigil);
          }
        }

        var kicker = [];
        if (ch.meta.vigil) kicker.push(ch.meta.vigil);
        // only add "CHAPTER N" when the title doesn't already name the section
        if (!/^(chapter|prologue|epilogue|interlude|prelude|part)\b/i.test(ch.meta.title)) {
          kicker.push("CHAPTER " + (ROMAN[i] || n));
        }
        if (ch.meta.folio) kicker.push("FOLIO " + ch.meta.folio);
        document.getElementById("ch-kicker").textContent = kicker.join("  ·  ");
        document.getElementById("ch-title").textContent = ch.meta.title;

        window.DWFormat.render(ch.blocks, document.getElementById("ch-body"));

        var prev = document.getElementById("nav-prev");
        var next = document.getElementById("nav-next");

        if (prevCh) {
          prev.href = "read.html?ch=" + i;
          prev.querySelector(".ch-nav-title").textContent = prevCh.meta.title;
        } else {
          prev.classList.add("is-disabled");
          prev.removeAttribute("href");
          prev.setAttribute("aria-disabled", "true");
          prev.querySelector(".ch-nav-title").textContent = "This is the first chapter";
        }

        if (nextCh) {
          next.href = "read.html?ch=" + (i + 2);
          next.querySelector(".ch-nav-title").textContent = nextCh.meta.title;
        } else {
          next.classList.add("is-disabled");
          next.removeAttribute("href");
          next.setAttribute("aria-disabled", "true");
          var coming = manifest.forthcoming
            ? window.DWFormat.vigilShort(manifest.forthcoming) + " — forthcoming"
            : "The story continues soon";
          next.querySelector(".ch-nav-title").textContent = coming;
          document.getElementById("ch-finis").textContent = "finis — for now";
        }
      });
    })
    .catch(function (err) {
      document.getElementById("ch-title").textContent = "The page is missing";
      var body = document.getElementById("ch-body");
      body.textContent = "";
      var p = document.createElement("p");
      p.textContent = "This chapter could not be found in the Somnium Records. " +
        "Return to the contents and try another door.";
      body.appendChild(p);
      if (window.console) console.error(err);
    });

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
