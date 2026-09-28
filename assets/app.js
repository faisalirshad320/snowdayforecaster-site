/* Snow Day Forecaster — predictor UI. Depends on model.js (window.SnowModel) and window.SDF_COEF. */
(function () {
  "use strict";
  var M = window.SnowModel.load(window.SDF_COEF);
  var CFG = {
    forecast: "https://api.open-meteo.com/v1/forecast",   // swap to customer-api.open-meteo.com + apikey on a paid plan
    apikey: "",
    nws: "https://api.weather.gov",
    cacheMin: 30
  };
  var $ = function (id) { return document.getElementById(id); };
  var form = $("zip-form"), input = $("zip"), out = $("result"), status = $("status"), geoBtn = $("geo");

  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function say(msg, isErr) { status.textContent = msg; status.className = "status" + (isErr ? " err" : ""); }

  function lookupZip(zip) {
    return fetch("/zip/" + zip.slice(0, 2) + ".json").then(function (r) {
      if (!r.ok) throw new Error("zip");
      return r.json();
    }).then(function (t) {
      var e = t[zip];
      if (!e) throw new Error("zip");
      return { lat: e[0], lon: e[1], place: e[2] + ", " + e[3], state: e[3] };
    });
  }

  function getJSON(url) {
    return fetch(url, { headers: { Accept: "application/geo+json, application/json" } }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }

  function openMeteo(lat, lon) {
    var q = "?latitude=" + lat.toFixed(3) + "&longitude=" + lon.toFixed(3) +
      "&daily=snowfall_sum,precipitation_sum,temperature_2m_max,apparent_temperature_min" +
      "&past_days=7&forecast_days=5&timezone=auto&temperature_unit=fahrenheit&precipitation_unit=inch" +
      (CFG.apikey ? "&apikey=" + CFG.apikey : "");
    return getJSON(CFG.forecast + q).then(function (j) { return { daily: j.daily, limited: false, src: "Open-Meteo" }; });
  }

  // Fallback: NWS gridpoint forecast (no past days, so snow already on the ground is unknown).
  function nwsDaily(lat, lon) {
    return getJSON(CFG.nws + "/points/" + lat.toFixed(4) + "," + lon.toFixed(4)).then(function (pt) {
      var tz = pt.properties.timeZone;
      return getJSON(pt.properties.forecastGridData).then(function (g) {
        var P = g.properties, fmt = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" });
        var days = {};
        function day(vt) { return fmt.format(new Date(vt.split("/")[0])); }
        function each(layer, fn) { (P[layer] && P[layer].values || []).forEach(function (v) { if (v.value !== null) fn(day(v.validTime), v.value); }); }
        function rec(k) { return days[k] || (days[k] = { snow: 0, qpf: 0, tmax: -99, amin: 99 }); }
        each("snowfallAmount", function (k, v) { rec(k).snow += v / 25.4; });
        each("quantitativePrecipitation", function (k, v) { rec(k).qpf += v / 25.4; });
        each("maxTemperature", function (k, v) { var r = rec(k); r.tmax = Math.max(r.tmax, v * 9 / 5 + 32); });
        each("apparentTemperature", function (k, v) { var r = rec(k); r.amin = Math.min(r.amin, v * 9 / 5 + 32); });
        var keys = Object.keys(days).sort().slice(0, 5);
        var today = keys[0], d0 = new Date(today + "T12:00:00Z");
        var d = { time: [], snowfall_sum: [], precipitation_sum: [], temperature_2m_max: [], apparent_temperature_min: [] };
        for (var b = 2; b >= 1; b--) {          // two neutral padding days before today
          var pd = new Date(d0.getTime() - b * 864e5).toISOString().slice(0, 10);
          d.time.push(pd); d.snowfall_sum.push(0); d.precipitation_sum.push(0); d.temperature_2m_max.push(45); d.apparent_temperature_min.push(40);
        }
        keys.forEach(function (k) {
          var r = days[k];
          d.time.push(k); d.snowfall_sum.push(r.snow); d.precipitation_sum.push(r.qpf);
          d.temperature_2m_max.push(r.tmax > -99 ? r.tmax : 40); d.apparent_temperature_min.push(r.amin < 99 ? r.amin : 35);
        });
        return { daily: d, limited: true, src: "National Weather Service" };
      });
    });
  }

  function alerts(lat, lon) {
    return getJSON(CFG.nws + "/alerts/active?point=" + lat.toFixed(4) + "," + lon.toFixed(4)).then(function (j) {
      return (j.features || []).map(function (f) { return f.properties.event; })
        .filter(function (e) { return /winter|snow|ice|blizzard|cold|chill|freez/i.test(e); })
        .filter(function (e, i, a) { return a.indexOf(e) === i; });
    }).catch(function () { return []; });
  }

  function band(p) {
    if (p >= 0.9) return ["Almost certain", "b5"];
    if (p >= 0.7) return ["Very likely", "b4"];
    if (p >= 0.5) return ["Likely", "b3"];
    if (p >= 0.3) return ["Possible", "b2"];
    if (p >= 0.1) return ["Unlikely", "b1"];
    return ["Very unlikely", "b0"];
  }
  function dayName(iso, k) {
    var dt = new Date(iso + "T12:00:00");
    var name = dt.toLocaleDateString("en-US", { weekday: "long" });
    return (k === 0 ? "Tomorrow · " : "") + name + ", " + dt.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }

  function predict(loc) {
    var key = "sdf:v1:" + loc.lat.toFixed(2) + "," + loc.lon.toFixed(2), cached = store(key);
    var wx = cached && Date.now() - cached.t < CFG.cacheMin * 6e4 ? Promise.resolve(cached.wx) :
      openMeteo(loc.lat, loc.lon).catch(function () { return nwsDaily(loc.lat, loc.lon); }).then(function (w) { store(key, { t: Date.now(), wx: w }); return w; });
    return Promise.all([wx, alerts(loc.lat, loc.lon)]).then(function (res) {
      var w = res[0], d = w.daily, pack = M.packSeries(d);
      var todayIso = new Date().toLocaleDateString("en-CA");
      var i0 = d.time.indexOf(todayIso); if (i0 < 0) i0 = d.time.length - 5;
      var tier = M.tierFor(loc.state, loc.lat), days = [];
      for (var k = 1; k <= 3 && i0 + k < d.time.length; k++) {
        var i = i0 + k, f = M.features(d, i, pack), p = M.probability(f, tier);
        var wk = new Date(d.time[i] + "T12:00:00").getDay();
        days.push({ iso: d.time[i], p: p, f: f, weekend: wk === 0 || wk === 6 });
      }
      return { loc: loc, days: days, alerts: res[1], limited: w.limited, src: w.src };
    });
  }

  function render(r) {
    var h = '<p class="place">' + esc(r.loc.place) + "</p>";
    if (r.alerts.length) h += '<p class="alert" role="note">NWS: ' + r.alerts.map(esc).join(" · ") + "</p>";
    h += '<ol class="days">';
    r.days.forEach(function (x, k) {
      var pct = Math.min(99, Math.max(1, Math.round(x.p * 100))), b = band(x.p);
      var delay = !x.weekend && x.p >= 0.12 && x.p < 0.45 ? '<span class="delay">Delay possible</span>' : "";
      h += '<li class="day ' + (k === 0 ? "lead " : "") + b[1] + '">' +
        '<p class="when">' + dayName(x.iso, k) + "</p>" +
        (x.weekend ? '<p class="pct wk">Weekend</p><p class="why">' + esc(M.driver(x.f)) + "</p>" :
          '<p class="pct"><span>' + pct + '</span>%</p><p class="verdict">' + b[0] + " " + delay + "</p>" +
          '<div class="bar" aria-hidden="true"><i style="width:' + Math.max(2, pct) + '%"></i></div>' +
          '<p class="why">' + esc(M.driver(x.f)) + "</p>") + "</li>";
    });
    h += "</ol>";
    if (r.limited) h += '<p class="note">Backup forecast in use: snow already on the ground isn’t counted, so after a storm the real chance may be higher.</p>';
    h += '<p class="note">Forecast: ' + esc(r.src) + '. Your district decides; this is a probability, not an announcement. <a href="/methodology/">How accurate is it?</a></p>' +
      '<div class="share"><button type="button" id="share">Share this forecast</button></div>';
    out.innerHTML = h; out.hidden = false;
    var sb = $("share");
    sb.addEventListener("click", function () {
      var url = location.origin + "/?zip=" + (r.loc.zip || ""), lead = r.days.filter(function (x) { return !x.weekend; })[0];
      var text = lead ? Math.round(lead.p * 100) + "% chance of a snow day " + dayName(lead.iso, 1).split(",")[0] + " in " + r.loc.place : "Snow day forecast";
      if (navigator.share) navigator.share({ title: "Snow Day Forecaster", text: text, url: url }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(text + " " + url).then(function () { sb.textContent = "Link copied"; });
    });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function run(loc) {
    say("Checking the forecast…");
    out.setAttribute("aria-busy", "true");
    return predict(loc).then(function (r) { render(r); say(""); })
      .catch(function () { say("The forecast service didn’t answer. Try again in a minute.", true); })
      .then(function () { out.removeAttribute("aria-busy"); });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var zip = input.value.trim();
    if (!/^\d{5}$/.test(zip)) { say("Enter a 5-digit US ZIP code.", true); input.focus(); return; }
    lookupZip(zip).then(function (loc) {
      loc.zip = zip; store("sdf:zip", zip);
      history.replaceState(null, "", "/?zip=" + zip);
      return run(loc);
    }).catch(function () { say("We couldn’t find ZIP " + zip + ". Check the number and try again.", true); });
  });

  if (geoBtn && navigator.geolocation) {
    geoBtn.hidden = false;
    geoBtn.addEventListener("click", function () {
      say("Finding your location…");
      navigator.geolocation.getCurrentPosition(function (pos) {
        var lat = pos.coords.latitude, lon = pos.coords.longitude;
        getJSON(CFG.nws + "/points/" + lat.toFixed(4) + "," + lon.toFixed(4)).then(function (pt) {
          var rl = pt.properties.relativeLocation.properties;
          return run({ lat: lat, lon: lon, place: rl.city + ", " + rl.state, state: rl.state });
        }).catch(function () { say("Location works for US addresses only. Enter a ZIP instead.", true); });
      }, function () { say("Location permission was declined. Enter a ZIP instead.", true); }, { timeout: 10000 });
    });
  }

  var qz = new URLSearchParams(location.search).get("zip") || store("sdf:zip");
  if (qz && /^\d{5}$/.test(qz)) { input.value = qz; form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event("submit")); }
})();
