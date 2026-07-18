/* Dreamweaver — builds the novel table of contents from chapters/manifest.json */

(function () {
  "use strict";

  var list = document.getElementById("toc-list");
  if (!list) return;

  fetch("chapters/manifest.json", { cache: "no-cache" })
    .then(function (res) { return res.json(); })
    .then(function (manifest) {
      var files = manifest.chapters || [];
      return Promise.all(files.map(function (file) {
        return fetch("chapters/" + file, { cache: "no-cache" })
          .then(function (res) { return res.text(); })
          .then(function (text) { return window.DWFormat.parse(text).meta; });
      })).then(function (metas) {
        list.textContent = "";
        var lastVigil = null;

        metas.forEach(function (meta, idx) {
          if (meta.vigil && meta.vigil !== lastVigil) {
            lastVigil = meta.vigil;
            var vig = document.createElement("li");
            vig.className = "toc-vigil";
            vig.textContent = meta.vigil;
            list.appendChild(vig);
          }
          var li = document.createElement("li");
          li.className = "toc-row";
          var a = document.createElement("a");
          a.className = "toc-link";
          a.href = "read.html?ch=" + (idx + 1);
          var span = document.createElement("span");
          span.textContent = meta.title;
          var leader = document.createElement("i");
          var folio = document.createElement("b");
          folio.textContent = meta.folio || "";
          a.appendChild(span); a.appendChild(leader); a.appendChild(folio);
          li.appendChild(a);
          list.appendChild(li);
        });

        if (manifest.forthcoming) {
          var vig = document.createElement("li");
          vig.className = "toc-vigil";
          vig.textContent = manifest.forthcoming;
          list.appendChild(vig);
          var li = document.createElement("li");
          li.className = "toc-row toc-muted";
          li.innerHTML = "<span>— forthcoming —</span><i></i><b>&nbsp;</b>";
          list.appendChild(li);
        }
      });
    })
    .catch(function (err) {
      var li = document.createElement("li");
      li.className = "toc-row toc-muted";
      li.textContent = "The contents could not be loaded.";
      list.appendChild(li);
      if (window.console) console.error(err);
    });
})();
