/* Dreamweaver — reveals, nav state, hero burst ornament */

(function () {
  "use strict";

  /* radial burst ornament in the hero (24 fine spokes) */
  var burst = document.getElementById("burst-lines");
  if (burst) {
    var NS = "http://www.w3.org/2000/svg";
    for (var i = 0; i < 24; i++) {
      var a = (i / 24) * Math.PI * 2;
      var line = document.createElementNS(NS, "line");
      line.setAttribute("x1", (Math.cos(a) * 14).toFixed(2));
      line.setAttribute("y1", (Math.sin(a) * 14).toFixed(2));
      line.setAttribute("x2", (Math.cos(a) * 30).toFixed(2));
      line.setAttribute("y2", (Math.sin(a) * 30).toFixed(2));
      burst.appendChild(line);
    }
  }

  /* scroll reveals */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach(function (el) { revealObserver.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in-view"); });
  }

  /* active nav link follows the section in view */
  var links = document.querySelectorAll(".nav-link");
  var sections = document.querySelectorAll("section[id]");
  if ("IntersectionObserver" in window && links.length && sections.length) {
    var navObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.getAttribute("id");
          links.forEach(function (link) {
            link.classList.toggle(
              "active",
              link.getAttribute("href") === "#" + id
            );
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (s) { navObserver.observe(s); });
  }
})();
