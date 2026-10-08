/* Snow Day Forecaster — live state board. Runs the published model (model.js) for a list of
   cities embedded in the page and shows the chance of a snow day tomorrow in each. */
(function () {
  "use strict";
  if (!window.SnowModel || !window.SDF_COEF) return;
  var M = window.SnowModel.load(window.SDF_COEF);
  var FORECAST = "https://api.open-meteo.com/v1/forecast", CACHE_MIN = 30;
  var el = document.getElementById("stateboard"), src = document.getElementById("sb-cities");
  if (!el || !src) return;
  var cities; try { cities = JSON.parse(src.textContent); } catch (e) { return; }

  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function band(p) {
    if (p >= 0.9) return ["Almost certain", "b5"]; if (p >= 0.7) return ["Very likely", "b4"];
    if (p >= 0.5) return ["Likely", "b3"]; if (p >= 0.3) return ["Possible", "b2"];
    if (p >= 0.1) return ["Unlikely", "b1"]; return ["Very unlikely", "b0"];
  }
  function wx(c) {
    var key = "sdf:v1:" + c.lat.toFixed(2) + "," + c.lon.toFixed(2), cached = store(key);
    if (cached && Date.now() - cached.t < CACHE_MIN * 6e4) return Promise.resolve(cached.wx);
    var q = "?latitude=" + c.lat.toFixed(3) + "&longitude=" + c.lon.toFixed(3) +
      "&daily=snowfall_sum,precipitation_sum,temperature_2m_max,apparent_temperature_min" +
      "&past_days=7&forecast_days=5&timezone=auto&temperature_unit=fahrenheit&precipitation_unit=inch";
    return fetch(FORECAST + q).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (j) { var w = { daily: j.daily, limited: false, src: "Open-Meteo" }; store(key, { t: Date.now(), wx: w }); return w; });
  }
  function score(c) {
    return wx(c).then(function (w) {
      var d = w.daily, pack = M.packSeries(d), todayIso = new Date().toLocaleDateString("en-CA");
      var i0 = d.time.indexOf(todayIso); if (i0 < 0) i0 = d.time.length - 5;
      var tier = M.tierFor(c.st, c.lat), days = [];
      for (var k = 1; k <= 2 && i0 + k < d.time.length; k++) {
        var i = i0 + k, f = M.features(d, i, pack), p = M.probability(f, tier), wk = new Date(d.time[i] + "T12:00:00").getDay();
        days.push({ iso: d.time[i], p: p, f: f, weekend: wk === 0 || wk === 6 });
      }
      return { c: c, days: days };
    }).catch(function () { return { c: c, err: true }; });
  }
  function cell(x) {
    if (!x) return "<td>—</td>";
    if (x.weekend) return '<td><span class="sb-wk">Weekend</span></td>';
    var pct = Math.min(99, Math.max(1, Math.round(x.p * 100))), b = band(x.p);
    return '<td><span class="sb-pct ' + b[1] + '"><b>' + pct + '%</b> ' + b[0] + "</span></td>";
  }
  function dayHead(iso, k) {
    var dt = new Date(iso + "T12:00:00");
    return (k === 0 ? "Tomorrow, " : "") + dt.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  }
  function render(rows) {
    var first = rows.filter(function (r) { return !r.err; })[0];
    var h1 = first ? dayHead(first.days[0].iso, 0) : "Tomorrow", h2 = first && first.days[1] ? dayHead(first.days[1].iso, 1) : "Day after";
    var h = '<div class="tw"><table class="sb"><thead><tr><th>City</th><th>' + esc(h1) + "</th><th>" + esc(h2) + "</th><th>Why</th></tr></thead><tbody>";
    rows.forEach(function (r) {
      h += "<tr><td><a href=\"/?zip=" + esc(r.c.zip) + '">' + esc(r.c.name) + "</a></td>";
      if (r.err) h += "<td colspan=\"3\">Forecast unavailable</td>";
      else h += cell(r.days[0]) + cell(r.days[1]) + "<td class=\"sb-why\">" + esc(M.driver(r.days[0].f)) + "</td>";
      h += "</tr>";
    });
    h += "</tbody></table></div>";
    var lead = rows.filter(function (r) { return !r.err && !r.days[0].weekend; });
    var sumEl = document.getElementById("sb-summary");
    if (!lead.length && sumEl) sumEl.textContent = rows.some(function (r) { return !r.err; }) ? "Tomorrow is a weekend, so no school day to forecast; the day-after column shows Monday where available." : "The forecast service didn’t answer. Reload in a minute, or check a single ZIP code on the calculator.";
    if (lead.length) {
      var top = lead.slice().sort(function (a, b) { return b.days[0].p - a.days[0].p; })[0];
      var avg = lead.reduce(function (s, r) { return s + r.days[0].p; }, 0) / lead.length;
      var sum = document.getElementById("sb-summary");
      if (sum) sum.textContent = "Right now the highest chance tomorrow is " + Math.round(top.days[0].p * 100) + "% in " + top.c.name +
        "; the average across these " + lead.length + " cities is " + Math.round(avg * 100) + "%. Updated " + new Date().toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }) + " from the latest forecast.";
    }
    el.innerHTML = h; el.removeAttribute("aria-busy");
  }
  el.setAttribute("aria-busy", "true");
  Promise.all(cities.map(score)).then(render);
})();
