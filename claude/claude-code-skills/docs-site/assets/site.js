(function () {
  var nav = document.getElementById("nav"), page = window.PAGE || "";
  if (nav && window.NAV) {
    nav.innerHTML = window.NAV.map(function (sec) {
      var open = sec.items.some(function (it) { return it[0] === page; });
      return "<details" + (open ? " open" : "") + "><summary>" + sec.label + "</summary>" + sec.items.map(function (it) {
        return '<a href="' + (window.SITE_ROOT || ".") + "/" + it[0] + '"' + (it[0] === page ? ' class="cur"' : "") + ">" +
          it[1].replace(/[&<>]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]; }) + "</a>";
      }).join("") + "</details>";
    }).join("");
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
})();
