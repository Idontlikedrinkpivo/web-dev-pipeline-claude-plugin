(function () {
  var nav = document.getElementById("nav"), page = window.PAGE || "";
  if (nav && window.NAV) {
    var root0 = window.SITE_ROOT || ".";
    var h = function (t) { return t.replace(/[&<>]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]; }); };
    var link = function (it) {
      return '<a href="' + root0 + "/" + it[0] + '"' + (it[0] === page ? ' class="cur" aria-current="page"' : "") + ">" +
        (it[2] ? '<b class="id">' + h(it[2]) + "</b>" : "") + "<span>" + h(it[1]) + "</span></a>";
    };
    nav.innerHTML = window.NAV.map(function (sec) {
      return '<div class="sec"><div class="sec-h">' + h(sec.label) + "</div>" + sec.items.map(function (it) {
        if (!it.g) return link(it);
        var open = it.items.some(function (x) { return x[0] === page; });
        return '<details class="grp"' + (open ? " open" : "") + "><summary><span>" + h(it.g) + "</span><em>" +
          it.items.length + "</em></summary><div>" + it.items.map(link).join("") + "</div></details>";
      }).join("") + "</div>";
    }).join("");
    var cur = nav.querySelector("a.cur");
    if (cur) nav.scrollTop = cur.offsetTop - nav.clientHeight / 2;  // the menu only, not the page
  }
  var foot = document.getElementById("foot");
  if (foot && window.FOOT) foot.textContent = window.FOOT;
  var q = document.getElementById("q"), box = document.getElementById("results");
  var root = window.SITE_ROOT || ".", docs = window.DOCS || [], ids = window.IDS || {};
  var sel = -1;
  function go(u) { location.href = root + "/" + u; }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function render() {
    var v = q.value.trim(), out = [];
    if (!v) { box.style.display = "none"; return; }
    var id = v.toUpperCase().replace(/^З/, "З");
    if (ids[id] || ids[v]) out.push('<a href="' + root + "/" + (ids[id] || ids[v]) + '"><b>' + esc(v) + "</b><small>перейти к определению</small></a>");
    var words = v.toLowerCase().split(/\s+/).filter(Boolean), hits = [];
    docs.forEach(function (d) {
      var hay = (d.t + " " + d.x).toLowerCase(), ok = words.every(function (w) { return hay.indexOf(w) >= 0; });
      if (!ok) return;
      var score = words.reduce(function (s, w) { return s + (d.t.toLowerCase().indexOf(w) >= 0 ? 10 : 0); }, 0);
      var i = d.x.toLowerCase().indexOf(words[0]), snip = d.x.slice(Math.max(0, i - 60), i + 120);
      hits.push({d: d, s: score, snip: snip});
    });
    hits.sort(function (a, b) { return b.s - a.s; }).slice(0, 20).forEach(function (h) {
      out.push('<a href="' + root + "/" + h.d.u + '">' + esc(h.d.t) + "<small>" + esc(h.d.s ? h.d.s + " · " : "") + "…" + esc(h.snip) + "…</small></a>");
    });
    if (!out.length) out.push("<a>Ничего не найдено</a>");
    box.innerHTML = out.join(""); box.style.display = "block"; sel = -1;
  }
  if (q) {
    q.addEventListener("input", render);
    q.addEventListener("keydown", function (e) {
      var items = box.querySelectorAll("a[href]");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault(); sel = Math.max(0, Math.min(items.length - 1, sel + (e.key === "ArrowDown" ? 1 : -1)));
        items.forEach(function (a, i) { a.classList.toggle("on", i === sel); });
      } else if (e.key === "Enter" && items.length) { location.href = items[Math.max(sel, 0)].href; }
      else if (e.key === "Escape") { box.style.display = "none"; q.blur(); }
    });
    document.addEventListener("click", function (e) { if (!box.contains(e.target) && e.target !== q) box.style.display = "none"; });
    document.addEventListener("keydown", function (e) { if (e.key === "/" && document.activeElement !== q) { e.preventDefault(); q.focus(); } });
  }
  document.querySelectorAll("nav a").forEach(function (a) { a.addEventListener("click", function () { document.body.classList.remove("nav-open"); }); });

  // Back to the same spot. Before a link takes the reader elsewhere on the site, the page keeps where they were (a
  // stack in the tab's sessionStorage). «← Назад» in the header and the browser's Back return to that spot, and the
  // API page's «Назад к документации» returns to the page and the spot the reader came from.
  function load(k) { try { return JSON.parse(sessionStorage.getItem(k) || "null"); } catch (e) { return null; } }
  function keep(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  var here = location.pathname, stack = load("docs-back") || [], back = document.getElementById("back");
  var nt = (window.performance && performance.getEntriesByType && (performance.getEntriesByType("navigation")[0] || {}).type) || "";
  var at = -1;
  for (var k = stack.length - 1; k >= 0; k--) if (stack[k].p === here) { at = k; break; }
  if (at >= 0 && (nt === "back_forward" || load("docs-ret") === here)) {
    var y = stack[at].y;
    stack = stack.slice(0, at); keep("docs-back", stack);
    try { sessionStorage.removeItem("docs-ret"); } catch (e) {}
    window.scrollTo(0, y);
    window.addEventListener("load", function () { window.scrollTo(0, y); });
  }
  function show() {
    var top = stack[stack.length - 1];
    if (!back) return;
    back.hidden = !top;
    if (top) back.title = "Вернуться: " + top.t;
  }
  show();
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a || a === back || a.target === "_blank" || a.origin !== location.origin) return;
    if (a.pathname === here && !a.hash) return;
    stack.push({p: here, y: window.scrollY, t: document.title.split(" — ")[0], h: a.pathname === here ? a.hash : ""});
    stack = stack.slice(-50); keep("docs-back", stack); show();
  }, true);
  window.addEventListener("popstate", function () {  // the browser's Back after a jump inside the page
    var top = stack[stack.length - 1];
    if (top && top.p === here && top.h && location.hash !== top.h) { stack.pop(); keep("docs-back", stack); show(); }
  });
  if (back) back.addEventListener("click", function (e) {
    e.preventDefault();
    var top = stack[stack.length - 1];
    if (!top) return;
    if (top.p === here) { stack.pop(); keep("docs-back", stack); show(); window.scrollTo(0, top.y); return; }
    keep("docs-ret", top.p);
    location.href = top.p;
  });
})();
